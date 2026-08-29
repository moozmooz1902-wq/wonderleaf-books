"""Background worker: the loop behind the Play button.

Runs as its own process so it survives the UI redrawing, and keeps going while
you work. Every cycle it:

  1. reads control.json for stop/pause/refill commands from the UI
  2. tops the queue up when it runs dry, choosing products the way the
     analytics say to - listings that sell get more videos, dead ones get none
  3. claims one task, builds it, writes the result, and persists state

State lives entirely on disk, so closing the laptop mid-task loses at most the
task in flight - it returns to pending on the next start.

  python -m wonderfeed.worker            # run until stopped
  python -m wonderfeed.worker --once     # single task, for testing
"""

import argparse
import json
import os
import random
import signal
import sys
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path

from . import listings as listings_mod
from .config import ConfigError, load_products, load_settings, resolve_path, secret
from .queue import DONE, FAILED, PENDING, Queue
from .run import build_one, pick_jobs
from .state import State

DEFAULTS = {
    "poll_seconds": 3,
    "refill_batch": 12,
    "daily_cap": 24,
    "idle_sleep": 20,
    "log_lines": 200,
}


def paths(settings):
    out = resolve_path(settings["output"]["dir"])
    return {
        "out": out,
        "queue": out / "queue.json",
        "status": out / "worker_status.json",
        "control": out / "control.json",
        "pid": out / "worker.pid",
    }


def live_worker_pid(p):
    """PID of a worker already running, or None.

    The queue is single-writer by design. Two workers racing on it corrupt the
    ordering and, worse, spend twice the API budget - so this is enforced rather
    than assumed.
    """
    try:
        pid = int(p["pid"].read_text().strip())
    except (OSError, ValueError):
        return None
    if pid == os.getpid():
        return None
    try:
        os.kill(pid, 0)
    except OSError:
        return None  # stale pid file from a crash; safe to take over
    return pid


def worker_config(settings):
    cfg = dict(DEFAULTS)
    cfg.update(settings.get("worker") or {})
    return cfg


class Worker:
    def __init__(self, settings, products, dry_run=False):
        self.settings = settings
        self.products = products
        self.dry_run = dry_run
        self.cfg = worker_config(settings)
        self.p = paths(settings)
        self.p["out"].mkdir(parents=True, exist_ok=True)
        self.queue = Queue(self.p["queue"])
        self.state = State()
        self.log_lines = []
        self.stopping = False
        self.paused = False
        self.keys = {"anthropic": "", "fal": ""}

    # -- plumbing ---------------------------------------------------------

    def log(self, msg):
        stamp = datetime.now().strftime("%H:%M:%S")
        line = f"{stamp}  {msg}"
        self.log_lines.append(line)
        del self.log_lines[:-self.cfg["log_lines"]]
        try:
            print(line, flush=True)
        except (BrokenPipeError, OSError, ValueError):
            # The launching terminal was closed. The UI reads the log from
            # worker_status.json, so carry on writing there instead of dying.
            pass
        self.write_status()

    def write_status(self, current=None, state=None):
        payload = {
            "pid": os.getpid(),
            "state": state or ("stopping" if self.stopping
                               else "paused" if self.paused else "working"),
            "counts": self.queue.counts(),
            "done_today": self.queue.done_today(),
            "daily_cap": self.cfg["daily_cap"],
            "current": current,
            "log": self.log_lines[-60:],
            "dry_run": self.dry_run,
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }
        tmp = self.p["status"].with_suffix(".tmp")
        with tmp.open("w", encoding="utf-8") as fh:
            json.dump(payload, fh, indent=2)
        tmp.replace(self.p["status"])

    def read_control(self):
        """Commands from the UI. Consumed once, then cleared."""
        if not self.p["control"].exists():
            return {}
        try:
            with self.p["control"].open(encoding="utf-8") as fh:
                cmd = json.load(fh)
        except (json.JSONDecodeError, OSError):
            return {}
        try:
            self.p["control"].unlink()
        except OSError:
            pass
        return cmd

    def handle_control(self):
        cmd = self.read_control()
        if not cmd:
            return
        if cmd.get("stop"):
            self.log("stop requested - finishing current task")
            self.stopping = True
        if "pause" in cmd:
            self.paused = bool(cmd["pause"])
            self.log("paused" if self.paused else "resumed")
        if cmd.get("refill"):
            self.refill(int(cmd["refill"]))
        if cmd.get("retry_failed"):
            n = self.queue.retry_failed()
            self.log(f"requeued {n} failed task(s)")
        if cmd.get("clear_finished"):
            n = self.queue.clear_finished()
            self.log(f"cleared {n} finished task(s)")

    # -- planning ---------------------------------------------------------

    def priority_products(self):
        """Let the analytics steer volume: sellers get more, dead ones none.

        A listing marked CULL is not worth another video, and one that is
        selling deserves the shots. Products with no listing registered yet are
        treated as untested and stay in the pool.
        """
        cfg = listings_mod.config(self.settings)
        try:
            lst = listings_mod.Listings()
        except Exception:
            return self.products, {}

        verdicts = {}
        for listing in lst.live():
            verdict, _, _, _ = listings_mod.assess(listing, cfg, self.state)
            # Worst verdict wins if several listings share a product.
            rank = {"CULL": 0, "WATCH": 1, "NO DATA": 2, "TOO EARLY": 3, "KEEP": 4}
            pid = listing["product_id"]
            if pid not in verdicts or rank[verdict] < rank[verdicts[pid]]:
                verdicts[pid] = verdict

        culled = {p_id for p_id, v in verdicts.items() if v == "CULL"}
        pool = [p for p in self.products if p["id"] not in culled]
        # Sellers appear twice, so they take roughly double the volume.
        for p in list(pool):
            if verdicts.get(p["id"]) == "KEEP":
                pool.append(p)
        return (pool or self.products), verdicts

    def refill(self, n=None):
        n = n or self.cfg["refill_batch"]
        pool, verdicts = self.priority_products()
        keeps = sum(1 for v in verdicts.values() if v == "KEEP")
        culls = sum(1 for v in verdicts.values() if v == "CULL")
        try:
            jobs = pick_jobs(pool, self.state, self.settings, n, None, random)
        except ConfigError as exc:
            self.log(f"cannot plan work: {exc}")
            return 0
        self.queue.enqueue_many([
            {"kind": "video", "product_id": j["product"]["id"],
             "angle": j["angle"], "room": j["room"]}
            for j in jobs
        ])
        self.log(f"queued {len(jobs)} task(s)"
                 + (f" - {keeps} selling listing(s) prioritised, "
                    f"{culls} culled product(s) skipped" if verdicts else ""))
        return len(jobs)

    # -- execution --------------------------------------------------------

    def build(self, task):
        product = next((p for p in self.products if p["id"] == task["product_id"]), None)
        if not product:
            raise ConfigError(f"product '{task['product_id']}' is no longer in products.yaml")
        job = {"product": product, "angle": task["angle"], "room": task["room"]}
        out_dir = resolve_path(self.settings["output"]["dir"])
        result = build_one(job, self.settings, self.state, self.keys, out_dir,
                           self.dry_run, log=lambda m: self.log(f"    {m.strip()}"))
        self.state.save()
        return result

    def cycle(self):
        self.handle_control()
        if self.stopping:
            return False

        if self.paused:
            self.write_status(state="paused")
            time.sleep(self.cfg["poll_seconds"])
            return True

        if self.queue.done_today() >= self.cfg["daily_cap"]:
            self.write_status(state="daily cap reached")
            time.sleep(self.cfg["idle_sleep"])
            return True

        if self.queue.pending_count() == 0:
            if self.refill() == 0:
                self.write_status(state="idle - nothing to build")
                time.sleep(self.cfg["idle_sleep"])
                return True

        task = self.queue.claim()
        if not task:
            time.sleep(self.cfg["poll_seconds"])
            return True

        label = f"{task['product_id']} / {task['angle'][:40]}"
        self.write_status(current={"id": task["id"], "label": label})
        self.log(f"building {task['id']}: {label}")
        try:
            result = self.build(task)
            self.queue.complete(task, output=result.get("path"))
            self.log(f"done {task['id']} -> {Path(result['path']).name}")
        except Exception as exc:
            self.queue.fail(task, exc)
            status = "will retry" if task["status"] == PENDING else "given up"
            self.log(f"FAILED {task['id']} ({status}): {exc}")
            traceback.print_exc(limit=2)
        self.write_status()
        return True

    def run(self, once=False):
        existing = live_worker_pid(self.p)
        if existing:
            msg = (f"Another worker is already running (pid {existing}). "
                   f"Refusing to start a second one - they would race on the "
                   f"queue and double your API spend.")
            print(msg, file=sys.stderr, flush=True)
            self.write_status(state=f"blocked: worker {existing} already running")
            return

        self.p["pid"].write_text(str(os.getpid()), encoding="utf-8")
        recovered = self.queue.recover()
        if recovered:
            self.log(f"recovered {recovered} task(s) interrupted by the last shutdown")
        self.log(f"worker started (pid {os.getpid()})"
                 + ("  [DRY RUN]" if self.dry_run else ""))

        def handle_signal(signum, frame):
            self.log("shutdown signal - stopping after this task")
            self.stopping = True

        for sig in (signal.SIGINT, signal.SIGTERM):
            try:
                signal.signal(sig, handle_signal)
            except (ValueError, OSError):
                pass  # not the main thread

        try:
            while True:
                if not self.cycle():
                    break
                if once:
                    break
        finally:
            try:
                # Only clear the lock if it is still ours.
                if self.p["pid"].exists() and \
                        self.p["pid"].read_text().strip() == str(os.getpid()):
                    self.p["pid"].unlink()
            except OSError:
                pass
            # Log first: log() rewrites status, so writing "stopped" after it
            # is what actually leaves the final state correct.
            self.log("worker stopped")
            self.write_status(state="stopped")


def main(argv=None):
    ap = argparse.ArgumentParser(description="Run the Wonderfeed background worker.")
    ap.add_argument("--once", action="store_true", help="build a single task and exit")
    ap.add_argument("--dry-run", action="store_true", help="no API calls, no spend")
    args = ap.parse_args(argv)

    try:
        settings = load_settings()
        products = load_products()
    except ConfigError as exc:
        print(f"Config error: {exc}", file=sys.stderr)
        return 2

    w = Worker(settings, products, dry_run=args.dry_run)
    if not args.dry_run:
        try:
            w.keys["anthropic"] = secret("ANTHROPIC_API_KEY")
            w.keys["fal"] = secret("FAL_KEY")
        except ConfigError as exc:
            print(f"Config error: {exc}", file=sys.stderr)
            return 2
    w.run(once=args.once)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

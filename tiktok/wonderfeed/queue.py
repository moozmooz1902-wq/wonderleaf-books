"""Durable work queue.

The whole point of the desktop tool is that you can close the laptop mid-batch
and lose nothing, so the queue lives on disk and every state change is written
immediately with an atomic replace. A task interrupted while running is picked
back up on the next start rather than silently lost.

Single-writer by design: only the worker mutates this file. The UI reads it and
sends commands through control.json instead, which removes any need for locking.
"""

import json
import os
from datetime import datetime, timezone
from pathlib import Path

PENDING = "pending"
RUNNING = "running"
DONE = "done"
FAILED = "failed"

MAX_ATTEMPTS = 2


def _now():
    return datetime.now(timezone.utc).isoformat()


class Queue:
    def __init__(self, path):
        self.path = Path(path)
        self.data = {"version": 1, "tasks": []}
        if self.path.exists():
            try:
                with self.path.open(encoding="utf-8") as fh:
                    self.data = json.load(fh)
            except (json.JSONDecodeError, OSError):
                # A torn file should not brick the tool; start clean but keep
                # the old one so nothing is silently destroyed.
                self.path.replace(self.path.with_suffix(".corrupt.json"))

    def save(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        tmp = self.path.with_suffix(".tmp")
        with tmp.open("w", encoding="utf-8") as fh:
            json.dump(self.data, fh, indent=2)
            fh.flush()
            os.fsync(fh.fileno())
        tmp.replace(self.path)

    # -- lifecycle --------------------------------------------------------

    def recover(self):
        """Anything left RUNNING died with the last process. Requeue it.

        The interrupted attempt is refunded: being killed by a shutdown is not
        the task's fault, and without this, closing the laptop twice on the same
        task would exhaust its retries and park it as failed.
        """
        recovered = 0
        for t in self.data["tasks"]:
            if t["status"] == RUNNING:
                t["status"] = PENDING
                t["started_at"] = None
                t["attempts"] = max(0, t.get("attempts", 1) - 1)
                recovered += 1
        if recovered:
            self.save()
        return recovered

    def enqueue(self, task):
        task.setdefault("status", PENDING)
        task.setdefault("attempts", 0)
        task.setdefault("created_at", _now())
        task.setdefault("id", f"t{len(self.data['tasks']) + 1:05d}")
        self.data["tasks"].append(task)
        return task

    def enqueue_many(self, tasks):
        for t in tasks:
            self.enqueue(t)
        self.save()

    def claim(self):
        """Take the oldest pending task and mark it running."""
        for t in self.data["tasks"]:
            if t["status"] == PENDING:
                t["status"] = RUNNING
                t["started_at"] = _now()
                t["attempts"] = t.get("attempts", 0) + 1
                self.save()
                return t
        return None

    def complete(self, task, output=None):
        task["status"] = DONE
        task["finished_at"] = _now()
        task["output"] = output
        task["error"] = None
        self.save()

    def fail(self, task, error):
        """Retry once, then park it as failed."""
        task["error"] = str(error)[:500]
        if task.get("attempts", 1) < MAX_ATTEMPTS:
            task["status"] = PENDING
            task["started_at"] = None
        else:
            task["status"] = FAILED
            task["finished_at"] = _now()
        self.save()

    def retry_failed(self):
        n = 0
        for t in self.data["tasks"]:
            if t["status"] == FAILED:
                t.update(status=PENDING, attempts=0, error=None, started_at=None)
                n += 1
        if n:
            self.save()
        return n

    def clear_finished(self):
        before = len(self.data["tasks"])
        self.data["tasks"] = [t for t in self.data["tasks"]
                              if t["status"] not in (DONE, FAILED)]
        self.save()
        return before - len(self.data["tasks"])

    # -- reporting --------------------------------------------------------

    def counts(self):
        c = {PENDING: 0, RUNNING: 0, DONE: 0, FAILED: 0}
        for t in self.data["tasks"]:
            c[t["status"]] = c.get(t["status"], 0) + 1
        return c

    def pending_count(self):
        return sum(1 for t in self.data["tasks"] if t["status"] == PENDING)

    def done_today(self):
        today = datetime.now(timezone.utc).date().isoformat()
        return sum(1 for t in self.data["tasks"]
                   if t["status"] == DONE and (t.get("finished_at") or "").startswith(today))

    def recent(self, limit=20):
        return sorted(
            [t for t in self.data["tasks"] if t["status"] in (DONE, FAILED)],
            key=lambda t: t.get("finished_at") or "",
            reverse=True,
        )[:limit]

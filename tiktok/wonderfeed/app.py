"""Wonderfeed desktop control panel.

  streamlit run wonderfeed/app.py

Press Play and leave it running in a background tab while you work. The worker
runs as its own detached process, so closing this page does not stop it, and
stopping the laptop mid-batch loses nothing: the queue is on disk and the
interrupted task returns to pending on the next start.
"""

import json
import os
import subprocess
import sys
import time
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from wonderfeed import listings as listings_mod  # noqa: E402
from wonderfeed.config import ConfigError, ROOT, load_products, load_settings  # noqa: E402
from wonderfeed.queue import Queue  # noqa: E402
from wonderfeed.state import State  # noqa: E402
from wonderfeed.worker import paths  # noqa: E402

REFRESH_SECONDS = 3


# -- process control -----------------------------------------------------


def worker_pid(p):
    try:
        pid = int(p["pid"].read_text().strip())
    except (OSError, ValueError):
        return None
    try:
        os.kill(pid, 0)  # signal 0 just tests for existence
    except OSError:
        return None
    return pid


def missing_keys(dry_run):
    """Keys the worker will need. Checked here so Play fails loudly, not silently."""
    if dry_run:
        return []
    return [k for k in ("ANTHROPIC_API_KEY", "FAL_KEY") if not os.environ.get(k, "").strip()]


def start_worker(dry_run):
    log_path = ROOT / "out" / "worker.log"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    args = [sys.executable, "-m", "wonderfeed.worker"]
    if dry_run:
        args.append("--dry-run")
    with log_path.open("a", encoding="utf-8") as log:
        subprocess.Popen(
            args, cwd=str(ROOT), stdout=log, stderr=subprocess.STDOUT,
            start_new_session=True,  # detached: survives this page closing
        )


def send(p, command):
    with p["control"].open("w", encoding="utf-8") as fh:
        json.dump(command, fh)


def read_status(p):
    try:
        with p["status"].open(encoding="utf-8") as fh:
            return json.load(fh)
    except (OSError, json.JSONDecodeError):
        return {}


# -- UI ------------------------------------------------------------------


def main():
    st.set_page_config(page_title="Wonderfeed", page_icon="▶", layout="wide")

    try:
        settings = load_settings()
        products = load_products()
    except ConfigError as exc:
        st.error(f"**Config error**\n\n{exc}")
        st.stop()

    p = paths(settings)
    p["out"].mkdir(parents=True, exist_ok=True)
    pid = worker_pid(p)
    running = pid is not None
    status = read_status(p)

    st.title("Wonderfeed")
    st.caption(f"{len(products)} product(s) loaded · output `{p['out']}`")

    # -- controls --------------------------------------------------------
    c1, c2, c3, c4, c5 = st.columns([1, 1, 1, 1, 3])
    dry = st.session_state.setdefault("dry_run", False)

    with c1:
        if st.button("▶  Play", type="primary", disabled=running,
                     use_container_width=True):
            gaps = missing_keys(st.session_state["dry_run"])
            if gaps:
                st.session_state["start_error"] = (
                    f"Missing {' and '.join(gaps)}. Put them in `tiktok/.env`:\n\n"
                    "```\nANTHROPIC_API_KEY=sk-ant-...\nFAL_KEY=...\n```\n"
                    "Or switch on **Dry run** to watch the loop work for free."
                )
            else:
                st.session_state.pop("start_error", None)
                start_worker(st.session_state["dry_run"])
                time.sleep(2.0)
            st.rerun()
    with c2:
        if st.button("⏸  Pause", disabled=not running, use_container_width=True):
            send(p, {"pause": not (status.get("state") == "paused")})
            time.sleep(0.5)
            st.rerun()
    with c3:
        if st.button("⏹  Stop", disabled=not running, use_container_width=True):
            send(p, {"stop": True})
            time.sleep(0.5)
            st.rerun()
    with c4:
        if st.button("↻  Refill", disabled=not running, use_container_width=True):
            send(p, {"refill": settings.get("worker", {}).get("refill_batch", 12)})
            st.rerun()
    with c5:
        st.session_state["dry_run"] = st.toggle(
            "Dry run (no API calls, no spend)", value=dry, disabled=running,
            help="Builds with placeholder visuals so you can watch the loop work "
                 "without spending anything.",
        )

    if running:
        state = status.get("state", "working")
        badge = {"paused": "⏸ paused", "stopping": "⏹ stopping"}.get(state, f"● {state}")
        st.success(f"**Worker running** (pid {pid}) — {badge}"
                   + ("  ·  DRY RUN" if status.get("dry_run") else ""))
    else:
        if st.session_state.get("start_error"):
            st.error(st.session_state["start_error"])
        else:
            log_file = ROOT / "out" / "worker.log"
            tail = ""
            if log_file.exists():
                lines = log_file.read_text(encoding="utf-8", errors="replace").splitlines()
                tail = "\n".join(lines[-6:]).strip()
            # A worker that died on startup leaves an error here and no pid.
            if tail and ("error" in tail.lower() or "traceback" in tail.lower()):
                st.error("**The worker stopped with an error.**")
                st.code(tail, language=None)
            else:
                st.info("**Stopped.** Press Play — it picks up exactly where it left off.")

    # -- counters --------------------------------------------------------
    counts = status.get("counts") or Queue(p["queue"]).counts()
    done_today = status.get("done_today", 0)
    cap = status.get("daily_cap", settings.get("worker", {}).get("daily_cap", 24))
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Today", f"{done_today}/{cap}")
    k2.metric("Queued", counts.get("pending", 0))
    k3.metric("Built", counts.get("done", 0))
    k4.metric("Failed", counts.get("failed", 0))

    current = status.get("current")
    if current and running:
        st.progress(min(done_today / max(cap, 1), 1.0),
                    text=f"Building  ·  {current.get('label', '')}")

    tab_activity, tab_output, tab_analytics = st.tabs(
        ["Activity", "Finished videos", "Analytics"]
    )

    with tab_activity:
        log = status.get("log") or []
        if log:
            st.code("\n".join(log[-40:]), language=None)
        else:
            st.caption("No activity yet. Press Play.")
        cc1, cc2 = st.columns(2)
        with cc1:
            if st.button("Retry failed tasks", disabled=not running):
                send(p, {"retry_failed": True})
                st.rerun()
        with cc2:
            if st.button("Clear finished tasks", disabled=not running):
                send(p, {"clear_finished": True})
                st.rerun()

    with tab_output:
        videos = sorted(p["out"].glob("*.mp4"), key=lambda f: f.stat().st_mtime,
                        reverse=True)
        if not videos:
            st.caption("Nothing built yet.")
        for video in videos[:12]:
            sidecar = video.with_suffix(".txt")
            with st.expander(f"{video.name}  ·  {video.stat().st_size // 1024} KB"):
                col_v, col_t = st.columns([1, 2])
                with col_v:
                    st.video(str(video))
                with col_t:
                    if sidecar.exists():
                        st.text(sidecar.read_text(encoding="utf-8"))
                    st.download_button("Download MP4", video.read_bytes(),
                                       file_name=video.name, mime="video/mp4",
                                       key=f"dl-{video.name}")

    with tab_analytics:
        st.markdown("**Which listings are selling** — drives what the worker builds next.")
        upload = st.file_uploader(
            "Seller Center CSV export", type=["csv"],
            help="Product performance export. Updates the verdicts below.",
        )
        if upload is not None:
            tmp = p["out"] / "_upload.csv"
            tmp.write_bytes(upload.getvalue())
            try:
                lst = listings_mod.Listings()
                n = listings_mod.import_csv(lst, tmp, log=lambda m: None)
                lst.save()
                st.success(f"Imported stats for {n} listing(s).")
            except Exception as exc:
                st.error(f"Import failed: {exc}")
            finally:
                tmp.unlink(missing_ok=True)

        cfg = listings_mod.config(settings)
        lst = listings_mod.Listings()
        live = lst.live()
        if not live:
            st.caption("No listings registered yet. Add them with "
                       "`python -m wonderfeed.listings add`.")
        else:
            rows = []
            for listing in live:
                verdict, reason, totals, videos = listings_mod.assess(
                    listing, cfg, State()
                )
                rows.append({
                    "SKU": listing["sku"],
                    "Product": listing["product_id"],
                    "Verdict": verdict,
                    "Days": listings_mod.days_live(listing),
                    "Videos": videos,
                    "Views": totals["views"],
                    "Units": totals["units"],
                    "Why": reason,
                })
            order = {"CULL": 0, "WATCH": 1, "NO DATA": 2, "TOO EARLY": 3, "KEEP": 4}
            rows.sort(key=lambda r: order.get(r["Verdict"], 9))
            st.dataframe(rows, use_container_width=True, hide_index=True)
            culls = [r for r in rows if r["Verdict"] == "CULL"]
            if culls:
                st.warning(
                    f"**{len(culls)} dead listing(s)** — delist these in Seller "
                    f"Center and free the slots: "
                    + ", ".join(r["SKU"] for r in culls)
                )
                st.caption("The worker already skips culled products when it "
                           "queues new videos, and gives selling ones double the "
                           "volume.")

    if running:
        time.sleep(REFRESH_SECONDS)
        st.rerun()


if __name__ == "__main__":
    main()

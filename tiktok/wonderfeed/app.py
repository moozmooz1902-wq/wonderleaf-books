"""Wonderfeed control panel.

  ./start.sh          (start.bat on Windows)

Designed so someone who has never seen it can run it: one big button, plain
English, and a setup check that says exactly what is missing before they press
anything. Everything else is behind an Advanced toggle.
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
from wonderfeed import netinfo  # noqa: E402
from wonderfeed import ui_products  # noqa: E402
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
        os.kill(pid, 0)
    except OSError:
        return None
    return pid


def missing_keys(practice):
    if practice:
        return []
    return [k for k in ("ANTHROPIC_API_KEY", "FAL_KEY")
            if not os.environ.get(k, "").strip()]


def start_worker(practice):
    log_path = ROOT / "out" / "worker.log"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    args = [sys.executable, "-m", "wonderfeed.worker"]
    if practice:
        args.append("--dry-run")
    with log_path.open("a", encoding="utf-8") as log:
        subprocess.Popen(args, cwd=str(ROOT), stdout=log,
                         stderr=subprocess.STDOUT, start_new_session=True)


def send(p, command):
    with p["control"].open("w", encoding="utf-8") as fh:
        json.dump(command, fh)


def read_status(p):
    try:
        with p["status"].open(encoding="utf-8") as fh:
            return json.load(fh)
    except (OSError, json.JSONDecodeError):
        return {}


# -- readiness -----------------------------------------------------------


def readiness(products, practice):
    """What is stopping a real run. Plain English, one line each."""
    checks = []
    real_gaps = [k for k in ("ANTHROPIC_API_KEY", "FAL_KEY")
                 if not os.environ.get(k, "").strip()]
    if practice and real_gaps:
        # Practice mode does not need keys, but reporting "Ready" would be a lie
        # that bites the moment someone switches practice mode off.
        detail = (f"Not needed in practice mode — but {' and '.join(real_gaps)} "
                  f"must be in `tiktok/.env` before real videos will work")
        ok = None
    elif real_gaps:
        detail = f"Missing {' and '.join(real_gaps)} — add them to `tiktok/.env`"
        ok = False
    else:
        detail = "Ready"
        ok = True
    checks.append({"ok": ok, "label": "API keys", "detail": detail})

    with_photo = [p for p in products if p.get("images")]
    checks.append({
        "ok": True if with_photo else (None if practice else False),
        "label": "Product photos",
        "detail": (f"{len(with_photo)} of {len(products)} products have a photo"
                   if with_photo else
                   "No product has a photo yet — add one to `tiktok/assets/` and "
                   "list it under `images:` in config/products.yaml"),
    })

    with_link = [p for p in products if p.get("link")]
    checks.append({
        "ok": True if with_link else (None if practice else False),
        "label": "Shop links",
        "detail": (f"{len(with_link)} of {len(products)} products have a link"
                   if with_link else
                   "No product has a TikTok Shop link yet — paste it into "
                   "config/products.yaml"),
    })
    return checks


# -- views ---------------------------------------------------------------


def render_simple(p, status, running, practice, counts, videos):
    """The whole job in one screen: press the button, collect the videos."""
    done_today = status.get("done_today", 0)
    cap = status.get("daily_cap", 24)

    if running:
        state = status.get("state", "working")
        if state == "paused":
            st.warning("###  ⏸  Paused")
        else:
            current = (status.get("current") or {}).get("label", "")
            st.success(f"###  ●  Making videos…\n\n"
                       f"{done_today} made today"
                       + (f" · now building **{current}**" if current else ""))
    else:
        st.info("###  ⏹  Not running\n\nPress the green button to start.")

    big = st.container()
    with big:
        if running:
            if st.button("■   S T O P", type="secondary", use_container_width=True):
                send(p, {"stop": True})
                time.sleep(0.6)
                st.rerun()
        else:
            if st.button("▶   S T A R T", type="primary", use_container_width=True):
                gaps = missing_keys(practice)
                if gaps:
                    st.session_state["start_error"] = (
                        f"Cannot start: missing {' and '.join(gaps)}.\n\n"
                        "Add them to the file `tiktok/.env`, or switch on "
                        "**Practice mode** in the sidebar to try it for free."
                    )
                else:
                    st.session_state.pop("start_error", None)
                    start_worker(practice)
                    time.sleep(2.0)
                st.rerun()

    if st.session_state.get("start_error"):
        st.error(st.session_state["start_error"])

    st.divider()
    ready = len(videos)
    if ready:
        st.markdown(f"### 📁  {ready} video{'s' if ready != 1 else ''} ready to post")
        st.caption(f"They are in the folder: `{p['out']}`")
        with st.expander("What do I do with these?", expanded=(ready > 0 and not running)):
            st.markdown(
                "1. Open **TikTok Studio** on a computer (tiktokstudio.com) and "
                "sign in to the shop account.\n"
                "2. Click **Upload**, and drag in a video from the folder above.\n"
                "3. Open the matching **`.txt` file** — it has the caption. "
                "Copy and paste it in.\n"
                "4. Click **Add link → Products** and tag the product the "
                "`.txt` file names.\n"
                "5. Turn on **AI-generated content** under *More options*.\n"
                "6. Choose **Schedule**, pick a time, and post.\n\n"
                "Do a few in one sitting — you can schedule up to 10 days ahead, "
                "so one session covers the week."
            )
    else:
        st.caption("No finished videos yet. They will appear here.")


def render_advanced(p, status, running, counts, videos, settings, products):
    done_today = status.get("done_today", 0)
    cap = status.get("daily_cap", 24)
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Today", f"{done_today}/{cap}")
    k2.metric("Queued", counts.get("pending", 0))
    k3.metric("Built", counts.get("done", 0))
    k4.metric("Failed", counts.get("failed", 0))

    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("⏸ Pause / Resume", disabled=not running, use_container_width=True):
            send(p, {"pause": status.get("state") != "paused"})
            time.sleep(0.5)
            st.rerun()
    with c2:
        if st.button("↻ Queue more now", disabled=not running, use_container_width=True):
            send(p, {"refill": settings.get("worker", {}).get("refill_batch", 12)})
            st.rerun()
    with c3:
        if st.button("↺ Retry failed", disabled=not running, use_container_width=True):
            send(p, {"retry_failed": True})
            st.rerun()

    tab_log, tab_videos, tab_analytics = st.tabs(
        ["Activity log", "Finished videos", "Analytics"])

    with tab_log:
        log = status.get("log") or []
        st.code("\n".join(log[-40:]) if log else "Nothing yet.", language=None)

    with tab_videos:
        if not videos:
            st.caption("Nothing built yet.")
        for video in videos[:12]:
            sidecar = video.with_suffix(".txt")
            with st.expander(f"{video.name}  ·  {video.stat().st_size // 1024} KB"):
                cv, ct = st.columns([1, 2])
                with cv:
                    st.video(str(video))
                with ct:
                    if sidecar.exists():
                        st.text(sidecar.read_text(encoding="utf-8"))

    with tab_analytics:
        st.markdown("**Which listings are selling** — this steers what gets built next.")
        upload = st.file_uploader("Seller Center CSV export", type=["csv"])
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
        live = listings_mod.Listings().live()
        if not live:
            st.caption("No listings registered yet.")
            return
        rows = []
        for listing in live:
            verdict, reason, totals, vids = listings_mod.assess(listing, cfg, State())
            rows.append({"SKU": listing["sku"], "Product": listing["product_id"],
                         "Verdict": verdict, "Days": listings_mod.days_live(listing),
                         "Videos": vids, "Views": totals["views"],
                         "Units": totals["units"], "Why": reason})
        order = {"CULL": 0, "WATCH": 1, "NO DATA": 2, "TOO EARLY": 3, "KEEP": 4}
        rows.sort(key=lambda r: order.get(r["Verdict"], 9))
        st.dataframe(rows, use_container_width=True, hide_index=True)
        culls = [r["SKU"] for r in rows if r["Verdict"] == "CULL"]
        if culls:
            st.warning(f"**Dead listings — delist these and free the slots:** "
                       f"{', '.join(culls)}")


def main():
    st.set_page_config(page_title="Wonderfeed", page_icon="▶", layout="centered")
    st.markdown("""<style>
      div.stButton > button { height: 5.5rem; font-size: 1.6rem; font-weight: 700;
                              letter-spacing: .06em; border-radius: 12px; }
      div.stButton > button p { font-size: 1.6rem; font-weight: 700; }
      /* START is green, STOP is amber - the on-screen copy names the colour. */
      div.stButton > button[kind="primary"] {
          background-color: #17803d; border-color: #17803d; color: #fff; }
      div.stButton > button[kind="primary"]:hover {
          background-color: #126430; border-color: #126430; color: #fff; }
      div.stButton > button[kind="secondary"] {
          background-color: #b45309; border-color: #b45309; color: #fff; }
      div.stButton > button[kind="secondary"]:hover {
          background-color: #92400e; border-color: #92400e; color: #fff; }
      /* keep the smaller Advanced and sidebar controls normal size */
      section[data-testid="stSidebar"] div.stButton > button {
          height: 2.6rem; font-size: 1rem; letter-spacing: normal; }
    </style>""", unsafe_allow_html=True)

    try:
        settings = load_settings()
        products = load_products()
    except ConfigError as exc:
        st.title("Wonderfeed")
        st.error(f"**Setup not finished**\n\n{exc}")
        st.stop()

    p = paths(settings)
    p["out"].mkdir(parents=True, exist_ok=True)
    pid = worker_pid(p)
    running = pid is not None
    status = read_status(p)
    counts = status.get("counts") or Queue(p["queue"]).counts()
    videos = sorted(p["out"].glob("*.mp4"), key=lambda f: f.stat().st_mtime,
                    reverse=True)

    with st.sidebar:
        page = st.radio("Screen", ["▶ Run", "📦 Products & listings"],
                        label_visibility="collapsed")
        st.divider()
        st.header("Settings")
        practice = st.toggle(
            "Practice mode", value=st.session_state.get("practice", False),
            disabled=running,
            help="Makes videos with placeholder pictures instead of real ones. "
                 "Costs nothing. Use it to try the buttons.",
        )
        st.session_state["practice"] = practice
        if practice:
            st.caption("⚠️ Practice mode: videos use placeholder pictures. "
                       "Do not post them.")
        st.divider()
        advanced = st.toggle("Advanced view", value=False)
        st.divider()
        staff_url = netinfo.urls().get("other_devices")
        if staff_url:
            st.caption("**Link for your staff**")
            st.code(staff_url, language=None)
            st.caption("They open this on their own phone or laptop. Nothing to "
                       "install. Same wifi as this computer.")
            st.divider()
        st.caption("**Ready to run?**")
        for check in readiness(products, practice):
            icon = {True: "✅", False: "⚠️", None: "➖"}[check["ok"]]
            st.markdown(f"{icon} **{check['label']}** — {check['detail']}")

    st.title("Wonderfeed")
    if not running and not videos:
        st.caption("Press Start. It makes TikTok videos for your products and "
                   "puts them in a folder for you to post.")

    if not running:
        log_file = ROOT / "out" / "worker.log"
        if log_file.exists() and not st.session_state.get("start_error"):
            tail = "\n".join(log_file.read_text(encoding="utf-8",
                                                errors="replace").splitlines()[-6:])
            if "error" in tail.lower() or "traceback" in tail.lower():
                st.error("**It stopped with a problem:**")
                st.code(tail, language=None)

    if page.startswith("📦"):
        ui_products.render(settings)
    else:
        render_simple(p, status, running, practice, counts, videos)
        if advanced:
            st.divider()
            render_advanced(p, status, running, counts, videos, settings, products)

    if running and not page.startswith("📦"):
        # Never auto-refresh the Products screen - it would wipe half-typed forms.
        time.sleep(REFRESH_SECONDS)
        st.rerun()


if __name__ == "__main__":
    main()

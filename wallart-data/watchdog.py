#!/usr/bin/env python3
"""Watch the wall-art shards and stop any pod that is billing for nothing.

Three ways a community pod ends up costing money and producing none:
  CUDA_DEAD_ON_THIS_HOST          torch cannot init, nvidia-smi lies
  R2_TLS_INTERCEPTED_ON_THIS_HOST a middlebox breaks every R2 call
  SHARD COMPLETE / UNFINISHED     the work is done or the clock ran out
All four end the pod. Everything else is left alone.
"""
import json, re, subprocess, sys, time

API = "https://rest.runpod.io/v1"
DEAD = ("CUDA_DEAD_ON_THIS_HOST", "R2_TLS_INTERCEPTED_ON_THIS_HOST")
# GEN_DONE and GEN_CRASHED both mean the worker process has EXITED. A pod
# whose worker has exited produces nothing and bills until deleted, and on
# 14 Oct three of them sat that way for forty-five minutes because the
# watchdog only knew the two markers the worker prints on a tidy finish -
# and a crash prints neither. Whatever the reason the process is gone, the
# pod's job here is over.
DONE = ("SHARD COMPLETE", "UNFINISHED:", "GEN_DONE", "GEN_CRASHED")


def curl(*args):
    """Decode with errors="replace", because these downloads get cut off.

    boot.log is multi-megabyte and curl --max-time stops it part way through.
    Stopping part way through means stopping part way through a UTF-8
    character, and text=True then raised UnicodeDecodeError out of
    subprocess.run - which killed the watchdog, the one process whose job is
    to notice a dead pod. It had run for hours before a log grew big enough
    for the cut to land mid-character; the failure was always available and
    just needed the right number of bytes.

    Nothing here needs byte-perfect text - the log is searched for fixed
    markers and done.txt is counted by newline - so a replacement character
    at the truncation point costs nothing and crashing costs a pod that bills
    while producing nothing.
    """
    r = subprocess.run(["curl", "-sS", "--max-time", "60", *args],
                       capture_output=True)
    return r.stdout.decode("utf-8", errors="replace")


def pods():
    try:
        d = json.loads(curl(f"{API}/pods"))
    except Exception:
        return []
    d = d if isinstance(d, list) else d.get("pods", [])
    return [p for p in d if p.get("desiredStatus") == "RUNNING"
            and str(p.get("name", "")).startswith("wa-v3-")]


def log(pid):
    """The TAIL of boot.log, except there is no tail to fetch.

    python -m http.server ignores Range, so a growing multi-megabyte log can
    only be downloaded from the start, and curl --max-time cuts it off part
    way. The last "kept N / M" in what arrives is therefore frozen near the
    truncation point: six pods all reported exactly 996 generated, unchanged
    across two polls, while done.txt showed 1,300 to 1,520 and climbing.
    So progress comes from done.txt, which is one short line per panel, and
    boot.log is only read for the markers - which appear early enough in a
    failed pod's log to survive the truncation.
    """
    return curl(f"https://{pid}-8000.proxy.runpod.net/boot.log")


def done_count(pid):
    t = curl(f"https://{pid}-8000.proxy.runpod.net/art/done.txt")
    return t.count("\n")


def kill(pid, why):
    curl("-X", "DELETE", f"{API}/pods/{pid}")
    print(f"{time.strftime('%H:%M:%S')}  KILLED {pid}  {why}", flush=True)


deadline = time.time() + float(sys.argv[1] if len(sys.argv) > 1 else 1500)
while time.time() < deadline:
    on = pods()
    if not on:
        print(f"{time.strftime('%H:%M:%S')}  no wa-v3 pods running", flush=True)
        break
    for p in on:
        pid, name = p["id"], p.get("name")
        t = log(pid)
        hit = next((m for m in DEAD + DONE if m in t), None)
        if hit:
            kill(pid, f"{name} {hit}")
            continue
        n = done_count(pid)
        if n:
            print(f"{time.strftime('%H:%M:%S')}  {pid} {name}  {n:,} panels",
                  flush=True)
        else:
            mark = "booting" if "GPU" in t or "pip" in t or not t.strip() else "?"
            print(f"{time.strftime('%H:%M:%S')}  {pid} {name}  {mark}"
                  f"  ({len(t)} bytes of log)", flush=True)
    time.sleep(120)
print("watchdog window over", flush=True)

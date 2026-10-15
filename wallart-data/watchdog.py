#!/usr/bin/env python3
"""Watch the wall-art shards and stop any pod that is billing for nothing.

Three ways a community pod ends up costing money and producing none:
  CUDA_DEAD_ON_THIS_HOST          torch cannot init, nvidia-smi lies
  R2_TLS_INTERCEPTED_ON_THIS_HOST a middlebox breaks every R2 call
  SHARD COMPLETE / UNFINISHED     the work is done or the clock ran out
All four end the pod. Everything else is left alone.
"""
import json, os, re, subprocess, sys, time

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


CRASHDIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "notes", "crashlogs")
# Kept because the log dies with the pod. wa-v3-9 crashed four times in ten
# minutes on 15 Oct and all four pods were deleted here, unexamined, before
# anyone could fetch a log - the 14 Oct shadowed-variable bug was only ever
# caught because it was watched live. The text is already in memory when the
# marker is matched, so keeping it costs one write and no extra request.
def keep(pid, name, why, text):
    try:
        os.makedirs(CRASHDIR, exist_ok=True)
        stamp = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
        f = os.path.join(CRASHDIR, f"{stamp}_{name}_{pid}.log")
        with open(f, "w") as fh:
            fh.write(f"# {why}\n# saved by watchdog before deleting the pod\n")
            fh.write(text[-40000:])
        print(f"{time.strftime('%H:%M:%S')}  kept log {f}", flush=True)
    except Exception as e:
        # Never let bookkeeping stop a kill - an undeleted pod bills.
        print(f"{time.strftime('%H:%M:%S')}  could not keep log: {e}",
              flush=True)


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
        # A marker only counts in a log that belongs to a real run. wa-v3-9
        # was killed on GEN_CRASHED at 18:30:44 on 15 Oct when the pod was
        # 76 seconds old, and again twice in the next eight minutes - and a
        # 76-second-old pod has an EMPTY boot.log: measured on the fourth
        # one, nvidia-smi does not run until two minutes in and the first
        # bytes appear after that. So whatever was matched did not come from
        # that pod's own worker, and three paid-for pods were deleted on the
        # strength of it. The worker's own invocation line is printed before
        # any marker can be and survives the truncation that eats the tail,
        # so requiring it costs nothing and rules out an empty body, a proxy
        # error page and anything else that is not this run.
        started = "gen_gated.py --subjects" in t
        # CUDA_DEAD is printed by run.sh BEFORE the worker is invoked, so it
        # must never be gated on the run line - that pod has no working
        # device and bills until it is deleted. R2_TLS comes out of the
        # worker itself (gen/gen_gated.py:469), so it is covered either way.
        hit = next((m for m in DEAD if m in t), None)
        if hit is None and started:
            hit = next((m for m in DONE if m in t), None)
        if hit:
            if hit == "GEN_CRASHED" or hit in DEAD:
                keep(pid, name, f"{name} {hit}", t)
            kill(pid, f"{name} {hit}")
            continue
        n = done_count(pid)
        if n:
            print(f"{time.strftime('%H:%M:%S')}  {pid} {name}  {n:,} panels",
                  flush=True)
        else:
            mark = ("booting" if "GPU" in t or "pip" in t or not t.strip()
                    else "running" if started else "NO RUN LINE IN LOG")
            print(f"{time.strftime('%H:%M:%S')}  {pid} {name}  {mark}"
                  f"  ({len(t)} bytes of log)", flush=True)
    time.sleep(120)
print("watchdog window over", flush=True)

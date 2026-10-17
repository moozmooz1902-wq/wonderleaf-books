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
SKU_LINE = re.compile(r"^WA-[0-9a-f]{16}$")
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
    """The shard list, or None when the API could not be read.

    These must not be the same value. This returned [] on any failure - a
    curl that timed out, a truncated body, a rate-limit page - and the loop
    below treated an empty list as "the run is over" and exited. On 15 Oct
    at 19:03 one unreadable response ended the watchdog two minutes after it
    had polled twelve healthy pods, and the fleet ran unsupervised until a
    person noticed. Nothing was wrong with the pods.

    None means "ask again". [] means the API answered and there are no
    shards, which is the only reading worth stopping for.
    """
    try:
        d = json.loads(curl(f"{API}/pods"))
    except Exception:
        return None
    if isinstance(d, dict):
        d = d.get("pods")
    if not isinstance(d, list):
        return None
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
    """Count SKU lines, not lines.

    done.txt does not exist until the first panel is uploaded, and until then
    python -m http.server answers with its 404 page - which is thirteen lines
    long. Counting newlines therefore reported "13 panels" for every pod that
    had got its web server up and generated nothing, and the number sat at 13
    without moving, which is indistinguishable from the frozen done.txt that
    gave away three stalled shards on 14 Oct. It read as progress on 15 Oct
    and was taken for it.

    Every real line is a SKU: "WA-" and sixteen hex characters. Requiring
    that shape costs nothing, ignores the error page, and also drops the
    half-line left when curl --max-time cuts the download mid-write.
    """
    t = curl(f"https://{pid}-8000.proxy.runpod.net/art/done.txt")
    return sum(1 for ln in t.splitlines() if SKU_LINE.match(ln))


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
# Stop on a real empty fleet, not on one bad reading, and not on one pass
# that happened to land between a shard expiring and fill_shards.sh putting
# the next one up - which at twelve staggered expiries is a normal moment.
EMPTY_PASSES_BEFORE_STOP = 3
empty = 0

# A POD THAT NEVER BOOTS IS INVISIBLE TO EVERY OTHER RULE HERE. Each marker
# this watchdog kills on is printed BY the pod, so a pod that never starts
# prints none of them and is never killed. wa-v3-11 sat at "booting (0 bytes
# of log)" for 171 minutes on 17 Oct while this loop reported it faithfully
# every two minutes and did nothing, because there was nothing to match.
#
# Worse than the $0.63 it burned: --max-hours is enforced by the worker, and
# the worker never ran, so its ten-hour clock never started either. Left
# alone it would have billed until a person noticed.
#
# Measured boot times: nvidia-smi at about two minutes, first panels by
# eight to ten. Fifteen consecutive empty polls at 120s apart is thirty
# minutes, which is three times the slowest healthy boot seen.
DEAD_BOOT_POLLS = 15
silent = {}
while time.time() < deadline:
    on = pods()
    if on is None:
        print(f"{time.strftime('%H:%M:%S')}  pod list unreadable, retrying",
              flush=True)
        time.sleep(30)
        continue
    if not on:
        empty += 1
        print(f"{time.strftime('%H:%M:%S')}  no wa-v3 pods running "
              f"({empty} of {EMPTY_PASSES_BEFORE_STOP})", flush=True)
        if empty >= EMPTY_PASSES_BEFORE_STOP:
            break
        time.sleep(60)
        continue
    empty = 0
    for p in on:
        pid, name = p["id"], p.get("name")
        t = log(pid)
        # A marker only counts in a log that belongs to a real run: the
        # worker's own invocation line has to be in the same body. It is
        # printed before any marker can be and survives the truncation that
        # eats the tail, so requiring it costs nothing and rules out an
        # empty body, a proxy error page, and anything else that did not
        # come from this run.
        #
        # This started as a wrong reading and the guard is worth keeping
        # anyway. Three wa-v3-9 pods were killed on GEN_CRASHED at 76, 170
        # and 170 seconds old on 15 Oct, and that looked impossible because
        # the fourth one took two minutes just to reach nvidia-smi - so the
        # match seemed to be coming from something other than the pod's own
        # log. It was not: the cause was transformers 5.20.0, published at
        # 18:01 that day, and on a host with the container image already
        # cached a pod really can boot, pip install and fail the diffusers
        # import inside 76 seconds. One slow pod is not the floor for all of
        # them. What the guard actually buys is that a DELETE needs positive
        # evidence from this run rather than a substring anywhere in
        # whatever the proxy returned.
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
            silent.pop(pid, None)
            print(f"{time.strftime('%H:%M:%S')}  {pid} {name}  {n:,} panels",
                  flush=True)
        else:
            # Nothing in the log AND nothing generated. One such reading is a
            # pod still coming up; fifteen in a row is a pod that never will.
            if not t.strip():
                silent[pid] = silent.get(pid, 0) + 1
                if silent[pid] >= DEAD_BOOT_POLLS:
                    kill(pid, f"{name} NEVER BOOTED "
                              f"({silent[pid]} polls, no log, no panels)")
                    silent.pop(pid, None)
                    continue
            else:
                silent.pop(pid, None)
            mark = ("booting" if "GPU" in t or "pip" in t or not t.strip()
                    else "running" if started else "NO RUN LINE IN LOG")
            extra = (f"  [silent {silent[pid]}/{DEAD_BOOT_POLLS}]"
                     if silent.get(pid) else "")
            print(f"{time.strftime('%H:%M:%S')}  {pid} {name}  {mark}"
                  f"  ({len(t)} bytes of log){extra}", flush=True)
    # Pods that have gone away should not keep a counter alive.
    silent = {k: v for k, v in silent.items() if k in {p["id"] for p in on}}
    time.sleep(120)
print("watchdog window over", flush=True)

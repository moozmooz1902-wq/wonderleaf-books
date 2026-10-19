#!/usr/bin/env python3
"""Delete render pods the moment they stop rendering.

A pod that has finished its ranges keeps billing until it is DELETED -
stopping it is not enough. render_worker prints one of two lines and then
exits, and the pod sits there at 32 to 64 cents an hour until something
notices. This is that something.

Same two rules the generation watchdog learned the hard way:
  * an unreadable pod list means ASK AGAIN, never "the fleet is empty".
    One bad read ended the generation watchdog on 15 Oct and the fleet ran
    unsupervised until a person noticed.
  * an empty log is not a dead pod. It is a pod still installing boto3.
"""
import json, os, re, subprocess, sys, time

API = "https://rest.runpod.io/v1"
DONE = ("RENDER COMPLETE", "UNFINISHED:", "RENDER_EXIT")
PREFIX = "wa-render"
DONEFILE = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "done_parts.txt")


def curl(*a):
    return subprocess.run(["curl", "-sS", "--max-time", "60", *a],
                          capture_output=True, text=True).stdout


def pods():
    try:
        d = json.loads(curl(f"{API}/pods"))
    except Exception:
        return None
    if not isinstance(d, list):
        return None
    return [p for p in d if p.get("desiredStatus") == "RUNNING"
            and str(p.get("name", "")).startswith(PREFIX)]


deadline = time.time() + float(sys.argv[1] if len(sys.argv) > 1 else 36000)
empty = 0
while time.time() < deadline:
    on = pods()
    if on is None:
        print(f"{time.strftime('%H:%M:%S')}  pod list unreadable, retrying",
              flush=True)
        time.sleep(60)
        continue
    if not on:
        empty += 1
        print(f"{time.strftime('%H:%M:%S')}  no render pods ({empty}/3)",
              flush=True)
        if empty >= 3:
            break
        time.sleep(60)
        continue
    empty = 0
    for p in on:
        pid, name = p["id"], p["name"]
        t = curl(f"https://{pid}-8000.proxy.runpod.net/boot.log")
        hit = next((m for m in DONE if m in t), None)
        if hit:
            curl("-X", "DELETE", f"{API}/pods/{pid}")
            print(f"{time.strftime('%H:%M:%S')}  KILLED {pid} {name}  {hit}",
                  flush=True)
            # RENDER COMPLETE means that part's ranges are exhausted and it
            # must never be relaunched - the same end-of-run churn
            # fill_shards.sh learned about, where every replacement pays a
            # boot to generate nothing. UNFINISHED means the clock ran out
            # with work left, so that part SHOULD come back.
            if hit == "RENDER COMPLETE":
                try:
                    k = name.rsplit("-", 1)[-1]
                    with open(DONEFILE, "a") as fh:
                        fh.write(k + "\n")
                except Exception as e:
                    print(f"  could not record {name}: {e}", flush=True)
            continue
        m = re.findall(r"([\d,]+) panels, ([\d,]+) pictures, "
                       r"([\d.]+) min, ([\d,]+) panels/hr", t)
        if m:
            a, b, mins, rate = m[-1]
            print(f"{time.strftime('%H:%M:%S')}  {name:<13} {a:>9} panels "
                  f"{b:>10} pictures  {rate:>8}/hr", flush=True)
        else:
            print(f"{time.strftime('%H:%M:%S')}  {name:<13} starting "
                  f"({len(t)} bytes of log)", flush=True)
    time.sleep(180)
print("reaper window over", flush=True)

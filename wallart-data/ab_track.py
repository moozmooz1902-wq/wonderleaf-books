#!/usr/bin/env python3
"""Snapshot every shard's reject breakdown, and print the MARGINAL rates.

Cumulative counters cannot answer any question worth asking here. A shard
carries its retry backlog in them for hours - a fresh one reads 20-50% while
the fleet is at 6% - so every comparison has to be done on the difference
between two readings, and until now I have been doing that arithmetic by
hand from numbers scattered across an afternoon, which is how the 06:00 A/B
got called from a sample of 92.

Writes notes/ab_snapshots.jsonl, one line per run, and prints the change
since the previous line. No pods, no cost: it reads the small files the
pods already serve.

    python3 ab_track.py                 # snapshot and print deltas
    python3 ab_track.py --label "clean-at-end started"
"""
import argparse, json, os, subprocess, sys, time
from concurrent.futures import ThreadPoolExecutor

API = "https://rest.runpod.io/v1"
HERE = os.path.dirname(os.path.abspath(__file__))
STORE = os.path.join(HERE, "notes", "ab_snapshots.jsonl")
GATE_MARKS = ("PEOPLE", "EYES", "EMPTY")


def curl(url, timeout=40):
    """errors="replace", for the same reason watchdog.py does it.

    This script reads each pod's boot.log to find which prompt variant it is
    running. That log is multi-megabyte, curl --max-time cuts it off part
    way, and a cut part way through the file is a cut part way through a
    UTF-8 character - so text=True raised UnicodeDecodeError and took the
    whole hourly reading with it.

    I fixed exactly this in watchdog.py on 13 Oct and did not look for the
    other script that reads the same log the same way. Both are now the only
    two places that fetch boot.log; if a third appears, it needs this too.
    """
    r = subprocess.run(["curl", "-sS", "--max-time", str(timeout), url],
                       capture_output=True)
    return r.stdout.decode("utf-8", errors="replace")


def pods():
    out = curl(f"{API}/pods", 60)
    try:
        d = json.loads(out)
    except Exception:
        return []
    if not isinstance(d, list):
        return []
    return [p for p in d
            if p.get("desiredStatus") == "RUNNING"
            and str(p.get("name", "")).startswith("wa-v3-")]


def read_shard(p):
    pid, name = p["id"], p["name"]
    base = f"https://{pid}-8000.proxy.runpod.net/art"
    kept = sum(1 for l in curl(f"{base}/done.txt").splitlines() if l.strip())
    counts = {"text": 0, "PEOPLE": 0, "EYES": 0, "EMPTY": 0}
    n = 0
    for line in curl(f"{base}/rejects.jsonl").splitlines():
        try:
            d = json.loads(line)
        except Exception:
            continue
        n += 1
        m = d.get("marks") or []
        tag = (m[0][0] if m and isinstance(m[0], list) and m[0][0] in GATE_MARKS
               else "text")
        counts[tag] += 1
    # The variant announces itself in its own log, so the arm is read from
    # the pod and never inferred from a pod id I am holding in my head.
    boot = curl(f"https://{pid}-8000.proxy.runpod.net/boot.log", 25)
    arm = "clean_at_end" if "PROMPT VARIANT" in boot else "shipped"
    return {"id": pid, "name": name, "started": p.get("lastStartedAt", "")[:19],
            "kept": kept, "rejected": n, "arm": arm, **counts}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--label", default="")
    a = ap.parse_args()
    ps = pods()
    if not ps:
        print("no shards running")
        return
    with ThreadPoolExecutor(12) as ex:
        rows = list(ex.map(read_shard, ps))
    snap = {"t": int(time.time()), "iso": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "label": a.label, "shards": rows}

    prev = None
    if os.path.exists(STORE):
        for line in open(STORE):
            try:
                prev = json.loads(line)
            except Exception:
                pass
    os.makedirs(os.path.dirname(STORE), exist_ok=True)
    with open(STORE, "a") as fh:
        fh.write(json.dumps(snap) + "\n")

    by_arm = {}
    print(f"{snap['iso']}  {len(rows)} shards" + (f"  [{a.label}]" if a.label else ""))
    if prev is None:
        print("first snapshot - nothing to compare against yet")
    pm = {r["id"]: r for r in prev["shards"]} if prev else {}
    hdr = f"{'shard':<9} {'arm':<13} {'+kept':>7} {'+rej':>6} {'rate':>6} {'+text':>6} {'text/gen':>9}"
    print(hdr); print("-" * len(hdr))
    for r in sorted(rows, key=lambda x: (x["arm"], x["name"])):
        o = pm.get(r["id"])
        if not o:
            print(f"{r['name']:<9} {r['arm']:<13} {'(new)':>7}")
            continue
        dk, dr = r["kept"] - o["kept"], r["rejected"] - o["rejected"]
        dt = r["text"] - o["text"]
        gen = dk + dr
        if gen <= 0:
            continue
        print(f"{r['name']:<9} {r['arm']:<13} {dk:>7,} {dr:>6,} "
              f"{100*dr/gen:>5.1f}% {dt:>6,} {100*dt/gen:>8.2f}%")
        s = by_arm.setdefault(r["arm"], [0, 0, 0])
        s[0] += dk; s[1] += dr; s[2] += dt
    if by_arm:
        print()
        for arm, (dk, dr, dt) in sorted(by_arm.items()):
            gen = dk + dr
            print(f"  {arm:<13} {dk:,} kept, {dr:,} rejected = {100*dr/gen:.1f}% "
                  f"| text {dt:,} = {100*dt/gen:.2f}% of everything generated")
        if len(by_arm) == 2:
            print("\n  text per generation is the number that decides this, "
                  "not text's share of rejections")


if __name__ == "__main__":
    main()

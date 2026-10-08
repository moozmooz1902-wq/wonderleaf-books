#!/usr/bin/env python3
"""Pull every listing title out of all three dumps into one normalised file.

The dumps are eBay File Exchange exports. Some have a header row and some do
not (the first row is data), and the column order is the same 36-column layout
in both cases, so the title is column 5 and the parent rows are the ones whose
Relationship column (6) is empty.
"""
import csv, glob, os, sys, json
csv.field_size_limit(50 << 20)
BASE = ("/tmp/claude-0/-home-user-wonderleaf-books/"
        "af9e3fdd-8129-53fc-a69c-916ae3713d2b/scratchpad/")
OUT = BASE + "an/titles.csv"

SETS = {"displate": BASE + "mega/f1/*/*.csv",
        "art800k":  BASE + "mega/f2/*/*.csv",
        "fy300k":   BASE + "mega/f3/*/*.csv"}

I_TITLE, I_REL, I_PIC = 5, 6, 26
n = 0
with open(OUT, "w", newline="", encoding="utf-8") as out:
    w = csv.writer(out)
    w.writerow(["set", "file", "title", "picurl"])
    for name, pat in SETS.items():
        for p in sorted(glob.glob(pat)):
            got = 0
            try:
                with open(p, newline="", encoding="utf-8", errors="replace") as f:
                    r = csv.reader(f)
                    for row in r:
                        if len(row) <= I_PIC:
                            continue
                        if (row[I_REL] or "").strip():      # variation row
                            continue
                        t = (row[I_TITLE] or "").strip()
                        if not t or t.lower().startswith("*title"):
                            continue
                        pic = (row[I_PIC] or "").strip()
                        # titles can contain tabs AND newlines, which broke the
                        # first version of this file; flatten both
                        flat = " ".join(t.split())
                        w.writerow([name, os.path.basename(p), flat, pic])
                        got += 1; n += 1
            except Exception as e:
                print(f"  !! {p}: {type(e).__name__} {e}", flush=True)
            print(f"  {name:<9} {got:>8,}  {os.path.basename(p)[:52]}", flush=True)
print(f"\ntotal titles: {n:,} -> {OUT}")

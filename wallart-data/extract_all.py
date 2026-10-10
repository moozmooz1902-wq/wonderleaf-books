#!/usr/bin/env python3
"""Read every competitor CSV properly. Three traps, all hit and all handled.

1. The Fy! files have NO HEADER ROW. Reading them with a header consumed the
   first listing and made every title column look empty - which is why an
   earlier pass wrongly reported "no titles". Layout is detected, not assumed.

2. Column count varies (36 or 38) because their own exporter did not quote
   descriptions containing commas: "Los Angeles, Us, Geometric Illustration"
   spills across three fields. So the row is parsed from BOTH ends - the first
   27 fields and the last 8 are fixed, and whatever is left in the middle is
   the description, rejoined.

3. Embedded newlines and tabs: csv.reader in, csv.writer out, so no field can
   shift. The earlier pass flattened tabs only and corrupted attribution.

Resumable: a file is appended to done.txt only after its rows are written.
"""
import csv, os, re, glob, json, collections

csv.field_size_limit(10**9)
BASE = "/tmp/claude-0/-home-user-wonderleaf-books/af9e3fdd-8129-53fc-a69c-916ae3713d2b/scratchpad"
MEGA, OUT = os.path.join(BASE, "mega2"), os.path.join(BASE, "learn")
ROWS, DONE = os.path.join(OUT, "rows.tsv"), os.path.join(OUT, "done.txt")

# File Exchange layout, by position. Stable for the first 27 and the last 8.
FRONT = ["action", "sku", "itemid", "category", "storecat", "title", "rel",
         "reldet", "cond", "ctype", "colour", "ilen", "iwid", "material",
         "mounting", "csize", "transp", "fthick", "style", "mpn", "features",
         "adjust", "care", "dept", "room", "pattern", "picurl"]      # 0..26
BACK  = ["format", "duration", "price", "qty", "location",
         "shipprof", "retprof", "payprof"]                            # last 8
KEEP  = ["set", "file"] + FRONT + ["descr"] + BACK

HDR0 = "*action(siteid"          # Displate files start with this; Fy! files do not

MONEY = re.compile(r"^\d+\.\d{2}$")

def parse(row):
    """Anchor on values, not positions.

    Fields 0..26 are reliable in every file. After that three things vary:
    their exporter did not quote commas in descriptions (so the description
    spans 1-4 fields), variation rows carry a trailing junk field from a stray
    comma, and variation rows have no Format/Duration at all - they start at
    StartPrice. So the tail is found by looking for 'FixedPrice', and failing
    that for the first money-shaped field.
    """
    if len(row) < len(FRONT) + 2:
        return None
    front = [v for v in row[:len(FRONT)]]
    rest  = row[len(FRONT):]
    descr = fmt = dur = price = qty = loc = ""
    profs = ["", "", ""]
    if "FixedPrice" in rest:                      # parent row
        i = rest.index("FixedPrice")
        descr = ", ".join(v for v in rest[:i] if v)
        t = rest[i:] + [""] * 8
        fmt, dur, price, qty, loc = t[0], t[1], t[2], t[3], t[4]
        profs = t[5:8]
    else:                                          # variation row
        mi = next((j for j, v in enumerate(rest) if MONEY.match(v.strip())), None)
        if mi is not None:
            t = rest[mi:] + [""] * 6
            price, qty, loc = t[0], t[1], t[2]
            profs = t[3:6]
    rec = front + [descr, fmt, dur, price, qty, loc] + profs
    return [v.replace("\r", " ").replace("\n", " ").strip() for v in rec]


done = {l.strip() for l in open(DONE)} if os.path.exists(DONE) else set()
files = []
for s in ("displate", "fy", "raw800k"):
    for fn in sorted(glob.glob(os.path.join(MEGA, s, "**", "*.csv"), recursive=True)):
        files.append((s, fn))
todo = [(s, f) for s, f in files if f not in done]
print(f"{len(files)} CSVs, {len(done)} done, {len(todo)} to read", flush=True)

fresh = not done
out = open(ROWS, "a", encoding="utf-8", newline="")
w = csv.writer(out, delimiter="\t", lineterminator="\n")
if fresh:
    w.writerow(KEEP)
dlog = open(DONE, "a")
widths = collections.Counter(); hdrkind = collections.Counter(); total = 0

for setname, fn in todo:
    base, n, bad = os.path.basename(fn), 0, 0
    try:
        with open(fn, newline="", encoding="utf-8", errors="replace") as f:
            r = csv.reader(f)
            first = next(r, None)
            if first is None:
                dlog.write(fn + "\n"); dlog.flush(); continue
            # header or data? only the Displate exports carry a header line
            has_header = first and first[0].strip().lower().startswith(HDR0)
            hdrkind[f"{setname}:{'header' if has_header else 'headerless'}"] += 1
            rows = r if has_header else __import__("itertools").chain([first], r)
            for row in rows:
                widths[len(row)] += 1
                rec = parse(row)
                if rec is None:
                    bad += 1; continue
                w.writerow([setname, base] + rec)
                n += 1
    except Exception as e:
        print(f"  ERROR {base}: {e}", flush=True); continue
    total += n; out.flush()
    dlog.write(fn + "\n"); dlog.flush()
    print(f"  {setname:<9} {base:<54} {n:>8,} rows" + (f"  ({bad} short)" if bad else ""), flush=True)

print(f"\n{total:,} rows appended", flush=True)
print("row widths seen:", dict(widths.most_common(8)), flush=True)
print("layouts:", dict(hdrkind), flush=True)
json.dump({"widths": dict(widths), "layouts": dict(hdrkind)},
          open(os.path.join(OUT, "layouts.json"), "w"), indent=1)

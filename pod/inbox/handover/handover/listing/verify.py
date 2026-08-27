"""
verify.py — confirm the pod is running the current files, not older copies.

    python3 verify.py

Prints the settings that actually matter and flags anything stale. Every check
here corresponds to a bug that has already shipped once on this project.
"""

import os
import sys

EXPECTED = {
    "dtf.py": [
        ("VIGNETTE_START", 0.42, "vignette fades the mid-edges, not just corners"),
        ("VIGNETTE_END", 0.94, ""),
        ("DEFAULT_MARGIN", 0.80, "print is ~9.6in wide, not 11.3in"),
        ("BORDER_MAX", 75, "light-background reject threshold"),
    ],
    "photo_mockup.py": [
        ("OUT_W", 1800, "HD listing image"),
        ("OUT_H", 2400, ""),
        ("FORCE_WHITE", False, "MUST be False or colour is destroyed"),
    ],
}

print("FILE CHECK\n")
ok = True

for fname, checks in EXPECTED.items():
    if not os.path.exists(fname):
        print(f"  MISSING: {fname}")
        ok = False
        continue

    ns = {}
    src = open(fname, encoding="utf-8").read()
    # Pull constants without importing (avoids side effects). Handles tuple
    # assignment too — "OUT_W, OUT_H = 1800, 2400" is one statement, and the
    # first version of this checker reported both as missing.
    for line in src.splitlines():
        line = line.strip()
        if "=" not in line or line.startswith("#"):
            continue
        lhs, rhs = line.split("=", 1)
        rhs = rhs.split("#")[0].strip()
        names = [n.strip() for n in lhs.split(",")]
        if not all(n.replace("_", "").isalnum() for n in names if n):
            continue
        try:
            val = eval(rhs)
        except Exception:
            continue
        if len(names) == 1:
            ns[names[0]] = val
        elif isinstance(val, tuple) and len(val) == len(names):
            for n, v in zip(names, val):
                ns[n] = v

    print(f"  {fname}")
    for var, want, note in checks:
        got = ns.get(var, "NOT FOUND")
        good = got == want
        if not good:
            ok = False
        mark = "ok " if good else "OLD"
        extra = f"   <- {note}" if note and not good else ""
        print(f"    [{mark}] {var:<16} = {got}"
              + ("" if good else f"   expected {want}") + extra)
    print()

# --- the graphics engine ---------------------------------------------------
if os.path.exists("graphics.py"):
    src = open("graphics.py", encoding="utf-8").read()
    # Strip comments first — the removed style names are mentioned in the
    # comments explaining why they were removed, which tripped the old check.
    code = "\n".join(l.split("#")[0] for l in src.splitlines())
    print("  graphics.py")
    checks = [
        ("stained glass" not in code, "hard-edged panel styles removed"),
        ("art nouveau" not in code, "ornate border styles removed"),
        ("fades into black" in code, "subject dissolves into the shirt"),
        ("grey background" in code, "pale backgrounds in the negative prompt"),
        ("vivid colour" in code or "multicolour" in code,
         "colour is requested"),
    ]
    for good, note in checks:
        if not good:
            ok = False
        print(f"    [{'ok ' if good else 'OLD'}] {note}")
    print()

# --- queue -----------------------------------------------------------------
if os.path.exists("generation_queue.csv"):
    import csv
    csv.field_size_limit(min(sys.maxsize, 2**31 - 1))
    with open("generation_queue.csv", encoding="utf-8") as f:
        first = next(csv.DictReader(f))
    print("  generation_queue.csv")
    neg_ok = "grey background" in first.get("negative", "")
    if not neg_ok:
        ok = False
    print(f"    [{'ok ' if neg_ok else 'OLD'}] negative prompt blocks pale backgrounds")
    print()

print("=" * 56)
print("ALL CURRENT" if ok else "SOME FILES ARE OUT OF DATE — re-upload them")

print("""
COST SETTINGS — these are flags and pod choices, not files:

  cheapest   ./venv/bin/python pod_sdxl.py --hires 0   (on Community Cloud)
  quality    ./venv/bin/python pod_sdxl.py             (hires 1536, default)

  Community vs Secure Cloud is chosen when you deploy the pod.
  Community is half price; a reclaimed pod loses nothing because output
  streams to R2 as it is produced.
""")

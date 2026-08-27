"""
audit.py — run this before spending GPU hours.

Every check here corresponds to something that has already gone wrong once on
this project. Cheap to run, expensive to skip.

    python3 audit.py generation_queue.csv
"""

import csv, re, sys
from collections import Counter

QUEUE = sys.argv[1] if len(sys.argv) > 1 else "generation_queue.csv"
rows = list(csv.DictReader(open(QUEUE, encoding="utf-8")))

fails, warns = [], []


def check(ok, label, detail="", warn=False):
    mark = "PASS" if ok else ("WARN" if warn else "FAIL")
    print(f"  [{mark}] {label}" + (f"  — {detail}" if detail else ""))
    if not ok:
        (warns if warn else fails).append(label)


print(f"AUDIT: {QUEUE}  ({len(rows):,} designs)\n")

# --- 1. uniqueness. The whole project turned on this once already. ---------
print("UNIQUENESS")
prompts = [r["prompt"] for r in rows]
combos = [(r["subject"], r["scene"], r["style"], r["composition"])
          for r in rows]
check(len(prompts) == len(set(prompts)), "no duplicate prompts",
      f"{len(prompts) - len(set(prompts))} dupes")
check(len(combos) == len(set(combos)), "no duplicate design combinations",
      f"{len(combos) - len(set(combos))} dupes")
check(len(set(r["index"] for r in rows)) == len(rows), "no duplicate indices")

# --- 2. token limits. SDXL's CLIP truncates at 77 and drops the tail, which
# is where the printability instructions live. Bitten twice. -----------------
print("\nPROMPT LENGTH")
est = [len(p) / 4.75 for p in prompts]
check(max(est) < 72, "prompts inside CLIP's 77-token limit",
      f"max ~{max(est):.0f} tokens")
neg = len(rows[0]["negative"]) / 4.75
check(neg < 72, "negative prompt inside limit", f"~{neg:.0f} tokens")

# --- 3. colour. Regressed once when prompts were shortened. ----------------
print("\nCOLOUR")
colour_words = ("multicolour", "vibrant", "vivid", "colour")
have = sum(1 for p in prompts if any(w in p.lower() for w in colour_words))
check(have == len(prompts), "every prompt asks for colour",
      f"{len(prompts) - have} missing")
mono = sum(1 for r in rows if "greyscale" in r["style"].lower()
           or "monochrome charcoal" in r["style"].lower())
share = mono / len(rows) * 100
check(5 <= share <= 25, "monochrome is a deliberate minority",
      f"{share:.0f}% of the run", warn=True)
pal = [int(r["palette"]) for r in rows]
check(sum(pal) / len(pal) >= 4.0, "average palette is rich",
      f"{sum(pal)/len(pal):.1f} colours")

# --- 4. spread. One template producing 725k designs is what killed the text
# engine; the same failure shape applies here. ------------------------------
print("\nSPREAD")
subj = Counter(r["subject"] for r in rows)
top_subj, top_n = subj.most_common(1)[0]
check(top_n / len(rows) < 0.02, "no subject dominates",
      f"largest is {top_subj} at {top_n/len(rows)*100:.2f}%")
check(len(subj) >= 250, "wide subject coverage", f"{len(subj)} subjects")
check(len(set(r["scene"] for r in rows)) >= 25, "wide scene coverage",
      f"{len(set(r['scene'] for r in rows))} scenes")
check(len(set(r["style"] for r in rows)) >= 15, "wide style coverage",
      f"{len(set(r['style'] for r in rows))} styles")

fam = Counter(r["family"] for r in rows)
biggest = fam.most_common(1)[0]
check(biggest[1] / len(rows) < 0.30, "no family dominates",
      f"{biggest[0]} at {biggest[1]/len(rows)*100:.0f}%")

# --- 5. sense checks. Pairings that read as machine output. ----------------
print("\nPAIRING SENSE")
thermal = 0
for r in rows:
    s = set(r["subject"].lower().split())
    sc = r["scene"].lower()
    if s & {"ember", "fire", "phoenix"} and any(
            w in sc for w in ("snow", "frozen", "ice")):
        thermal += 1
    if s & {"frost", "arctic", "polar"} and any(
            w in sc for w in ("flame", "ember")):
        thermal += 1
check(thermal == 0, "no thermal contradictions", f"{thermal} found")

# Scenes are atmosphere now, not locations, so the old habitat check no
# longer applies — foliage framing a dog is the panther reference, not an
# error. What still matters is that no scene depicts a full painted place.
scenic = sum(1 for r in rows if any(w in r["scene"].lower() for w in
             ("field", "forest", "ruins", "archway", "wasteland")))
check(scenic == 0, "no full painted scenes", f"{scenic} found")

# --- 6. print readiness ----------------------------------------------------
print("\nPRINT READINESS")
check(all("text" in r["negative"].lower() for r in rows),
      "text excluded via negative prompt")
check(all("black" in p.lower() for p in prompts),
      "every prompt specifies pure black, without asking for a painted panel")
# This check used to REQUIRE a fade instruction in every prompt. That was the
# original reference look, but it is the direct cause of the print problems:
# faded edges will not hold adhesive powder and print thin and patchy. The
# design should sit solid on a black ground instead. The check is inverted.
check(not any("fades into black" in p.lower() or "fading to black" in p.lower()
              or "dissolving into black" in p.lower() for p in prompts),
      "no fade-out instructions (they will not print)")
# Every subject has to be something a buyer would search for AND something
# that makes a striking image. Breadth is worthless if it fills the store
# with listings nobody wants. This catches the obvious failures — dull
# utility objects and species with no audience — so the list cannot quietly
# drift back toward padding.
DULL = (
    "squeegee", "theodolite", "set square", "calipers", "cement mixer",
    "forklift", "dumper", "hard hat", "shuttlecock", "curling stone",
    "bird table", "log pile", "farm gate", "milk churn", "butter churn",
    "wheat sheaf", "rock tumbler", "trail camera", "kelly kettle",
    "reading glasses", "library ladder",
)
# a bare object is dull; the same object with flowers or an animal is a
# design. "Watering Can And Blooms" is cottagecore, not a garden centre
# catalogue, so the check looks at what the subject is PAIRED with.
SAVED_BY = ("and ", " with ", "blooms", "flowers", "roses")
_bad = sorted({r["subject"] for r in rows
               if any(d in r["subject"].lower() for d in DULL)
               and not any(k in r["subject"].lower() for k in SAVED_BY)})
check(not _bad, "no dull utility objects as subjects",
      ", ".join(_bad[:4]) if _bad else f"{len(set(r['subject'] for r in rows)):,} subjects")

# Case-insensitive and near-duplicate subject check.
#
# The earlier check compared subject names exactly, so "Quill and Inkwell" and
# "Quill And Inkwell" both survived — and worse, graphics.py defines subjects
# in TWO lists, so a dedup pass over the first one silently left the second
# untouched. Both failures produced listings that differ only by capitals.
_subs = sorted({r["subject"] for r in rows})
_lower = [x.lower() for x in _subs]
check(len(_lower) == len(set(_lower)),
      "no subjects differing only by capitals",
      f"{len(_lower) - len(set(_lower))} found")

def _core(n):
    w = set(re.sub(r"[^a-z ]", "", n.lower()).split())
    return frozenset(w - {"and", "the", "of", "vintage", "retro", "antique",
                          "old", "classic", "a"})

_groups = {}
for _s in _subs:
    _groups.setdefault(_core(_s), []).append(_s)
_near = [v for v in _groups.values() if len(v) > 1]
check(not _near, "no near-duplicate subjects (same words reordered)",
      "; ".join(", ".join(v) for v in _near[:2]) if _near
      else f"{len(_subs):,} distinct subjects")

check(all("saturated" in p.lower() or "vibrant" in p.lower()
          or "vivid" in p.lower() for p in prompts),
      "every prompt asks for strong colour")
check(all("faded" in r["negative"].lower()
          and "desaturated" in r["negative"].lower() for r in rows),
      "faded and dull colour blocked in the negative")
check(all("no border" in r["negative"].lower() or "border" in r["negative"].lower()
          for r in rows),
      "borders and frames excluded")
hard = sum(1 for r in rows if any(w in r["style"].lower() for w in
           ("stained glass", "art nouveau", "vector mascot", "sticker",
            "knotwork", "papercut", "low poly", "flat vector")))
check(hard == 0, "no hard-edged panel styles", f"{hard} found")
# Adult content must be blocked on every prompt without exception — this is
# a listing-removal and account-standing issue, not a taste one.
adult = ("nude", "naked", "topless", "sexual", "erotic", "lingerie")
check(all(all(w in r["negative"].lower() for w in adult) for r in rows),
      "adult content blocked in every negative prompt")
human = [r for r in rows if r["family"] == "human"]
check(all("fully clothed" in r["prompt"].lower() for r in human),
      "human subjects specify fully clothed",
      f"{len(human):,} human designs")
check(all("border" in r["negative"].lower() for r in rows),
      "borders excluded (a bounded shape prints as a rectangle)")
check(all("white background" in r["negative"].lower() for r in rows),
      "light backgrounds excluded (must knock out cleanly)")

# --- summary ---------------------------------------------------------------
print("\n" + "=" * 60)
if fails:
    print(f"FAILED {len(fails)} CHECK(S) — do not run until fixed:")
    for f in fails:
        print(f"  * {f}")
    sys.exit(1)
print("ALL CHECKS PASSED")
if warns:
    print(f"\n{len(warns)} warning(s), review but not blocking:")
    for w in warns:
        print(f"  * {w}")
print(f"\n{len(rows):,} designs ready to generate")

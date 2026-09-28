#!/usr/bin/env python3
"""Mine real slogan templates out of designs_read.jsonl.

The 8 templates we have now were inferred from 5 images and explain 7.1% of
sales. This reads what is ACTUALLY printed on 22,485 designs that sold, and
derives the templates from the text itself.

    python3 analyse_reads.py designs_read.jsonl

Writes:
  MINED_TEMPLATES.csv   slogan skeletons + fillers + sales they explain
  MINED_SUBJECTS.csv    what gets illustrated, ranked by sales
  READ_FINDINGS.csv     every headline number, with the caveat attached
"""
import csv, json, re, sys
from collections import Counter, defaultdict

SRC = sys.argv[1] if len(sys.argv) > 1 else "designs_read.jsonl"

# Words that carry the joke/subject and must never be masked away wholesale;
# masking these is how you end up with the useless template "{X}".
STOP = {"a","an","the","of","and","or","to","in","on","is","it","for","with",
        "my","me","i","you","your","we","our","this","that","at","as","be",
        "but","not","are","was","by","from"}


# ------------------------------------------------------------------ loading
def load(path):
    rows, broken = [], 0
    for line in open(path, encoding="utf-8"):
        line = line.strip()
        if not line:
            continue
        try:
            r = json.loads(line)
        except Exception:
            broken += 1
            continue
        lines = r.get("text_lines") or []
        if not isinstance(lines, list):
            lines = [str(lines)]
        r["lines"] = [str(x).strip() for x in lines if str(x).strip()]
        r["slogan"] = " ".join(r["lines"])
        rows.append(r)
    return rows, broken


def norm(s):
    s = s.upper()
    s = re.sub(r"[^A-Z0-9' ]+", " ", s)
    return re.sub(r"\s+", " ", s).strip()


# ------------------------------------------------- template mining
def mine(rows, min_fillers=4):
    """A template is a token sequence with one contiguous span masked out.

    It only counts as a template if the mask attracts several DIFFERENT
    fillers - otherwise it is just one slogan with a hole punched in it.
    """
    cand = defaultdict(lambda: {"fillers": Counter(), "sold": 0, "n": 0})

    for r in rows:
        toks = norm(r["slogan"]).split()
        if not (3 <= len(toks) <= 14):
            continue
        sold = r.get("sold") or 0
        seen = set()
        for i in range(len(toks)):
            for j in range(i + 1, min(i + 4, len(toks)) + 1):   # spans of 1-4
                span = toks[i:j]
                if all(t in STOP for t in span):
                    continue
                skel = tuple(toks[:i]) + ("{X}",) + tuple(toks[j:])
                # a skeleton that is nearly all mask tells us nothing
                if sum(1 for t in skel if t != "{X}" and t not in STOP) < 2:
                    continue
                if skel in seen:
                    continue
                seen.add(skel)
                c = cand[skel]
                c["fillers"][" ".join(span)] += 1
                c["sold"] += sold
                c["n"] += 1

    out = []
    for skel, c in cand.items():
        if len(c["fillers"]) < min_fillers:
            continue
        out.append({
            "template": " ".join(skel),
            "distinct_fillers": len(c["fillers"]),
            "designs": c["n"],
            "units_sold": c["sold"],
            "top_fillers": " | ".join(f for f, _ in c["fillers"].most_common(12)),
        })

    # A longer skeleton that covers the same designs as a shorter one is the
    # more useful brief, so prefer specific over generic on equal sales.
    out.sort(key=lambda d: (-d["units_sold"], -d["distinct_fillers"]))
    return dedupe(out)


def dedupe(templates, keep=400):
    """Drop a template whose designs are already explained by a better one."""
    kept, claimed = [], set()
    for t in templates:
        key = frozenset(re.sub(r"\{X\}", "", t["template"]).split())
        if any(key <= k or k <= key for k in claimed):
            continue
        claimed.add(key)
        kept.append(t)
        if len(kept) >= keep:
            break
    return kept


# ------------------------------------------------- reporting
def pct(a, b):
    return f"{100.0*a/b:.1f}%" if b else "n/a"


def main():
    rows, broken = load(SRC)
    if not rows:
        sys.exit(f"no usable rows in {SRC}")
    total_sold = sum(r.get("sold") or 0 for r in rows)
    with_text = [r for r in rows if r["lines"]]
    illus = [r for r in rows if r.get("main_image") not in (None, "", "null")]

    print(f"{len(rows):,} designs read  ({broken:,} unparseable lines skipped)")
    print(f"{len(with_text):,} carry text  ({pct(len(with_text), len(rows))})")
    print(f"{len(illus):,} carry an illustration  ({pct(len(illus), len(rows))})")
    print(f"{total_sold:,} units across the set\n")

    templates = mine(rows)
    explained = sum(t["units_sold"] for t in templates)
    print(f"{len(templates):,} templates mined, explaining {pct(explained, total_sold)} "
          f"of units (old hand-written set: 7.1%)\n")
    print("top 25 by units:")
    for t in templates[:25]:
        print(f"  {t['units_sold']:>7,}u  {t['distinct_fillers']:>4} fillers   "
              f"{t['template'][:70]}")

    with open("MINED_TEMPLATES.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(templates[0].keys()))
        w.writeheader(); w.writerows(templates)

    subj = defaultdict(lambda: [0, 0])
    for r in illus:
        k = norm(str(r["main_image"]))[:60]
        if k:
            subj[k][0] += 1; subj[k][1] += r.get("sold") or 0
    srows = sorted(({"subject": k, "designs": v[0], "units_sold": v[1]}
                    for k, v in subj.items()), key=lambda d: -d["units_sold"])
    with open("MINED_SUBJECTS.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["subject", "designs", "units_sold"])
        w.writeheader(); w.writerows(srows[:3000])
    print(f"\ntop illustrated subjects: "
          f"{', '.join(d['subject'].lower() for d in srows[:12])}")

    def dist(field):
        c = Counter(); u = Counter()
        for r in rows:
            v = str(r.get(field) or "unknown")
            c[v] += 1; u[v] += r.get("sold") or 0
        return c, u

    find = []
    for field in ("style", "layout"):
        c, u = dist(field)
        print(f"\n{field}:")
        for k, n in c.most_common():
            upd = u[k] / n if n else 0
            print(f"  {k:<22} {n:>7,} designs  {u[k]:>8,}u  {upd:.2f} u/design")
            find.append({"finding": f"{field}={k}", "designs": n,
                         "units": u[k], "units_per_design": f"{upd:.2f}"})

    with open("READ_FINDINGS.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["finding", "designs", "units",
                                           "units_per_design"])
        w.writeheader(); w.writerows(find)
    print("\nwrote MINED_TEMPLATES.csv, MINED_SUBJECTS.csv, READ_FINDINGS.csv")


if __name__ == "__main__":
    main()

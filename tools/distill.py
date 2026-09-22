"""Turn the per-image fingerprints into a written style spec.

    python3 tools/distill.py           # stats only, no API calls
    python3 tools/distill.py --prompt  # also have Claude write the generator prompt

Reads data/analyzed.jsonl and writes data/STYLE_SPEC.md — the distilled,
human-readable answer to "what do these designs actually have in common,
and what do the winners do that the rest don't".

That file is the thing that persists between sessions. It is what makes
generation grounded in your data instead of guesswork.
"""

import json
import os
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ANALYZED = ROOT / "data" / "analyzed.jsonl"
SPEC = ROOT / "data" / "STYLE_SPEC.md"

MODEL = os.environ.get("ANALYSIS_MODEL", "claude-sonnet-5")


def load():
    if not ANALYZED.exists():
        sys.exit("No data/analyzed.jsonl — run tools/analyze.py first.")
    rows = []
    for line in ANALYZED.read_text().splitlines():
        line = line.strip()
        if line:
            rows.append(json.loads(line))
    return [r for r in rows if r.get("is_tshirt_design", True)]


def score(row):
    """Rough winner score from whatever performance signal exists."""
    perf = row.get("performance") or {}
    try:
        reviews = float(str(perf.get("review_count", "")).replace(",", "") or 0)
    except ValueError:
        reviews = 0
    try:
        rating = float(perf.get("rating") or 0)
    except ValueError:
        rating = 0
    try:
        bsr = float(str(perf.get("bsr", "")).replace(",", "") or 0)
    except ValueError:
        bsr = 0
    try:
        sold = float(str(perf.get("quantity_sold", "")).replace(",", "") or 0)
    except ValueError:
        sold = 0
    gut = float(perf.get("gut_score") or 0)

    # Units sold is the strongest signal there is — weight it above the rest.
    s = sold * 100 + gut * 20 + reviews + (rating * 10 if rating else 0)
    if bsr:
        s += max(0, 1_000_000 - bsr) / 10_000
    return s


def tally(rows, key, top=8):
    counter = Counter()
    for row in rows:
        value = row.get(key)
        if isinstance(value, list):
            counter.update(v for v in value if v)
        elif value:
            counter[value] += 1
    return counter.most_common(top)


def section(title, pairs, total):
    if not pairs:
        return f"### {title}\n\n_no data_\n\n"
    out = [f"### {title}\n"]
    for value, n in pairs:
        pct = round(100 * n / total) if total else 0
        out.append(f"- **{value}** — {n} ({pct}%)")
    return "\n".join(out) + "\n\n"


def build_stats(rows, winners):
    total = len(rows)
    md = [
        "# Style Spec\n\n",
        f"_Distilled from {total} analysed designs"
        + (f", {len(winners)} of them flagged as winners" if winners else "")
        + ". Regenerate with `python3 tools/distill.py`._\n\n",
        "## What these designs have in common\n\n",
    ]

    for label, key in [
        ("Layout", "layout"),
        ("Hook type", "hook_type"),
        ("Illustration style", "illustration_style"),
        ("Niche", "niche"),
        ("Print complexity", "print_complexity"),
    ]:
        md.append(section(label, tally(rows, key), total))

    typo_style = Counter(
        (r.get("typography") or {}).get("style") for r in rows
        if (r.get("typography") or {}).get("style")
    )
    md.append(section("Typography", typo_style.most_common(8), total))

    effects = Counter()
    for row in rows:
        effects.update(e for e in (row.get("typography") or {}).get("effects", [])
                       if e and e != "none")
    md.append(section("Type effects", effects.most_common(8), total))

    colors = Counter()
    for row in rows:
        for c in row.get("palette", [])[:3]:
            colors[c["hex"]] += 1
    md.append(section("Most common colours (top 3 per design)",
                      colors.most_common(12), total))

    counts = [r.get("color_count", 0) for r in rows if r.get("color_count")]
    if counts:
        md.append(f"Average significant colour count: "
                  f"**{sum(counts) / len(counts):.1f}**\n\n")

    md.append("## Title formulas\n\n")
    for formula, n in tally(rows, "title_formula", top=25):
        md.append(f"- `{formula}`" + (f" ×{n}" if n > 1 else "") + "\n")

    md.append("\n## Slogan formulas\n\n")
    for formula, n in tally(rows, "slogan_formula", top=25):
        md.append(f"- `{formula}`" + (f" ×{n}" if n > 1 else "") + "\n")

    md.append("\n## Keywords being targeted\n\n")
    kw = tally(rows, "keywords_visible", top=30)
    md.append(", ".join(f"{k} ({n})" for k, n in kw) + "\n")

    if winners:
        md.append("\n## What the winners do differently\n\n")
        w_total = len(winners)
        for label, key in [("Layout", "layout"), ("Hook type", "hook_type"),
                           ("Illustration style", "illustration_style")]:
            all_share = {v: n / total for v, n in tally(rows, key, top=20)}
            lines = []
            for value, n in tally(winners, key, top=6):
                w_share = n / w_total
                delta = (w_share - all_share.get(value, 0)) * 100
                arrow = "over" if delta > 5 else ("under" if delta < -5 else "same")
                lines.append(
                    f"- **{value}** — {round(w_share * 100)}% of winners "
                    f"vs {round(all_share.get(value, 0) * 100)}% overall "
                    f"({arrow}-represented)")
            md.append(f"### {label}\n\n" + "\n".join(lines) + "\n\n")

        md.append("### Winning titles verbatim\n\n")
        for row in winners[:15]:
            md.append(f"- {row.get('title', '')}\n")

    risky = [r for r in rows if r.get("ip_risk") in ("possible", "clear")]
    if risky:
        md.append(f"\n## IP flags — {len(risky)} design(s)\n\n")
        for row in risky[:15]:
            md.append(f"- **{row.get('ip_risk')}** — {row.get('title', '')[:70]}"
                      f" — {row.get('quality_notes', '')}\n")
        md.append("\nThese are examples NOT to imitate. Learn the structure, "
                  "never the protected element.\n")

    return "".join(md)


def write_generator_prompt(rows, winners, stats_md):
    """Have Claude read the distilled stats and write the generator prompt."""
    import anthropic

    key = os.environ.get("ANTHROPIC_API_KEY")
    if not key:
        print("\nSkipping --prompt: ANTHROPIC_API_KEY not set.")
        return ""

    sample = [
        {k: r.get(k) for k in ("title", "shirt_text", "niche", "hook_type",
                               "layout", "title_formula", "slogan_formula",
                               "illustration_style", "quality_notes")}
        for r in (winners or rows)[:40]
    ]

    print(f"\nWriting generator prompt with {MODEL}...")
    client = anthropic.Anthropic(api_key=key)
    resp = client.messages.create(
        model=MODEL,
        max_tokens=3000,
        messages=[{"role": "user", "content": f"""Here is a distilled analysis \
of real t-shirt designs from a print-on-demand marketplace, plus the raw \
fingerprints of the best performers.

{stats_md[:6000]}

Best performers:
{json.dumps(sample, indent=2)[:12000]}

Write the house rules for generating NEW designs in this space. Be concrete
and specific to THIS data — cite the actual patterns above, not generic
print-on-demand advice. Cover:

1. The niches and audiences that are working here
2. The slogan structures worth reusing, with slots
3. Title construction rules
4. Visual direction: layout, typography, illustration style, colour count
5. What to avoid — the patterns that look lazy or oversaturated in this set
6. Hard rules: never reproduce a real design, never use protected IP

Write it as direct instructions to a designer. Markdown, no preamble."""}],
    )
    return resp.content[0].text.strip()


def main(want_prompt=False):
    rows = load()
    if not rows:
        sys.exit("No usable designs in data/analyzed.jsonl.")

    ranked = sorted(rows, key=score, reverse=True)
    scored = [r for r in ranked if score(r) > 0]
    # Top third by performance, but only where a signal actually exists.
    winners = scored[:max(1, len(scored) // 3)] if scored else []

    stats_md = build_stats(rows, winners)

    if want_prompt:
        generated = write_generator_prompt(rows, winners, stats_md)
        if generated:
            stats_md += "\n\n---\n\n# House Rules for New Designs\n\n" + generated + "\n"

    SPEC.write_text(stats_md, encoding="utf-8")
    print(f"\nWrote data/STYLE_SPEC.md ({len(stats_md.splitlines())} lines) "
          f"from {len(rows)} designs.")
    if not winners:
        print("No performance data found — fill in rating/review_count/bsr "
              "to unlock the 'what the winners do differently' section.")


if __name__ == "__main__":
    main(want_prompt="--prompt" in sys.argv)

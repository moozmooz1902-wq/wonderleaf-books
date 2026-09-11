"""Read every design image with Claude's vision and extract a fingerprint.

    python3 tools/analyze.py            # analyse anything not yet done
    python3 tools/analyze.py --redo     # re-analyse everything

This is the step that actually learns from the artwork. Each image plus its
listing title goes to Claude, which returns a strict JSON fingerprint:
what is drawn, how it is laid out, the typography, and — most valuable —
the generalised TITLE and SLOGAN formulas behind it.

Results are cached in data/analyzed.jsonl keyed by image hash, so re-runs
cost nothing for images already done.

Needs ANTHROPIC_API_KEY in the environment.
"""

import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from palette import extract_palette  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
IMAGES = ROOT / "data" / "images"
DESIGNS = ROOT / "data" / "designs.jsonl"
ANALYZED = ROOT / "data" / "analyzed.jsonl"

MODEL = os.environ.get("ANALYSIS_MODEL", "claude-sonnet-5")

PROMPT = """You are analysing a t-shirt design for a print-on-demand research \
dataset. Study the image closely and extract its structure.

Listing title: {title}
Measured palette (from pixel data, trust this over your own estimate): {palette}

Describe what is ACTUALLY there. Do not flatter the design and do not
invent detail you cannot see. If the image is not a t-shirt design, set
"is_tshirt_design" to false and leave the rest minimal.

The two most important fields are title_formula and slogan_formula. Those
are the abstract patterns, with the specifics replaced by {{SLOTS}}, so the
same structure can be reused for a different subject. For example:
  "Best {{ROLE}} Ever" -> "Best {{ROLE}} Ever"
  "It's a Bassett Hound Thing You Wouldn't Understand"
      -> "It's a {{NOUN}} Thing You Wouldn't Understand"
  "Sorry I'm Late My Dog Wanted Cuddles"
      -> "Sorry I'm Late, My {{SUBJECT}} {{RELATABLE_EXCUSE}}"

Return ONLY valid JSON, no preamble:

{{
  "is_tshirt_design": true,
  "shirt_text": ["each line of text printed on the shirt, verbatim, in order"],
  "has_text": true,
  "subject": "the main visual element in a few words, or null if text-only",
  "illustration_style": "one of: none, flat_vector, hand_drawn, cartoon_mascot, line_art, watercolour, distressed_vintage, photographic, 3d_render",
  "typography": {{
    "style": "one of: bold_sans, script, serif, slab, handwritten, mixed, novelty",
    "case": "one of: uppercase, title_case, lowercase, mixed",
    "effects": ["outline", "drop_shadow", "distressed", "arched", "gradient", "none"]
  }},
  "layout": "one of: stacked_centered, arched_text, badge_circle, left_chest, full_front_scene, text_over_illustration, illustration_over_text",
  "niche": "specific audience, e.g. 'pediatric nurse' not 'nurse'",
  "audience_detail": "who buys this and the occasion they buy it for",
  "hook_type": "one of: pun, in_group_joke, pride_statement, sarcasm, wholesome, milestone_gift, hobby_identity",
  "hook_explanation": "one sentence on why this lands with that audience",
  "title_formula": "the listing title abstracted into {{SLOTS}}",
  "slogan_formula": "the shirt text abstracted into {{SLOTS}}",
  "keywords_visible": ["search terms this design is clearly targeting"],
  "print_complexity": "one of: low, medium, high",
  "ip_risk": "none | possible | clear — flag visible brands, characters or known trademarked phrases",
  "quality_notes": "one blunt line: what makes it work, or why it looks lazy"
}}"""


def load_jsonl(path):
    rows = {}
    if path.exists():
        for line in path.read_text().splitlines():
            line = line.strip()
            if line:
                row = json.loads(line)
                rows[row["id"]] = row
    return rows


def media_type(path):
    return {
        ".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
        ".webp": "image/webp", ".gif": "image/gif",
    }.get(path.suffix.lower(), "image/png")


def analyze_one(client, design, image_path):
    import base64

    colors = extract_palette(image_path)
    palette_text = ", ".join(
        f"{c['hex']} ({int(c['share'] * 100)}%)" for c in colors["palette"]
    ) or "could not measure"

    data = base64.standard_b64encode(image_path.read_bytes()).decode()
    resp = client.messages.create(
        model=MODEL,
        max_tokens=1500,
        messages=[{
            "role": "user",
            "content": [
                {"type": "image", "source": {
                    "type": "base64",
                    "media_type": media_type(image_path),
                    "data": data,
                }},
                {"type": "text", "text": PROMPT.format(
                    title=design.get("title") or "(none given)",
                    palette=palette_text,
                )},
            ],
        }],
    )

    text = resp.content[0].text.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1] if "\n" in text else text
        if text.endswith("```"):
            text = text.rsplit("```", 1)[0]
        text = text.strip()

    result = json.loads(text)
    result["id"] = design["id"]
    result["title"] = design.get("title", "")
    result["niche_given"] = design.get("niche", "")
    result["label"] = design.get("label", "positive")
    result["performance"] = design.get("performance", {})
    result.update(colors)
    return result


def main(redo=False):
    import anthropic

    key = os.environ.get("ANTHROPIC_API_KEY")
    if not key:
        sys.exit("Set ANTHROPIC_API_KEY first:  export ANTHROPIC_API_KEY=sk-ant-...")
    if not DESIGNS.exists():
        sys.exit("No data/designs.jsonl — run tools/ingest.py first.")

    designs = load_jsonl(DESIGNS)
    done = {} if redo else load_jsonl(ANALYZED)
    todo = [d for d in designs.values() if d["id"] not in done]

    if not todo:
        print(f"All {len(designs)} designs already analysed. --redo to force.")
        return 0

    print(f"Analysing {len(todo)} of {len(designs)} designs with {MODEL}...\n")
    client = anthropic.Anthropic(api_key=key)
    failed = 0

    for n, design in enumerate(todo, 1):
        image_path = IMAGES / design["image_file"]
        label = design.get("title", design["id"])[:50]
        if not image_path.exists():
            print(f"  [{n}/{len(todo)}] SKIP {label} — image missing")
            failed += 1
            continue
        try:
            result = analyze_one(client, design, image_path)
        except Exception as e:
            print(f"  [{n}/{len(todo)}] FAILED {label} — {e}")
            failed += 1
            continue

        done[result["id"]] = result
        # Write after each one so a crash never loses completed work.
        with open(ANALYZED, "w", encoding="utf-8") as fh:
            for row in done.values():
                fh.write(json.dumps(row, ensure_ascii=False) + "\n")
        print(f"  [{n}/{len(todo)}] {label}\n"
              f"        {result.get('layout')} / {result.get('hook_type')}"
              f" / {result.get('illustration_style')}")

    print(f"\n{len(done)} analysed, {failed} failed → data/analyzed.jsonl")
    print("Next: python3 tools/distill.py")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(redo="--redo" in sys.argv))

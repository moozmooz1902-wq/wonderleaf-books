#!/usr/bin/env python3
"""
Assemble generation inputs from the data pool.

Two jobs:

  1. `render`   - build the image prompt for a concept by composing its style/layout
                  DNA with the concept's own subject and palette. Constraint on six
                  axes is what pulls output off the generative mean.

  2. `metadata` - emit ONE model request per (concept x platform), carrying that
                  platform's exact limits. Never ask one call to write metadata for
                  every platform at once - the limits conflict and the model averages
                  them into something that violates all of them.

Stdlib only.

Usage:
    python3 build_prompt.py render   concepts.json
    python3 build_prompt.py metadata concepts.json --platform redbubble
    python3 build_prompt.py brief    --product poster --style ps_wpa_park --niche nb_travel_place
"""

import argparse
import json
import sys
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / "data"


def load(name):
    with open(DATA / name, encoding="utf-8") as fh:
        return json.load(fh)


SPECS = load("platform_specs.json")
STYLES = {s["id"]: s for s in load("poster_style_dna.json")["styles"]}
LAYOUTS = {a["id"]: a for a in load("tshirt_layout_archetypes.json")["archetypes"]}
PALETTES = {p["id"]: p for p in load("palettes.json")["palettes"]}
POSTER_NICHES = {n["id"]: n for n in load("poster_niches.json")["niches"]}
TSHIRT_NICHES = {n["id"]: n for n in load("tshirt_niches.json")["niches"]}
RUBRIC = load("quality_rubric.json")
UNIVERSAL_TEE_RULES = load("tshirt_layout_archetypes.json")["_meta"]["universal_rules"]


# ------------------------------------------------------------- render

def build_render(concept):
    """Compose the positive and negative prompt from style DNA + concept specifics."""
    v = concept["visual"]
    klass = concept["product_class"]
    dna = STYLES.get(v.get("style_id")) if klass == "poster" else LAYOUTS.get(v.get("layout_id"))
    if dna is None:
        raise SystemExit(f"{concept.get('concept_id')}: unknown style/layout id")

    pal = v.get("palette") or []
    if not pal and v.get("palette_id"):
        pal = PALETTES[v["palette_id"]]["hex"]
    pal_name = PALETTES.get(v.get("palette_id"), {}).get("name", "custom palette")

    positive = ", ".join(filter(None, [
        dna["render_cues"],
        f"subject: {v.get('subject')}" if v.get("subject") else None,
        f"palette {pal_name} strictly limited to {' '.join(pal)}" if pal else None,
        v.get("composition"),
        v.get("typography"),
        v.get("texture"),
    ]))

    negatives = list(dict.fromkeys(
        (dna.get("avoid") or []) + (v.get("avoid") or []) + RUBRIC["slop_padding_terms"]
    ))

    out = {
        "concept_id": concept.get("concept_id"),
        "product_class": klass,
        "positive_prompt": positive,
        "negative_prompt": ", ".join(negatives),
        "output_spec": concept.get("production"),
        "thumbnail_check": v.get("reads_at_250px_via") or dna.get("reads_at_250px_via"),
    }
    if klass == "tshirt":
        out["text_slots"] = v.get("text_slots", {})
        out["hard_rules"] = UNIVERSAL_TEE_RULES
    else:
        out["hard_rules"] = [
            "One focal subject only",
            "No frame or border drawn inside the artwork",
            "Keep all readable content at least 200px from every edge",
            "Avoid a very dark overall composition - Displate rejects for it",
            "No upscaling and no filters used to mask quality",
        ]
    return out


# ----------------------------------------------------------- metadata

def build_metadata_request(concept, platform):
    """One model request, carrying exactly one platform's limits."""
    spec = SPECS["platforms"].get(platform)
    if spec is None:
        raise SystemExit(f"unknown platform {platform!r}")
    meta = spec.get("metadata", {})
    d, a, v = concept["demand"], concept["angle"], concept["visual"]

    fields = {}
    t = meta.get("title", {})
    if t:
        fields["title"] = {
            "max_chars": t.get("max_chars"),
            "min_chars": t.get("min_chars"),
            "rule": t.get("rule"),
        }
    tg = meta.get("tags", {})
    if tg:
        fields["tags"] = {
            "count": tg.get("count"),
            "max_chars_each": tg.get("max_chars_each"),
            "rule": tg.get("rule"),
        }
    if meta.get("description"):
        fields["description"] = {"rule": meta["description"]["rule"]}
    if meta.get("bullets"):
        fields["bullets"] = meta["bullets"]
    if meta.get("brand"):
        fields["brand"] = meta["brand"]
    if meta.get("attributes"):
        fields["attributes"] = meta["attributes"]

    hard = [
        "Write for ONE buyer intent - this listing, this phrase.",
        "The title owns the primary phrase. Tags cover ADJACENT phrases the title does not contain.",
        "No tag may be a subset of the title's words - that wastes the slot.",
        "The description must not repeat the title verbatim.",
        "Multi-word phrase tags only. Single broad words rank for nothing.",
        "No brand, franchise, character, band, team or artist names anywhere, including backend terms.",
    ]
    if v.get("subject") and concept["angle"]["emotional_job"] == "room_decor":
        hard.append("Decor listing: the title MUST contain a colour word and, where it fits, a room word.")
    if concept["angle"]["emotional_job"] == "gift_for_relationship":
        hard.append("Gift listing: the title MUST contain the relationship word the buyer searches "
                    "(mom, dad, nana, wife, coworker...).")

    return {
        "concept_id": concept.get("concept_id"),
        "platform": platform,
        "context": {
            "primary_query": d["query"],
            "adjacent_queries": d["adjacent"],
            "audience": a["audience"],
            "insider_vocab": a["insider_vocab"],
            "emotional_job": a["emotional_job"],
            "subject": v.get("subject"),
            "style": v.get("style_id") or v.get("layout_id"),
            "palette_name": PALETTES.get(v.get("palette_id"), {}).get("name"),
        },
        "fields": fields,
        "hard_rules": hard,
        "return_shape": {k: ("string" if k != "tags" else "array of strings") for k in fields},
    }


# -------------------------------------------------------------- brief

def specificity_instruction(niche):
    """Decor niches are graded by search grammar; t-shirt niches by a specificity ladder."""
    ladder = niche.get("specificity_ladder")
    if ladder:
        return ("Every concept must sit at specificity rung >= 2 on this niche's ladder: "
                f"{ladder}")
    grammar = load("poster_niches.json")["_meta"]["search_grammar"]
    market = niche.get("market", "decor")
    key = "collector" if market == "collector" else "decor"
    return ("Every concept must be born from a full search phrase in this market's grammar - "
            f"{grammar[key]} - never from a bare theme.")


def build_brief(product, style_id, niche_id):
    """A generation brief: everything a model needs to invent concepts INSIDE a lane."""
    if product == "poster":
        dna, niches = STYLES.get(style_id), POSTER_NICHES
    else:
        dna, niches = LAYOUTS.get(style_id), TSHIRT_NICHES
    niche = niches.get(niche_id)
    if dna is None:
        raise SystemExit(f"unknown style/layout {style_id!r}")
    if niche is None:
        raise SystemExit(f"unknown niche {niche_id!r}")

    return {
        "product_class": product,
        "style_or_layout": dna,
        "niche": niche,
        "instructions": [
            "Generate concepts ONLY inside this style x niche lane.",
            "Every concept starts from a search phrase, never from a theme.",
            specificity_instruction(niche),
            "Use the niche's insider_vocab - that vocabulary is the belonging signal."
            if niche.get("insider_vocab") else
            "Decor listings: the title must carry a COLOUR word and, where it fits, a ROOM word - "
            f"colours that matter here: {niche.get('colour_words_that_matter')}; "
            f"rooms: {niche.get('room_words')}",
            "Do not vary the palette between concepts in the same set family.",
            "Vary the SUBJECT, never the colourway. Colourways are product options, not listings.",
            f"IP tier for this niche is {niche.get('ip_risk')} - obey the corresponding rule.",
            "Emit objects conforming to schemas/concept.schema.json.",
        ],
    }


# ---------------------------------------------------------------- cli

def read_concepts(path):
    with open(path, encoding="utf-8") as fh:
        payload = json.load(fh)
    return payload if isinstance(payload, list) else [payload]


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    r = sub.add_parser("render", help="build image prompts")
    r.add_argument("path")

    m = sub.add_parser("metadata", help="build one metadata request per concept x platform")
    m.add_argument("path")
    m.add_argument("--platform", required=True)

    b = sub.add_parser("brief", help="build a generation brief for a style x niche lane")
    b.add_argument("--product", choices=["poster", "tshirt"], required=True)
    b.add_argument("--style", required=True, help="style_id or layout_id")
    b.add_argument("--niche", required=True)

    args = ap.parse_args()

    if args.cmd == "render":
        out = [build_render(c) for c in read_concepts(args.path)]
    elif args.cmd == "metadata":
        out = [build_metadata_request(c, args.platform) for c in read_concepts(args.path)]
    else:
        out = build_brief(args.product, args.style, args.niche)

    json.dump(out, sys.stdout, indent=2, ensure_ascii=False)
    print()


if __name__ == "__main__":
    try:
        main()
    except BrokenPipeError:          # piping into head/less
        sys.stderr.close()

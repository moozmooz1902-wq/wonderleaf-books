#!/usr/bin/env python3
"""
Validate and score POD concepts against the six gates in data/quality_rubric.json.

Stdlib only - no dependencies.

Usage:
    python3 validate_concept.py concepts.json
    python3 validate_concept.py live_catalogue.json new_batch.json --verbose
    python3 validate_concept.py concepts.json --json > report.json

Each file may be a single concept object or a list of them. Pass the live
catalogue alongside a new batch so G6 (dedup) can see both - dedup only
catches what it is shown.

Exit code 0 if every concept passes, 1 otherwise.
"""

import argparse
import json
import re
import sys
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / "data"


def load(name):
    with open(DATA / name, encoding="utf-8") as fh:
        return json.load(fh)


RUBRIC = load("quality_rubric.json")
SPECS = load("platform_specs.json")["platforms"]
IP = load("ip_risk_rules.json")
POSTER_STYLES = {s["id"] for s in load("poster_style_dna.json")["styles"]}
TSHIRT_LAYOUTS = {a["id"] for a in load("tshirt_layout_archetypes.json")["archetypes"]}
PALETTES = {p["id"] for p in load("palettes.json")["palettes"]}

APPAREL_PLATFORMS = {"amazon_merch", "teepublic"}
WORD_RE = re.compile(r"[a-z0-9']+")


def tokens(text):
    return set(WORD_RE.findall((text or "").lower()))


def trigrams(text):
    norm = " ".join(sorted(WORD_RE.findall((text or "").lower())))
    return {norm[i:i + 3] for i in range(max(0, len(norm) - 2))}


class Result:
    """Accumulates gate outcomes for one concept."""

    def __init__(self, concept_id):
        self.concept_id = concept_id
        self.kills = []      # (gate, check_id, message)
        self.deductions = [] # (gate, check_id, message, points)
        self.notes = []

    def kill(self, gate, check, msg):
        self.kills.append((gate, check, msg))

    def deduct(self, gate, check, msg, points):
        self.deductions.append((gate, check, msg, points))

    def note(self, msg):
        self.notes.append(msg)

    @property
    def score(self):
        return max(0, 100 - sum(d[3] for d in self.deductions))

    @property
    def passed(self):
        return not self.kills and self.score >= RUBRIC["pass_threshold"]

    def to_dict(self):
        return {
            "concept_id": self.concept_id,
            "passed": self.passed,
            "score": self.score,
            "kills": [{"gate": g, "check": c, "message": m} for g, c, m in self.kills],
            "deductions": [{"gate": g, "check": c, "message": m, "points": p}
                           for g, c, m, p in self.deductions],
            "notes": self.notes,
        }


# ---------------------------------------------------------------- gates

def gate_g0(c, r):
    d = c.get("demand") or {}
    q = (d.get("query") or "").strip()
    if not q:
        return r.kill("G0", "g0_query_present", "demand.query is missing")
    words = q.split()
    if not 2 <= len(words) <= 6:
        r.kill("G0", "g0_query_present",
               f"demand.query is {len(words)} words; must be 2-6: {q!r}")
    if q.lower() in RUBRIC["generic_noun_denylist"]:
        r.kill("G0", "g0_not_generic", f"demand.query {q!r} is a generic term")
    if len(words) == 1:
        r.kill("G0", "g0_not_generic", f"demand.query {q!r} is a single word")

    adjacent = d.get("adjacent") or []
    if len(set(adjacent)) < 8:
        r.kill("G0", "g0_adjacent",
               f"demand.adjacent has {len(set(adjacent))} distinct phrases; needs >= 8")

    if d.get("evidence") not in RUBRIC["allowed_evidence_types"]:
        r.kill("G0", "g0_evidence", f"demand.evidence {d.get('evidence')!r} is not an allowed type")
    if d.get("evidence") == "qualitative" and not d.get("evidence_note"):
        r.kill("G0", "g0_evidence", "qualitative evidence requires an evidence_note naming the source")

    vol = d.get("est_monthly_volume")
    if vol is None:
        if d.get("evidence") != "qualitative":
            r.deduct("G0", "g0_volume", "no est_monthly_volume and evidence is not qualitative", 10)
    elif vol < 1000:
        r.deduct("G0", "g0_volume",
                 f"est_monthly_volume {vol} < 1000; justify via the long-tail ecosystem", 10)

    if d.get("competition") == "high" and not (c.get("angle") or {}).get("differentiator"):
        r.kill("G0", "g0_competition",
               "competition is 'high' but angle.differentiator is empty")


def gate_g1(c, r):
    a = c.get("angle") or {}
    aud = (a.get("audience") or "").strip().lower()
    if not aud:
        r.kill("G1", "g1_audience", "angle.audience is missing")
    elif aud in {"everyone", "anyone", "general", "all"} or len(aud.split()) < 3:
        r.kill("G1", "g1_audience",
               f"angle.audience {aud!r} is not specific enough - name who exactly buys this")

    if len(a.get("insider_vocab") or []) < 3:
        r.kill("G1", "g1_vocab", "angle.insider_vocab needs >= 3 community terms")

    if a.get("emotional_job") not in RUBRIC["allowed_emotional_jobs"]:
        r.kill("G1", "g1_job", f"angle.emotional_job {a.get('emotional_job')!r} is not allowed")

    rung = a.get("specificity_rung")
    if not isinstance(rung, int) or rung < 2:
        r.kill("G1", "g1_ladder",
               f"angle.specificity_rung is {rung}; must be >= 2 (rungs 0-1 are the dead generic tiers)")


def gate_g2(c, r):
    v = c.get("visual") or {}
    klass = c.get("product_class")

    if klass == "poster":
        sid = v.get("style_id")
        if sid not in POSTER_STYLES:
            r.kill("G2", "g2_style", f"visual.style_id {sid!r} not in poster_style_dna.json")
    elif klass == "tshirt":
        lid = v.get("layout_id")
        if lid not in TSHIRT_LAYOUTS:
            r.kill("G2", "g2_style", f"visual.layout_id {lid!r} not in tshirt_layout_archetypes.json")

    pal = v.get("palette") or []
    pid = v.get("palette_id")
    if pid and pid not in PALETTES:
        r.kill("G2", "g2_palette", f"visual.palette_id {pid!r} not in palettes.json")
    if not pal and not pid:
        r.kill("G2", "g2_palette", "no palette or palette_id - unspecified palette is the #1 cause of generic output")
    if len(pal) > 6:
        r.kill("G2", "g2_palette", f"palette has {len(pal)} colours; max 6")

    for axis in ("composition", "typography", "texture"):
        if not (v.get(axis) or "").strip():
            r.kill("G2", "g2_axes", f"visual.{axis} is empty")

    if len(v.get("avoid") or []) < 3:
        r.kill("G2", "g2_avoid", "visual.avoid needs >= 3 negative constraints")

    if not (v.get("reads_at_250px_via") or "").strip():
        r.kill("G2", "g2_thumbnail", "visual.reads_at_250px_via is empty - state what carries this at thumbnail size")

    prompt = (v.get("render_prompt") or "").lower()
    hits = [t for t in RUBRIC["slop_padding_terms"] if t in prompt]
    if hits:
        r.kill("G2", "g2_no_slop_padding",
               f"render_prompt contains slop padding: {hits} - this pulls output back to the mean")

    fonts = re.findall(r"\b(?:serif|sans|slab|script|mono|display|grotesque|gothic)\b",
                       (v.get("typography") or "").lower())
    if len(fonts) > 3:
        r.deduct("G2", "g2_font_count", f"{len(fonts)} type families named; max 3", 5)


def gate_g3(c, r):
    p = c.get("production") or {}
    platforms = p.get("target_platforms") or []
    if not platforms:
        return r.kill("G3", "g3_ratio", "production.target_platforms is empty")

    ratio = p.get("aspect_ratio")
    px = p.get("px") or [0, 0]

    for name in platforms:
        spec = SPECS.get(name)
        if not spec:
            r.kill("G3", "g3_ratio", f"unknown platform {name!r}")
            continue
        f = spec.get("file", {})

        if name == "displate":
            if ratio != "1:1.4":
                r.kill("G3", "g3_ratio", f"Displate requires 1:1.4, got {ratio!r}")
            if min(px) < f.get("min_short_edge_px", 0):
                r.kill("G3", "g3_px",
                       f"Displate needs >= {f['min_short_edge_px']}px on the short edge, got {min(px)}")
            if (p.get("edge_buffer_px") or 0) < f.get("edge_buffer_px", 0):
                r.kill("G3", "g3_edge_buffer",
                       f"Displate needs >= {f['edge_buffer_px']}px edge buffer, got {p.get('edge_buffer_px')}")

        if name == "amazon_merch":
            want = f.get("px")
            if list(px) != want:
                r.kill("G3", "g3_px", f"Amazon Merch requires {want}, got {px}")
            if p.get("background") != "transparent":
                r.kill("G3", "g3_transparency",
                       "Amazon Merch requires a transparent background - white prints as a white rectangle")

        if name == "etsy" and c.get("product_class") == "poster":
            allowed = f.get("printable_ratios", [])
            if ratio not in allowed:
                r.kill("G3", "g3_ratio", f"Etsy printable ratio {ratio!r} not in {allowed}")
            if not p.get("ratio_exports"):
                r.deduct("G3", "g3_ratio",
                         "no ratio_exports listed - ship each ratio family as its own regenerated file", 5)

        if name == "redbubble" and c.get("product_class") == "poster":
            if max(px) < 3840:
                r.kill("G3", "g3_px", f"Redbubble art print master should be >= 3840px, got {max(px)}")

    if p.get("colour_mode") != "sRGB":
        r.kill("G3", "g3_px", f"colour_mode must be sRGB, got {p.get('colour_mode')!r}")

    if c.get("product_class") == "tshirt":
        if p.get("background") != "transparent":
            r.kill("G3", "g3_transparency", "apparel files must have a transparent background")
        if p.get("garment_safe") != "both":
            r.deduct("G3", "g3_garment_contrast",
                     f"garment_safe is {p.get('garment_safe')!r} - halves your garment colour options "
                     "unless two exports are supplied", 5)
        if (p.get("ink_count") or 0) > 6:
            r.deduct("G3", "g3_garment_contrast",
                     f"{p['ink_count']} inks reads as a photo print, not apparel", 5)


def gate_g4(c, r):
    meta = c.get("metadata") or {}
    if not meta:
        return r.kill("G4", "g4_title_len", "metadata is empty")

    is_decor = (c.get("angle") or {}).get("emotional_job") == "room_decor"
    is_gift = (c.get("angle") or {}).get("emotional_job") == "gift_for_relationship"

    for platform, m in meta.items():
        spec = SPECS.get(platform, {}).get("metadata", {})
        title = m.get("title") or ""
        tags = m.get("tags") or []
        desc = m.get("description") or ""
        t_spec = spec.get("title", {})

        lo, hi = t_spec.get("min_chars", 0), t_spec.get("max_chars")
        if hi and len(title) > hi:
            r.kill("G4", "g4_title_len",
                   f"[{platform}] title is {len(title)} chars; max {hi}")
        if len(title) < lo:
            r.kill("G4", "g4_title_len",
                   f"[{platform}] title is {len(title)} chars; min {lo}")

        tag_spec = spec.get("tags", {})
        want = tag_spec.get("count")
        if want:
            if len(tags) != want:
                r.kill("G4", "g4_tag_count",
                       f"[{platform}] has {len(tags)} tags; needs exactly {want}")
            cap = tag_spec.get("max_chars_each")
            over = [t for t in tags if cap and len(t) > cap]
            if over:
                r.kill("G4", "g4_tag_len",
                       f"[{platform}] tags over {cap} chars: {over}")
            if tags:
                phrases = sum(1 for t in tags if len(t.split()) > 1)
                if phrases / len(tags) < 0.6:
                    r.kill("G4", "g4_tag_phrases",
                           f"[{platform}] only {phrases}/{len(tags)} tags are multi-word phrases; "
                           "single broad words rank for nothing")
                tt = tokens(title)
                subs = [t for t in tags if tokens(t) and tokens(t) <= tt]
                if subs:
                    r.kill("G4", "g4_tag_not_title",
                           f"[{platform}] tags duplicate title tokens (wasted slots): {subs}")

        if title and desc and title.strip().lower() in desc.strip().lower():
            r.kill("G4", "g4_desc_not_title",
                   f"[{platform}] description repeats the title verbatim")

        if platform == "amazon_merch":
            bullets = m.get("bullets") or []
            if len(bullets) != 2:
                r.kill("G4", "g4_title_len", f"[amazon_merch] needs exactly 2 bullets, got {len(bullets)}")
            for i, b in enumerate(bullets, 1):
                if not 10 <= len(b) <= 255:
                    r.kill("G4", "g4_title_len",
                           f"[amazon_merch] bullet {i} is {len(b)} chars; must be 10-255")
            total = sum(len(b.encode()) for b in bullets)
            if total > 1000:
                r.deduct("G4", "g4_title_len",
                         f"[amazon_merch] bullets total {total} bytes; only the first 1000 are indexed", 5)

        low = title.lower()
        if is_decor and c.get("product_class") == "poster":
            if not any(w in low for w in RUBRIC["colour_words"]):
                r.deduct("G4", "g4_colour_word",
                         f"[{platform}] decor title has no colour word - invisible to half the decor market", 5)
        if is_gift:
            if not any(w in low for w in RUBRIC["relationship_words"]):
                r.deduct("G4", "g4_relationship_word",
                         f"[{platform}] gift title has no relationship word - gift buyers search the recipient", 5)


def _shipped_text(c):
    parts = []
    v = c.get("visual") or {}
    parts.append(v.get("subject", ""))
    parts.append(v.get("render_prompt", ""))
    for slot in (v.get("text_slots") or {}).values():
        parts.append(slot if isinstance(slot, str) else " ".join(map(str, slot)))
    for m in (c.get("metadata") or {}).values():
        parts += [m.get("title", ""), m.get("description", ""),
                  m.get("backend_search_terms", ""), m.get("brand", "")]
        parts += m.get("tags") or []
        parts += m.get("bullets") or []
    return " \n ".join(p for p in parts if p)


def gate_g5(c, r):
    text = _shipped_text(c)
    for rule in IP["high_risk_patterns"]:
        m = re.search(rule["pattern"], text)
        if m:
            r.kill("G5", "g5_denylist",
                   f"{rule['tier']} IP hit {m.group(0)!r} - {rule['reason']}")

    ipf = c.get("ip") or {}
    tier = ipf.get("tier")
    if not tier:
        r.kill("G5", "g5_tier", "ip.tier is not set")
    elif tier == "R4":
        r.kill("G5", "g5_tier", "ip.tier is R4 - forbidden")
    if tier in ("R1", "R2") and not ipf.get("screened_against"):
        r.kill("G5", "g5_screened",
               f"tier {tier} requires ip.screened_against[] (USPTO / EUIPO / WIPO with a date)")
    if tier == "R3" and not ipf.get("public_domain_source"):
        r.kill("G5", "g5_pd_verified",
               "tier R3 requires a verified open-access public_domain_source")


def gate_g6(c, r, seen_keys, seen_titles):
    d = c.get("dedup") or {}
    key = d.get("hard_key")
    if not key:
        v = c.get("visual") or {}
        key = "|".join([
            v.get("style_id") or v.get("layout_id") or "?",
            v.get("palette_id") or "?",
            v.get("subject_lemma") or "?",
        ])
        r.note(f"dedup.hard_key derived as {key!r}")
    if "?" in key:
        r.kill("G6", "g6_hard_key", f"dedup.hard_key incomplete: {key!r}")
    if key in seen_keys:
        r.kill("G6", "g6_hard_key",
               f"duplicate hard_key {key!r} - already used by {seen_keys[key]}")
    else:
        seen_keys[key] = c.get("concept_id")

    for m in (c.get("metadata") or {}).values():
        t = m.get("title") or ""
        tg = trigrams(t)
        if not tg:
            continue
        for other_id, other in seen_titles:
            if other_id == c.get("concept_id"):
                continue
            overlap = len(tg & other) / max(1, len(tg | other))
            if overlap > 0.6:
                r.kill("G6", "g6_title_trigram",
                       f"title {t!r} is {overlap:.0%} similar to concept {other_id}")
                break
        seen_titles.append((c.get("concept_id"), tg))


def validate(concept, seen_keys, seen_titles):
    r = Result(concept.get("concept_id", "<unnamed>"))
    if concept.get("product_class") not in ("poster", "tshirt"):
        r.kill("G0", "schema", f"product_class must be 'poster' or 'tshirt', got {concept.get('product_class')!r}")
        return r
    for fn in (gate_g0, gate_g1, gate_g2, gate_g3, gate_g4, gate_g5):
        fn(concept, r)
    gate_g6(concept, r, seen_keys, seen_titles)
    return r


# ---------------------------------------------------------------- cli

def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("paths", nargs="+",
                    help="JSON files: each a concept object or a list of them")
    ap.add_argument("--json", action="store_true", help="emit a machine-readable report")
    ap.add_argument("--verbose", "-v", action="store_true", help="show deductions on passing concepts too")
    args = ap.parse_args()

    concepts = []
    for path in args.paths:
        with open(path, encoding="utf-8") as fh:
            payload = json.load(fh)
        concepts += payload if isinstance(payload, list) else [payload]

    seen_keys, seen_titles = {}, []
    results = [validate(c, seen_keys, seen_titles) for c in concepts]

    if args.json:
        passed = sum(1 for r in results if r.passed)
        json.dump({
            "total": len(results),
            "passed": passed,
            "gate_pass_rate": round(passed / max(1, len(results)), 3),
            "results": [r.to_dict() for r in results],
        }, sys.stdout, indent=2)
        print()
    else:
        for r in results:
            mark = "PASS" if r.passed else "KILL"
            print(f"[{mark}] {r.concept_id}  score={r.score}")
            for gate, check, msg in r.kills:
                print(f"    x {gate}/{check}: {msg}")
            if args.verbose or not r.passed:
                for gate, check, msg, pts in r.deductions:
                    print(f"    - {gate}/{check} (-{pts}): {msg}")
                for n in r.notes:
                    print(f"    . {n}")
        passed = sum(1 for r in results if r.passed)
        rate = passed / max(1, len(results))
        print(f"\n{passed}/{len(results)} passed  (gate_pass_rate={rate:.0%})")
        if rate > 0.6:
            print("WARNING: pass rate above 60%. Either the batch is unusually good, "
                  "or the gates are being fed pre-filtered data. Target is 20-40%.")

    return 0 if all(r.passed for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())

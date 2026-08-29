"""Build a catalogue of listing concepts to fill the shop's slots.

The cap is the constraint, so the job is to fill every slot with a *different
bet*, not a hundred variations of one taste. Two rules shape what gets
generated:

1. Identity beats aesthetics. "Classic car posters" is a category; "Mk1 Golf
   GTI, for the person who actually owned one" is a buyer. Across print-on-
   demand, role- and passion-specific designs consistently outsell generic
   ones in the same category.
2. Everything is a trio. The set is the offer - it answers "what goes next to
   it", which is the real reason walls stay bare.

  python -m wonderfeed.catalogue --count 100 --write
  python -m wonderfeed.catalogue --niche cars --count 12
"""

import argparse
import json
import re
import sys

import yaml

from . import compliance
from .config import ConfigError, ROOT, load_settings, secret

# Grounded in what recurs across POD/Etsy/TikTok Shop trend reporting for 2026:
# botanical and nature, retro and vintage poster styles, identity and role art,
# faith and affirmation, pets, travel, and humour.
NICHES = {
    # HIGH RISK. Vehicle designs are protected by copyright, design right and
    # trademark - a recognisable model infringes even unnamed and unbadged. So
    # this niche is steered entirely onto factual and original subjects.
    "cars": "Motoring culture WITHOUT any identifiable vehicle. Allowed: circuit "
            "and rally-stage layouts (a track outline is a geographic fact), road "
            "trip routes, elevation profiles of famous climbs, vintage petrol "
            "station and garage nostalgia of your own design, generic silhouettes "
            "not traceable to a model, tools and parts as abstract studies. "
            "NEVER a marque, model, badge, number plate or recognisable shape.",
    "family": "Family and household: new babies, first homes, blended families, "
              "grandparents, pets as family, house rules, family name and "
              "established-year prints.",
    "botanical": "Plants, flowers, foliage, herbs, mushrooms, pressed-flower "
                 "and line-art botanical styles.",
    "identity": "Job and vocation pride: nurses, teachers, tradespeople, chefs, "
                "midwives, firefighters. Specific roles, not 'profession art'.",
    # HIGH RISK. Album covers, band marks and likenesses are all protected.
    "music": "Music culture WITHOUT any real artist, band or release. Allowed: "
             "instruments as studies, generic genre scenes, record-shop and "
             "sound-system culture, abstract waveform and frequency art, original "
             "typography about listening. NEVER a band name, album cover, logo, "
             "lyric or performer's likeness.",
    # HIGH RISK. Club badges, kit designs and player likenesses are protected.
    "sport": "Sport WITHOUT any club, competition or athlete. Allowed: city and "
             "ground-neutral typography, marathon and cycling route maps, "
             "climbing topos, generic silhouettes of a movement, original "
             "pitch/court geometry. NEVER a badge, kit, competition name, player "
             "or the word 'official'.",
    "travel": "Cities, coastlines, national parks, retro railway and airline "
              "poster styles, UK destinations.",
    "affirmation": "Calm affirmations, gratitude, mantras, minimalist quotes "
                   "for bedrooms and home offices.",
    "pets": "Dogs, cats, breed-specific portraits, line-art pet illustrations, "
            "memorial and 'house rules' pet prints.",
    "humour": "Funny bathroom, kitchen and loo prints, dry British humour, "
              "house-share and flat jokes.",
    "kids": "Nursery and children's rooms: animals, alphabets, space, "
            "dinosaurs, gentle pastel and Scandi styles.",
    "food": "Kitchen and dining: coffee, wine, baking, cocktails, market "
            "produce, recipe and spice-chart styles.",
}

PROMPT = """You are building a print-on-demand catalogue for a UK TikTok Shop \
selling wall art as SETS OF THREE prints.

NICHE: {niche}
{niche_brief}

Generate {count} DISTINCT product concepts in this niche.

The single most important rule: **be specific to a buyer, not to a category.**
Role- and passion-specific designs consistently outsell generic ones in the same
category. So not "car prints" but a particular model and the person who wants it.
Not "family art" but a specific family moment.

Each concept must be:
- A set of THREE prints that hang together and make sense as a trio
- Sellable at £18-£35 for the set
- Buildable as a printed poster or framed print (no fabric, no 3D, no lighting)
- **Clear of third-party IP.** This is the hard constraint, not a preference:
  no brand or marque names, no club badges, no band or album references, no film,
  TV, game or book properties, no characters, no living people, no song lyrics or
  in-copyright quotations. Vehicle and product *designs* are protected even when
  unnamed and unbadged, so do not describe a recognisable one. Prefer subjects
  that are original, generic, or factual (layouts, routes, coastlines, star
  charts) - those cannot be owned.
- Distinct from the others: no two concepts may share the same core subject

For each concept give:
- "id": short kebab-case slug, unique, max 32 chars, ending in "-trio"
- "name": the listing title as a shopper would see it, under 60 characters
- "description": 1-2 sentences describing the three prints and who they are for
- "price_gbp": a number between 18 and 35
- "rooms": 3 rooms/settings this suits, each a short phrase describing a real
  UK domestic space
- "angles": 5 audience angles - the specific viewer situation a video would
  open on. 4-14 words, lowercase, no full stop, no product name. Situational,
  not descriptive.

Return ONLY a JSON array of objects. No preamble, no code fence."""


def _slug(text, fallback="set"):
    s = re.sub(r"[^a-z0-9]+", "-", str(text).lower()).strip("-")
    return (s[:32].rstrip("-") or fallback)


def validate_concept(c, seen_ids):
    """Reject anything the pipeline could not actually build from."""
    if not isinstance(c, dict):
        return None
    cid = _slug(c.get("id") or c.get("name") or "")
    if not cid or cid in seen_ids:
        return None
    name = str(c.get("name", "")).strip()
    desc = str(c.get("description", "")).strip()
    if not name or not desc:
        return None
    angles = [str(a).strip().rstrip(".") for a in (c.get("angles") or []) if str(a).strip()]
    rooms = [str(r).strip() for r in (c.get("rooms") or []) if str(r).strip()]
    if len(angles) < 3 or not rooms:
        return None
    try:
        price = round(float(c.get("price_gbp", 24.99)), 2)
    except (TypeError, ValueError):
        price = 24.99
    seen_ids.add(cid)
    return {
        "id": cid,
        "name": name[:60],
        "link": "",  # filled in once the listing exists in Seller Center
        "price_gbp": price,
        "images": [],  # add a real product photo before generating video
        "description": desc,
        "rooms": rooms[:3],
        "angles": angles,
        "niche": c.get("niche") or "",
    }


def generate_niche(niche, count, api_key, settings, seen_ids, log=print):
    import anthropic

    client = anthropic.Anthropic(api_key=api_key)
    resp = client.messages.create(
        model=settings["models"]["script_model"],
        max_tokens=8000,
        messages=[{"role": "user", "content": PROMPT.format(
            niche=niche, niche_brief=NICHES[niche], count=count,
        )}],
    )
    text = resp.content[0].text.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1].rsplit("```", 1)[0].strip()
    raw = json.loads(text)
    if not isinstance(raw, list):
        raise ValueError("model did not return a JSON array")

    out, blocked = [], 0
    for c in raw:
        if isinstance(c, dict):
            c["niche"] = niche
        ok = validate_concept(c, seen_ids)
        if not ok:
            continue
        verdict, reasons = compliance.screen(ok)
        if verdict == compliance.Verdict.BLOCK:
            # Never let an infringing concept reach products.yaml.
            blocked += 1
            seen_ids.discard(ok["id"])
            log(f"    blocked '{ok['id']}': {reasons[0]}")
            continue
        ok["ip_review"] = reasons or None
        out.append(ok)
    note = f", {blocked} blocked on IP" if blocked else ""
    log(f"  {niche}: {len(out)}/{count} usable{note}")
    return out


def allocate(count, niches):
    """Spread the target across niches as evenly as possible."""
    base, extra = divmod(count, len(niches))
    return {n: base + (1 if i < extra else 0) for i, n in enumerate(niches)}


def fake_concepts(niche, count, seen_ids):
    """Offline stand-ins, for exercising allocation and write-back."""
    out = []
    for i in range(count):
        c = {
            "id": f"{niche}-{i + 1:02d}-trio",
            "name": f"{niche.title()} Trio {i + 1}",
            "description": f"Three {niche} prints designed to hang as a set.",
            "price_gbp": 24.99,
            "rooms": ["a modern living room", "a small bedroom", "a hallway"],
            "angles": [f"{niche} angle {j + 1}" for j in range(5)],
            "niche": niche,
        }
        ok = validate_concept(c, seen_ids)
        if ok:
            out.append(ok)
    return out


def write_back(concepts, path=None, log=print):
    """Merge concepts into products.yaml, never overwriting an existing id."""
    path = path or ROOT / "config" / "products.yaml"
    data = {"products": []}
    if path.exists():
        with path.open(encoding="utf-8") as fh:
            data = yaml.safe_load(fh) or {"products": []}
    data.setdefault("products", [])

    existing = {p["id"] for p in data["products"]}
    added = [c for c in concepts if c["id"] not in existing]
    data["products"].extend(added)

    with path.open("w", encoding="utf-8") as fh:
        yaml.safe_dump(data, fh, sort_keys=False, allow_unicode=True, width=100)
    log(f"  {len(added)} added, {len(concepts) - len(added)} already present")
    return path, len(data["products"])


def main(argv=None):
    ap = argparse.ArgumentParser(description="Generate a catalogue of listing concepts.")
    ap.add_argument("--count", type=int, default=100, help="total concepts to generate")
    ap.add_argument("--niche", action="append",
                    help=f"restrict to a niche (repeatable). Known: {', '.join(NICHES)}")
    ap.add_argument("--write", action="store_true", help="merge into config/products.yaml")
    ap.add_argument("--dry-run", action="store_true",
                    help="offline placeholders - proves allocation and write-back")
    ap.add_argument("--list-niches", action="store_true")
    args = ap.parse_args(argv)

    if args.list_niches:
        for n, brief in NICHES.items():
            print(f"{n:<12} {brief}")
        return 0

    niches = args.niche or list(NICHES)
    unknown = [n for n in niches if n not in NICHES]
    if unknown:
        print(f"Unknown niche(s): {', '.join(unknown)}\nKnown: {', '.join(NICHES)}",
              file=sys.stderr)
        return 2

    try:
        settings = load_settings()
        api_key = "" if args.dry_run else secret("ANTHROPIC_API_KEY")
    except ConfigError as exc:
        print(f"Config error: {exc}", file=sys.stderr)
        return 2

    plan = allocate(args.count, niches)
    print(f"Generating {args.count} concepts across {len(niches)} niche(s)"
          f"{'  [DRY RUN]' if args.dry_run else ''}")

    seen_ids = set()
    concepts = []
    for niche, n in plan.items():
        if n <= 0:
            continue
        try:
            if args.dry_run:
                concepts.extend(fake_concepts(niche, n, seen_ids))
            else:
                concepts.extend(generate_niche(niche, n, api_key, settings, seen_ids))
        except Exception as exc:
            print(f"  {niche}: FAILED ({exc})")

    print(f"\n{len(concepts)} usable concepts.")
    if not args.write:
        for c in concepts[:15]:
            print(f"  [{c['niche']:<11}] {c['id']:<34} £{c['price_gbp']:<6} {c['name']}")
        if len(concepts) > 15:
            print(f"  ... and {len(concepts) - 15} more")
        print("\nRe-run with --write to merge them into products.yaml.")
        return 0

    path, total = write_back(concepts)
    print(f"products.yaml now holds {total} products.")
    print("\nNext:")
    print("  1. Create the listings in Seller Center, then paste each `link` "
          "and a product photo path into products.yaml")
    print("  2. Register them:  python -m wonderfeed.listings add --sku ... "
          "--product <id>")
    print("  3. Build videos:   python -m wonderfeed.run --count 20")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

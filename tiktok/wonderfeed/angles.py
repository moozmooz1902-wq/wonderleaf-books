"""Generate audience angles in bulk, and write them back into products.yaml.

Angles are the variety engine. One product against thirty angles gives thirty
genuinely different videos; the same product with one angle gives thirty
near-duplicates, which TikTok's duplicate detection notices.

  python -m wonderfeed.angles --product botanical-3set --count 30
  python -m wonderfeed.angles --product botanical-3set --count 30 --write
"""

import argparse
import json
import sys

import yaml

from .config import ConfigError, ROOT, load_products, load_settings, secret

PROMPT = """You write TikTok hook angles for a UK wall-art shop.

PRODUCT
Name: {name}
Price: £{price}
Description: {description}

An "angle" is the specific viewer situation a video opens on - the problem, \
moment or feeling that makes someone stop scrolling. It is NOT a description \
of the product and NOT a hook line. It is the premise a scriptwriter builds on.

Good angles (note how specific and situational these are):
- "renting and not allowed to drill into the walls"
- "the wall behind the sofa has been bare since moving in two years ago"
- "spent the whole budget on the sofa and nothing is left for the walls"
- "parents visiting at the weekend and the flat looks unfinished"

Bad angles (too generic, or product-led):
- "beautiful wall art" / "high quality prints" / "affordable decor"

Write {count} DISTINCT angles for this product. Vary across:
- life events (moving in, new job, break-up, baby, first flat, downsizing)
- constraints (renting, budget, small space, awkward wall, magnolia paint)
- social pressure (visitors, housemates, dating, video calls)
- seasonal and calendar moments (dark January, spring clean, Christmas)
- practical friction (hanging it straight, what goes next to what, sizing)

Rules:
- British context throughout (flats, renting, magnolia, Ikea, B&Q).
- Each angle 4-14 words, lowercase, no full stop.
- No two angles may share the same core premise.
- Do not mention the product name.

{avoid_block}
Return ONLY a JSON array of strings. No preamble, no code fence."""


def generate(product, count, api_key, settings, existing=(), log=print):
    import anthropic

    avoid = ""
    if existing:
        avoid = (
            "These angles already exist - do not repeat or reword them:\n"
            + "\n".join(f"- {a}" for a in existing)
            + "\n"
        )

    client = anthropic.Anthropic(api_key=api_key)
    resp = client.messages.create(
        model=settings["models"]["script_model"],
        max_tokens=2000,
        messages=[{"role": "user", "content": PROMPT.format(
            name=product["name"],
            price=product.get("price_gbp", "—"),
            description=product["description"].strip(),
            count=count,
            avoid_block=avoid,
        )}],
    )
    text = resp.content[0].text.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1].rsplit("```", 1)[0].strip()
    angles = json.loads(text)
    if not isinstance(angles, list):
        raise ValueError("model did not return a JSON array")

    # De-duplicate against what is already there, case-insensitively.
    seen = {a.strip().lower() for a in existing}
    fresh = []
    for a in angles:
        a = str(a).strip().rstrip(".")
        if a and a.lower() not in seen:
            seen.add(a.lower())
            fresh.append(a)
    return fresh


def write_back(product_id, new_angles, path=None):
    """Append angles to products.yaml, preserving everything else."""
    path = path or ROOT / "config" / "products.yaml"
    with path.open(encoding="utf-8") as fh:
        data = yaml.safe_load(fh)
    for p in data["products"]:
        if p["id"] == product_id:
            p.setdefault("angles", []).extend(new_angles)
            break
    else:
        raise ConfigError(f"product '{product_id}' not found in {path.name}")
    with path.open("w", encoding="utf-8") as fh:
        yaml.safe_dump(data, fh, sort_keys=False, allow_unicode=True, width=100)
    return path


def main(argv=None):
    ap = argparse.ArgumentParser(description="Generate angles for a product.")
    ap.add_argument("--product", required=True, help="product id")
    ap.add_argument("--count", type=int, default=25)
    ap.add_argument("--write", action="store_true",
                    help="append them to config/products.yaml")
    args = ap.parse_args(argv)

    try:
        settings = load_settings()
        products = load_products()
        api_key = secret("ANTHROPIC_API_KEY")
    except ConfigError as exc:
        print(f"Config error: {exc}", file=sys.stderr)
        return 2

    product = next((p for p in products if p["id"] == args.product), None)
    if not product:
        print(f"No product with id '{args.product}'. Known: "
              f"{', '.join(p['id'] for p in products)}", file=sys.stderr)
        return 2

    existing = product.get("angles", [])
    print(f"Generating {args.count} angles for {product['name']} "
          f"({len(existing)} already defined)...")
    angles = generate(product, args.count, api_key, settings, existing)

    for a in angles:
        print(f"  - {a}")
    print(f"\n{len(angles)} new angles.")

    if args.write:
        path = write_back(args.product, angles)
        print(f"Appended to {path.relative_to(ROOT)} "
              f"(now {len(existing) + len(angles)} total).")
    else:
        print("Re-run with --write to append them to products.yaml.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

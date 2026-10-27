#!/usr/bin/env python3
"""Assign EAN-13 barcodes to OnBuy variants, from our own GS1 prefix.

WHAT THIS IS AND IS NOT. GS1 licenses a company a PREFIX. The licensee then
assigns every item reference inside that prefix themselves, for free, with
no further involvement from GS1 - that is the normal, documented way GTINs
are created, and it is almost certainly what "my friend generates his own
barcodes" means. This file does that part: it turns a prefix we hold into
as many unique, correctly-checksummed EAN-13s as the prefix has room for.

It does NOT invent a prefix, and it will not run without one. A barcode
does not identify a product, it identifies WHO LICENSED THE NUMBER - the
leading digits are a prefix GS1 issued to one specific company. Numbers
generated outside a prefix we hold either resolve to another company, so
our print claims to be their product, or resolve to nothing. OnBuy's
refusal of 27 Oct says "GS1 **registered**" precisely because they look the
number up. So PREFIX is required and there is no default.

CAPACITY, which is the whole economics. An EAN-13 is 12 digits plus a check
digit. A prefix of length P leaves 12-P digits for item references, so:

    prefix 5012345 (7)  ->     100,000 numbers
    prefix 501234  (6)  ->   1,000,000 numbers
    prefix 50123   (5)  ->  10,000,000 numbers

The shorter the prefix, the more numbers. GS1 UK prices these in blocks -
about GBP 120 for 1,000, GBP 250 for 10,000, GBP 425 for 100,000 as of
10 May 2026 - and once bought, every number inside is free. Cost per
barcode at the 100,000 tier is under half a penny.

ASSIGNMENT IS PERMANENT, AND THAT IS THE POINT OF THE MAP FILE. A GTIN, like
a SKU, must mean the same thing for ever: Google warns that changing an id
loses a product's history, and a marketplace catalogue keyed on barcodes is
worse - reassigning one silently moves a product. So assignments live in a
committed JSON file, new SKUs take the next free reference, and a SKU that
already has a number keeps it. Nothing is ever recomputed from row order.

Item references count up from zero in the order SKUs are first seen, which
is what GS1 recommend - no logic is built into the reference, because any
scheme that encodes meaning eventually runs out of room in the part that
carries the meaning rather than in the part that counts.

  usage: gtin.py --prefix 5012345 --assign out/onbuy/..._rows.jsonl
         gtin.py --verify
         gtin.py --selftest
"""
import argparse, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
MAP = os.path.join(HERE, "onbuy", "gtin_map.json")


def check_digit(twelve):
    """The EAN-13 check digit: alternate weights 1 and 3 from the left,
    then whatever gets the total to a multiple of ten.

    Verified against two barcodes from OnBuy's own Product Create Template
    - see selftest(). Getting this wrong produces numbers that look right
    and are rejected on upload, which is the worst kind of wrong.
    """
    if len(twelve) != 12 or not twelve.isdigit():
        raise ValueError(f"need 12 digits, got {twelve!r}")
    total = sum(int(d) * (1 if i % 2 == 0 else 3)
                for i, d in enumerate(twelve))
    return str((10 - total % 10) % 10)


def ean13(prefix, reference):
    """prefix + zero-padded item reference + check digit."""
    width = 12 - len(prefix)
    if width < 1:
        raise ValueError(f"prefix {prefix!r} leaves no room for a reference")
    if reference >= 10 ** width:
        raise ValueError(
            f"prefix {prefix!r} holds {10 ** width:,} numbers and reference "
            f"{reference:,} is past the end. A prefix cannot be extended - "
            f"GS1 issue a new, shorter one - so this is a buying decision, "
            f"not a bug to work around.")
    body = f"{prefix}{reference:0{width}d}"
    return body + check_digit(body)


def load_map():
    if os.path.exists(MAP):
        return json.load(open(MAP))
    return {"prefix": None, "next": 0, "skus": {}}


def save_map(m):
    os.makedirs(os.path.dirname(MAP), exist_ok=True)
    json.dump(m, open(MAP, "w"), indent=1, sort_keys=True)


def assign(rows_path, prefix, dry=False):
    """Give every VARIANT row a GTIN, keeping the ones already given.

    Product (parent) rows get none: OnBuy's template leaves the parent's
    EAN empty in all four of its worked examples, and the variant rows are
    what carry it.
    """
    m = load_map()
    if m["prefix"] and m["prefix"] != prefix:
        sys.exit(f"REFUSING: {MAP} was built with prefix {m['prefix']!r} and "
                 f"you passed {prefix!r}. Changing the prefix renumbers every "
                 f"product that is already live. If the prefix really has "
                 f"changed, that is a migration, not a flag.")
    m["prefix"] = prefix
    width = 12 - len(prefix)
    cap = 10 ** width

    want = []
    for line in open(rows_path):
        line = line.strip()
        if not line:
            continue
        r = json.loads(line)
        if r.get("_row") == "variant":
            want.append(r["sku"])

    new = [s for s in want if s not in m["skus"]]
    need = m["next"] + len(new)
    print(f"prefix {prefix}  capacity {cap:,}  already assigned "
          f"{len(m['skus']):,}  new {len(new):,}")
    if need > cap:
        sys.exit(f"REFUSING: this needs {need:,} numbers and the prefix holds "
                 f"{cap:,}. A shorter prefix is the fix and it has to be "
                 f"bought - see the capacity table at the top of this file.")
    for sku in new:
        m["skus"][sku] = ean13(prefix, m["next"])
        m["next"] += 1
    if dry:
        print("dry run - nothing written")
    else:
        save_map(m)
        print(f"wrote {MAP}  ({len(m['skus']):,} SKUs, next {m['next']:,})")
    if new:
        k = new[0]
        print(f"  example: {k} -> {m['skus'][k]}")
    print(f"  remaining in this prefix: {cap - m['next']:,}")
    return m


def verify():
    """Every number well formed, correctly checksummed, inside the prefix,
    and used once."""
    m = load_map()
    if not m["skus"]:
        print("no assignments yet")
        return 1
    bad = seen = 0
    used = {}
    for sku, g in m["skus"].items():
        if len(g) != 13 or not g.isdigit():
            print(f"  [BAD] {sku}: {g!r} is not 13 digits")
            bad += 1
            continue
        if check_digit(g[:12]) != g[12]:
            print(f"  [BAD] {sku}: {g} fails its check digit")
            bad += 1
        if not g.startswith(m["prefix"]):
            print(f"  [BAD] {sku}: {g} is outside prefix {m['prefix']}")
            bad += 1
        if g in used:
            print(f"  [BAD] {g} used by {used[g]} and {sku}")
            bad += 1
        used[g] = sku
        seen += 1
    print(f"{seen:,} GTINs, {len(used):,} distinct, {bad} problems")
    return bad


def selftest():
    """Check digits against two real barcodes from OnBuy's own template,
    and the capacity guard against its own boundary."""
    ok = True
    for full in ("5056343211950", "4038489028884", "0714131826797"):
        got = check_digit(full[:12])
        if got != full[12]:
            print(f"  FAIL {full}: computed {got}")
            ok = False
    # 501234 000000 -> weights 1,3,1,3,1,3 over 5,0,1,2,3,4 and zeros after:
    # 5 + 0 + 1 + 6 + 3 + 12 = 27, so the check digit is 3.
    # (The first version of this line expected 5, from mis-adding that sum
    # by hand. The three real barcodes above caught nothing, because they
    # were right - it was the expectation that was wrong. Hence working the
    # arithmetic out in the comment, where it can be checked.)
    if ean13("501234", 0) != "5012340000003":
        print(f"  FAIL first number: {ean13('501234', 0)}")
        ok = False
    try:
        ean13("5012345", 100000)      # 7-digit prefix holds exactly 100,000
        print("  FAIL capacity guard did not fire")
        ok = False
    except ValueError:
        pass
    print("selftest: " + ("all passed" if ok else "FAILURES ABOVE"))
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--prefix", help="the GS1 company prefix WE hold")
    ap.add_argument("--assign", metavar="ROWS_JSONL")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--verify", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        sys.exit(selftest())
    if a.verify:
        sys.exit(1 if verify() else 0)
    if a.assign:
        if not a.prefix:
            sys.exit("--prefix is required and has no default. It must be a "
                     "GS1 company prefix licensed to NORYMUS LIMITED. See "
                     "the note at the top of this file for why there is no "
                     "way around that.")
        if not a.prefix.isdigit() or not 4 <= len(a.prefix) <= 11:
            sys.exit(f"{a.prefix!r} is not a plausible GS1 company prefix")
        assign(a.assign, a.prefix, a.dry_run)
        return
    ap.print_help()


if __name__ == "__main__":
    main()

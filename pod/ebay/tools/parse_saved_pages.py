#!/usr/bin/env python3
"""
Extract listing data from eBay search pages saved from a browser.

    python3 parse_saved_pages.py --dir ~/Downloads/ebay_pages --out corpus.jsonl

WHY THIS AND NOT A SCRAPER

eBay now refuses automated requests from this machine, and getting round
that - proxies, rotating identities, spoofed browsers - is circumventing an
access control they have deliberately put up. If it is traced back it lands
on the selling accounts, which is a bad trade for a pile of titles.

A person browsing in a browser is what eBay expects. So: open a search,
Ctrl+S (Save Page As, "Web Page, Complete" or "HTML Only"), drop the file in
a folder, repeat. Every page is about 60 titles, or 240 with &_ipg=240 in
the URL. Twenty minutes of saving gives several thousand listings, which is
more than any amount of arguing with a 403.

The parser is deliberately tolerant. eBay's markup shifts, so it tries the
current class names first, then falls back to structure, then to plain text
patterns. Anything that yields a title with a price is kept.
"""

import argparse
import collections
import glob
import html
import json
import os
import re
import sys

# eBay's current search-result markup. Ordered most to least specific: the
# first that yields a plausible number of rows wins.
ITEM_BLOCK = re.compile(
    r'<li[^>]+class="[^"]*s-item[^"]*"[^>]*>(.*?)</li>', re.S | re.I)
ITEM_BLOCK_ALT = re.compile(
    r'<div[^>]+class="[^"]*s-card[^"]*"[^>]*>(.*?)</div>\s*</div>\s*</div>',
    re.S | re.I)

TITLE_PATTERNS = [
    re.compile(r'class="[^"]*s-item__title[^"]*"[^>]*>(?:<span[^>]*>)?(.*?)</', re.S | re.I),
    re.compile(r'class="[^"]*s-card__title[^"]*"[^>]*>(?:<span[^>]*>)?(.*?)</', re.S | re.I),
    re.compile(r'<h3[^>]*>(.*?)</h3>', re.S | re.I),
    re.compile(r'role="heading"[^>]*>(.*?)</', re.S | re.I),
]
PRICE_RE = re.compile(r'£\s?([\d,]+\.\d{2})')
SOLD_RE = re.compile(r'([\d,]+)\+?\s*sold', re.I)
WATCH_RE = re.compile(r'([\d,]+)\+?\s*watch', re.I)
TAG_RE = re.compile(r'<[^>]+>')

# Rows eBay injects that are not listings.
NOISE = re.compile(
    r"^shop on ebay$|^new listing$|^sponsored$|^results matching|"
    r"^tell us what you think|^shop by category$|^\s*$", re.I)


def text(s):
    s = TAG_RE.sub(" ", s or "")
    s = html.unescape(s)
    return re.sub(r"\s+", " ", s).strip()


def parse_page(raw):
    """Every listing on one saved page."""
    blocks = ITEM_BLOCK.findall(raw)
    if len(blocks) < 3:
        blocks = ITEM_BLOCK_ALT.findall(raw)
    out = []
    for b in blocks:
        title = ""
        for pat in TITLE_PATTERNS:
            m = pat.search(b)
            if m:
                title = text(m.group(1))
                if title:
                    break
        if not title or NOISE.match(title):
            continue
        # eBay prefixes some titles with this and it is not part of the title.
        title = re.sub(r"^new listing\s*", "", title, flags=re.I).strip()
        if len(title) < 12:
            continue
        plain = text(b)
        prices = [float(p.replace(",", "")) for p in PRICE_RE.findall(plain)]
        sold = SOLD_RE.search(plain)
        watch = WATCH_RE.search(plain)
        out.append({
            "title": title,
            "price_low": min(prices) if prices else None,
            "price_high": max(prices) if prices else None,
            "sold": int(sold.group(1).replace(",", "")) if sold else None,
            "watchers": int(watch.group(1).replace(",", "")) if watch else None,
        })
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", required=True,
                    help="folder of saved .html pages")
    ap.add_argument("--out", default="corpus.jsonl")
    ap.add_argument("--stats", action="store_true")
    a = ap.parse_args()

    files = sorted(
        glob.glob(os.path.join(a.dir, "**", "*.htm*"), recursive=True))
    if not files:
        raise SystemExit(f"no .html files under {a.dir}")

    seen, rows, empty = set(), [], []
    for f in files:
        try:
            raw = open(f, encoding="utf-8", errors="replace").read()
        except Exception as e:
            print(f"  could not read {os.path.basename(f)}: {e}")
            continue
        got = parse_page(raw)
        if not got:
            empty.append(os.path.basename(f))
        for r in got:
            key = r["title"].lower()
            if key in seen:
                continue
            seen.add(key)
            r["source_file"] = os.path.basename(f)
            rows.append(r)
        print(f"  {os.path.basename(f)[:52]:<52} {len(got):>4} listings")

    with open(a.out, "w", encoding="utf-8") as fh:
        for r in rows:
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")

    print(f"\n  {len(files)} page(s), {len(rows):,} distinct listings -> {a.out}")
    if empty:
        print(f"  {len(empty)} page(s) yielded nothing - if these are real "
              f"search pages the markup has moved:")
        for f in empty[:5]:
            print(f"    {f}")

    if a.stats and rows:
        with_sold = [r for r in rows if r["sold"]]
        print(f"\n  {len(with_sold):,} listings show a sold count")
        if with_sold:
            print("  best sellers seen:")
            for r in sorted(with_sold, key=lambda x: -x["sold"])[:15]:
                p = f"£{r['price_low']:.2f}" if r["price_low"] else ""
                print(f"    {r['sold']:>6,} sold  {p:>8}  {r['title'][:64]}")
        words = collections.Counter()
        for r in rows:
            for w in re.findall(r"[A-Za-z']{3,}", r["title"].lower()):
                words[w] += 1
        print("\n  most common title words:")
        for w, n in words.most_common(30):
            print(f"    {n:>5}  {w}")


if __name__ == "__main__":
    main()

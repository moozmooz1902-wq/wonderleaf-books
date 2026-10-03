#!/usr/bin/env python3
"""Build the 7-store catalogue: one row per listing, 1,000,000 per store by default.

    python3 generate.py                      full run -> out/store{1..7}.csv.gz
    python3 generate.py --per-store 20000    quick trial
    python3 generate.py --plan-only          just print the allocation

How the volume is split (plan.json):
  - every store has PRIMARY niches that get `primary_share` (65%) of its rows,
    and the rest is spread over every other niche by demand, so no store is
    a one-trick catalogue and a cold niche cannot sink a whole store.
  - a niche can only supply as many listings as it has unique phrases x vmax
    colourways. When demand asks for more than that, the surplus moves to
    niches that still have room, instead of re-rolling duplicates. That is
    the lesson from store 1 (424k listings, 89% near-duplicates, no sales).
  - no two rows anywhere share the same phrase AND colourway, and the unique
    phrases are all used before any phrase gets a second colourway.

Row order inside each store file is the upload order: niches interleaved by
share, first colourway of every phrase before any second one.
"""
import argparse, base64, csv, gzip, hashlib, heapq, json, math, random, re, sys, time
from collections import defaultdict
from pathlib import Path

from phrases import load_niches, iter_niche, supply
from compliance import check as ip_check
from styles import PALETTES, PALETTE_MOODS, FONTSETS, FONT_MOODS, LAYOUTS, ORNAMENTS

HERE = Path(__file__).resolve().parent
OUT = HERE / "out"

SMALL = {"a", "an", "and", "the", "of", "in", "on", "to", "for", "at", "by", "or", "is",
         "with", "as", "but", "from", "&"}


# ------------------------------------------------------------------ allocation

def allocate(plan, niches):
    P = plan["primary_share"]
    def pl(n):   # AI micro-niches inherit their parent's demand and store
        return plan["niches"].get(n) or plan["niches"].get(niches[n].get("parent", n), {})
    w = {n: pl(n).get("demand", 3) for n in niches}
    vmax, cap = {}, {}
    cpv = plan.get("colours_per_venue", 4)
    tvar = plan.get("template_variants", 2)
    for n, m in niches.items():
        vmax[n] = min(pl(n).get("vmax", 400), len(m["rooms"]) * cpv)
        nf = len(m["fixed"])
        cap[n] = nf * vmax[n] + (supply(m) - nf) * min(tvar, vmax[n])
        if "max_listings" in pl(n):     # stop one template family swamping the catalogue
            cap[n] = min(cap[n], pl(n)["max_listings"])
    stores = plan["stores"]
    primary = {s["id"]: set(s["niches"]) for s in stores}

    alloc = {}
    for s in stores:
        pri = [n for n in niches if niches[n].get("parent", n) in primary[s["id"]]]
        oth = [n for n in niches if n not in pri]
        a = {}
        for group, share in ((pri, P), (oth, 1 - P)):
            tw = sum(w[n] for n in group) or 1
            for n in group:
                a[n] = s["rows"] * s.get("headroom", 1.0) * share * w[n] / tw
        alloc[s["id"]] = a

    # water-fill: shrink over-subscribed niches, hand the freed rows to niches with room
    for _ in range(50):
        need = defaultdict(float)
        for a in alloc.values():
            for n, v in a.items():
                need[n] += v
        over = {n for n in niches if need[n] > cap[n] + 0.5}
        if not over:
            break
        for sid, a in alloc.items():
            freed = 0.0
            for n in over:
                keep = a[n] * cap[n] / need[n]
                freed += a[n] - keep
                a[n] = keep
            # freed rows stay on-theme: they go only to this store's own niches.
            # If those are full too, the store is simply smaller - better than
            # padding a business store with family-name prints.
            # freed rows go to this store's own niches first; only when those are
            # full do they spill to any niche with room, so the store still
            # reaches its target (every row stays globally unique either way)
            room = [n for n in niches if n not in over and need[n] < cap[n]]
            targets = [n for n in room if niches[n].get("parent", n) in primary[sid]] or room
            tw = sum(w[n] for n in targets) or 1
            for n in targets:
                a[n] += freed * w[n] / tw
    # integerise per store, fixing rounding on the largest niche
    out = {}
    for sid, a in alloc.items():
        out[sid] = {n: int(v) for n, v in a.items()}
    return out, cap, vmax, min(tvar, 400)


# ------------------------------------------------------------------ titles

def title_phrase(phrase):
    attrib = None
    if " ~ " in phrase:
        phrase, attrib = phrase.split(" ~ ", 1)
    t = re.sub(r"\s*/\s*", " ", phrase.replace("*", "")).strip()
    words = t.split()
    tc = [w if (i and w.lower() in SMALL) else (w[:1].upper() + w[1:]) for i, w in enumerate(words)]
    t = " ".join(tc).rstrip(",;")
    if attrib:
        short = " ".join(t.split()[:6]).rstrip(",.;:")
        t = f"{attrib} {short}"
    return t


def fit(parts, limit=80, keep=1):
    """Join parts in priority order within `limit` characters.
    The first part (the phrase) is trimmed at a word boundary so that the next
    `keep` parts always fit - those carry the search keywords that must never
    be squeezed out. Later parts are added only while they fit."""
    head, must, rest = parts[0], parts[1:1 + keep], parts[1 + keep:]
    need = sum(len(p) + 1 for p in must if p)
    if len(head) + need > limit:
        cut = head[: max(0, limit - need)].rsplit(" ", 1)[0]
        head = cut.rstrip(",.;:&-")
    out = " ".join([head] + [p for p in must if p]).strip()
    for p in rest:
        if p and len(out) + 1 + len(p) <= limit:
            out += " " + p
    return out[:limit]


# The words buyers type for each kind of print. They go straight after the phrase
# and can never be trimmed, so a funny print is found by "funny", a religious one
# by "religious"/"christian", a memorial one by "memorial"/"remembrance", etc.
# Every phrase here was checked against eBay UK's search-box suggestions (what UK
# buyers actually type, ranked by search volume): research/keywords.py, KEYWORDS.md.
MOOD = {
    "funny_sarcasm": "Funny Quote", "bathroom": "Funny Bathroom", "hobbies": "Funny",
    "heritage_dialect": "Funny", "man_cave": "Man_Cave", "laundry_utility": "Funny Laundry_Room",
    "bar_pub": "Home_Bar", "coffee_cafe": "Coffee_Bar Kitchen", "kitchen": "Kitchen Quote",
    "garden_outdoor": "Garden Quote", "faith_christian": "Christian Religious",
    "scripture": "Bible_Verse Christian", "faith_blessings": "Religious Christian",
    "faith_islamic": "Islamic Muslim", "faith_dharmic": "Spiritual",
    "memorial": "Memorial", "motivation": "Motivational",
    "proverbs_classics": "Inspirational Quote", "words_aesthetic": "Minimalist Typography",
    "office_work": "Office Motivational", "fitness_selfcare": "Motivational",
    "home_family": "Family Quote", "personalised_family": "Family_Name Sign",
    "wedding_love": "Wedding Gift", "new_home": "New_Home", "milestones": "Gift",
    "places_towns": "Town Typography", "christmas_seasonal": "Christmas Quote",
    "travel_coastal": "Coastal", "nursery_kids": "Nursery Kids_Room",
    "classroom": "Educational Classroom", "biz_education": "Educational School",
    "thank_you_jobs": "Thank_You Gift", "pets": "Dog_Lover Pet", "biz_automotive": "Car_Showroom",
    "biz_hair_beauty": "Hair_Salon Beauty_Salon", "biz_hospitality": "Cafe Restaurant",
    "biz_fitness_venues": "Motivational Gym", "biz_health": "Medical Clinic",
    "biz_office_pro": "Office Motivational", "biz_retail_shop": "Shop Sign", "biz_trades_pets": "Workshop",
}
# Second keyword, added right after the first when the title has room.
EXTRA = {
    "bathroom": "Toilet", "laundry_utility": "Utility", "bar_pub": "Pub", "scripture": "Scripture",
    "faith_dharmic": "Zen", "memorial": "Remembrance", "motivation": "Inspirational",
    "fitness_selfcare": "Positive", "new_home": "Housewarming", "travel_coastal": "Seaside",
    "biz_automotive": "Garage", "man_cave": "Garage",
}


def mood_words(niche, phrase):
    """Niche keyword, sharpened by what the phrase actually is."""
    p = " ".join(re.findall(r"[a-z0-9']+", phrase.lower()))
    w = set(p.split())
    m = MOOD.get(niche, "")
    if niche == "milestones":
        m = ("Anniversary Gift" if "anniversary" in p else "Retirement Gift" if "retire" in p
             else "Graduation Gift" if ("graduat" in p or "class of" in p) else "Birthday Gift")
    elif niche == "pets" and w & {"cat", "cats", "kitten"}:
        m = "Cat_Lover Pet"
    elif niche == "wedding_love":
        m = ("Mr_and_Mrs Wedding" if {"mr", "mrs"} & w else "Wedding Gift" if w & {"married", "wedding", "wed"}
             else "Love_Quote Couple")
    elif niche == "thank_you_jobs":
        m = ("Teacher_Gift" if w & {"teacher", "teachers", "teaching", "miss", "sir"} else
             "Nurse_Gift" if w & {"nurse", "nurses", "nursing"} else
             "Leaving_Gift" if w & {"leaving", "retire", "goodbye"} else m)
    elif niche == "biz_hair_beauty" and w & {"barber", "barbers", "beard", "fade"}:
        m = "Barber_Shop"
    elif niche == "biz_health" and w & {"teeth", "tooth", "dentist", "dental", "smile", "floss"}:
        m = "Dentist Dental"
    elif niche == "memorial" and w & {"dog", "cat", "pet", "paw", "paws"}:
        m = "Pet_Memorial"
    return m


KINDS = ["Wall Art Print", "Print Wall Art", "Art Print Wall Decor", "Wall Art Poster Print"]


def _fresh(words, already):
    """Drop keywords already present so a title never says 'Anniversary Anniversary'.
    Words joined by _ are one keyword ('Coffee_Bar'): dropped whole if any of its words is there."""
    have = set(re.findall(r"[a-z']+", already.lower()))
    out = []
    for chunk in words.split():
        parts = chunk.split("_")
        if not any(p.lower() in have for p in parts):   # 'Coffee Coffee Bar' -> drop the whole keyword
            out.append(" ".join(parts))
    return " ".join(out)


def build_title(phrase, venue, colour, rnd, niche=""):
    kind = rnd.choice(KINDS)                # "Wall Art" and "Print" are always in the title
    head = title_phrase(phrase)
    mood = _fresh(mood_words(niche, phrase), head)
    if len(mood) + len(kind) > 30:          # long keyword phrase: shortest kind, so the phrase keeps its room
        kind = "Wall Art Print"
    core = f"{mood} {kind}".strip()
    extra = _fresh(EXTRA.get(niche, ""), head + " " + core)
    if _fresh(venue, head + " " + core + " " + extra) != venue:   # 'Kids Room ... Living' - skip a clashing room
        venue = ""
    gift = "" if "gift" in (head + " " + core).lower() else "Gift"
    return fit([head, core, extra, venue, colour, "A4 A3 A2", gift, "Framed"])


# ------------------------------------------------------------------ style picks

def style_pools(meta):
    pals, fonts = [], []
    for m in meta["mood"]:
        pals += PALETTE_MOODS.get(m, [])
        fonts += FONT_MOODS.get(m, [])
    pals = list(dict.fromkeys(pals)) + [p for p in PALETTES if p not in pals]
    fonts = list(dict.fromkeys(fonts)) or list(FONTSETS)
    return pals, fonts


def pick_layout(phrase, rnd):
    n = phrase.count(" / ") + 1
    long_text = " ~ " in phrase or len(phrase) > 70
    if long_text:
        return rnd.choice(["stack", "frame", "arch", "left", "corner"])
    if n == 1:
        return rnd.choice(["stack", "badge", "frame", "arch", "corner", "left"])
    if n >= 3:
        return rnd.choice(LAYOUTS)
    return rnd.choice(["stack", "frame", "rules", "arch", "badge", "ribbon", "left", "corner"])


SLOT_WORDS = None


def microkey(phrase, meta):
    """The audience a templated phrase speaks to: the breed, hobby, job, drink,
    relation or place that filled its slot. Names/surnames/years are not
    audiences, so plain phrases and name templates return ''."""
    global SLOT_WORDS
    if SLOT_WORDS is None:
        from phrases import load_slots
        sl = load_slots()
        SLOT_WORDS = {}
        for k in ("breed", "hobby", "job", "drink", "rel", "town", "county", "age", "anniv"):
            for vals in sl[k]:
                SLOT_WORDS[vals[0].lower()] = f"{k}:{vals[0]}"
    toks = re.sub(r"[^a-z0-9' ]+", " ", phrase.lower()).split()
    for size in (3, 2, 1):
        for j in range(len(toks) - size + 1):
            tag = SLOT_WORDS.get(" ".join(toks[j:j + size]))
            if tag:
                return tag
    return ""


def img_path(phrase, pal, fonts, layout, orn):
    b = base64.urlsafe_b64encode(phrase.encode()).decode().rstrip("=")
    return f"/r/{pal}/{fonts}/{layout}/{orn}/{b}.jpg"


# ------------------------------------------------------------------ main

FIELDS = ["sku", "store", "niche", "micro_niche", "phrase", "variant", "palette", "fonts", "layout", "ornament",
          "colour", "room", "occasion", "title", "img_path"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--plan", default=str(HERE / "plan.json"))
    ap.add_argument("--per-store", type=int)
    ap.add_argument("--plan-only", action="store_true")
    ap.add_argument("--out", default=str(OUT))
    ap.add_argument("--seed", type=int, default=2026)
    a = ap.parse_args()

    plan = json.loads(Path(a.plan).read_text())
    if a.per_store:          # quick trial: scale every store down proportionally
        big = max(st["rows"] for st in plan["stores"])
        for st in plan["stores"]:
            st["rows"] = max(1, st["rows"] * a.per_store // big)
    niches = load_niches()
    alloc, cap, vmax, tvar = allocate(plan, niches)
    stores = {s["id"]: s for s in plan["stores"]}

    total = {n: min(cap[n], sum(alloc[s][n] for s in alloc)) for n in niches}
    tot_cap = sum(cap.values())
    target = sum(st["rows"] for st in plan["stores"])
    if tot_cap < target:
        print(f"NOTE: unique-design capacity is {tot_cap:,} listings, below the "
              f"{target:,} target. Add phrases (expand_phrases.py) to close the gap.\n")
    print(f"{'niche':22s} {'supply':>12s} {'vmax':>4s} {'listings':>10s} {'phrases':>9s} {'avg colourways':>14s}")
    report = {}
    for n in sorted(niches, key=lambda n: -total[n]):
        sup = supply(niches[n])
        nf = len(niches[n]["fixed"])
        phr = min(sup, max(min(nf, total[n]), nf + max(0, total[n] - nf * vmax[n]) // max(1, min(tvar, vmax[n]))))
        cw = total[n] / phr if phr else 0
        report[n] = {"supply": sup, "listings": total[n], "unique_phrases": phr, "colourways_per_phrase": round(cw, 2)}
        print(f"{n:22s} {sup:>12,} {vmax[n]:>4} {total[n]:>10,} {phr:>9,} {cw:>14.2f}")
    grand = sum(total.values())
    uniq = sum(r["unique_phrases"] for r in report.values())
    print(f"{'TOTAL':22s} {'':>12s} {'':>4s} {grand:>10,} {uniq:>9,} {grand / max(uniq, 1):>14.2f}")
    if a.plan_only:
        return

    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    t0 = time.time()

    # 1. per niche: the unique phrases, then the (phrase, variant) jobs dealt to stores
    store_jobs = {sid: {} for sid in alloc}
    seen = set()
    for n, meta in niches.items():
        need = total[n]
        if not need:
            continue
        fixed_set = set(meta["fixed"])
        tv = min(tvar, vmax[n])
        # enough phrases that every one stays within its own cap
        phr, room = [], 0
        for p in iter_niche(meta, seen, seed=a.seed):
            phr.append(p)
            room += vmax[n] if p in fixed_set else tv
            if room >= need:
                break
        caps = [vmax[n] if p in fixed_set else tv for p in phr]
        need = min(need, sum(caps))
        quota = {sid: alloc[sid][n] for sid in alloc if alloc[sid][n]}
        scale = need / max(1, sum(quota.values()))
        quota = {sid: max(1, int(q * scale)) for sid, q in quota.items()}
        lists = {sid: [] for sid in quota}
        heap = [(0.0, sid) for sid in quota]
        heapq.heapify(heap)
        made, k = 0, max(caps)
        for v in range(k):
            for i in range(len(phr)):
                if made >= need or not heap:
                    break
                if v >= caps[i]:
                    continue
                r, sid = heapq.heappop(heap)
                lists[sid].append((i, v))
                made += 1
                if len(lists[sid]) < quota[sid]:
                    heapq.heappush(heap, (len(lists[sid]) / quota[sid], sid))
        for sid, l in lists.items():
            store_jobs[sid][n] = (phr, l)
        print(f"  {n:22s} {len(phr):>9,} phrases  {made:>9,} rows  ({time.time() - t0:.0f}s)", flush=True)

    # 2. per store: interleave niches by share and write rows
    codes = {n: hashlib.md5(n.encode()).hexdigest()[:3].upper() for n in niches}
    summary = {"plan": plan, "niches": report, "stores": {}}
    micros = set()
    blocked = 0
    pools = {}
    for sid in sorted(store_jobs):
        jobs = store_jobs[sid]
        path = out / f"{stores[sid]['bucket']}.csv.gz"
        heap = [(0.0, n) for n in jobs if jobs[n][1]]
        heapq.heapify(heap)
        pos = {n: 0 for n in jobs}
        counts = defaultdict(int)
        with gzip.open(path, "wt", encoding="utf-8", newline="", compresslevel=3) as fh:
            w = csv.writer(fh)
            w.writerow(FIELDS)
            row_no = 0
            while heap and row_no < stores[sid]["rows"]:
                _, n = heapq.heappop(heap)
                phr, lst = jobs[n]
                i, v = lst[pos[n]]
                pos[n] += 1
                if pos[n] < len(lst):
                    heapq.heappush(heap, (pos[n] / len(lst), n))
                meta = niches[n]
                phrase = phr[i]
                rnd = random.Random(f"{a.seed}|{n}|{i}|{v}")
                if n not in pools:
                    pools[n] = style_pools(meta)
                pals, fonts = pools[n]
                venues = meta["rooms"]
                # variant v -> a unique (venue, colourway) pair for this phrase:
                # the same words reach a different market AND look different
                vr, vq = v % len(venues), v // len(venues)
                shuf = random.Random(f"{a.seed}|{n}|{i}")
                vorder = venues[:]; shuf.shuffle(vorder)
                head = pals[:8]; shuf.shuffle(head)
                porder = head + pals[8:]
                pal = porder[(vq + vr) % len(porder)]
                room = vorder[vr]
                fset = rnd.choice(fonts)
                layout = pick_layout(phrase, rnd)
                orn = rnd.choice(ORNAMENTS.get(meta.get("parent", n), ["none"]))
                colour = PALETTES[pal][0]
                occ = meta["occasion"][0] if meta["occasion"] else ""
                title = build_title(phrase, room, colour, rnd, meta.get("parent", n))
                if ip_check(title):          # e.g. a venue word that collides with a brand
                    blocked += 1
                    continue
                row_no += 1
                sku = f"{stores[sid]['sku']}{codes[n]}{row_no:07d}"
                micro = f"{n}|{room}|{microkey(phrase, meta)}"
                micros.add(micro)
                w.writerow([sku, sid, n, micro, phrase, v, pal, fset, layout, orn, colour, room, occ,
                            title,
                            img_path(phrase, pal, fset, layout, orn)])
                counts[n] += 1
        summary["stores"][sid] = {"name": stores[sid]["name"], "rows": row_no, "by_niche": dict(counts)}
        print(f"store {sid} {stores[sid]['name']:26s} {row_no:>9,} rows  {path.stat().st_size / 1e6:.0f} MB  ({time.time() - t0:.0f}s)", flush=True)

    summary["micro_niches"] = len(micros)
    summary["ip_blocked_titles"] = blocked
    print(f"titles blocked by the IP check: {blocked:,}")
    print(f"distinct micro-niches (niche x venue x audience): {len(micros):,}")
    (out / "summary.json").write_text(json.dumps(summary, indent=1))
    print(f"done in {time.time() - t0:.0f}s")


if __name__ == "__main__":
    main()

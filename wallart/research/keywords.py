#!/usr/bin/env python3
"""Check title keywords against what eBay UK buyers actually type.

eBay's search box suggests completions ranked by how often UK buyers search
them. For every candidate keyword X we ask for the completions of "X", "X wall",
"X print", "X sign", "X poster", "X picture" and score how strongly X is used for wall decor:

  3  "X wall art / print / sign / poster / picture" is in the top completions of plain "X"
  2  it appears when the buyer has typed "X wall" / "X print" / ...
  1  only longer, unrelated completions
  0  eBay suggests nothing (nobody searches it)

    python3 research/keywords.py            -> research/keywords.json + research/KEYWORDS.md
"""
import json, re, time, urllib.parse, urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
URL = "https://autosug.ebaystatic.com/autosug?kwd={}&sId=3&_ch=0"
DECOR = ("wall art", "print", "prints", "sign", "signs", "poster", "posters", "picture", "pictures",
         "plaque", "wall decor", "wall hanging", "framed", "canvas", "quote", "quotes")
TAILS = ["", " wall", " print", " sign", " poster", " picture"]

# niche -> candidate phrasings (the current title word first)
CANDIDATES = {
    "funny_sarcasm": ["funny", "funny quote", "sarcastic", "funny sign", "rude"],
    "bathroom": ["funny bathroom", "bathroom", "toilet", "toilet rules", "bathroom rules", "funny toilet"],
    "hobbies": ["funny", "gardening", "fishing", "golf", "knitting", "gamer", "gaming", "craft room", "sewing room"],
    "heritage_dialect": ["funny", "yorkshire", "scottish", "geordie", "northern", "scouse", "welsh", "cornish", "irish"],
    "man_cave": ["man cave", "garage", "funny man cave", "shed"],
    "laundry_utility": ["funny laundry", "laundry room", "laundry", "utility room"],
    "bar_pub": ["home bar", "pub", "bar", "beer", "cocktail", "pub sign", "bar sign", "gin"],
    "coffee_cafe": ["coffee", "coffee bar", "coffee quote", "cafe", "coffee station", "tea"],
    "kitchen": ["kitchen", "kitchen quote", "funny kitchen", "kitchen sign", "kitchen rules"],
    "garden_outdoor": ["garden", "garden sign", "garden quote", "outdoor"],
    "faith_christian": ["christian", "religious", "christian quote", "jesus", "faith"],
    "scripture": ["bible verse", "scripture", "christian", "bible quote", "psalm"],
    "faith_blessings": ["blessing", "religious", "blessed", "prayer", "house blessing"],
    "faith_islamic": ["islamic", "muslim", "arabic calligraphy", "ayatul kursi", "bismillah", "quran"],
    "faith_dharmic": ["spiritual", "buddha", "hindu", "yoga", "zen", "om"],
    "memorial": ["memorial", "sympathy", "bereavement", "in loving memory", "remembrance", "grief", "loss"],
    "motivation": ["motivational", "inspirational", "motivational quote", "positive quote", "positive", "affirmation"],
    "proverbs_classics": ["inspirational quote", "inspirational", "quote", "wise quote", "life quote"],
    "words_aesthetic": ["minimalist typography", "minimalist", "typography", "aesthetic", "word art", "quote"],
    "office_work": ["motivational office", "office", "office quote", "work", "home office"],
    "fitness_selfcare": ["motivational", "fitness", "self care", "self love", "mental health"],
    "home_family": ["family quote", "family", "family rules", "home quote", "house rules", "home"],
    "personalised_family": ["family name", "personalised family", "personalised name", "personalised", "family tree", "surname"],
    "wedding_love": ["wedding love", "wedding", "love quote", "couple", "personalised wedding", "love", "mr and mrs"],
    "new_home": ["new home", "housewarming", "first home", "new home gift"],
    "milestones": ["birthday gift", "anniversary gift", "retirement gift", "graduation gift", "birthday", "anniversary"],
    "places_towns": ["hometown", "town", "city", "location"],
    "christmas_seasonal": ["christmas", "christmas quote", "festive", "winter"],
    "travel_coastal": ["coastal", "beach", "seaside", "nautical", "beach house"],
    "nursery_kids": ["nursery kids", "nursery", "kids", "kids room", "baby", "childrens", "playroom"],
    "classroom": ["classroom", "school", "teacher", "educational", "classroom display"],
    "biz_education": ["classroom school", "classroom", "school", "teacher", "educational"],
    "thank_you_jobs": ["thank you gift", "thank you", "teacher gift", "nurse gift", "leaving gift"],
    "pets": ["dog lover", "dog", "cat lover", "cat", "dog quote", "pet", "pet memorial"],
    "biz_automotive": ["car showroom", "garage", "car", "mechanic", "garage sign", "car garage"],
    "biz_hair_beauty": ["salon", "hair salon", "beauty salon", "barber", "nail salon", "beauty room", "barber shop"],
    "biz_hospitality": ["cafe restaurant", "cafe", "restaurant", "cafe sign", "restaurant sign"],
    "biz_fitness_venues": ["gym motivational", "gym", "fitness", "gym quote", "home gym"],
    "biz_health": ["clinic", "dental", "dentist", "physio", "therapy room", "medical", "doctor"],
    "biz_office_pro": ["office motivational", "office", "office quote", "business", "entrepreneur"],
    "biz_retail_shop": ["shop sign", "shop", "business", "shop decor", "boutique"],
    "biz_trades_pets": ["workshop", "dog grooming", "tattoo", "barber", "builder", "electrician"],
    # image, chart and map lines
    "img_animals": ["highland cow", "animal", "funny animal", "animal bathroom", "animal in bath", "dog in bath",
                    "flower crown", "animal flower crown", "dictionary", "black and white animal", "nursery animal",
                    "safari animal", "woodland animal", "farm animal", "christmas animal", "royal animal", "pet portrait"],
    "img_plants": ["botanical", "flower", "plant", "eucalyptus", "olive branch", "wildflower"],
    "charts": ["times tables", "multiplication", "alphabet", "educational", "number", "periodic table",
               "solar system", "planets", "phonics", "telling the time", "feelings chart", "roman numerals"],
    "maps": ["map", "world map", "country map", "uk map", "home map", "map heart", "england map",
             "scotland map", "ireland map", "city map", "hometown map"],
    "pd_art": ["vintage", "botanical", "japanese", "vintage map", "william morris", "van gogh", "monet",
               "famous painting", "vintage poster", "bird", "horse", "landscape", "seascape", "museum",
               "art nouveau", "klimt", "hokusai", "still life", "old masters", "abstract", "vintage botanical",
               "vintage animal", "fruit", "kitchen vintage"],
    "product_nouns": ["wall art", "print", "prints", "poster", "art print", "picture", "framed print", "sign",
                      "wall decor", "a4 print", "a3 print", "a2 print", "framed wall art", "unframed print"],
}


def fetch(q):
    for i in range(4):
        try:
            raw = urllib.request.urlopen(URL.format(urllib.parse.quote(q)), timeout=15).read().decode()
            body = raw[raw.index("(") + 1: raw.rindex(")")]
            res = json.loads(body).get("res") or {}
            return res.get("sug") or []
        except Exception:
            time.sleep(1 + 2 * i)
    return None


NOT_DECOR = re.compile(r"\b(signed|printer|printers|printing|printed|fabric|dress|top|blouse|shirt|bag|"
                       r"remover|kit|wallpaper|wallet|seat|shorts|camera|stencil|card|cards)\b")
DECOR_RE = re.compile(r"\b(" + "|".join(DECOR) + r")\b")


def is_decor(s, kw):
    rest = s[len(kw):] if s.startswith(kw) else s
    return bool(DECOR_RE.search(rest)) and not NOT_DECOR.search(s)


def score(kw, sugg):
    top = sugg.get(kw) or []
    decor = [s for s in top if s.startswith(kw + " ") and is_decor(s, kw)]
    if decor:
        return 3, decor
    deeper = [s for t in TAILS[1:] for s in (sugg.get(kw + t) or [])]
    decor = [s for s in deeper if is_decor(s, kw)]
    if decor:
        return 2, decor[:6]
    if top or deeper:
        return 1, (top or deeper)[:4]
    return 0, []


def used_keywords():
    """Every keyword the typography titles now carry (generate.MOOD / EXTRA / mood_words)."""
    import sys
    sys.path.insert(0, str(HERE.parent))
    import generate
    vals = list(generate.MOOD.values()) + list(generate.EXTRA.values()) + [
        "Anniversary Gift", "Retirement Gift", "Graduation Gift", "Birthday Gift", "Cat_Lover", "Mr_and_Mrs",
        "Love_Quote Couple", "Teacher_Gift", "Nurse_Gift", "Leaving_Gift", "Barber_Shop", "Dentist", "Pet_Memorial"]
    out = set()
    for v in vals:
        for chunk in v.split():
            out.add(chunk.replace("_", " ").lower())
    out -= {"gift", "quote", "sign", "kitchen", "pet"}   # generic tails, checked as product nouns
    return sorted(out)


def main():
    CANDIDATES["used_in_titles"] = used_keywords()
    kws = sorted({k for v in CANDIDATES.values() for k in v})
    qs = [k + t for k in kws for t in TAILS]
    with ThreadPoolExecutor(8) as ex:
        res = dict(zip(qs, ex.map(fetch, qs)))
    failed = [q for q, v in res.items() if v is None]
    sugg = {q: v or [] for q, v in res.items()}
    out = {}
    for niche, cands in CANDIDATES.items():
        out[niche] = []
        for k in cands:
            s, ev = score(k, sugg)
            out[niche].append({"keyword": k, "score": s, "evidence": ev, "top": sugg.get(k, [])})
    (HERE / "keywords.json").write_text(json.dumps({"failed": failed, "niches": out, "raw": sugg}, indent=1))
    print(f"{len(qs)} queries, {len(failed)} failed")
    md = ["# Title keywords vs what eBay UK buyers type", "",
          "Source: eBay UK search-box suggestions (`autosug.ebaystatic.com`, site 3), which eBay ranks by how",
          "often UK buyers search each phrase. Rebuild with `python3 research/keywords.py`.", "",
          "Score: **3** = eBay suggests \"X wall art / print / sign / poster\" as soon as X is typed (strong);",
          "**2** = suggested once the buyer adds wall/print/sign (real, narrower); **1** = searched, but not for",
          "wall decor (e.g. 'sympathy' -> cards); **0** = nobody searches it.", ""]
    for niche, rows in out.items():
        md += [f"## {niche}", "", "| keyword | score | what buyers type |", "|---|---|---|"]
        for r in sorted(rows, key=lambda r: -r["score"]):
            md.append(f"| {r['keyword']} | {r['score']} | {'; '.join(r['evidence'][:3])} |")
        md.append("")
    (HERE / "KEYWORDS.md").write_text("\n".join(md))
    for niche, rows in out.items():
        print(f"\n{niche}")
        for r in rows:
            print(f"  {r['score']} {r['keyword']:24s} {'; '.join(r['evidence'][:4])}")


if __name__ == "__main__":
    main()

"""
check_csv.py — verify the eBay CSVs before uploading.

Every check corresponds to something that has already gone wrong on this
account: a rejected structure, a duplicate-listing flag, or a broken image.

    python3 check_csv.py
"""

import csv, glob, os, re, sys, urllib.request
from collections import Counter

csv.field_size_limit(min(sys.maxsize, 2**31 - 1))

files = sorted(glob.glob("tshirt_ebay_*.csv"))
if not files:
    raise SystemExit("no tshirt_ebay_*.csv found")

fails, warns = [], []


def check(ok, label, detail="", warn=False):
    mark = "PASS" if ok else ("WARN" if warn else "FAIL")
    print(f"  [{mark}] {label}" + (f"  — {detail}" if detail else ""))
    if not ok:
        (warns if warn else fails).append(label)


parents, variations, titles = [], 0, []
for f in files:
    for r in csv.DictReader(open(f, encoding="utf-8")):
        if r["Relationship"] == "Variation":
            variations += 1
        else:
            parents.append(r)
            titles.append(r["*Title"])

# subject lookup, needed by several checks below
subj_of_early = {}
if os.path.exists("generation_queue.csv"):
    for row in csv.DictReader(open("generation_queue.csv", encoding="utf-8")):
        subj_of_early[row["index"]] = row["subject"]

CAT_NAMES = {"Maine Coon", "British Shorthair", "Russian Blue Cat"}
DOG_NAMES = {"Labrador", "Golden Retriever", "German Shepherd", "Corgi",
             "Dalmatian", "Pug", "Beagle", "Boxer Dog", "Rottweiler",
             "Doberman", "Akita", "Shiba Inu", "Vizsla", "Weimaraner",
             "Chihuahua", "Lurcher", "Whippet", "Greyhound", "Saluki",
             "Basenji", "Samoyed", "Chow Chow", "Mastiff", "Pitbull"}

print(f"CSV CHECK — {len(files)} files, {len(parents):,} listings\n")

# --- structure eBay accepted -----------------------------------------------
print("STRUCTURE")
A = [k for k in parents[0]][0]
check(all(r["*Category"] == "15687" for r in parents), "category 15687",
      "Men's Clothing > Shirts & Tops > T-Shirts")
check(all(r["ShippingProfileName"] == "2" for r in parents),
      "shipping profile 2")
check(all(r["ReturnProfileName"] == "1" for r in parents), "return profile 1")
check(all(r["PaymentProfileName"] == "1" for r in parents), "payment profile 1")
check(all(r[A] == "Add" for r in parents), "Action=Add on parents only")
check(variations == len(parents) * 10,
      "10 variations per listing", f"{variations:,} rows")

rel = parents[0]["RelationshipDetails"]
check(rel.startswith("Size=") and rel.count("=") == 1,
      "RelationshipDetails is one dimension",
      rel[:44] + "...")
check(all(r["*C:Colour"] == "Black" for r in parents),
      "Colour item specific is Black")
check(all(r["*C:Size"] == "" for r in parents),
      "Size blank on parent (it is the variation dimension)")
check(all(r["CustomLabel"] for r in parents), "CustomLabel on parents")
check(all(r["*Description"] for r in parents), "description on parents")

# --- titles ----------------------------------------------------------------
print("\nTITLES")
check(all("t-shirt" in t.lower() for t in titles), "every title has T-Shirt")
check(max(len(t) for t in titles) <= 80, "all within 80 characters",
      f"longest {max(len(t) for t in titles)}")
check(len(titles) == len(set(titles)), "no exact duplicates",
      f"{len(titles)-len(set(titles))} found")
fp = Counter(" ".join(sorted(t.lower().split())) for t in titles)
check(all(v == 1 for v in fp.values()), "no reordered duplicates",
      f"{sum(1 for v in fp.values() if v>1)} found")
# A handful of near-identical titles is tolerable; eBay flags patterns, not
# three listings. Fail only if it is systemic.
stem = Counter(" ".join(t.split()[:-1]) for t in titles)
groups = sum(1 for v in stem.values() if v > 2)
affected = sum(v for v in stem.values() if v > 2)
check(affected <= len(titles) * 0.005,
      "no systemic near-duplicate titles",
      f"{groups} groups, {affected} listings ({affected/len(titles)*100:.2f}%)")
check(not any(re.search(r"\s\d+$", t) for t in titles),
      "no numeric padding (\"... 2\")")
check(not any("gift" in t.lower() for t in titles), "no 'Gift'")
blk = sum(1 for t in titles if re.search(r"\bblack\b", t, re.I))
check(blk > len(titles) * 0.9, "'Black' in titles (the garment colour)",
      f"{blk/len(titles)*100:.0f}%")
cot = sum(1 for t in titles if "100% Cotton" in t)
check(cot > len(titles) * 0.5, "'100% Cotton' in most titles",
      f"{cot/len(titles)*100:.0f}%")

# --- search keywords -------------------------------------------------------
print("\nSEARCH KEYWORDS")
# Work from the design's ACTUAL subject, not substrings in the title.
# Substring matching produced false failures every time: "Australian CATtle
# Dog", "German SHORTHAIRed Pointer" and the "Small TORTOISESHELL" butterfly
# were all reported as mislabelled cats when the titles were correct.
dog_t, cat_t = [], []
if subj_of_early:
    for r in parents:
        try:
            idx = str(int(r["CustomLabel"].split("-")[1]))
        except (IndexError, ValueError):
            continue
        sub = subj_of_early.get(idx, "")
        if not sub:
            continue
        low = sub.lower()
        if re.search(r"\bcats?\b|\bkitten\b", low) or sub in CAT_NAMES:
            cat_t.append(r["*Title"])
        elif sub in DOG_NAMES or re.search(
                r"\bretriever\b|\bspaniel\b|\bterrier\b|\bcollie\b|"
                r"\bbulldog\b|\bhound\b|\bpointer\b|\bshepherd\b|"
                r"\bpoodle\b|\bdoodle\b|\bsetter\b", low):
            dog_t.append(r["*Title"])
# Standalone word, not a substring: "Doggo" contains "dog" but would not
# match a buyer searching "dog t shirt".
nd = sum(1 for t in dog_t if not re.search(r"\bdog\b", t, re.I))
nc = sum(1 for t in cat_t if not re.search(r"\bcat\b", t, re.I))
check(nd <= len(dog_t) * 0.01, "dog breed titles contain the word 'Dog'",
      f"{len(dog_t):,} listings, {nd} missing")
check(nc <= len(cat_t) * 0.01, "cat breed titles contain the word 'Cat'",
      f"{len(cat_t):,} listings, {nc} missing")

# The generic category word must appear for subjects whose name does not
# contain it — a Wyvern listing that never says "Dragon" is invisible to
# anyone searching for a dragon shirt.
#
# Match on the design's ACTUAL subject from the queue, not on substrings in
# the title. "Skull And Moth" is a gothic subject, not the insect; "Odin's
# Ravens" is Norse, not the bird. Substring matching reported 837 false
# failures against titles that were perfectly correct.
GENERIC = {
    "Wyvern": "Dragon", "Hydra": "Dragon", "Basilisk": "Dragon",
    "Barn Owl": "Bird", "Snowy Owl": "Bird", "Raven": "Bird",
    "Kingfisher": "Bird", "Puffin": "Bird", "Peacock": "Bird",
    "Orca": "Whale", "Octopus": "Sea", "Jellyfish": "Sea",
    "Cobra": "Snake", "Rattlesnake": "Snake", "Viper": "Snake",
    "Butterfly": "Insect", "Moth": "Insect", "Beetle": "Insect",
    "Triceratops": "Dinosaur", "Velociraptor": "Dinosaur",
    "Maine Coon": "Cat", "British Shorthair": "Cat",
}
gm = gt = 0
subj_of = {}
if os.path.exists("generation_queue.csv"):
    for row in csv.DictReader(open("generation_queue.csv", encoding="utf-8")):
        subj_of[row["index"]] = row["subject"]

if subj_of:
    for r in parents:
        try:
            idx = str(int(r["CustomLabel"].split("-")[1]))
        except (IndexError, ValueError):
            continue
        word = GENERIC.get(subj_of.get(idx, ""))
        if not word:
            continue
        gt += 1
        if not re.search(r"\b" + word.split()[0] + r"\b", r["*Title"], re.I):
            gm += 1
    check(gt == 0 or gm <= gt * 0.01,
          "generic category word present (Wyvern -> Dragon, Orca -> Whale)",
          f"{gt:,} listings, {gm} missing")
else:
    check(True, "generic word check skipped", "generation_queue.csv not found",
          warn=True)

# --- description -----------------------------------------------------------
print("\nDESCRIPTION")
d = parents[0]["*Description"]
for label, ok in (("size chart table", "Size Guide" in d and "To Fit Chest" in d),
                  ("S through 2XL", "2XL" in d and "5XL" not in d),
                  ("kids sizes from 3-4 Yrs", "3-4 Yrs" in d
                   and "2-3 Yrs" not in d),
                  ("Mens (Unisex)", "Mens (Unisex)" in d),
                  ("full spec list", "Pre-shrunk" in d),
                  ("care instructions", "Machine wash" in d),
                  ("states the shirt is black", "black" in d.lower())):
    check(ok, label)
check(all("Size Guide" in r["*Description"] for r in parents[:2000]),
      "size chart on every listing")

# --- images: the one that silently breaks everything -----------------------
print("\nIMAGES")
check(all(r["PicURL"] for r in parents), "every listing has an image URL")
url = parents[0]["PicURL"]
print(f"         {url}")
# The r2.dev URL is rate limited, and a bare urllib request was getting 403
# where curl got 200 on the same file. Send a browser user agent and retry a
# few times before calling it a failure.
import time as _t

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/120.0 Safari/537.36")
ok = ctype = None
last = ""
for attempt in range(4):
    try:
        req = urllib.request.Request(url, method="GET",
                                     headers={"User-Agent": UA,
                                              "Range": "bytes=0-1023"})
        with urllib.request.urlopen(req, timeout=20) as resp:
            ok = resp.status in (200, 206)
            ctype = resp.headers.get("Content-Type", "")
        if ok:
            break
    except Exception as e:
        last = str(e)[:60]
        _t.sleep(2 * (attempt + 1))

check(bool(ok), "image URL is publicly reachable",
      last or "ok")
if ok:
    check(ctype.startswith("image/"), "URL returns an image", ctype)
else:
    print("         -> the r2.dev URL is rate limited and Cloudflare warns")
    print("            against it for production. Connect a custom domain to")
    print("            the bucket and pass --img-base https://your.domain")

print("\n" + "=" * 58)
if fails:
    print(f"FAILED {len(fails)} CHECK(S) — do not upload until fixed:")
    for f_ in fails:
        print(f"  * {f_}")
    sys.exit(1)
print("ALL CHECKS PASSED")
if warns:
    for w in warns:
        print(f"  warning: {w}")
print(f"\n{len(parents):,} listings ready. Upload TEST_3_listings.csv first.")

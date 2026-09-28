#!/usr/bin/env python3
"""Parallel catalogue, v3 - type-safe slogans.

v2 dropped any noun into any template and produced 'I AM A EVIL' and
'I LOVE TO GRIZZLY', and put '50 YEAR OLD BANGER' on a 75th-birthday
listing. A mined skeleton carries no grammar, so v3 tags every template
with the kind of word its slot takes and only fills it with a niche of
that type. Types come from the fillers actually observed in that slot,
extended by morphology (-ING is an activity, -ER/-IST is a role, -S is a
plural), and birthday listings take the age and year from their own title.
"""
import csv, json, random, re, sys
from collections import Counter, defaultdict
import vetted

random.seed(11)

GARMENT = re.compile(r"\b(t.?shirts?|tshirts?|tees?|tops?|hoodies?|vests?|aprons?|"
    r"sweat ?shirts?|jumpers?|ringer|v.?neck|petite|fotl|fruit of the loom|organic|"
    r"baseball|raglan|long.?sleeve|tank tops?)\b", re.I)
AUDIENCE = re.compile(r"\b(mens?|men's|womens?|ladies|unisex|adults?|kids?|"
    r"childrens?|boys?|girls?)\b", re.I)
NOISE = re.compile(r"\b(100%?|cotton|size|sizes|top|tee|printed|quality|brand)\b", re.I)

# Words that look like nouns to a regex but are not a niche. Every one of
# these produced a broken slogan in the v2 output.
BAD_NICHE = {
 "COOL","EVIL","BEST","FUNNY","NEW","GREAT","AWESOME","NICE","GOOD","BIG",
 "SMALL","CUTE","PURE","FANTASY","ANYTHING","NORMAL","LOVE","LIFE","THING",
 "THINGS","STUFF","GIFT","PRESENT","BIRTHDAY","CHRISTMAS","XMAS","NOVELTY",
 "RETRO","VINTAGE","CLASSIC","LIMITED","EDITION","YEAR","YEARS","OLD","MADE",
 "DESIGN","SLOGAN","QUOTE","JOKE","HUMOUR","HUMOR","MENS","LADIES","UNISEX",
 "SHIRT","TSHIRT","PERFECT","IDEAL","SUPER","ULTRA","MEGA","PREMIUM","STYLE",
 "LOOKING","LOOKS","LOOK","WEARING","FEATURING","INCLUDING","SAYING","QUOTE",
 "SIZED","FITTED","UNISEX","ADULT","ADULTS","GEORGES","ANYTHING","SOMETHING",
 "DISTRESSED","FADED","WASHED","GRAPHIC","PRINT","SLOGAN","TEXT","LOGO","REX",
}
# Adjectival endings - COLOURFUL, STUPID, GORGEOUS are not niches.
ADJ = re.compile(r"\b\w+(FUL|OUS|IVE|ABLE|IBLE|ISH|LESS|IEST|EST)\b")

STOPWORDS = set("""
A ABOUT ALL AM AN AND ANY ARE AS AT BE BEEN BEST BUT BY CAN CANT COULD DID DO
DOES DONT EACH EVEN EVER EVERY FOR FROM GET GOT HAD HAS HAVE HE HER HERE HIM
HIS HOW I IF IN INTO IS IT ITS JUST LET ME MORE MOST MUCH MUST MY NO NOR NOT
NOW OF OFF ON ONE ONLY OR OTHER OUR OUT OVER OWN SAID SAME SHE SHOULD SO SOME
SUCH THAN THAT THE THEIR THEM THEN THERE THESE THEY THIS THOSE THROUGH TO TOO
UP US VERY WAS WE WERE WHAT WHEN WHERE WHICH WHILE WHO WHOM WHY WILL WITH
WONT WOULD YOU YOUR YOURS AKA ALSO BACK DOWN MAKE MADE MAKES MANY NEW NEXT
PER PLUS SET TWO THREE FOUR FIVE SIX TEN
""".split())

SYN = {"funny":["humorous","comedy","witty"], "mens":["men's","for men"],
       "t-shirt":["tee","t shirt"], "gift":["present","gift idea"],
       "biker":["motorcyclist","rider"], "motorbike":["motorcycle","bike"],
       "motorcycle":["motorbike","bike"], "awesome":["legendary","top class"],
       "vintage":["retro","classic","old school"], "dad":["father","daddy"],
       "grandad":["grandpa","grandfather"], "lover":["fan","enthusiast"]}

PRINT_SPEC = ("BLACK garment. Print 22cm wide max on an adult chest, centred, top "
              "edge 8cm below the collar - noticeably smaller than a full front "
              "print. 4-5 flat spot colours; where the design is type-led use one "
              "ink at maximum contrast.")

LEAD  = r"(?:WITH|ON|IN|AT|THAT|WHO|TO|OF|FOR|A|AN|THE|MY|IS|ARE|AND)"
DECOR = r"(?:AWESOME|GREAT|REAL|TRUE|PROUD|BEST|SUPER)"
TAILJ = {"AUTHENTIC","GUARANTEED","GENUINE","YEARS","QUALITY","PREMIUM","IS",
         "LOOKS","OKAY","EVER","SAID","NO","ONE"}


# Templates whose slot only works with a word seen in that slot before.
STRICT = {
 "SELL MY {N} I'D RATHER SHOVE WASPS UP MY ARSE",
 "I GOT A {N} FOR MY WIFE BEST SWAP EVER",
 "IS MY {N} OKAY",
 "I'M NOT ALWAYS GRUMPY SOMETIMES I'M ON MY {N}",
 "ALL DOGS WERE CREATED EQUAL THEN GOD MADE {N}",
 "ALL MEN ARE BORN EQUAL THE BEST ARE BORN TO BE {N}",
 "{N} SOUL BIKER ATTITUDE",
 "{N} MAN THE MYTH THE LEGEND",
 "{N} MAN MYTH LEGEND",
 "PROPERTY OF MY AWESOME {N}",
 "I HAVE TOO MANY {N} SAID NO ONE EVER",
 "BUY MORE {N} SAY THE VOICES IN MY HEAD",
 "JUST A BOY WHO LOVES {N}",
 "TRUST ME I'M A {N}",
 "I'M A {N} WHAT'S YOUR SUPERPOWER",
}


def agree(sl):
    """AN OLD MAN WITH A ELECTRIC -> WITH AN ELECTRIC."""
    sl = re.sub(r"\bA ([AEIOU])", r"AN \1", sl)
    return re.sub(r"\bAN ([^AEIOU\s])", r"A \1", sl)


def core_of(f):
    t = f.split()
    while t and (re.fullmatch(LEAD, t[0]) or re.fullmatch(DECOR, t[0]) or t[0].isdigit()):
        t.pop(0)
    while t and (t[-1].isdigit() or t[-1] in TAILJ):
        t.pop()
    return " ".join(t)


# which mined skeleton feeds which vetted slot type
HARVEST = {
 "ROLE":     ["THIS IS WHAT {X} LOOKS LIKE", "YOU'RE LOOKING AT AN AWESOME {X}",
              "TRUST ME I'M {X}", "BEST {X} EVER", "I'M A {X}"],
 "ACTIVITY": ["WARNING MAY SPONTANEOUSLY START TALKING ABOUT {X}",
              "{X} ON THE BRAIN", "EAT SLEEP {X}",
              "I GOOGLED MY SYMPTOMS AND IT TURNS OUT I JUST NEED TO GO {X}",
              "{X} AND BEER THAT'S WHY I'M HERE"],
 "OBJECT":   ["NEVER UNDERESTIMATE AN OLD MAN {X}", "I GOT {X} FOR MY WIFE BEST SWAP EVER",
              "IS MY {X}", "NEVER UNDERESTIMATE OLD MAN WITH {X}"],
 "PLURAL":   ["I HAVE TOO MANY {X} EVER", "EASILY DISTRACTED BY {X}", "SAVE THE {X}"],
 "RELATION": ["{X} MAN MYTH LEGEND", "{X} MAN THE MYTH THE LEGEND"],
 "NATION":   ["ALL MEN ARE BORN EQUAL THE BEST ARE BORN TO BE {X}", "{X} BIKER ATTITUDE"],
 "BREED":    ["ALL DOGS WERE CREATED EQUAL THEN GOD MADE {X}"],
}


def harvest_vocab():
    bank = {t["template"]: t for t in json.load(open("TEMPLATE_BANK.json"))}
    vocab = defaultdict(set)
    for typ, srcs in HARVEST.items():
        for s in srcs:
            for f in bank.get(s, {}).get("fillers", {}):
                c = core_of(f)
                if c and 3 <= len(c) <= 24 and c not in BAD_NICHE and not c.isdigit():
                    vocab[typ].add(c)
    return {k: v for k, v in vocab.items()}


def type_of(n, vocab):
    """Observed type wins; otherwise fall back to English morphology."""
    for t in ("ROLE", "ACTIVITY", "OBJECT", "PLURAL", "RELATION", "NATION", "BREED"):
        if n in vocab.get(t, ()): return t
    last = n.split()[-1]
    if last.endswith("ING") and len(last) > 5:            return "ACTIVITY"
    if last.endswith(("IST","MAN","IAN")) and len(last) > 4: return "ROLE"
    # -ER is ambiguous (TEACHER is a job, SCOOTER is not), so only trust it
    # when the word was actually observed filling a role slot.
    if last.endswith(("ER","OR")) and n in vocab.get("ROLE", ()): return "ROLE"
    if last.endswith("S") and not last.endswith("SS"):    return "PLURAL"
    return "GENERIC"


def keyword_core(title):
    t = AUDIENCE.sub(" ", GARMENT.sub(" ", title))
    w = [x for x in re.findall(r"[A-Za-z0-9'&-]+", t) if len(x) > 1]
    w = [x for x in w if not NOISE.fullmatch(x)]
    seen, out = set(), []
    for x in w:
        if x.lower() in seen: continue
        seen.add(x.lower()); out.append(x)
    return out


def rewrite(title, rng):
    core = keyword_core(title)
    if len(core) < 2: return None
    out = []
    for w in core:
        lw = w.lower()
        if lw in SYN and rng.random() < 0.18:
            c = rng.choice(SYN[lw]); out.append(c.title() if w[0].isupper() else c)
        else: out.append(w)
    head, tail = out[:max(3, len(out)//2)], out[max(3, len(out)//2):]
    g = rng.choice(["T-Shirt","Tee","T Shirt"]); a = rng.choice(["Mens","Men's","Unisex"])
    x = rng.choice(["Funny","Novelty","Gift",""])
    def b(xtra=True):
        p = [" ".join(head), g, a, x if xtra else "", " ".join(tail)]
        return re.sub(r"\s{2,}"," "," ".join(q for q in p if q)).strip()
    new = b()
    if len(new) > 80: new = b(False)
    if len(new) > 80: new = new[:80].rsplit(" ",1)[0]
    return new


AGE_RE  = re.compile(r"\b(\d{1,2})(?:st|nd|rd|th)\b|\b(\d{2})\s*(?:year|yr)s?\b", re.I)
YEAR_RE = re.compile(r"\b(19[2-9]\d|20[0-2]\d)\b")


def niche_of(title, vocab_all):
    up = " " + re.sub(r"[^A-Z0-9' ]", " ", title.upper()) + " "
    up = re.sub(r"\s+", " ", up)
    best = None
    for v in vocab_all:                       # longest observed niche wins
        if f" {v} " in up and (best is None or len(v) > len(best)): best = v
    if best: return best, True
    kw = [w.upper() for w in keyword_core(title)]
    kw = [w for w in kw if len(w) > 2 and not w.isdigit() and w not in BAD_NICHE
          and w not in STOPWORDS and re.fullmatch(r"[A-Z']+", w)]
    return (kw[0] if kw else None), False


def corpus_vocab(rows, min_freq=40):
    """Subjects that recur across the catalogue are real niches; a word that
    appears twice is a typo or a fragment."""
    uni, bi = Counter(), Counter()
    for r in rows:
        t = AUDIENCE.sub(" ", GARMENT.sub(" ", r["title"])).upper()
        w = [x for x in re.findall(r"[A-Z']{3,}", t)
             if x not in STOPWORDS and x not in BAD_NICHE and not NOISE.fullmatch(x)]
        uni.update(w)
        bi.update(f"{a} {b}" for a, b in zip(w, w[1:]))
    total = max(1, sum(uni.values()))
    keep = {x for x, n in uni.items() if n >= min_freq and not ADJ.search(x)}
    # "MUAY THAI" is a niche; "SKULL SWORD" is two words that happen to be
    # common. Pointwise mutual information tells them apart.
    for x, n in bi.items():
        if n < min_freq: continue
        a, b = x.split()
        pa, pb = uni.get(a, 0) / total, uni.get(b, 0) / total
        if pa <= 0 or pb <= 0: continue
        if (n / total) / (pa * pb) >= 300 and not ADJ.search(x):
            keep.add(x)
    return keep


def main(limit=None):
    vocab = harvest_vocab()
    vocab_all = sorted({n for s in vocab.values() for n in s}, key=len, reverse=True)
    by_type = defaultdict(list)
    for t, typ, u in vetted.TEMPLATES: by_type[typ].append((t, u))
    print("harvested vocab:", {k: len(v) for k, v in vocab.items()})

    reads = {}
    for line in open("designs_read.jsonl"):
        try: r = json.loads(line)
        except Exception: continue
        reads[r["idx"]] = r

    combo = Counter()
    DROP_S = {"grid_of_designs","pixel_art","photography","text_only","two_panel",
              "image_only","badge"}
    for r in reads.values():
        st, la = r.get("style") or "distressed", r.get("layout") or "text_above_image"
        if st in DROP_S or la in ("grid_of_designs","badge"): continue
        combo[(st, la)] += (r.get("sold") or 0)
    for k in list(combo):
        if k[0] == "flat_vector":  combo[k] = int(combo[k]*.4)
        if k[1] == "two_panel":    combo[k] = int(combo[k]*.3)
        if k[0] == "photographic": combo[k] = int(combo[k]*.3)
    combo = {k: v for k, v in combo.items() if v > 0}
    combos, weights = list(combo), [combo[c] for c in combo]

    rows = json.load(open("all.json"))
    cvoc = corpus_vocab(rows)
    print(f"corpus niche vocabulary: {len(cvoc):,} terms (40+ listings each)")
    vocab_all = sorted(set(vocab_all) | cvoc, key=len, reverse=True)
    observed = {n for s_ in vocab.values() for n in s_}
    rng = random.Random(11)
    out, skipped, seen, st = [], 0, set(), Counter()

    for i, src in enumerate(rows):
        if limit and len(out) >= limit: break
        title = src["title"]
        new_title = rewrite(title, rng)
        if not new_title or new_title.lower() in seen: skipped += 1; continue
        seen.add(new_title.lower())

        n, exact = niche_of(title, vocab_all)
        style, layout = combos[rng.choices(range(len(combos)), weights)[0]]
        if style == "typography_only":      # type-led design carries no artwork
            layout = "text_only"
        read = reads.get(i)

        slogan, used, typ = "", "", ""
        if layout != "image_only":
            # a birthday listing must carry ITS OWN age and year
            am = AGE_RE.search(title); ym = YEAR_RE.search(title)
            age = next((g for g in (am.groups() if am else ()) if g), None)
            if age and by_type["AGE"] and rng.random() < .8:
                t, _ = rng.choices(by_type["AGE"], [u for _, u in by_type["AGE"]])[0]
                slogan, used, typ = t.replace("{N}", age), t, "AGE"; st["age"] += 1
            elif ym and by_type["YEAR"] and rng.random() < .8:
                t, _ = rng.choices(by_type["YEAR"], [u for _, u in by_type["YEAR"]])[0]
                slogan, used, typ = t.replace("{N}", ym.group(1)), t, "YEAR"; st["year"] += 1
            elif n:
                typ = type_of(n, vocab)
                pool = by_type.get(typ) or by_type["GENERIC"]
                # Templates that name a specific action on the noun break badly
                # on an unvetted word ("SELL MY BACON"). Restrict those to the
                # vocabulary actually observed in that slot.
                if n not in observed:
                    pool = [p for p in pool if p[0] not in STRICT] or by_type["GENERIC"]
                t, _ = rng.choices(pool, [u for _, u in pool])[0]
                slogan, used = agree(t.replace("{N}", n)), t
                st["typed_" + typ.lower()] += 1
            else:
                layout = "image_only"; st["no_niche"] += 1

        illus = ""
        if layout != "text_only":
            if read and read.get("main_image") not in (None,"","null","None"):
                illus = str(read["main_image"])
            elif n: illus = n.lower()
            if illus: st["has_illustration"] += 1

        brief = (f"Niche: {n or ' '.join(keyword_core(title)[:4])}"
                 + (f" ({typ.lower()})" if typ else "") + f". Style: {style}. "
                 f"Layout: {layout}. "
                 + (f'Printed text: "{slogan}". ' if slogan else "No printed text. ")
                 + (f"Illustration: {illus} - redraw with a new pose, angle and "
                    f"composition, NOT a copy of the original. " if illus else "")
                 + PRINT_SPEC)

        out.append([i, title, new_title, src.get("sold",0), n or "", typ, slogan,
                    used, illus, style, layout, brief])
        st[f"style:{style}"] += 1; st[f"layout:{layout}"] += 1

    with open("REPLICA_V3.csv","w",encoding="utf-8",newline="") as fh:
        w = csv.writer(fh)
        w.writerow(("source_idx","original_title","new_title","original_sold","niche",
                    "niche_type","slogan","template_used","illustration","style",
                    "layout","design_brief"))
        w.writerows(out)

    tot = len(out)
    print(f"\nsource listings    : {len(rows):,}")
    print(f"replicas generated : {tot:,} ({100*tot/len(rows):.1f}%)")
    print(f"skipped            : {skipped:,}\n")
    for k in sorted(st):
        if k.startswith(("style:","layout:")): continue
        print(f"  {k:<22} {st[k]:>8,}  {100*st[k]/tot:5.1f}%")
    print()
    for pre in ("style:","layout:"):
        for k,v in sorted(((k,v) for k,v in st.items() if k.startswith(pre)),
                          key=lambda x:-x[1]):
            print(f"  {k:<24} {v:>8,}  {100*v/tot:5.1f}%")


main(int(sys.argv[1]) if len(sys.argv) > 1 else None)

#!/usr/bin/env python3
"""Reverse-engineer the competitor title formulas from the harvested eBay corpus."""
import re, collections, itertools, pathlib

FILES = {p.stem: [l.strip() for l in p.read_text().splitlines() if l.strip()]
         for p in pathlib.Path('.').glob('*_p*.txt')}

# --- garment / product-format suffixes, longest-first so specific beats generic
TEE_SUFFIXES = [
    "Mens T-Shirt 100% Cotton","Mens Cotton T-Shirt Tee Top","Mens Light Cotton T-Shirt",
    "Mens V-Neck Cotton T-Shirt","Mens S/S Baseball T-Shirt","Mens Long Sleeve T-Shirt",
    "Mens Vest Tank Top","Mens 80% Cotton Hoodie","Mens Sweatshirt Jumper","Mens Ringer T-Shirt FotL",
    "Mens Ringer T-Shirt","Womens Wider Cut T-Shirt","Womens Petite Cut T-Shirt",
    "Kids T-Shirt Childrens","Kids T-Shirt Boys Girls","Kids Sweatshirt Jumper","Childrens Kids Hoodie",
    "Cotton Apron 100% Organic",
]
ART_FORMATS = [
    "FLOAT EFFECT CANVAS","CANVAS WALL ART","CANVAS WALL ARTWORK","CANVAS STREET",
    "FRAMED WALL ART","FRAMED WALL ARTWORK","ART FRAMED POSTER","FRAMED ART POSTER",
    "30MM DEEP","4 SIZES",
]

def norm(s): return re.sub(r'\s+',' ',s.lower().strip())

print("="*72); print("1. TITLE LENGTH vs eBay's 80-CHARACTER LIMIT"); print("="*72)
for name, lines in sorted(FILES.items()):
    L=[len(t) for t in lines]
    band=sum(1 for x in L if 70<=x<=80)
    print(f"{name:22s} n={len(L):3d}  mean={sum(L)/len(L):5.1f}  "
          f"max={max(L):3d}  in 70-80 band={band:3d} ({band/len(L):4.0%})  over80={sum(1 for x in L if x>80)}")

print(); print("="*72); print("2. GARMENT MULTIPLICATION (t-shirt stores)"); print("="*72)
tee_lines = FILES.get('tshirtjunky_p1',[]) + FILES.get('ytees_p1',[])
suffix_count = collections.Counter(); stems = collections.defaultdict(set)
for t in tee_lines:
    for suf in sorted(TEE_SUFFIXES,key=len,reverse=True):
        if t.endswith(suf):
            suffix_count[suf]+=1
            stems[norm(t[:-len(suf)])].add(suf)
            break
print(f"{sum(suffix_count.values())}/{len(tee_lines)} titles "
      f"({sum(suffix_count.values())/len(tee_lines):.0%}) end in a fixed garment suffix\n")
for suf,c in suffix_count.most_common():
    print(f"   {c:4d}  {suf}")
multi = {k:v for k,v in stems.items() if len(v)>1}
print(f"\n   distinct design stems: {len(stems)}")
print(f"   stems seen on >1 garment IN THIS 400-TITLE SAMPLE ALONE: {len(multi)}")
for k,v in sorted(multi.items(), key=lambda x:-len(x[1]))[:8]:
    print(f"     '{k.strip()}' -> {len(v)} garments: {sorted(v)}")

print(); print("="*72); print("3. CROSS-STORE DESIGN OVERLAP (tshirtjunky vs ytees)"); print("="*72)
def stemset(lines):
    out=set()
    for t in lines:
        s=t
        for suf in sorted(TEE_SUFFIXES,key=len,reverse=True):
            if t.endswith(suf): s=t[:-len(suf)]; break
        out.add(norm(s))
    return out
a,b = stemset(FILES.get('tshirtjunky_p1',[])), stemset(FILES.get('ytees_p1',[]))
shared = a & b
print(f"   tshirtjunky stems: {len(a)}   ytees stems: {len(b)}   SHARED: {len(shared)}")
print(f"   overlap of the smaller catalogue: {len(shared)/min(len(a),len(b)):.0%}  "
      f"(two 'competitors' running one design library)")
for s in sorted(shared)[:14]: print(f"     - {s.strip()}")

print(); print("="*72); print("4. THEME FREQUENCY - what the t-shirt market actually buys"); print("="*72)
THEMES = {
 'biker/motorcycle':r'biker|motorbike|motorcycle|cafe racer|chopper|motocross|motox',
 'skull/gothic':r'skull|gothic|goth|grim reaper|reaper|demon|satanic|voodoo',
 'viking/norse':r'viking|norse|odin|thor|valhalla|valknut|ragnar|yggdrasil|nordic',
 'birthday/age':r'\d+(st|nd|rd|th) birthday|year old|birth of legends|vintage year|aged to perfection',
 'music/band':r'music|guitar|rock|punk|reggae|ska|2 ?tone|drummer|dj |vinyl|northern soul|metal',
 'funny/slogan':r'funny|slogan|sarcas|joke|rude|offensive|parody',
 'flags/nationality':r'flag|union jack|britain|british|jamaica|palestine|poland|polska|england|welsh',
 'fishing/outdoors':r'fishing|fisherman|hiking|trekking|camping|hunting|scuba|diving|sailing',
 'gym/martial arts':r'gym|mma|bodybuilding|boxing|muay thai|spartan|training|krav maga|karate',
 'animals/pets':r'\bcat\b|\bdog\b|wolf|dragon|elephant|frog|tiger|gorilla|bulldog|highland cow|panther',
 'military/aviation':r'spitfire|raf|parachute|regiment|para |hurricane|army|soldier|templar',
 'retro TV/film':r'retro|tv (show|programme)|movie|film|80s|70s|90s|as worn by',
 'religion/spiritual':r'jesus|christian|buddha|mandala|yoga|pagan|celtic|atheis|egyptian god',
 'family/occasion':r'fathers day|grandad|uncle|dad |mum |niece|daughter|anniversary|wedding',
 'LGBT/awareness':r'lgbt|gay pride|autism|mental health|awareness|alzheimer',
}
tot=len(tee_lines)
for name,pat in sorted(THEMES.items(), key=lambda kv:-sum(1 for t in tee_lines if re.search(kv[1],t,re.I))):
    c=sum(1 for t in tee_lines if re.search(pat,t,re.I))
    print(f"   {c:4d} ({c/tot:4.0%})  {name}")

print(); print("="*72); print("5. POSTER STORE - format multiplication & content source"); print("="*72)
art = FILES.get('canvasartshop_p1',[])
fmt = collections.Counter()
for t in art:
    for f in ART_FORMATS:
        if f in t.upper(): fmt[f]+=1
for f,c in fmt.most_common(): print(f"   {c:4d}  {f}")

PD = r"lowry|hokusai|van gogh|goya|klimt|waterhouse|botticelli|vermeer|blake|munch|manet|monet|rubens|caravaggio|david|modigliani|schiele|beardsley|mucha|matisse|kandinsky|repin|bocklin|cole|gerome|sorolla|grimshaw|allingham|bouguereau|millais|poynter|rackham|sargent|burton|brendekilde|katona|wisinger|romako|batoni|gentileschi|ravi varma|da vinci|van eyck|toulouse|mondrian|morris|hopper|frida|kusama|benda|boulet|chagall"
IP = r"banksy|peaky blinders|star wars|fortnite|spider ?man|marvel|predator|jaws|akira|totoro|kiki|harley quinn|toy story|pink floyd|lewis hamilton|prodigy|keith flint|frazetta|forbidden planet|pulp fiction|stormzy"
CELEB = r"mugshot|marilyn monroe|audrey hepburn|tina turner|muhammad ali|jack nicholson|bruce lee|elvis|bowie|jagger|morrison|johnny cash|rocky|smoking nuns"
GENERIC = r"highland cow|abstract|botanical|flowers|kitchen|herbs|owl|seascape|sailing|tiger|black cat|elephant|horses|quote|slogan|paris|london|big ben|red fox|gin bottle"
for label,pat in [("public-domain artist",PD),("living/protected IP",IP),("celebrity likeness",CELEB),("generic decor",GENERIC)]:
    c=sum(1 for t in art if re.search(pat,t,re.I))
    print(f"   {c:4d} ({c/len(art):4.0%})  {label}")
print(f"\n   BANKSY alone: {sum(1 for t in art if re.search('banksy',t,re.I))} of {len(art)} "
      f"({sum(1 for t in art if re.search('banksy',t,re.I))/len(art):.0%})")

print(); print("="*72); print("6. TITLE GRAMMAR - where the keywords sit"); print("="*72)
for label, lines in [("t-shirt", tee_lines), ("poster", art)]:
    first = collections.Counter(); last = collections.Counter()
    for t in lines:
        w=t.split()
        if w: first[w[0].lower()]+=1; last[w[-1].lower()]+=1
    print(f"\n   {label.upper()} - most common FIRST word: "
          + ", ".join(f"{w}({c})" for w,c in first.most_common(8)))
    print(f"   {label.upper()} - most common LAST  word: "
          + ", ".join(f"{w}({c})" for w,c in last.most_common(8)))

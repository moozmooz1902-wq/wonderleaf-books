"""Build the mixed catalogue: illustrated tier + type tier, plus the exact
image prompts to run on a GPU.

House style, derived from measuring 140,085 of the seller's own designs and
from looking at their top sellers directly:
  black garment, 4-5 spot colours, artwork covering 10-25% of the chest.
Our own look: one condensed grotesk throughout (not their sans/serif mix),
bold flat vector illustration (not their mix of engraving, silhouette and
cartoon) so the store reads as one brand.
"""
import csv, json, re, sys
from collections import Counter
sys.path.insert(0, ".")
from subjects_bank import S

rows = json.load(open("all.json"))
existing = {re.sub(r"[^a-z0-9]+"," ",r["title"].lower()).strip() for r in rows}
abstract = json.load(open("subjects_abstract.json"))
mined    = json.load(open("subjects_final.json"))

STYLE = ("bold flat vector illustration, {desc}, thick confident linework, "
         "limited palette of four flat spot colours on black, high contrast, "
         "screen-print separation, strong silhouette readable at arm's length, "
         "centred composition, isolated on solid black, no text, no lettering, "
         "no watermark, no gradient mesh, t-shirt graphic")
NEG = ("text, letters, words, watermark, signature, photorealistic, 3d render, "
       "soft gradients, drop shadow, busy background, clutter, low contrast")

ILLUS = [  # templates that carry an illustration
 ("never_underestimate",23.53,"NEVER UNDERESTIMATE / AN {OLD} / WITH {ART} {OBJC}",
  "{S} T-Shirt Never Underestimate An {Old} With {art} {Obj} Mens Funny"),
 ("its_a_thing",27.50,"IT'S A {SC} THING / ...YOU WOULDN'T UNDERSTAND",
  "It's A {S} Thing You Wouldn't Understand T-Shirt Mens Funny {KW}"),
 ("problem_solved",15.12,"PROBLEM / SOLVED",
  "{S} T-Shirt Problem Solved Mens Funny {KW}"),
 ("object_mosaic",22.80,"(image only, no text)",
  "{S} T-Shirt {ICON} Made Of {S} Mens Funny {KW}"),
 ("warning_talking",4.06,"WARNING / MAY SPONTANEOUSLY START TALKING ABOUT / {SC}",
  "{S} T-Shirt Warning May Start Talking About Mens Funny {KW}"),
 ("evolution",1.69,"(image only, no text)",
  "{S} T-Shirt Evolution Mens Funny {KW}"),
 ("vintage_illus",61.58,"VINTAGE {Y} / {SC} / PREMIUM QUALITY",
  "{S} T-Shirt Vintage {Y} Premium Quality {A}th Birthday Mens {KW}"),
 ("legend_illus",44.08,"{SC} LEGEND / SINCE {Y} / PREMIUM QUALITY",
  "{S} T-Shirt {A}th Birthday Legend Since {Y} Mens {KW}"),
]
TYPE = [   # pure type, no artwork needed - renders free
 ("vintage_year",61.58,"VINTAGE {Y} / {SC} / PREMIUM QUALITY",
  "{S} T-Shirt Vintage {Y} Premium Quality {A}th Birthday Mens Funny"),
 ("legend_since",44.08,"{SC} LEGEND / SINCE {Y} / PREMIUM QUALITY",
  "{S} T-Shirt {A}th Birthday Legend Since {Y} Mens Funny"),
]

ICONS = ["Skull","Heart","Union Jack","Map Of Britain","Anchor","Tree"]
SCENES = ["At Sunset","In A Storm","On A Mountain","By The Coast","In The Fog","At Dawn"]
OLD = [("OLD MAN","Old Man"),("OLD WOMAN","Old Woman")]
YEARS = list(range(1946, 2009)); NOW = 2026
def art(w): return "AN" if w.strip()[0].lower() in "aeiou" else "A"


def main():
    designs=[]; prompts={}; seen=set()

    def add(score,tpl,subj,variant,scene,text,title,illus_id):
        t=re.sub(r"\s{2,}"," ",title).strip()
        if len(t)>80: t=t[:80].rsplit(" ",1)[0]
        if t.lower() in seen: return
        seen.add(t.lower())
        norm=re.sub(r"[^a-z0-9]+"," ",t.lower()).strip()
        designs.append([f"{score:.2f}",tpl,subj,variant,scene,text,t,
                        "T-Shirt","Black",illus_id,
                        "no" if norm in existing else "yes"])

    # ---- illustrated tier
    for subj,desc,short,kw,w in S:
        a=art(short)
        base=dict(S=subj,SC=subj.upper(),Obj=short.title(),OBJC=short,
                  KW=kw,ART=a,art=a.lower())
        for key,upd,text,title in ILLUS:
            if key=="never_underestimate": variants=OLD
            elif key=="object_mosaic": variants=[(i,i) for i in ICONS]
            elif key in ("vintage_illus","legend_illus"): variants=[(str(y),NOW-y) for y in YEARS]
            else: variants=[("","")]
            for v1,v2 in variants:
                r=dict(base, OLD=v1 if key=="never_underestimate" else "OLD MAN",
                       Old=v2 if key=="never_underestimate" else "Old Man",
                       ICON=v1 if key=="object_mosaic" else "Skull",
                       Y=v1 if key in ("vintage_illus","legend_illus") else "1980",
                       A=str(v2) if key in ("vintage_illus","legend_illus") else "40")
                def f(x):
                    for k2,val in r.items(): x=x.replace("{%s}"%k2,str(val))
                    return x
                # one illustration per (subject, template family) - reused across variants
                fam = "mosaic" if key=="object_mosaic" else \
                      "evolution" if key=="evolution" else \
                      "insider" if key=="its_a_thing" else "hero"
                iid=f"{subj.lower().replace(' ','_')}__{fam}"
                if iid not in prompts:
                    d=desc
                    if fam=="mosaic": d=f"many small {short.lower()} silhouettes massed to form a large skull"
                    if fam=="evolution": d=f"four-stage silhouette progression from child to adult ending with {desc}"
                    if fam=="insider": d=f"a clean technical diagram only a {subj.lower()} enthusiast would recognise"
                    prompts[iid]=dict(id=iid,subject=subj,family=fam,
                                      prompt=STYLE.format(desc=d),negative=NEG)
                add(upd*w/2.5,key,subj,str(v2 or "-"),"",f(text),f(title),iid)
                if w>=2.0 and key in ("never_underestimate","object_mosaic"):
                    for sc in SCENES:
                        sid=f"{iid}__{sc.lower().replace(' ','_').replace('__','_')}"
                        if sid not in prompts:
                            prompts[sid]=dict(id=sid,subject=subj,family=fam+"_scene",
                                prompt=STYLE.format(desc=f"{desc}, {sc.lower()}"),negative=NEG)
                        add(upd*w/2.5,key,subj,str(v2 or "-"),sc,f(text),
                            f"{subj} T-Shirt {sc} {f(title)}",sid)

    # ---- type tier (no artwork)
    for s in mined+abstract:
        sub=s["subject"].title(); w=min(s["upd"],4)
        for key,upd,text,title in TYPE:
            for y in YEARS:
                r=dict(S=sub,SC=sub.upper(),Y=str(y),A=str(NOW-y))
                def f(x):
                    for k2,val in r.items(): x=x.replace("{%s}"%k2,str(val))
                    return x
                add(upd*w/2.5,key,sub,str(NOW-y),"",f(text),f(title),"")

    designs.sort(key=lambda r:-float(r[0]))
    with open("CATALOGUE_MIXED.csv","w",encoding="utf-8",newline="") as fh:
        w2=csv.writer(fh)
        w2.writerow(("priority","template_id","subject","variant","scene","shirt_text",
                     "ebay_title","garment","colour","illustration_id","novel"))
        w2.writerows(designs)
    with open("ILLUSTRATIONS.csv","w",encoding="utf-8",newline="") as fh:
        w2=csv.writer(fh)
        w2.writerow(("illustration_id","subject","family","prompt","negative_prompt"))
        for p in prompts.values():
            w2.writerow((p["id"],p["subject"],p["family"],p["prompt"],p["negative"]))

    ill=sum(1 for d in designs if d[9])
    print(f"designs total          : {len(designs):,}")
    print(f"  illustrated          : {ill:,}  ({100*ill/len(designs):.1f}%)")
    print(f"  pure type            : {len(designs)-ill:,}")
    print(f"\nILLUSTRATIONS TO GENERATE: {len(prompts):,}")
    print(f"  reuse: {ill/max(len(prompts),1):.0f} designs per illustration")
    for fam,n in Counter(p['family'] for p in prompts.values()).most_common():
        print(f"    {fam:<18}{n:>5}")


main()

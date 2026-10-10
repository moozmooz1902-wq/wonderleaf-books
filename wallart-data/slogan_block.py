import csv, re
csv.field_size_limit(10**9)
P='/tmp/claude-0/-home-user-wonderleaf-books/af9e3fdd-8129-53fc-a69c-916ae3713d2b/scratchpad/ebay/RELIST_old_wall_art_FINAL.csv'
f=open(P,newline='',encoding='utf-8-sig',errors='replace')
for _ in range(3): f.readline()
r=csv.reader(f); hdr=[h.strip() for h in next(r)]; ix={h:i for i,h in enumerate(hdr)}
B='Framed Wall Art Poster Canvas Print Picture'
rows=[]
for row in r:
    t=row[ix['Title']].strip() if ix['Title']<len(row) else ''
    if not t: continue
    s=t.replace(B,'').replace('Framed Art Print','').strip().lower()
    w=row[ix['Watchers']].strip() if ix['Watchers']<len(row) else ''
    try: wn=int(w) if w else 0
    except ValueError: wn=0
    rows.append((wn,s))
n=len(rows); base=sum(1 for w,_ in rows if w>0)/n
PAT=[r"\bkeep calm\b", r"\bjust a (girl|boy|man|woman|mum|dad)\b",
     r"\bi (love|hate|am|do|just|really)\b", r"\bnever (trust|dreamt|underestimate)\b",
     r"\bfunny\b", r"\bsarcas", r"\bjoke\b", r"\bworld.?s best\b",
     r"\bdefinition meaning\b", r"\bbecause\b", r"\bdon.?t\b",
     r"\bmy (wife|husband|cat|dog)\b", r"\bretired\b", r"\bsorry\b", r"\byou\b"]
rx=re.compile("|".join(PAT))
slog=[(w,s) for w,s in rows if rx.search(s)]
oth=[(w,s) for w,s in rows if not rx.search(s)]
sw=sum(1 for w,_ in slog if w>0); ow=sum(1 for w,_ in oth if w>0)
print(f"{n:,} listings, base {base*100:.2f}%")
print(f"slogan-pattern : {len(slog):>7,} ({len(slog)/n*100:4.1f}%)  watched {sw:>4}  rate {sw/len(slog)*100:.2f}%")
print(f"everything else: {len(oth):>7,} ({len(oth)/n*100:4.1f}%)  watched {ow:>4}  rate {ow/len(oth)*100:.2f}%")
exp=len(slog)*base
print(f"slogan z = {(sw-exp)/exp**0.5:+.1f}")
print(f"rest-only base would be {ow/len(oth)*100:.2f}% ({ow/len(oth)/base:.2f}x current)")

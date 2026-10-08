#!/usr/bin/env python3
"""How much of this catalogue is place-based, and which UK places are missing."""
import collections, re, json, sys
BASE = ("/tmp/claude-0/-home-user-wonderleaf-books/"
        "af9e3fdd-8129-53fc-a69c-916ae3713d2b/scratchpad/an/")

rows = []
with open(BASE + "titles.tsv", encoding="utf-8") as f:
    next(f)
    for line in f:
        p = line.rstrip("\n").split("\t")
        if len(p) >= 3:
            rows.append((p[0], p[2]))
print(f"titles {len(rows):,}")

PLACE_WORDS = ("map", "maps", "skyline", "city", "cityscape", "flag", "street",
               "streets", "metro", "subway", "underground", "coast", "harbour",
               "harbor", "bay", "island", "county", "state", "nation", "town")
place_hits = collections.Counter()
for st, t in rows:
    lw = t.lower()
    for w in PLACE_WORDS:
        if re.search(rf"\b{w}\b", lw):
            place_hits[w] += 1
print("\nplace-type words in titles:")
for w, n in place_hits.most_common():
    print(f"   {n:>8,}  {100*n/len(rows):5.2f}%  {w}")

# 76 UK cities (ONS/official), the 48 English ceremonial counties and the
# best-known UK towns - do they appear?
UK_CITIES = """London Birmingham Leeds Glasgow Sheffield Bradford Liverpool Edinburgh Manchester
Bristol Wakefield Cardiff Coventry Nottingham Leicester Sunderland Belfast Newcastle Brighton Hull
Plymouth Stoke Wolverhampton Derby Swansea Southampton Salford Aberdeen Westminster Portsmouth York
Peterborough Dundee Lancaster Oxford Newport Preston StAlbans Norwich Chester Cambridge Salisbury
Exeter Gloucester Lisburn Chichester Winchester Londonderry Carlisle Worcester Bath Durham Lincoln
Hereford Armagh Inverness Stirling Canterbury Lichfield Newry Ripon Bangor Truro Ely Wells
Perth Dunfermline Doncaster Colchester Milton Southend Wrexham Dunstable Kirkwall Elgin""".split()
UK_COUNTIES = """Bedfordshire Berkshire Bristol Buckinghamshire Cambridgeshire Cheshire Cornwall Cumbria
Derbyshire Devon Dorset Durham Essex Gloucestershire Hampshire Herefordshire Hertfordshire Kent
Lancashire Leicestershire Lincolnshire Merseyside Norfolk Northamptonshire Northumberland
Nottinghamshire Oxfordshire Rutland Shropshire Somerset Staffordshire Suffolk Surrey Sussex
Warwickshire Wiltshire Worcestershire Yorkshire""".split()
UK_OTHER = """Cotswolds Snowdonia Dartmoor Exmoor Cairngorms Pembrokeshire Northumbria Lakeland
Windermere Keswick Ambleside Whitby Scarborough Harrogate Ilkley Skipton Richmond Alnwick Bamburgh
Lindisfarne Durdle Lulworth StIves Padstow Fowey Polperro Mousehole Looe Newquay Tintagel
Clovelly Lynmouth Minehead Weymouth Swanage Poole Bournemouth Lymington Beaulieu Rye Hastings
Eastbourne Seaford Lewes Arundel Bosham Emsworth Cowes Yarmouth Shanklin Ventnor Tenby Aberystwyth
Portmeirion Conwy Caernarfon Llandudno Betws Beddgelert Hay Brecon Gower Mumbles Oban Mallaig
Skye Mull Iona Islay Jura Arran Harris Lewis Orkney Shetland Ullapool Plockton Applecross
Pitlochry Aviemore Braemar Ballater Crathie Melrose Peebles Moffat Portpatrick Bute""".split()

idx = collections.Counter()
for st, t in rows:
    for w in re.findall(r"[A-Za-z][A-Za-z'-]+", t):
        idx[w.lower()] += 1

def report(name, names):
    present = [(n, idx[n.lower()]) for n in names if idx.get(n.lower(), 0) >= 3]
    missing = [n for n in names if idx.get(n.lower(), 0) < 3]
    print(f"\n### {name}: {len(present)} present, {len(missing)} missing/thin")
    print("   best covered:", ", ".join(f"{n}({c:,})" for n, c in
                                        sorted(present, key=lambda x: -x[1])[:18]))
    print("   MISSING OR THIN:", ", ".join(missing[:60]))
    return present, missing

res = {}
for nm, lst in (("UK cities", UK_CITIES), ("UK counties", UK_COUNTIES),
                ("UK towns, coast and country", UK_OTHER)):
    p, m = report(nm, lst)
    res[nm] = {"present": p, "missing": m}

# which world places DO dominate, for contrast
WORLD = """Paris Rome London NewYork Tokyo Berlin Barcelona Amsterdam Prague Vienna Lisbon Madrid
Venice Florence Milan Dublin Copenhagen Stockholm Oslo Helsinki Reykjavik Moscow Istanbul Cairo
Dubai Sydney Melbourne Toronto Vancouver Montreal Chicago Boston Seattle Miami LosAngeles
SanFrancisco Austin Denver Nashville Detroit Philadelphia Houston Dallas Atlanta Phoenix Portland
Shanghai Beijing Seoul Singapore Bangkok Mumbai Delhi Capetown Rio Buenos Lima Santiago""".split()
p, m = report("World cities", WORLD)
res["World cities"] = {"present": p, "missing": m}
json.dump(res, open(BASE + "places.json", "w"), indent=1)

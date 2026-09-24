"""Generate a large design catalogue from templates mined out of real sales data.

Briefs live in TEMPLATES.csv (one row per template). The batch references them
by template_id so the file stays workable instead of repeating a 600-character
brief 300,000 times.
"""
import csv, json, re, itertools

rows = json.load(open("all.json"))
existing = {re.sub(r"[^a-z0-9]+", " ", r["title"].lower()).strip() for r in rows}

# ---- templates: measured units/design from the catalogue --------------------
T = [
 ("legend_since", 44.08, "{SUBJ_CAPS} LEGEND / SINCE {YEAR} / PREMIUM QUALITY",
  "{SUBJ} T-Shirt {AGE}th Birthday Legend Since {YEAR} Mens {KW}",
  "Black tee. Distressed white and gold print with a circular badge. {SUBJ_CAPS} LEGEND "
  "arched over the top of the badge, SINCE {YEAR} in the largest weight at the centre, "
  "PREMIUM QUALITY on a small ribbon banner beneath. Heavy worn texture, gold accent rule."),
 ("vintage_year", 61.58, "VINTAGE {YEAR} / {SUBJ_CAPS} / PREMIUM QUALITY",
  "{SUBJ} T-Shirt Vintage {YEAR} Premium Quality {AGE}th Birthday Mens {KW}",
  "Black tee, distressed cream print. VINTAGE {YEAR} in a heavy retro slab serif with a "
  "faded sunburst behind it, {SUBJ_CAPS} beneath in condensed caps, PREMIUM QUALITY on a "
  "thin banner. Seventies record-sleeve feel."),
 ("never_underestimate", 23.53, "NEVER UNDERESTIMATE / AN {OLD} / WITH {ART} {OBJ_CAPS}",
  "{SUBJ} T-Shirt Never Underestimate An {Old} With {art} {Obj} Mens Funny",
  "Single-colour print, chest centred. (1) NEVER UNDERESTIMATE over two lines in heavy "
  "condensed sans caps, the widest element. (2) AN {OLD} in a lighter SERIF, letter-spaced, "
  "smaller - the sans/serif alternation is the signature, never one face throughout. "
  "(3) Single-colour illustration of {OBJ} in strict side profile. (4) WITH {ART} small "
  "serif caps. (5) {OBJ_CAPS} largest single word, heavy display face. One ink, maximum "
  "contrast: white on black or dark, black on olive or light."),
 ("problem_solved", 15.12, "PROBLEM / SOLVED",
  "{SUBJ} T-Shirt Problem Solved Mens Funny {KW}",
  "Black tee. Two white rounded-square outline panels. LEFT: pictogram man frowning beside "
  "an angry pictogram woman. RIGHT: the same man smiling beside a white silhouette of {OBJ}. "
  "PROBLEM under the left panel, SOLVED under the right, bold condensed caps. White only."),
 ("weekend_forecast", 5.55, "WEEKEND FORECAST / {SUBJ_CAPS} / WITH A CHANCE OF / DRINKING",
  "Weekend Forecast {SUBJ} Drinking - Mens Funny T-Shirt {KW}",
  "Natural/cream tee. WEEKEND FORECAST arched in heavy black caps. Centre: colourful "
  "hand-drawn cartoon of {OBJ}. Below, {SUBJ_CAPS} in heavy black caps, WITH A CHANCE OF "
  "reversed out of a solid red bar, DRINKING with two letters replaced by pint glasses."),
 ("warning_talking", 4.06, "WARNING / MAY START TALKING ABOUT / {SUBJ_CAPS}",
  "{SUBJ} T-Shirt Warning May Start Talking About Mens Funny {KW}",
  "Black tee. Yellow triangular hazard sign containing a black silhouette of {OBJ}. WARNING "
  "in heavy yellow caps, MAY START TALKING ABOUT smaller in white, {SUBJ_CAPS} largest in white."),
 ("evolution", 1.69, "THE EVOLUTION OF / {SUBJ_CAPS}",
  "{SUBJ} T-Shirt Evolution Mens Funny {KW}",
  "Black tee, white silhouettes. Four-stage evolution march left to right, ape to upright "
  "human, the final figure using {OBJ}. THE EVOLUTION OF {SUBJ_CAPS} beneath in condensed caps."),
 ("relation_best", 25.61, "BEST {REL_CAPS} / IN THE WORLD / {SUBJ_CAPS}",
  "{SUBJ} T-Shirt Best {Rel} Mens Funny Fathers Day {KW}",
  "Black tee, white print. BEST {REL_CAPS} small at top, IN THE WORLD large in heavy "
  "condensed caps, white line illustration of {OBJ} beneath, {SUBJ_CAPS} on a rule at the base."),
]

# ---- subject bank -----------------------------------------------------------
SUB = [
 ("Biker","a chopper motorcycle in side profile","MOTORBIKE","Motorcycle Chopper Cafe Racer Rider",4.00),
 ("Motorcycle","a sports motorcycle","MOTORCYCLE","Motorbike Superbike Moto GP Rider",4.36),
 ("Cafe Racer","a cafe racer motorcycle","CAFE RACER","Biker Motorbike Motorcycle Retro",4.00),
 ("Skull","a detailed human skull","SKULL","Gothic Tattoo Biker Death Metal",1.84),
 ("Guitar","an electric guitar","GUITAR","Guitarist Electric Acoustic Bass Strings",2.30),
 ("Drumming","a full drum kit","DRUM KIT","Drummer Drums Sticks Band Rock",2.00),
 ("Fishing","a fishing rod with a hooked carp","FISHING ROD","Angler Carp Fisherman Tackle",1.50),
 ("Cycling","a road bicycle","BICYCLE","Cyclist Mountain Bike MTB Road Racer",1.40),
 ("Farming","a tractor in side profile","TRACTOR","Farmer Tractor Farm Agriculture",2.10),
 ("Trucker","an articulated lorry","LORRY","Lorry Driver Truck HGV Trucking",1.64),
 ("Gym","a loaded barbell","BARBELL","Weightlifting Training Fitness Lifter",2.55),
 ("Boxing","a pair of hanging boxing gloves","PAIR OF BOXING GLOVES","Boxer Ring Sparring MMA",1.30),
 ("Darts","a dartboard with three darts","SET OF DARTS","Player Oche Arrows Pub League",1.20),
 ("Golf","a golf club and ball","SET OF GOLF CLUBS","Golfer Clubs Putter Course",1.20),
 ("Rugby","a rugby ball","RUGBY BALL","Rugby Union League Scrum Forward",1.20),
 ("Scuba Diving","a diving mask and regulator","SET OF DIVE GEAR","Diver Dive Flippers Ocean",1.40),
 ("Camper Van","a classic camper van","CAMPER VAN","Campervan Van Life Camping Road Trip",1.30),
 ("Metal Detecting","a metal detector","METAL DETECTOR","Detectorist Treasure Finds Hobby",1.00),
 ("Photography","a DSLR camera with a long lens","CAMERA","Photographer Lens Shutter",1.20),
 ("Welding","a welding mask with sparks","WELDING TORCH","Welder Fabricator MIG TIG",1.10),
 ("Woodworking","a hand plane and chisel","CHISEL","Carpenter Joiner Woodwork Workshop",1.10),
 ("Gardening","a spade and watering can","GARDEN SPADE","Gardener Allotment Veg Plot",1.00),
 ("Barbecue","a kettle barbecue with flames","BARBECUE","BBQ Grill Smoker Griller Meat",1.00),
 ("Running","a pair of running shoes","PAIR OF RUNNING SHOES","Runner Marathon 10k Jogging",1.20),
 ("Sailing","a yacht heeling over","SAILING BOAT","Sailor Yacht Boat Crew Regatta",1.00),
 ("Horse Riding","a horse's head with a bridle","HORSE","Equestrian Rider Pony Stables",1.10),
 ("Snooker","a snooker cue and black ball","SNOOKER CUE","Pool Cue Billiards Break",1.00),
 ("Model Railway","a steam locomotive","MODEL RAILWAY","Trains Railway Modeller OO Gauge",0.90),
 ("Bird Watching","binoculars and a bird","PAIR OF BINOCULARS","Birder Twitcher Birding RSPB",0.90),
 ("Bee Keeping","a beehive with bees","BEEHIVE","Beekeeper Apiary Bees Honey",0.90),
 ("Kayaking","a kayak and paddle","KAYAK","Canoe Paddle River Watersport",0.90),
 ("Climbing","a carabiner and rope","CLIMBING ROPE","Climber Bouldering Crag Belay",0.90),
 ("Narrowboat","a narrowboat on a canal","NARROWBOAT","Canal Boat Barge Waterways Locks",0.90),
 ("Surfing","a surfboard and wave","SURFBOARD","Surfer Surf Board Waves Beach",1.00),
 ("Skiing","crossed skis and poles","PAIR OF SKIS","Skier Snow Slopes Alpine Winter",1.00),
 ("Chess","a knight chess piece","CHESS BOARD","Chess Player Grandmaster Pieces",0.90),
 ("Baking","a stand mixer and rolling pin","ROLLING PIN","Baker Cake Bake Pastry Kitchen",0.90),
 ("Home Brewing","a pint glass and hops","HOME BREW KIT","Homebrew Beer Ale CAMRA Real Ale",1.00),
 ("Drone Flying","a quadcopter drone","DRONE","Drone Pilot FPV Quadcopter",0.90),
 ("Off Roading","a 4x4 on rough ground","4X4","Off Road 4x4 Land Rover Green Laning",2.00),
 ("Karting","a go-kart","GO KART","Karting Race Track Circuit Racer",1.00),
 ("Motocross","a motocross bike mid-jump","MOTOCROSS BIKE","MX Enduro Dirt Bike Scrambler",1.60),
 ("Caravanning","a touring caravan","CARAVAN","Caravan Club Touring Camping Site",1.30),
 ("Allotment","a wheelbarrow and vegetables","ALLOTMENT","Grow Your Own Veg Plot Gardener",0.90),
 ("Archery","a bow and arrow","BOW AND ARROW","Archer Archery Target Field",1.20),
 ("Shooting","a clay pigeon and shotgun","SHOTGUN","Clay Pigeon Shooting Field Sport",1.10),
 ("Rowing","a rowing scull and oars","ROWING BOAT","Rower Rowing Crew Regatta Oars",0.90),
 ("Swimming","a pair of goggles","PAIR OF GOGGLES","Swimmer Swim Pool Lengths Front Crawl",0.90),
 ("Football","a football","FOOTBALL","Footballer Soccer Sunday League Striker",0.74),
 ("Cricket","a cricket bat and ball","CRICKET BAT","Cricketer Batsman Bowler Wicket",0.90),
]

REL = [("DAD","Dad"),("GRANDAD","Grandad"),("UNCLE","Uncle"),("MUM","Mum"),
       ("NANNY","Nanny"),("SON","Son"),("BROTHER","Brother"),("HUSBAND","Husband")]
OLD = [("OLD MAN","Old Man"),("OLD WOMAN","Old Woman")]
AGES = [18,21,30,40,50,60,70,80]
THIS_YEAR = 2026


def art(w): return "AN" if w.strip()[0].lower() in "aeiou" else "A"


def variants(key):
    if key in ("legend_since","vintage_year"):
        return [(str(THIS_YEAR-a), a) for a in AGES for _ in (0,)] + \
               [(str(y), THIS_YEAR-y) for y in range(1945, 2009) if (THIS_YEAR-y) not in AGES]
    if key == "never_underestimate": return OLD
    if key == "relation_best": return REL
    return [("","")]


def main(target=300_000):
    tpl_rows=[("template_id","measured_units_per_design","shirt_text_pattern",
               "title_pattern","design_brief")]
    for key,upd,text,title,brief in T:
        tpl_rows.append((key,f"{upd:.2f}",text,title,brief))
    with open("TEMPLATES.csv","w",encoding="utf-8",newline="") as fh:
        csv.writer(fh).writerows(tpl_rows)

    out=[("score","template_id","subject","variant","shirt_text","ebay_title",
          "garment","colour","novel")]
    seen=set()
    for key,upd,text,title,brief in sorted(T,key=lambda x:-x[1]):
        for subj,obj,short,kw,w in SUB:
            for v1,v2 in variants(key):
                a=art(short)
                rep={"{SUBJ}":subj,"{SUBJ_CAPS}":subj.upper(),"{OBJ}":obj,
                     "{OBJ_CAPS}":short,"{Obj}":short.title(),"{KW}":kw,
                     "{ART}":a,"{art}":a.lower(),
                     "{OLD}":v1 if key=="never_underestimate" else "OLD MAN",
                     "{Old}":v2 if key=="never_underestimate" else "Old Man",
                     "{REL_CAPS}":v1 if key=="relation_best" else "DAD",
                     "{Rel}":v2 if key=="relation_best" else "Dad",
                     "{YEAR}":v1 if key in ("legend_since","vintage_year") else "1980",
                     "{AGE}":str(v2) if key in ("legend_since","vintage_year") else "40"}
                def f(s):
                    for k,val in rep.items(): s=s.replace(k,str(val))
                    return s
                t=re.sub(r"\s{2,}"," ",f(title)).strip()
                if len(t)>80: t=t[:80].rsplit(" ",1)[0]
                k2=t.lower()
                if k2 in seen: continue
                seen.add(k2)
                norm=re.sub(r"[^a-z0-9]+"," ",t.lower()).strip()
                colour=("Natural/Cream" if key=="weekend_forecast"
                        else "Black or Olive" if key=="never_underestimate" else "Black")
                out.append((f"{upd*w/2.5:.1f}",key,subj,str(v2 or "-"),f(text),t,
                            "T-Shirt",colour,"no" if norm in existing else "yes"))
                if len(out)>target: break
    body=sorted(out[1:], key=lambda r:-float(r[0]))
    with open("CATALOGUE_300K.csv","w",encoding="utf-8",newline="") as fh:
        w=csv.writer(fh); w.writerow(out[0]); w.writerows(body)
    from collections import Counter
    print(f"generated {len(body):,} unique designs")
    print(f"novel (not in your catalogue): {sum(1 for r in body if r[8]=='yes'):,}")
    for k,n in Counter(r[1] for r in body).most_common():
        print(f"   {k:<22}{n:>8,}")


main()

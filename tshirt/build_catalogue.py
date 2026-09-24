"""Generate the full design catalogue. Black t-shirts only.

Every design is included - prioritised by measured performance, never filtered
out. Hot themes additionally get scene variations.

Templates carry measured units/design from the seller's own 167,695-design
history. Two were added from direct visual inspection of top sellers:
  - its_a_thing   : the insider-knowledge graphic (HGV gearbox shift pattern)
  - object_mosaic : many small objects composing a larger icon (bikes -> skull)
"""
import csv, json, re
from collections import Counter

rows = json.load(open("all.json"))
existing = {re.sub(r"[^a-z0-9]+"," ",r["title"].lower()).strip() for r in rows}
GARMENT, COLOUR = "T-Shirt", "Black"          # black tees only, per store limit

TEMPLATES = [
 ("vintage_year", 61.58, "VINTAGE {YEAR} / {SUBJ_CAPS} / PREMIUM QUALITY",
  "{SUBJ} T-Shirt Vintage {YEAR} Premium Quality {AGE}th Birthday Mens {KW}",
  "Black tee, distressed cream print. VINTAGE {YEAR} in heavy retro slab serif over a faded "
  "sunburst, {SUBJ_CAPS} beneath in condensed caps, PREMIUM QUALITY on a thin banner."),
 ("legend_since", 44.08, "{SUBJ_CAPS} LEGEND / SINCE {YEAR} / PREMIUM QUALITY",
  "{SUBJ} T-Shirt {AGE}th Birthday Legend Since {YEAR} Mens {KW}",
  "Black tee, distressed white and gold circular badge. {SUBJ_CAPS} LEGEND arched over the top, "
  "SINCE {YEAR} largest at centre, PREMIUM QUALITY on a ribbon banner. Worn texture, gold rule."),
 ("its_a_thing", 27.50, "IT'S A {SUBJ_CAPS} THING / ... YOU WOULDN'T UNDERSTAND",
  "It's A {SUBJ} Thing You Wouldn't Understand T-Shirt Mens Funny {KW}",
  "Black tee, white print. TOP: a piece of INSIDER KNOWLEDGE only this audience recognises, "
  "drawn as a clean technical diagram - not a generic silhouette. For {SUBJ} use {INSIDER}. "
  "Beneath, IT'S A {SUBJ_CAPS} THING... YOU WOULDN'T UNDERSTAND over three lines in bold "
  "condensed caps, left aligned. The graphic must reward recognition, not decorate."),
 ("never_underestimate", 23.53, "NEVER UNDERESTIMATE / AN {OLD} / WITH {ART} {OBJ_CAPS}",
  "{SUBJ} T-Shirt Never Underestimate An {Old} With {art} {Obj} Mens Funny",
  "Black tee, white print, chest centred. (1) NEVER UNDERESTIMATE over two lines, heavy "
  "condensed sans caps, widest element. (2) AN {OLD} in a lighter SERIF, letter-spaced, smaller "
  "- the sans/serif alternation is the signature, never one face throughout. (3) White "
  "illustration of {OBJ} in strict side profile. (4) WITH {ART} small serif caps. "
  "(5) {OBJ_CAPS} largest single word, heavy display face."),
 ("object_mosaic", 22.80, "(no text - image only)",
  "{SUBJ} T-Shirt {MOSAIC_ICON} Made Of {SUBJ} Mens Funny {KW}",
  "Black tee, single-colour white print, no text at all. Dozens of small {OBJ} silhouettes at "
  "varying scales, tessellated so their massed outline forms a large {MOSAIC_ICON}. Densest at "
  "the centre, sparser at the edges so the icon's silhouette reads instantly from across a room. "
  "One or two objects at full size near the middle as focal points."),
 ("problem_solved", 15.12, "PROBLEM / SOLVED",
  "{SUBJ} T-Shirt Problem Solved Mens Funny {KW}",
  "Black tee. Two white rounded-square outline panels. LEFT: pictogram man frowning beside an "
  "angry pictogram woman. RIGHT: same man smiling beside a white silhouette of {OBJ}. PROBLEM "
  "under the left panel, SOLVED under the right, bold condensed caps. White only."),
 ("warning_talking", 4.06, "WARNING / MAY SPONTANEOUSLY START TALKING ABOUT / {SUBJ_CAPS}",
  "{SUBJ} T-Shirt Warning May Spontaneously Start Talking About Mens Funny {KW}",
  "Black tee. Top third: a full-colour cartoon character engaged in {SUBJ}, holding a pint. "
  "Beneath, WARNING reversed out of a red rounded rectangle with a white keyline, then MAY "
  "SPONTANEOUSLY START TALKING ABOUT in small white caps, then {SUBJ_CAPS} largest in white."),
 ("evolution", 1.69, "THE EVOLUTION OF / {SUBJ_CAPS}",
  "{SUBJ} T-Shirt Evolution Mens Funny {KW}",
  "Black tee, white silhouettes. Four-stage evolution march left to right, ape to upright human, "
  "final figure using {OBJ}. THE EVOLUTION OF {SUBJ_CAPS} beneath in condensed caps."),
]

# subject, illustration object, short noun, keywords, measured theme weight, insider detail
SUB = [
 ("Biker","a chopper motorcycle in side profile","MOTORBIKE","Motorcycle Chopper Cafe Racer",4.00,"a carburettor exploded-view diagram"),
 ("Motorcycle","a sports motorcycle","MOTORCYCLE","Motorbike Superbike Moto GP Rider",4.36,"a six-speed sequential gearshift pattern"),
 ("Motocross","a motocross bike mid-jump","MOTOCROSS BIKE","MX Enduro Dirt Bike Scrambler",1.60,"a rutted berm cornering line diagram"),
 ("Off Roading","a 4x4 on rough ground","4X4","Off Road 4x4 Land Rover Green Laning",2.00,"a transfer-box high/low ratio diagram"),
 ("Trucker","an articulated lorry","LORRY","Lorry Driver Truck HGV Trucking",1.64,"an HGV splitter gearbox shift pattern"),
 ("Farming","a tractor in side profile","TRACTOR","Farmer Tractor Farm Agriculture",2.10,"a three-point linkage diagram"),
 ("Gym","a loaded barbell","BARBELL","Weightlifting Training Fitness Lifter",2.55,"a plate-loading maths chart"),
 ("Guitar","an electric guitar","GUITAR","Guitarist Electric Acoustic Bass Strings",2.30,"a barre chord fingering chart"),
 ("Drumming","a full drum kit","DRUM KIT","Drummer Drums Sticks Band Rock",2.00,"a paradiddle rudiment notation"),
 ("Skull","a detailed human skull","SKULL","Gothic Tattoo Biker Death Metal",1.84,"an anatomical skull cross-section"),
 ("Fishing","a fishing rod with a hooked carp","FISHING ROD","Angler Carp Fisherman Tackle",1.50,"a hair-rig knot tying diagram"),
 ("Cycling","a road bicycle","BICYCLE","Cyclist Mountain Bike MTB Road Racer",1.40,"a derailleur gear-ratio chart"),
 ("Scuba Diving","a diving mask and regulator","SET OF DIVE GEAR","Diver Dive Flippers Ocean",1.40,"a no-decompression limit table"),
 ("Boxing","a pair of hanging boxing gloves","PAIR OF BOXING GLOVES","Boxer Ring Sparring MMA",1.30,"a hand-wrapping sequence diagram"),
 ("Camper Van","a classic camper van","CAMPER VAN","Campervan Van Life Camping Road Trip",1.30,"a 12v leisure battery wiring schematic"),
 ("Caravanning","a touring caravan","CARAVAN","Caravan Club Touring Camping Site",1.30,"a noseweight and towing load diagram"),
 ("Darts","a dartboard with three darts","SET OF DARTS","Player Oche Arrows Pub League",1.20,"a checkout finishing chart"),
 ("Golf","a golf club and ball","SET OF GOLF CLUBS","Golfer Clubs Putter Course",1.20,"a stableford scoring table"),
 ("Rugby","a rugby ball","RUGBY BALL","Rugby Union League Scrum Forward",1.20,"a scrum formation diagram"),
 ("Archery","a bow and arrow","BOW AND ARROW","Archer Archery Target Field",1.20,"a sight-marks distance table"),
 ("Running","a pair of running shoes","PAIR OF RUNNING SHOES","Runner Marathon 10k Jogging",1.20,"a marathon pace split table"),
 ("Photography","a DSLR camera with a long lens","CAMERA","Photographer Lens Shutter",1.20,"an aperture and shutter exposure triangle"),
 ("Welding","a welding mask with sparks","WELDING TORCH","Welder Fabricator MIG TIG",1.10,"a weld symbol notation chart"),
 ("Woodworking","a hand plane and chisel","CHISEL","Carpenter Joiner Woodwork Workshop",1.10,"a dovetail joint cutting diagram"),
 ("Horse Riding","a horse's head with a bridle","HORSE","Equestrian Rider Pony Stables",1.10,"a dressage arena letter diagram"),
 ("Shooting","a clay pigeon and shotgun","SHOTGUN","Clay Pigeon Shooting Field Sport",1.10,"a choke constriction chart"),
 ("Metal Detecting","a metal detector","METAL DETECTOR","Detectorist Treasure Finds Hobby",1.00,"a ground-balance and discrimination dial"),
 ("Gardening","a spade and watering can","GARDEN SPADE","Gardener Allotment Veg Plot",1.00,"a companion planting grid"),
 ("Barbecue","a kettle barbecue with flames","BARBECUE","BBQ Grill Smoker Griller Meat",1.00,"a meat internal-temperature chart"),
 ("Home Brewing","a pint glass and hops","HOME BREW KIT","Homebrew Beer Ale CAMRA Real Ale",1.00,"a hydrometer gravity reading scale"),
 ("Sailing","a yacht heeling over","SAILING BOAT","Sailor Yacht Boat Crew Regatta",1.00,"a points-of-sail diagram"),
 ("Surfing","a surfboard and wave","SURFBOARD","Surfer Surf Board Waves Beach",1.00,"a swell period and tide chart"),
 ("Skiing","crossed skis and poles","PAIR OF SKIS","Skier Snow Slopes Alpine Winter",1.00,"a piste difficulty grading key"),
 ("Snooker","a snooker cue and black ball","SNOOKER CUE","Pool Cue Billiards Break",1.00,"a ball-value and re-spot diagram"),
 ("Karting","a go-kart","GO KART","Karting Race Track Circuit Racer",1.00,"a racing line apex diagram"),
 ("Climbing","a carabiner and rope","CLIMBING ROPE","Climber Bouldering Crag Belay",0.90,"a figure-of-eight knot sequence"),
 ("Kayaking","a kayak and paddle","KAYAK","Canoe Paddle River Watersport",0.90,"a river grade classification key"),
 ("Narrowboat","a narrowboat on a canal","NARROWBOAT","Canal Boat Barge Waterways Locks",0.90,"a lock operation sequence diagram"),
 ("Model Railway","a steam locomotive","MODEL RAILWAY","Trains Railway Modeller OO Gauge",0.90,"an OO gauge track plan"),
 ("Bird Watching","binoculars and a bird","PAIR OF BINOCULARS","Birder Twitcher Birding RSPB",0.90,"a wing-silhouette identification key"),
 ("Bee Keeping","a beehive with bees","BEEHIVE","Beekeeper Apiary Bees Honey",0.90,"a hive frame inspection diagram"),
 ("Chess","a knight chess piece","CHESS BOARD","Chess Player Grandmaster Pieces",0.90,"an algebraic notation board grid"),
 ("Baking","a stand mixer and rolling pin","ROLLING PIN","Baker Cake Bake Pastry Kitchen",0.90,"a baker's percentage table"),
 ("Allotment","a wheelbarrow and vegetables","ALLOTMENT","Grow Your Own Veg Plot Gardener",0.90,"a crop rotation four-bed plan"),
 ("Rowing","a rowing scull and oars","ROWING BOAT","Rower Rowing Crew Regatta Oars",0.90,"a stroke-rate and split chart"),
 ("Drone Flying","a quadcopter drone","DRONE","Drone Pilot FPV Quadcopter",0.90,"an airspace class boundary map"),
 ("Cricket","a cricket bat and ball","CRICKET BAT","Cricketer Batsman Bowler Wicket",0.90,"a fielding position map"),
 ("Football","a football","FOOTBALL","Footballer Soccer Sunday League",0.74,"a 4-4-2 formation diagram"),
 ("Swimming","a pair of goggles","PAIR OF GOGGLES","Swimmer Swim Pool Lengths",0.90,"a tumble-turn sequence diagram"),
]

MOSAIC = ["Skull","Heart","Union Jack","Map Of Britain","Lion Head","Anchor","Tree","Wolf Head"]
SCENES = ["In The Forest","In The Desert","At Sunset","In A Storm","On A Mountain",
          "By The Coast","In The Snow","Under Neon Lights","In The Fog","At Dawn"]
OLD = [("OLD MAN","Old Man"),("OLD WOMAN","Old Woman")]
AGES = [18,21,30,40,50,60,70,80]
YEARS = list(range(1945, 2009))
NOW = 2026
HOT = 2.0      # theme weight above which a subject also gets scene variations


def art(w): return "AN" if w.strip()[0].lower() in "aeiou" else "A"


def main():
    with open("TEMPLATES.csv","w",encoding="utf-8",newline="") as fh:
        w=csv.writer(fh)
        w.writerow(("template_id","measured_units_per_design","shirt_text","design_brief"))
        for k,u,t,_,b in TEMPLATES: w.writerow((k,f"{u:.2f}",t,b))

    out=[]; seen=set()
    for key,upd,text,title,brief in TEMPLATES:
        for subj,obj,short,kw,weight,insider in SUB:
            if key in ("vintage_year","legend_since"):
                variants=[(str(y), NOW-y) for y in YEARS]
            elif key=="never_underestimate": variants=OLD
            elif key=="object_mosaic": variants=[(m,m) for m in MOSAIC]
            else: variants=[("","")]
            for v1,v2 in variants:
                a=art(short)
                rep={"{SUBJ}":subj,"{SUBJ_CAPS}":subj.upper(),"{OBJ}":obj,"{OBJ_CAPS}":short,
                     "{Obj}":short.title(),"{KW}":kw,"{ART}":a,"{art}":a.lower(),
                     "{INSIDER}":insider,
                     "{OLD}":v1 if key=="never_underestimate" else "OLD MAN",
                     "{Old}":v2 if key=="never_underestimate" else "Old Man",
                     "{MOSAIC_ICON}":v1 if key=="object_mosaic" else "Skull",
                     "{YEAR}":v1 if key in ("vintage_year","legend_since") else "1980",
                     "{AGE}":str(v2) if key in ("vintage_year","legend_since") else "40"}
                def f(s):
                    for k2,val in rep.items(): s=s.replace(k2,str(val))
                    return s
                t=re.sub(r"\s{2,}"," ",f(title)).strip()
                if len(t)>80: t=t[:80].rsplit(" ",1)[0]
                if t.lower() in seen: continue
                seen.add(t.lower())
                norm=re.sub(r"[^a-z0-9]+"," ",t.lower()).strip()
                out.append([f"{upd*weight/2.5:.2f}",key,subj,str(v2 or "-"),"",
                            f(text),t,GARMENT,COLOUR,"no" if norm in existing else "yes"])
                # hot themes get scene variations of the illustration
                if weight>=HOT and key in ("never_underestimate","object_mosaic","its_a_thing"):
                    for sc in SCENES:
                        t2=f"{subj} T-Shirt {sc} {f(text).split(' / ')[0][:28]} Mens Funny {kw}"
                        t2=re.sub(r"\s{2,}"," ",t2)[:80].rsplit(" ",1)[0]
                        if t2.lower() in seen: continue
                        seen.add(t2.lower())
                        out.append([f"{upd*weight/2.5:.2f}",key,subj,str(v2 or "-"),sc,
                                    f(text),t2,GARMENT,COLOUR,"yes"])

    out.sort(key=lambda r:-float(r[0]))
    with open("CATALOGUE.csv","w",encoding="utf-8",newline="") as fh:
        w=csv.writer(fh)
        w.writerow(("priority_score","template_id","subject","variant","scene",
                    "shirt_text","ebay_title","garment","colour","novel"))
        w.writerows(out)
    print(f"designs generated : {len(out):,}   (black t-shirts only)")
    print(f"not already listed: {sum(1 for r in out if r[9]=='yes'):,}")
    print(f"with scene variants: {sum(1 for r in out if r[4]):,}")
    for k,n in Counter(r[1] for r in out).most_common():
        print(f"   {k:<22}{n:>8,}")


main()

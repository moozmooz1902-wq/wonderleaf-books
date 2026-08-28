#!/usr/bin/env python3
"""
Demand banks for the UK eBay t-shirt catalogue.

THE RULE THAT GOVERNS EVERYTHING HERE
    A variation only counts if it changes WHO IS SEARCHING.

    Restyling or recolouring the same design does not. That is what produced
    424,117 wall art listings collapsing to 43,483 real products and 45,015
    distinct titles - 10 listings competing for one search.

    Recipient, occasion, age, nationality and sub-type DO change the searcher.
    "50th birthday gift for grandad" and "50th birthday gift for dad" are
    different searches, bought by different people, at different times.

Every entry below is a phrase a UK buyer types.
"""

# --------------------------------------------------------------- recipients
# The single biggest legitimate multiplier. Each is a distinct gift search.
RECIPIENTS = [
    ("Dad", "for Dad"), ("Mum", "for Mum"), ("Grandad", "for Grandad"),
    ("Nan", "for Nan"), ("Nanny", "for Nanny"), ("Grandma", "for Grandma"),
    ("Uncle", "for Uncle"), ("Auntie", "for Auntie"), ("Brother", "for Brother"),
    ("Sister", "for Sister"), ("Son", "for Son"), ("Daughter", "for Daughter"),
    ("Husband", "for Husband"), ("Wife", "for Wife"), ("Boyfriend", "for Boyfriend"),
    ("Girlfriend", "for Girlfriend"), ("Him", "for Him"), ("Her", "for Her"),
    ("Best Friend", "for Best Friend"), ("Colleague", "for a Colleague"),
    ("Godfather", "for Godfather"), ("Stepdad", "for Stepdad"),
    ("Father in Law", "for Father in Law"), ("Grandson", "for Grandson"),
]

# Regional UK grandparent names - a genuinely under-served long tail
GRANDPARENT_NAMES = [
    "Nan", "Nanny", "Nana", "Grandma", "Gran", "Granny", "Grandad", "Grampy",
    "Grandpa", "Pops", "Papa", "Taid", "Nain", "Bampi", "Gigi", "Mimi",
]

# --------------------------------------------------------------- occasions
OCCASIONS = [
    ("Birthday", "Birthday Gift"), ("Christmas", "Christmas Gift"),
    ("Fathers Day", "Fathers Day Gift"), ("Mothers Day", "Mothers Day Gift"),
    ("Retirement", "Retirement Gift"), ("Anniversary", "Anniversary Gift"),
    ("Leaving", "Leaving Gift"), ("Graduation", "Graduation Gift"),
    ("Valentines", "Valentines Gift"), ("New Job", "New Job Gift"),
    ("Secret Santa", "Secret Santa Gift"), ("Housewarming", "Housewarming Gift"),
]

MILESTONE_AGES = [16, 18, 20, 21, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 85, 90]
ALL_AGES = list(range(16, 91))

# ------------------------------------------------------------- occupations
# UK trade and profession vocabulary, as people describe themselves
OCCUPATIONS = """
electrician plumber carpenter joiner welder mechanic builder bricklayer scaffolder
plasterer roofer painter decorator glazier tiler groundworker labourer gasfitter
heating-engineer hgv-driver lorry-driver van-driver bus-driver taxi-driver
train-driver forklift-driver crane-operator digger-driver farmer shepherd
gamekeeper tree-surgeon landscaper gardener groundsman fisherman
nurse midwife paramedic doctor surgeon dentist pharmacist physiotherapist
radiographer care-worker support-worker health-visitor
teacher headteacher teaching-assistant lecturer tutor lollipop-lady
firefighter police-officer paramedic prison-officer soldier sailor
airman coastguard lifeguard security-guard
chef sous-chef baker butcher barista bartender waiter publican
barber hairdresser beautician tattooist nail-tech masseuse
accountant solicitor architect engineer surveyor estate-agent
recruiter salesman marketer designer developer programmer sysadmin
electrical-engineer civil-engineer mechanical-engineer draughtsman
postman binman refuse-collector cleaner caretaker janitor
warehouse-operative picker packer driver-mate courier delivery-driver
apprentice-mechanic apprentice-electrician trainee-plumber
vet vet-nurse dog-groomer farrier stable-hand zookeeper
pilot cabin-crew air-traffic-controller train-guard signalman
librarian archivist curator museum-guide
plumber-mate scaffolder-mate steel-erector rigger fabricator
machinist toolmaker fitter turner miller cnc-operator
seamstress upholsterer cobbler locksmith glazier-apprentice
optician audiologist podiatrist osteopath chiropractor
social-worker youth-worker counsellor therapist psychologist
journalist photographer videographer sound-engineer lighting-tech
roadie stagehand bouncer doorman dj-professional
window-cleaner chimney-sweep pest-controller drain-engineer
""".split()

# ------------------------------------------------------------- dog breeds
DOG_BREEDS = """
labrador golden-retriever cocker-spaniel springer-spaniel sprocker cockapoo
cavapoo labradoodle goldendoodle border-collie collie sheepdog german-shepherd
staffordshire-bull-terrier staffy jack-russell parson-russell patterdale
border-terrier yorkshire-terrier west-highland-terrier scottie cairn-terrier
bull-terrier english-bull-terrier french-bulldog english-bulldog pug
chihuahua dachshund miniature-dachshund whippet greyhound lurcher saluki
beagle basset-hound bloodhound foxhound pointer setter irish-setter
weimaraner vizsla ridgeback rottweiler doberman boxer great-dane mastiff
bullmastiff st-bernard newfoundland leonberger husky malamute samoyed
akita shiba-inu chow-chow shar-pei dalmatian poodle toy-poodle bichon
maltese shih-tzu lhasa-apso pekingese pomeranian papillon havanese
schnauzer miniature-schnauzer giant-schnauzer airedale welsh-terrier
lakeland-terrier bedlington-terrier kerry-blue-terrier soft-coated-wheaten
irish-wolfhound deerhound afghan-hound borzoi bearded-collie
old-english-sheepdog rough-collie shetland-sheepdog corgi welsh-corgi
cavalier-king-charles king-charles-spaniel clumber-spaniel field-spaniel
brittany-spaniel english-springer welsh-springer flat-coated-retriever
curly-coated-retriever chesapeake-retriever nova-scotia-duck-toller
portuguese-water-dog spanish-water-dog lagotto standard-poodle
rescue-dog three-legged-dog senior-dog puppy
""".split()

CAT_BREEDS = """
ragdoll british-shorthair maine-coon persian siamese bengal sphynx
russian-blue norwegian-forest birman burmese tonkinese abyssinian
scottish-fold munchkin devon-rex cornish-rex savannah tabby ginger-cat
black-cat tortoiseshell calico tuxedo-cat moggy rescue-cat kitten
""".split()

# ---------------------------------------------------------------- hobbies
HOBBIES = """
carp-fishing sea-fishing fly-fishing match-fishing pike-fishing coarse-fishing
game-fishing beach-casting kayak-fishing
gardening allotment vegetable-growing greenhouse-growing bonsai orchid-growing
composting beekeeping chicken-keeping
darts snooker pool bowls crown-green-bowls skittles dominoes
golf crazy-golf disc-golf pitch-and-putt
cycling road-cycling mountain-biking gravel-riding bmx track-cycling
motorcycling cafe-racer motocross trials-riding adventure-riding scootering
running trail-running marathon-running 5k-running ultra-running
swimming open-water-swimming cold-water-swimming wild-swimming
hiking hillwalking munro-bagging wild-camping bushcraft rambling
climbing bouldering trad-climbing via-ferrata caving potholing
sailing kayaking canoeing paddleboarding rowing windsurfing kitesurfing surfing
scuba-diving freediving snorkelling wreck-diving
birdwatching twitching wildlife-photography astrophotography stargazing
metal-detecting fossil-hunting rockhounding geocaching
model-railways model-building scale-modelling tabletop-wargaming wargaming tabletop-gaming
tabletop-rpg board-gaming chess bridge poker
knitting crochet quilting cross-stitch embroidery sewing dressmaking
woodworking woodturning whittling carpentry-hobby blacksmithing
pottery ceramics glassblowing candle-making soap-making
baking sourdough cake-decorating brewing homebrew winemaking cheesemaking
photography film-photography darkroom drone-flying
vinyl-collecting record-collecting stamp-collecting coin-collecting
gaming retro-gaming speedrunning arcade-collecting
karate judo taekwondo boxing kickboxing muay-thai jiu-jitsu wrestling
weightlifting powerlifting bodybuilding crossfit calisthenics yoga pilates
caravanning camping motorhoming van-life narrowboating
horse-riding dressage showjumping eventing carriage-driving
rugby cricket football netball hockey badminton squash tennis table-tennis
""".split()

# ------------------------------------------------------- nations / heritage
NATIONS = """
England Scotland Wales Ireland Jamaica Poland Romania India Pakistan Bangladesh
Nigeria Ghana Kenya SouthAfrica Zimbabwe Somalia Ethiopia Eritrea Sudan Egypt
Morocco Algeria Tunisia Libya Turkey Iran Iraq Syria Lebanon Palestine Israel
Italy Spain Portugal France Germany Netherlands Belgium Denmark Sweden Norway
Finland Iceland Austria Switzerland Greece Cyprus Malta Croatia Serbia Bosnia
Albania Kosovo Bulgaria Hungary Czechia Slovakia Slovenia Lithuania Latvia
Estonia Ukraine Russia Belarus Georgia Armenia Azerbaijan Kazakhstan
China Japan Korea Vietnam Thailand Philippines Indonesia Malaysia Singapore
Nepal SriLanka Afghanistan Australia NewZealand Fiji Samoa Tonga
Canada USA Mexico Brazil Argentina Chile Colombia Peru Ecuador Venezuela
Cuba Trinidad Barbados Grenada StLucia Guyana Haiti Dominica Bahamas
""".split()

# ------------------------------------------------------------ UK regions
UK_PLACES = """
Yorkshire Lancashire Cornwall Devon Somerset Dorset Kent Essex Sussex Norfolk
Suffolk Cumbria Northumberland Durham Cheshire Derbyshire Staffordshire
Shropshire Herefordshire Worcestershire Warwickshire Leicestershire
Lincolnshire Nottinghamshire Northamptonshire Oxfordshire Berkshire Hampshire
Wiltshire Gloucestershire London Liverpool Manchester Birmingham Leeds
Sheffield Newcastle Sunderland Middlesbrough Hull Bradford Bolton Blackburn
Preston Wigan Oldham Rochdale Stockport Salford Glasgow Edinburgh Aberdeen
Dundee Inverness Stirling Perth Cardiff Swansea Newport Wrexham Bangor
Belfast Derry Portsmouth Southampton Brighton Bristol Plymouth Exeter
Nottingham Leicester Coventry Stoke Derby Norwich Ipswich Peterborough
""".split()


def pretty(token):
    """cocker-spaniel -> Cocker Spaniel ; hgv-driver -> HGV Driver"""
    ACRONYM = {"hgv": "HGV", "cnc": "CNC", "dj": "DJ", "bmx": "BMX", "usa": "USA"}
    parts = token.replace("_", "-").split("-")
    out = []
    for p in parts:
        out.append(ACRONYM.get(p.lower(), p.capitalize()))
    s = " ".join(out)
    # a few multi-word nations arrive glued together
    for glued, spaced in (("Southafrica", "South Africa"), ("Newzealand", "New Zealand"),
                          ("Srilanka", "Sri Lanka"), ("Stlucia", "St Lucia")):
        s = s.replace(glued, spaced)
    return s


if __name__ == "__main__":
    for name, bank in [("occupations", OCCUPATIONS), ("dog breeds", DOG_BREEDS),
                       ("cat breeds", CAT_BREEDS), ("hobbies", HOBBIES),
                       ("nations", NATIONS), ("uk places", UK_PLACES),
                       ("recipients", RECIPIENTS), ("occasions", OCCASIONS),
                       ("grandparent names", GRANDPARENT_NAMES)]:
        print(f"  {len(bank):4d}  {name}")
    print(f"\n  sample: {[pretty(x) for x in DOG_BREEDS[:6]]}")
    print(f"  sample: {[pretty(x) for x in OCCUPATIONS[:6]]}")

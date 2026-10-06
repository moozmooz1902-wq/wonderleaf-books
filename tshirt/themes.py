"""Theme of a listing, and the words buyers type to find it.

Modelled on the wall-art branch's MOOD map: each theme carries the search
keywords for that kind of shirt, and those words are never trimmed out of
the title. The point is that "Funny" belongs on a joke shirt and NOT on a
memorial or a resurrection design - putting it there is both bad search and
bad taste.

Order matters: the first theme whose pattern matches wins, so the specific
ones (memorial, faith) are tested before the catch-all humour one.
"""
import re

THEMES = [
 ("memorial",  r"memorial|in loving memory|rest in peace|\brip\b|angel wings|forever in our|"
               r"remembrance|sympathy|guardian angel|never forgotten",
               "Memorial"),
 ("faith",     r"christian|christianity|jesus|god bless|godly|bible|scripture|\bfaith\b|"
               r"church|psalm|\blord\b|blessed|prayer|\brisen\b|resurrection|baptism|"
               r"catholic|islamic|muslim|allah|\bamen\b|holy spirit",
               "Christian"),
 ("veteran",   r"veteran|army|navy|\braf\b|soldier|regiment|military|armed forces|"
               r"remembrance day|poppy|\bwar\b|infantry|\bmarines?\b|airborne",
               "Military Veteran"),
 ("awareness", r"awareness|autism|cancer|mental health|suicide|diabetes|alzheimer|"
               r"dementia|charity|survivor",
               "Awareness"),
 ("biker",     r"biker|motorbike|motorcycle|cafe racer|chopper|harley|motocross|"
               r"superbike|rider|two wheels",
               "Biker"),
 ("gym",       r"\bgym\b|bodybuilding|weightlifting|fitness|workout|deadlift|squat|"
               r"powerlifting|crossfit|muscle|training",
               "Gym"),
 ("fishing",   r"fishing|angler|angling|carp|fisherman|tackle|\bbait\b",
               "Fishing"),
 ("music",     r"guitar|drummer|drums|bass|band|rock|metal|punk|\bdj\b|vinyl|"
               r"music|reggae|piano|singer",
               "Music"),
 ("gaming",    r"gaming|gamer|console|playstation|xbox|level up|retro gaming|arcade|"
               r"video game|rpg",
               "Gaming"),
 ("pets",      r"\bdog\b|\bcat\b|puppy|kitten|terrier|retriever|spaniel|bulldog|"
               r"pug\b|collie|labrador|dog mum|dog dad|cat lover",
               "Pet Lover"),
 ("football",  r"football|rugby|cricket|golf|snooker|darts|boxing|\bmma\b|"
               r"martial arts|karate|judo|basketball|tennis",
               "Sports"),
 ("fishing2",  r"hunting|shooting|camping|hiking|climbing|kayak|canoe|sailing|surfing|"
               r"scuba|diving|caravan|4x4|off road",
               "Outdoors"),
 ("farming",   r"farmer|farming|tractor|agriculture|livestock|combine",
               "Farming"),
 ("trades",    r"plumber|electrician|welder|carpenter|builder|mechanic|engineer|"
               r"scaffolder|roofer|lorry|trucker|hgv|driver|chef|nurse|teacher|"
               r"firefighter|paramedic|police",
               "Work"),
 ("birthday",  r"\b\d{1,2}(st|nd|rd|th)\b|birthday|aged to perfection|born in|"
               r"vintage 19|legend since|years old",
               "Birthday"),
 ("family",    r"\bdad\b|daddy|father|grandad|grandpa|mum\b|mummy|mother|nanny|"
               r"uncle|son\b|daughter|husband|wife|family",
               "Family"),
 ("patriotic", r"union jack|england|scotland|wales|ireland|british|welsh|scottish|"
               r"irish|\buk\b|flag|patriot|viking|norse",
               "Patriotic"),
 ("seasonal",  r"christmas|xmas|santa|halloween|easter|valentine|new year",
               "Novelty"),
 ("drinking",  r"beer|pub|wine|gin|whisky|vodka|drinking|cocktail|lager|ale|"
               r"hangover|prosecco",
               "Beer"),
 ("nerd",      r"science|maths|physics|chemistry|computer|coding|programmer|\bit\b|"
               r"geek|nerd|space|astronomy|dinosaur",
               "Geek"),
 ("rude",      r"arse|shit|\bfuck|bastard|bollocks|twat|wanker|piss|sarcastic|rude",
               "Rude Funny"),
]

FALLBACK = "Funny"

# Secondary terms, used only to fill the title out towards eBay's 80
# characters. Relevant to the theme, so they are extra search coverage
# rather than padding. 43% of titles were finishing under 60 characters.
EXTRA = {
 "humour":   "Novelty Joke Gift Idea Present Birthday",
 "memorial": "Remembrance Sympathy Keepsake Gift",
 "faith":    "Religious Jesus God Bible Gift",
 "veteran":  "Army Forces Regiment Gift Present",
 "awareness":"Support Charity Gift Present",
 "biker":    "Motorcycle Motorbike Rider Gift Present",
 "gym":      "Workout Bodybuilding Training Gift",
 "fishing":  "Angler Carp Tackle Gift Present",
 "music":    "Band Guitar Rock Gift Present",
 "gaming":   "Gamer Console Retro Gift Present",
 "pets":     "Dog Lover Owner Puppy Gift Present",
 "football": "Fan Supporter Sport Gift Present",
 "fishing2": "Outdoor Adventure Hobby Gift Present",
 "farming":  "Farmer Tractor Agriculture Gift",
 "trades":   "Tradesman Worker Job Gift Present",
 "birthday": "Gift Present Party Celebration Idea",
 "family":   "Gift Present Fathers Day Idea",
 "patriotic":"Flag Pride Nation Gift Present",
 "seasonal": "Gift Present Party Xmas Idea",
 "drinking": "Pub Beer Lager Gift Present",
 "nerd":     "Science Geek Nerd Gift Present",
 "rude":     "Offensive Joke Adult Gift",
}


def extra_terms(theme):
    return EXTRA.get(theme, EXTRA["humour"]).split()


ANTI = re.compile(r"atheist|atheism|anti.?war|sarcas", re.I)


def theme_of(title, slogan=""):
    s = f"{title} {slogan}".lower()
    if ANTI.search(s):          # atheist/anti-war designs are jokes, not faith
        return "humour", FALLBACK
    for name, pat, kw in THEMES:
        if re.search(pat, s):
            return name, kw
    return "humour", FALLBACK

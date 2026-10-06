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
               "Memorial Remembrance Gift"),
 ("faith",     r"christian|christianity|jesus|god bless|godly|bible|scripture|\bfaith\b|"
               r"church|psalm|\blord\b|blessed|prayer|\brisen\b|resurrection|baptism|"
               r"catholic|islamic|muslim|allah|\bamen\b|holy spirit",
               "Christian Faith Religious"),
 ("veteran",   r"veteran|army|navy|\braf\b|soldier|regiment|military|armed forces|"
               r"remembrance day|poppy|\bwar\b|infantry|\bmarines?\b|airborne",
               "Military Veteran Gift"),
 ("awareness", r"awareness|autism|cancer|mental health|suicide|diabetes|alzheimer|"
               r"dementia|charity|survivor",
               "Awareness Support Gift"),
 ("biker",     r"biker|motorbike|motorcycle|cafe racer|chopper|harley|motocross|"
               r"superbike|rider|two wheels",
               "Biker Motorbike Gift"),
 ("gym",       r"\bgym\b|bodybuilding|weightlifting|fitness|workout|deadlift|squat|"
               r"powerlifting|crossfit|muscle|training",
               "Gym Training Fitness"),
 ("fishing",   r"fishing|angler|angling|carp|fisherman|tackle|\bbait\b",
               "Fishing Angling Gift"),
 ("music",     r"guitar|drummer|drums|bass|band|rock|metal|punk|\bdj\b|vinyl|"
               r"music|reggae|piano|singer",
               "Music Band Gift"),
 ("gaming",    r"gaming|gamer|console|playstation|xbox|level up|retro gaming|arcade|"
               r"video game|rpg",
               "Gaming Gamer Gift"),
 ("pets",      r"\bdog\b|\bcat\b|puppy|kitten|terrier|retriever|spaniel|bulldog|"
               r"pug\b|collie|labrador|dog mum|dog dad|cat lover",
               "Dog Cat Lover Gift"),
 ("football",  r"football|rugby|cricket|golf|snooker|darts|boxing|\bmma\b|"
               r"martial arts|karate|judo|basketball|tennis",
               "Sports Fan Gift"),
 ("fishing2",  r"hunting|shooting|camping|hiking|climbing|kayak|canoe|sailing|surfing|"
               r"scuba|diving|caravan|4x4|off road",
               "Outdoors Hobby Gift"),
 ("farming",   r"farmer|farming|tractor|agriculture|livestock|combine",
               "Farming Tractor Gift"),
 ("trades",    r"plumber|electrician|welder|carpenter|builder|mechanic|engineer|"
               r"scaffolder|roofer|lorry|trucker|hgv|driver|chef|nurse|teacher|"
               r"firefighter|paramedic|police",
               "Work Trade Gift"),
 ("birthday",  r"\b\d{1,2}(st|nd|rd|th)\b|birthday|aged to perfection|born in|"
               r"vintage 19|legend since|years old",
               "Birthday Gift Present"),
 ("family",    r"\bdad\b|daddy|father|grandad|grandpa|mum\b|mummy|mother|nanny|"
               r"uncle|son\b|daughter|husband|wife|family",
               "Family Gift Present"),
 ("patriotic", r"union jack|england|scotland|wales|ireland|british|welsh|scottish|"
               r"irish|\buk\b|flag|patriot|viking|norse",
               "Patriotic Flag Gift"),
 ("seasonal",  r"christmas|xmas|santa|halloween|easter|valentine|new year",
               "Christmas Halloween Gift"),
 ("drinking",  r"beer|pub|wine|gin|whisky|vodka|drinking|cocktail|lager|ale|"
               r"hangover|prosecco",
               "Beer Drinking Gift"),
 ("nerd",      r"science|maths|physics|chemistry|computer|coding|programmer|\bit\b|"
               r"geek|nerd|space|astronomy|dinosaur",
               "Geek Science Gift"),
 ("rude",      r"arse|shit|\bfuck|bastard|bollocks|twat|wanker|piss|sarcastic|rude",
               "Rude Offensive Funny"),
]

FALLBACK = "Funny Novelty Gift"


ANTI = re.compile(r"atheist|atheism|anti.?war|sarcas", re.I)


def theme_of(title, slogan=""):
    s = f"{title} {slogan}".lower()
    if ANTI.search(s):          # atheist/anti-war designs are jokes, not faith
        return "humour", FALLBACK
    for name, pat, kw in THEMES:
        if re.search(pat, s):
            return name, kw
    return "humour", FALLBACK

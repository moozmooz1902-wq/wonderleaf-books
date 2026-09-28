"""Hand-vetted templates, each tied to the kind of word its slot needs.

The miner found 89 skeletons. Some are real slogans; some are mining noise
("PURE FANTASY {X} NORMAL") or third-party IP. More importantly, a skeleton
carries no grammar: dropping a noun into "I PLAN {X}" gives "I PLAN GRIZZLY".
So each surviving template is written out in full and tagged with the slot
type it takes, and the vocabulary for each type is harvested from the
fillers that were actually observed in that slot.
"""

# slot types: ROLE (a job or person), ACTIVITY (a sport or gerund),
# OBJECT (one countable thing), PLURAL, YEAR, AGE, RELATION, NATION, BREED
TEMPLATES = [
 # ---- ROLE -------------------------------------------------------------
 ("THIS IS WHAT AN AWESOME {N} LOOKS LIKE",                       "ROLE", 4446),
 ("YOU'RE LOOKING AT AN AWESOME {N}",                             "ROLE",  239),
 ("TRUST ME I'M A {N}",                                           "ROLE",  144),
 ("BEST {N} EVER",                                                "ROLE",   81),
 ("I'M A {N} WHAT'S YOUR SUPERPOWER",                             "ROLE",  120),
 # ---- ACTIVITY ---------------------------------------------------------
 ("WARNING MAY SPONTANEOUSLY START TALKING ABOUT {N}",            "ACTIVITY",1501),
 ("WEEKEND FORECAST {N} WITH A CHANCE OF DRINKING",               "ACTIVITY",1479),
 ("{N} ON THE BRAIN",                                             "ACTIVITY", 384),
 ("I GOOGLED MY SYMPTOMS AND IT TURNS OUT I JUST NEED TO GO {N}", "ACTIVITY", 186),
 ("{N} AND BEER THAT'S WHY I'M HERE",                             "ACTIVITY",  63),
 ("EAT SLEEP {N} REPEAT",                                         "ACTIVITY", 231),
 ("YES I HAVE A RETIREMENT PLAN I PLAN ON {N}",                   "ACTIVITY", 615),
 # ---- OBJECT -----------------------------------------------------------
 ("NEVER UNDERESTIMATE AN OLD MAN WITH A {N}",                    "OBJECT", 2374),
 ("SELL MY {N} I'D RATHER SHOVE WASPS UP MY ARSE",                "OBJECT", 1583),
 ("I GOT A {N} FOR MY WIFE BEST SWAP EVER",                       "OBJECT",  284),
 ("IS MY {N} OKAY",                                               "OBJECT",  209),
 ("I'M NOT ALWAYS GRUMPY SOMETIMES I'M ON MY {N}",                "OBJECT",   78),
 # ---- PLURAL -----------------------------------------------------------
 ("I HAVE TOO MANY {N} SAID NO ONE EVER",                         "PLURAL",  150),
 ("EASILY DISTRACTED BY {N}",                                     "PLURAL",   59),
 ("SAVE THE {N}",                                                 "PLURAL",  298),
 ("BUY MORE {N} SAY THE VOICES IN MY HEAD",                       "PLURAL",   66),
 ("JUST A BOY WHO LOVES {N}",                                     "PLURAL",   91),
 # ---- YEAR -------------------------------------------------------------
 ("PREMIUM QUALITY VINTAGE {N} AGED TO PERFECTION "
  "ALL ORIGINAL PARTS LIMITED EDITION 100 GENUINE",               "YEAR",  2140),
 ("ORIGINAL PARTS VINTAGE AGED TO PERFECTION {N} "
  "100 AUTHENTIC GUARANTEED PREMIUM QUALITY",                     "YEAR",  3864),
 ("THE BIRTH OF LEGENDS {N} EST 100 PREMIUM VINTAGE "
  "GUARANTEED AGED TO PERFECTION",                                "YEAR",  1187),
 ("LEGEND SINCE {N}",                                             "YEAR",   261),
 ("VINTAGE MADE IN {N} ALL ORIGINAL PARTS",                       "YEAR",   285),
 ("PREMIUM ORIGINAL PARTS MOSTLY VINTAGE {N} "
  "100 AUTHENTIC GUARANTEED",                                     "YEAR",    91),
 # ---- AGE --------------------------------------------------------------
 ("LEVEL {N} UNLOCKED",                                           "AGE",    781),
 ("CHEERS AND BEERS TO {N} YEARS",                                "AGE",    268),
 ("{N} YEAR OLD BANGER MOSTLY ORIGINAL PARTS "
  "BODYWORK NEEDS ATTENTION SPARE TYRE",                          "AGE",    337),
 ("SO HAPPY I'M {N} TODAY",                                       "AGE",     66),
 ("IF YOU HAVEN'T GROWN UP BY THE TIME YOU'RE {N} "
  "YOU DON'T HAVE TO",                                            "AGE",     75),
 # ---- RELATION ---------------------------------------------------------
 ("{N} MAN THE MYTH THE LEGEND",                                  "RELATION",216),
 ("{N} MAN MYTH LEGEND",                                          "RELATION",194),
 ("PROPERTY OF MY AWESOME {N}",                                   "RELATION",1681),
 # ---- NATION / BREED ---------------------------------------------------
 ("ALL MEN ARE BORN EQUAL THE BEST ARE BORN TO BE {N}",           "NATION",  661),
 ("{N} SOUL BIKER ATTITUDE",                                      "NATION",  139),
 ("ALL DOGS WERE CREATED EQUAL THEN GOD MADE {N}",                "BREED",   281),
 # ---- GENERIC (safe with any bare noun) --------------------------------
 ("PEACE LOVE {N}",                                               "GENERIC", 175),
 ("I LOVE {N}",                                                   "GENERIC",  91),
 ("EAT SLEEP {N} REPEAT",                                         "GENERIC", 231),
 ("{N} ON THE BRAIN",                                             "GENERIC", 384),
 ("WARNING MAY SPONTANEOUSLY START TALKING ABOUT {N}",            "GENERIC", 400),
 ("EASILY DISTRACTED BY {N}",                                     "GENERIC",  59),
 ("I GOOGLED MY SYMPTOMS AND IT TURNS OUT I JUST NEED MORE {N}",  "GENERIC", 186),
]

# Templates deliberately dropped, and why. Kept in the file so the decision
# is reviewable rather than invisible.
DROPPED = {
 "USCSS NOSTROMO {X}":            "third-party IP (Alien / Weyland-Yutani)",
 "MICK'S GYM 1976 TRAINING EST":  "third-party IP (Rocky)",
 "TVR MEDIUM {X}":                "third-party IP (car marque)",
 "PURE FANTASY {X} NORMAL":       "mining noise - skeleton is not the real slogan",
 "{X} ANYTHING OUT NORMAL":       "mining noise - shifted duplicate of the above",
 "STRENGTH AND COURAGE JUDO":     "garbled OCR of a crowded design",
 "JIU JITSU IN JIUJITSU":         "garbled OCR",
 "SPEED JUNKIES HI SPEED MOTORS": "club/chapter branding, not a transferable joke",
 "THIS IS WHAT AN AWESOME {X} LIKE": "shifted duplicate of THIS IS WHAT ... LOOKS LIKE",
 "{X} I'D RATHER SHOVE WASPS":    "kept, but rewritten as SELL MY {N} ... for grammar",
 "I AM {X}":                      "slot too loose - produced 'I AM A EVIL'",
 "THIS IS {X}":                   "slot too loose",
 "I'M NOT {X}":                   "slot too loose",
 "THE LEGEND {X}":                "slot too loose",
 "BLOOD SWEAT {X}":               "slot too loose",
}

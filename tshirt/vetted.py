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
 ("WARNING MAY SPONTANEOUSLY START TALKING ABOUT {N}",            "GENERIC", 180),
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


# ---------------------------------------------------------------------------
# Twists on the families that already sell. The seller's point: "Best Dad
# Ever" is a hot seller, so give it siblings - "Perfect Dad", "World's
# Okayest Dad" - rather than one design. Each line below is a variation on a
# template the miner found in designs that sold, keeping the slot type so the
# grammar stays safe.
# ---------------------------------------------------------------------------
TEMPLATES += [
 # ---- ROLE
 ("WORLD'S BEST {N}",                                             "ROLE",  900),
 ("WORLD'S OKAYEST {N}",                                          "ROLE",  700),
 ("{N} OF THE YEAR",                                              "ROLE",  600),
 ("CERTIFIED {N}",                                                "ROLE",  550),
 ("PROFESSIONAL {N} SINCE DAY ONE",                               "ROLE",  500),
 ("IT'S A {N} THING YOU WOULDN'T UNDERSTAND",                     "ROLE",  850),
 ("{N} BY DAY LEGEND BY NIGHT",                                   "ROLE",  600),
 ("KEEP CALM I'M A {N}",                                          "ROLE",  500),
 ("NEVER UNDERESTIMATE A {N}",                                    "ROLE",  800),
 ("BEHIND EVERY GREAT TEAM IS AN AWESOME {N}",                    "ROLE",  450),
 ("THE {N} THE MYTH THE LEGEND",                                  "ROLE",  950),
 ("PROUD {N}",                                                    "ROLE",  400),
 ("{N} MODE ON",                                                  "ROLE",  380),
 ("NOT ALL HEROES WEAR CAPES SOME ARE A {N}",                     "ROLE",  520),
 # ---- OBJECT
 ("I'D RATHER BE ON MY {N}",                                      "OBJECT",820),
 ("LIFE IS BETTER WITH A {N}",                                    "OBJECT",760),
 ("MY OTHER RIDE IS A {N}",                                       "OBJECT",640),
 ("THE {N} IS CALLING AND I MUST GO",                             "OBJECT",700),
 ("YOU HAD ME AT {N}",                                            "OBJECT",520),
 ("ALL I NEED IS A {N}",                                          "OBJECT",600),
 ("BORN TO RIDE A {N}",                                           "OBJECT",580),
 ("HAPPINESS IS A {N}",                                           "OBJECT",540),
 ("TOUCH MY {N} AND WE HAVE A PROBLEM",                           "OBJECT",480),
 # ---- ACTIVITY
 ("I'D RATHER BE {N}",                                            "ACTIVITY",880),
 ("{N} IS MY THERAPY",                                            "ACTIVITY",820),
 ("SORRY I'M LATE I WAS {N}",                                     "ACTIVITY",640),
 ("LIVE LOVE {N}",                                                "ACTIVITY",600),
 ("{N} ALL DAY EVERY DAY",                                        "ACTIVITY",560),
 ("MY WEEKEND IS ALREADY BOOKED {N}",                             "ACTIVITY",520),
 ("{N} BECAUSE PEOPLE ARE EXHAUSTING",                            "ACTIVITY",600),
 ("I WORK HARD SO I CAN KEEP {N}",                                "ACTIVITY",540),
 ("{N} IS NOT A HOBBY IT'S A LIFESTYLE",                          "ACTIVITY",680),
 # ---- PLURAL
 ("JUST A BLOKE WHO LOVES {N}",                                   "PLURAL", 620),
 ("CRAZY ABOUT {N}",                                              "PLURAL", 540),
 ("ALL YOU NEED IS LOVE AND {N}",                                 "PLURAL", 580),
 ("MY HEART BELONGS TO {N}",                                      "PLURAL", 500),
 ("{N} MAKE ME HAPPY PEOPLE NOT SO MUCH",                         "PLURAL", 620),
 # ---- RELATION
 ("PERFECT {N}",                                                  "RELATION",700),
 ("NUMBER ONE {N}",                                               "RELATION",650),
 ("LIKE A NORMAL {N} ONLY COOLER",                                "RELATION",600),
 ("{N} OF THE YEAR EVERY YEAR",                                   "RELATION",560),
 ("AWESOME {N} SINCE DAY ONE",                                    "RELATION",520),
 # ---- AGE
 ("{N} AND STILL AWESOME",                                        "AGE",    700),
 ("{N} YEARS YOUNG",                                              "AGE",    660),
 ("{N} AND FABULOUS",                                             "AGE",    520),
 ("LEVEL {N} COMPLETE",                                           "AGE",    600),
 ("OFFICIALLY {N} AND LOVING IT",                                 "AGE",    540),
 # ---- GENERIC (safe with any noun)
 ("OBSESSED WITH {N}",                                            "GENERIC",560),
 ("{N} MAKES EVERYTHING BETTER",                                  "GENERIC",520),
 ("TALK {N} TO ME",                                               "GENERIC",480),
 ("POWERED BY {N}",                                               "GENERIC",540),
 ("{N} ENTHUSIAST",                                               "GENERIC",460),
]

# Displate: 2.7M images, and the first real demand signal in this project

Harvested 10 October 2026. This closes the one gap noted in `live_catalogue_6_4m.md`
("Displate's sitemap index returned 403 to the Python client, so Displate is not in
this manifest"). It also produced something the project did not have before: a list
of **real search queries**, not product listings.

Everything below is machine-counted from files fetched in this session. Where a number
is a floor or a ceiling rather than a measurement, the line says so.

## What was blocking it, and what it actually was

Not a block at all. `displate.com/sitemap.xml` is a **301 redirect** to
`sitemaps.displate.com`. The Python client was not following it and reported the
redirect body as a failure. `curl -sSL` has always worked. `robots.txt` allows `/`
and publicly names eight sitemap indexes, so none of this needed scraping.

Scripts: `wallart-data/build_displate.py` (harvest, resumable), `mine_displate.py`,
`mine_demand.py`, `demand_ip.py`, `demand_cities.py`.

## The catalogue

| Measure | Value |
|---|---|
| Product sitemaps fetched | 278 of 278 (166 non-licensed + 112 licensed), zero failures |
| Image records | **2,717,198** |
| Records with an image URL | 2,717,198 (100%) |
| Non-licensed (artist originals) | 2,692,858 — **99.1%** |
| Licensed IP | 24,340 — **0.9%** |
| Distinct image file hashes | 2,714,514 |
| Exact file reused across listings | 2,684 — **0.1%** |

Displate's sitemaps carry `<loc>` + `<image:loc>` and **no titles** — products are
bare numeric IDs (`displate.com/displate/437`). So Displate feeds the captioning
corpus, not the title-mining corpus. Titles would need 2.7M page fetches; not worth it.

### The 0.1% figure is a floor, not a near-duplicate rate

Displate filenames are content hashes, so an identical *file* in two listings is
detectable, but the same artwork re-exported gets a new hash. 0.1% measures exact
file reuse only. Displate's true near-duplicate rate needs perceptual hashing of
the pixels — that is the captioning pass, not this harvest.

### Opposite catalogue strategies, measured

| | Fy! / iamfy.co | Displate |
|---|---|---|
| Listings | 6,448,043 | 2,717,198 |
| Distinct designs | 607,667 | 2,714,514 (file-level) |
| Repeat rate | **83.0%** | **0.1%** (floor) |
| Titles in sitemap | yes | no |

Fy! runs ~608k designs listed about ten times each. Displate runs ~2.7M genuinely
distinct files. Both are large catalogues; only one is large because of variant
inflation. Our 89%-near-duplication problem is the Fy! failure mode, not the
Displate one.

### Upload volume by year

From the `/artwork/YYYY-MM-DD/` folder in each image URL:

| Year | Total | Non-licensed | Licensed |
|---|---|---|---|
| 2013 | 1,922 | 1,922 | 0 |
| 2014 | 8,554 | 8,554 | 0 |
| 2015 | 14,650 | 14,650 | 0 |
| 2016 | 12,365 | 12,365 | 0 |
| 2017 | 14,210 | 13,932 | 278 |
| 2018 | 64,004 | 63,740 | 264 |
| 2019 | 283,106 | 282,056 | 1,050 |
| 2020 | 343,257 | 342,225 | 1,032 |
| 2021 | 295,229 | 293,059 | 2,170 |
| 2022 | 290,014 | 285,596 | 4,418 |
| 2023 | 402,912 | 398,977 | 3,935 |
| 2024 | 279,682 | 275,792 | 3,890 |
| 2025 | 331,430 | 327,282 | 4,148 |
| 2026 | 375,831 | 372,676 | 3,155 |

2019 is the step change. 2026 is a partial year and is already the third-largest,
so Displate is still absorbing roughly 350k new images a year.

## The 191 licensed brands: use this as a negative list

`brands_sitemap1.xml` names every franchise Displate holds a licence for. This is
directly useful as a **compliance filter** — a generated design whose prompt or
title touches any of these is an infringement risk, and Displate having the licence
is proof the rights are owned and enforced.

Among them: star-wars, marvel, dc-comics, disney (+ disney-pixar, disney-princess,
disney-stitch, disney-villains), game-of-thrones, house-of-the-dragon, the-witcher,
middleearth, wizarding-world, dune, alien, predator, godzilla-classic, the-matrix,
john-wick, friends, the-big-bang-theory, south-park, spongebob-squarepants,
looney-tunes, hannabarbera, cartoon-network, tmnt, transformers, power-rangers,
naruto, one-piece, dragon-ball (+ -super, -z), demon-slayer, jujutsu-kaisen,
my-hero-academia, death-note, tokyo-ghoul, attack-adjacent titles, call-of-duty,
fortnite, minecraft-adjacent, world-of-warcraft, league-of-legends, valorant,
overwatch, cyberpunk-2077, elden-ring, dark-souls, bloodborne, fallout, doom,
halo-game, playstation, sega-collection, warhammer, dungeons-and-dragons,
magic-the-gathering, nba, wwe, porsche, squid-game, stranger-things-series,
rick-and-morty, nightmare-before-christmas, wizard-of-oz, willy-wonka, and more.

Full list in `wallart-data/displate_brands.txt`.

## The search queries: 34,789 of them

`popular_searches_sitemap1.xml` publishes **34,789 distinct search URLs** —
`displate.com/search?q=...`. Displate only builds indexable pages for queries worth
ranking for, so this is a demand list, not a supply list. **It is the first
demand-side data in this project.** Everything before it was supply read as demand,
which the earlier notes flagged as the project's central blind spot.

It is a genuine log, not a curated list. The evidence is the misspellings: alongside
`abstract` sit `absract`, `abstact`, `abstarct`, `abstrac`, `abstrack`, `abstrat`,
`abstrct`, `abtract`, `absract`. Nobody curates those. Real users typed them.

### What Displate's customers actually search for

| Bucket | Queries | Share of all 34,789 |
|---|---|---|
| Match a licensed-brand phrase | 1,432 | **4.1%** (floor) |
| Contain a decor subject word | ~1,674 | ~4.8% |
| Neither | **31,715** | **91.2%** |

The 4.1% is a floor: it matches only Displate's own 191 partners plus 35 obvious
franchises. Franchises Displate does *not* licence still get searched.

Top franchise queries: star wars (118), call of duty (65), the witcher (37),
porsche (36), assassins creed (34), one piece (30), nba (29), naruto (28),
demon slayer (27), zelda (23), dark souls (22), doom (22), street fighter (21),
alien (21), friends (21), batman (20), marvel (20), playstation (19),
mandalorian (18), disney (18).

Decor subjects, as a share of the 33,357 non-franchise queries: animals 1.0%,
city/map/skyline 0.8%, landscape 0.6%, space 0.5%, vehicles 0.5%, botanical 0.4%,
sport 0.4%, typography 0.4%, food/drink 0.3%, abstract 0.2%.

### The 91% is named entities, and that is the finding

A 60-query random sample of the residual: cham syndulla, biff tannen, jack sparrow,
mos eisley cantina, matt bomer, jennifer connelly, bruce willis, bernd leno,
ao no exorcist, houseki no kuni, delicious in dungeon, pandora hearts,
fate grand order, command and conquer, myst, backrooms, mystery machine,
wolfsburg, nanchang, asakusa, quebec, ireland, aztecs, lord shiva, haeckel,
cassandre, dorian gray, invictus, mindfulness, brain anatomy, women empowerment,
funny vintage, asian cuisine, mustache, sweet pea.

Characters, actors, footballers, anime titles, game titles, bands. 17,099 of them
are a single word and 10,698 are two words — the shape of entity lookup, not of
decor browsing.

**So: Displate demand is fandom demand.** Its customers arrive knowing the name of
a thing they want on their wall. That is a different purchase from decor, and it is
why Displate's own catalogue is 99.1% artist originals while its marketing is
franchise-led: the artists supply the long tail that the licences create traffic for.

## UK places have almost no demand on Displate

This is a direct test of the Phase 1 plan (UK place atoms × lettering-free
treatments), so it was run carefully.

A naive match of 6,155 gazetteer atoms against the queries returned nonsense —
English river names are common words, so `Eye`, `Ray`, `Team`, `Wolf`, `Bride`,
`Box`, `Brain`, `Ted`, `Dean`, `Cover` and `Line` all "matched". That result is
discarded. The clean version uses only **50 unambiguous UK city names**, excluding
every name that is also a common English word (Bath, Wells, Derby, Lincoln, Perth,
Boston, Hull, Bangor, Newport, Richmond, Washington, Hamilton, Preston, Lancaster,
Chester), and strips the `new york` family from `york`.

| Measure | Value |
|---|---|
| UK city names tested | 50 |
| Cities with at least one search | 35 |
| Cities with **zero** searches | 15 |
| City-bearing queries | **87 of 34,789 — 0.25%** |

London leads with 16 (london, london bridge, london bus, london buses,
london calling, london england). Then manchester 9, liverpool 8, cambridge 7.

**And most of the multi-word hits are football clubs, which are trademarked and
unusable:** manchester city fc, manchester city womens fc, manchester derby,
liverpool fc, sheffield united, sheffield wednesday, nottingham forest,
leeds united, leicester city, norwich city, bristol city, birmingham city,
stoke city, wolverhampton wanderers. Strip those and UK *place* demand on Displate
is: London, and one query each for about thirty other cities.

Zero searches: salford, peterborough, dundee, salisbury, gloucester, inverness,
stirling, lichfield, ripon, truro, doncaster, colchester, wrexham, dunstable, elgin.

### What this does and does not mean

It does **not** kill Phase 1. Displate is a metal-poster brand with a gaming,
anime and film-skewed, globally distributed, male-skewed audience. eBay UK buyers
searching for a Sheffield skyline print are not on Displate and would not show up
here. The user's existing typography catalogue sells to that other audience.

What it does mean is narrower and still worth having: **Displate is not evidence
for the UK-place plan, and should not be cited as if it were.** The plan needs its
own demand check from a UK-facing source.

> **SUPERSEDED, same day.** That check has since been run, and it came back
> strongly positive. The seller's own eBay export carries a Watchers column:
> UK-place listings there watch at **7.91% against a 1.05% base, z = +12.6**,
> on 354 listings. Displate's indifference to UK places turns out to say
> something about Displate's audience, not about the plan. See
> `first_party_demand_watchers.md`.

## Taxonomy captured as a side effect

- **41 browse categories** — the clean top-level axis:
  abstract, animals, anime-and-manga, blueprints, books, cars, cartoons,
  celebrities, cityscapes, comics, contemporary-art, cute, fantasy, fashion,
  floral, food-and-kitchen, funny, gaming, inspirational, japanese-and-asian,
  kids-room, landscapes, mancave, maps, military, minimalistic, movies, music,
  nature, other, paintings, planes, pop-art, retro, space, sport, text-art,
  travel, tv-shows, united-states, vintage-posters.

  Note what is here that Fy! does not have: **mancave**, **blueprints**,
  **text-art**, **united-states** as a category in its own right. And note that
  `text-art` is a category on a site whose demand is 91% entity lookup — the
  typography catalogue we already sell has a home here conceptually.

- **105,844 artist-curated collection slugs** (non-licensed) + 999 licensed.
  A vocabulary source an order of magnitude larger than the Fy! collection axes:
  city-scapes, serene, zodiac-in-kanji, geometric-city, palette-color, surreal,
  nostalgia, toilet-humor, sport-courts, true-meanings-brushed, asian-japanese-landscape.

- **191 brands**, as above.

## Two legal notes the queries surfaced

- `haeckel` is searched. Ernst Haeckel's *Kunstformen der Natur* (1899–1904) is
  public domain and safe — the same category as the Redouté plates Fy! resells
  8,145 times. Worth having on the safe list.
- `cassandre` is searched. A. M. Cassandre died in 1968, so his art-deco posters
  are **in copyright in the UK and EU until 2039** (life + 70). Art-deco travel
  poster *style* is fine; Cassandre's actual designs are not. This is the kind of
  distinction that gets a catalogue removed, so it goes in the notes now.

Also present and deliberately not served, consistent with the standing content
rules: a tail of adult and political queries (`hot naked girls`,
`beautiful nude woman`, `anti apartheid`, and similar). Noted only so that nobody
later mistakes their absence for an oversight.

## Corpus status after this harvest

| Source | Images | Titles |
|---|---|---|
| Fy! / iamfy.co | 6,448,043 | 3,582,363 (607,667 distinct) |
| Displate | 2,717,198 | none in sitemaps |
| **Total** | **9,165,241** | 3,582,363 |

The captioning cost estimates in `live_catalogue_6_4m.md` were quoted against
"8–9M images"; the real figure is now measured at **9,165,241**, so those numbers
stand as given (~$302 for all of it on 10 GPUs, ~$20 for a 500,000-image sample).

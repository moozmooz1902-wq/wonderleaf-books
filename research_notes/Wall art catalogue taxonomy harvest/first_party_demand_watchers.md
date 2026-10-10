# The first first-party demand signal: 2,142 watchers on the seller's own catalogue

10 October 2026. Found in `RELIST_old_wall_art_FINAL.csv`, the seller's eBay
unsold-listings export. It has a **Watchers** column, and nothing else in this
project does. Every "what sells" number in the earlier notes is competitor
listing volume — supply read as demand. A watcher is a real person who saved a
real listing on the seller's own account.

Script: `wallart-data/mine_unsold.py`.

## The headline, and it is not comfortable

| | |
|---|---|
| Listings with a title | **168,819** |
| Total watchers across all of them | **2,142** |
| Listings with at least one watcher | **1,770 — 1.05%** |
| Most watchers on any single listing | 12 |

Ninety-nine listings in a hundred were never saved by anybody. That is the
real baseline, and it is the number any new catalogue has to beat. It is also
consistent with the wall-art branch's finding that 424k listings were not
selling, and with 89% near-duplication being the likeliest reason.

Listing shape in this export: `Color=Black;Unframed Print Only`, **A3 only**,
£29.95 framed and £14.99 unframed — a different and narrower ladder than the
Fy!-style dump (black/white/oak × A4/A3/A2 at £19.99/£24.99/£29.99).

## Which words beat the base rate

With only 1,770 watched listings, a lift ratio computed over hundreds of words
throws up large numbers by chance, so each word is scored in Poisson standard
deviations above its expected count, and only ≥3σ is reported. 764 words with
at least 150 listings were tested.

| σ | watched / listings | rate | word |
|---|---|---|---|
| 10.0 | 27 / 467 | **5.78%** | movie |
| 7.2 | 13 / 213 | **6.10%** | chopper |
| 6.6 | 68 / 2,959 | 2.30% | **vintage** |
| 6.6 | 11 / 180 | **6.11%** | tour |
| 6.5 | 22 / 573 | 3.84% | band |
| 5.9 | 9 / 151 | **5.96%** | **charcoal** |
| 4.8 | 9 / 197 | 4.57% | noir |
| 4.6 | 13 / 370 | 3.51% | ray |
| 4.4 | 9 / 219 | 4.11% | artwork |
| 4.3 | 14 / 443 | 3.16% | **japanese** |
| 4.3 | 8 / 190 | 4.21% | mortal |
| 4.1 | 19 / 728 | 2.61% | **moon** |
| 3.8 | 9 / 262 | 3.44% | sexy |
| 3.6 | 7 / 185 | 3.78% | **greek** |
| 3.6 | 11 / 369 | 2.98% | watch |
| 3.2 | 13 / 520 | 2.50% | pop |
| 3.2 | 20 / 945 | 2.12% | man |
| 3.0 | 11 / 435 | 2.53% | **tower** |

And the duds, at ≤ −3σ with at least 1,500 listings:

| σ | watched / listings | rate | word |
|---|---|---|---|
| −4.9 | 22 / 5,690 | **0.39%** | funny |
| −3.9 | 6 / 2,479 | **0.24%** | cute |
| −3.8 | 10 / 3,019 | 0.33% | you |
| −3.2 | 4 / 1,662 | 0.24% | day |
| −3.1 | 13 / 2,886 | 0.45% | shirt |

## What this actually says

**1. "Funny" and "cute" are actively harmful here.** At 0.39% and 0.24%
against a 1.05% base, humour and cuteness perform two to four times *worse*
than the catalogue average. There are 5,690 "funny" listings earning 22
watchers between them. This is the clearest instruction in the data: the
humour register that works on t-shirts does not work on wall art. `shirt` at
0.45% says the same thing — t-shirt crossover content fails as wall art.

**2. The seller's buyers behave more like Displate's than Fy!'s.** movie,
band, tour, mortal, pop, chopper all over-perform sharply. That is fandom
demand, and it matches Displate's search queries being 91.2% named entities.

This qualifies what I wrote in `seller_data_structure_and_frames.md`. I said
there that we are in the décor business and Fy! is the reference. On the
evidence of **this** catalogue's own watchers that is too simple: the people
already buying from this seller lean fandom. The honest statement is that Fy!
is the right model for *catalogue craft* — varied titles, 5.2% repeats, real
technique vocabulary — while the *subject* mix that earns watchers here is
closer to Displate's. Those are separable: we can copy Fy!'s method and point
it at subjects this audience responds to.

**3. Most of the fandom words are unusable, but not all.** movie, band, tour
and mortal mean licensed posters and trademarked logos; `mortal` is Mortal
Kombat. We cannot make those. But **chopper** at 6.10% is motorcycles, which
is free to make, and the *aesthetic* of a vintage tour poster or a film-noir
panel is a design language, not a property.

**4. The safe, high-performing, generatable set** — words that beat the base
rate with no IP attached:

    vintage (2.30%) · charcoal (5.96%) · noir (4.57%) · japanese (3.16%)
    moon (2.61%) · greek (3.78%) · tower (2.53%) · chopper (6.10%)
    pop (2.50%, as pop-art treatment)

**charcoal is the standout.** It is a *technique*, not a subject, it runs at
5.7× the base rate, and it is one of the eleven techniques already catalogued
in `the_grammar_of_what_sells.md` ("visible grain, scribbly open fill").
A technique that lifts engagement independent of subject is the most
transferable thing on this list.

## Limits, stated plainly

- **Watchers are not sales.** They are the strongest first-party signal here,
  but a save is not a purchase, and no sales data exists anywhere in this
  project.
- **This is a within-catalogue comparison.** It says which listings *in this
  catalogue* got saved, which is shaped by what the catalogue already
  contains. A word absent from the catalogue cannot show up at all, so this
  can rank what was tried but cannot discover what was never listed.
- **The base rate is tiny.** At 1.05%, the counts behind even the significant
  words are small — 9 watched listings for charcoal, 7 for greek. The σ test
  guards against the worst of that, but these should be treated as leads to
  test, not settled facts.
- `ray`, `watch`, `man` and `artwork` are probably artefacts of other words
  they appear inside or beside, and are not read as instructions here.

## UK places over-perform by 7.5x — the evidence Displate could not give

`displate_catalogue_and_demand.md` concluded that the UK-place plan had no
demand evidence behind it, because UK place names are only 0.25% of Displate's
search queries. That conclusion was right about Displate and wrong as a verdict
on the plan. This catalogue settles it from the other side.

Testing the same unambiguous UK settlement names against the seller's own
watchers:

| | |
|---|---|
| Listings naming a UK place | **354** — 0.21% of the catalogue |
| Of those, watched | **28** |
| Watch rate | **7.91%**, against a 1.05% base |
| Expected if UK places were ordinary | 3.7 |
| Significance | **z = +12.6** |

Per place, where there are at least ten listings:

| rate | watched / listings | place | example |
|---|---|---|---|
| 16.7% | 2 / 12 | Devon | *Hope Cove, Devon* |
| 11.5% | 3 / 26 | Manchester | *Manchester Rooftop Panorama* |
| 10.0% | 1 / 10 | Cornwall | *Fowey And Fowey Estuary* |
| 9.1% | 1 / 11 | Whitby | *The 199 Steps Whitby* |
| 8.3% | 1 / 12 | Liverpool | *Bob Paisley — Anfield* (likeness, unusable) |
| 5.1% | 5 / 99 | London | *Empty London Underground* |
| 5.0% | 1 / 20 | Yorkshire | *Yorkshire Tea* (trademark, unusable) |

And separately, *Sheffield — The Steel City* sits sixth in the whole catalogue
on 5 watchers.

**So the seller has barely tried UK places — 354 listings out of 168,819 — and
the ones tried beat the catalogue average seven and a half times over.** That
is the strongest argument in this project for Phase 1, and unlike everything
before it, it comes from the seller's own buyers rather than a competitor's
shelf.

Two of the seven examples are unusable (a manager's likeness, a tea brand), so
the clean rate is a little lower than 7.91%. The counts are small. But the
direction is not in doubt at z = +12.6.

## The top-watched listings are almost all copyrighted

Worth stating plainly, because it is the trap this catalogue already fell into.
The twenty most-watched listings include Escher, Mackintosh, Kay Nielsen, Nick
Cave, The A-Team, Mortal Kombat, The Red Shoes, Mr Blobby, Metal Gear Solid,
Dracula AD 1972, Banksy, Snoopy, Picasso, Xanadu, The Wizard of Oz, Hockney,
The Italian Job, Shin Megami Tensei and an adult performer's name.

Almost every top performer is a property we cannot make. The clean exceptions
are the ones to build on: *Sheffield — The Steel City* (5), *Golden Cranes
Japanese Art* (6), *Cap de Formentor Mallorca* (4), *Sa Calobra Mallorca
Cycling* (3), *Paris-Roubaix* (3), *Rugby — A Game For Gentlemen* (3),
*Shackleton's Endurance By Night* (3), *The 199 Steps Whitby*, *Hope Cove
Devon*. Places, cycling, Japanese subjects, polar history, rugby.

The watcher distribution is also flat — the top 10 listings hold only 2.7% of
all watchers, the top 500 hold 40.7%. There is no blockbuster to chase. Breadth
is what carries this catalogue, which supports generating at scale, provided
the breadth is aimed better than it has been.

## Every title wastes 56% of itself

Measured across all 168,819 listings:

- **100%** end with the same 43-character tail,
  `Framed Wall Art Poster Canvas Print Picture`.
- Mean title length 77.4 characters; mean *real content* 33.3 characters.
- **The boilerplate is 56% of the average title.**
- **102,783 listings (60.9%) have their content cut to exactly 35 characters**,
  and 131,423 (77.8%) land in the 33–36 character truncation band — mid-word:
  *"Maurits Escher Relativity, Dutch Gr"*, *"Charles Rennie Mackintosh - Window "*,
  *"Golden Cranes Japanese Art Framed A"*.

eBay allows 80 characters. This catalogue spends 43 of them on a phrase
identical across every listing, then truncates the only part that distinguishes
one listing from another. It is both a search problem — eBay sees 168,819
near-identical titles — and a straightforward, free fix.

## The duplication problem is in the pictures, not the titles

Measured on the live catalogue's title stems (boilerplate removed):

| | |
|---|---|
| Distinct stems | 165,316 of 168,819 — **2.1% exact duplicates** |
| Grouped by first three content words | 142,492 groups — **15.6% near-duplicate** |
| Watch rate, duplicate titles | 0.76% (n = 6,293) |
| Watch rate, unique titles | 1.06% (n = 162,526) |

So the live catalogue's *titles* are largely distinct — far better than the
raw800k source data at 54.3% repeats. The wall-art branch's "89%
near-duplication" therefore cannot be about titles. It is about the images,
which is exactly what the grammar notes predicted: *"near-duplicate checking
must run on the picture, not the title — the same panel with different words
is still a duplicate."* Confirmed from live data.

Duplicate titles do carry a penalty (0.76% vs 1.06%), but it is modest. Title
duplication is not the main lever here.

## 12,731 listings are t-shirt slogans sold as wall art

The biggest near-duplicate clusters give the game away: *keep calm and* (141),
*just a girl who…* (138), *never dreamt sexy…* (115), *support your local*
(90), and repeated stems like *"think like a proton and stay positive"*,
*"never trust an atom they make up everything"*, *"no pants are the best
pants"*, *"yes i really do need all these dice"*.

Counting listings matching a slogan pattern (keep calm, just a girl/boy,
I love/hate, never trust/dreamt, funny, world's best, definition meaning,
my wife/husband/cat/dog, retired, don't, you…):

| | listings | share | watched | rate |
|---|---|---|---|---|
| Slogan-pattern | **12,731** | 7.5% | 50 | **0.39%** |
| Everything else | 156,088 | 92.5% | 1,720 | **1.10%** |

**z = −7.2.** The slogan block performs 2.8× worse than the rest of the
catalogue. These are t-shirt products listed in a wall-art category, and they
are the clearest ending candidates in the file — 12,731 listings earning 50
watchers between them.

Removing the block only lifts the overall base rate from 1.05% to 1.10%, so
this is not the whole problem. But it is 12,731 slots of selling-limit space
returning almost nothing.

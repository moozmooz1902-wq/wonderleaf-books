# eBay UK competitor teardown — what they do that we don't

Corpus: **600 listing titles + price ladders** harvested 2026-08-27 from the three
stores you named, via the route eBay's `robots.txt` explicitly permits for
`Claude-User` (`Allow: /sch/`, `/str/` open bar a few params). A generic browser
UA gets 403'd by their bot detection; I didn't route around that.

| Store | eBay ID | Items sold | Sample |
|---|---|---|---|
| T-Shirt Junky | `t-shirt-junky` | **349,000** | 400 titles |
| Lovetshirts / YTees | `love_tshirts` | **193,000** | 200 titles |
| Canvas Art Shop | `canvasartshop` | **91,000** | 400 titles + prices |

Raw corpus in [`../research/ebay_corpus/`](../research/ebay_corpus/), analysis
script `analyse.py` reproduces every number below.

---

## Finding 1 — Not one title in 600 exceeds 80 characters. Not one.

```
canvasartshop   n=200  mean=73.6  max=80  82% sit in the 70-80 band  over-80: 0
tshirtjunky     n=200  mean=63.9  max=80  29% in band                over-80: 0
ytees           n=200  mean=62.4  max=80  22% in band                over-80: 0
```

eBay's title limit is 80 characters and **Cassini indexes the title above almost
everything else**. Canvas Art Shop is engineering titles to land in the 70–80
window — they are treating the title as a fixed-width keyword slot and filling
it. That is not writing; that is packing.

This is the single cheapest thing to fix. If our titles are shorter than ~70
chars, we are throwing away indexable surface on every listing we own. If any are
over 80, they're being truncated and the tail keywords never index at all.

## Finding 2 — The catalogue is a GRID, not a list of ideas

**74% of tee titles end in one of exactly 17 fixed garment suffixes:**

```
100  Mens T-Shirt 100% Cotton        12  Mens 80% Cotton Hoodie
 67  Mens Cotton T-Shirt Tee Top      7  Mens Sweatshirt Jumper
 57  Mens Vest Tank Top               5  Womens Wider Cut T-Shirt
 19  Mens Light Cotton T-Shirt        2  Mens S/S Baseball T-Shirt
 13  Kids T-Shirt Childrens           2  Cotton Apron 100% Organic
 ... plus Ringer, V-Neck, Long Sleeve, Petite Cut, Kids Hoodie, Kids Sweatshirt
```

Every title is `{design stem} + {garment suffix}`. In a **400-title sample alone**,
28 design stems already appear on 2–3 different garments:

```
"if this flag offends you union jack britain"  -> T-Shirt | Vest Tank Top | Sweatshirt
"cafe racer biker motorbike motorcycle"        -> Cotton Tee | Light Cotton | Vest
"nordic wolf viking"                           -> T-Shirt | Light Cotton | Sweatshirt
"rasta lion jamaica reggae music jamaican"     -> Kids Tee | Cotton Tee | Light Cotton
```

**This is the answer to "how do I get to millions".** They are not inventing
millions of ideas. They invent one design and multiply it across a product grid:

```
LISTINGS  =  DESIGNS  ×  GARMENTS  ×  STORES
             ↳ size and colour are VARIATIONS INSIDE one listing, never separate listings
```

20,000 designs × 17 garments × 3 stores = **1,020,000 listings** from 20,000
pieces of art. That is the whole model.

## Finding 3 — Your two "competitors" are one operation

`tshirtjunky` and `ytees` share **22 identical design stems in a 200-title sample
from each** — 12% overlap on a 5% sample of either catalogue. Same designs, same
suffix vocabulary, same price architecture, different storefront names.

```
cafe racer biker motorbike motorcycle · nordic wolf viking · monkey magic
distressed union jack flag great britain · gothic skull and crow with arch and moon
los muertow sugar skull day of the dead · hello darkness my old friend
```

They run **one design library across multiple storefronts**. That is exactly the
"seven different stores" structure you described wanting. It multiplies
impressions per design without multiplying design cost, and it hedges account
risk. The library is the asset; the stores are just distribution.

## Finding 4 — This is a UK market, and it is nothing like the US POD market

Theme mix across 400 tee titles:

| Share | Theme | Share | Theme |
|---|---|---|---|
| **20%** | Funny / rude slogan | 8% | Animals & pets |
| **15%** | Biker / motorcycle | 8% | Retro TV & film |
| **14%** | Music & band-adjacent | 6% | Viking / Norse |
| **12%** | Skull / gothic | 4% | Birthday & age |
| **10%** | Flags & nationality | 4% | Military & aviation |

The recurring vocabulary is **Union Jack, Cafe Racer, Northern Soul, 2-Tone Ska,
Knights Templar, Monkey Magic, Spitfire, Guinness, Rasta Lion, Sons of Arthritis,
"as worn by"**. Biker + skull + Viking + Union Jack alone is over a third of the
catalogue.

**My earlier research pointed at the US Etsy/Amazon market — nurses, dachshund
moms, retro sunsets, boho arches. That is the wrong market for these stores.**
The UK eBay buyer here is a 35–65 year old man buying a biker tee, a Spitfire
tee, a rude slogan tee, or a birthday tee. That work still applies when you open
on Etsy/Redbubble/Amazon, which is why I've kept it — but eBay UK needs its own
theme bank, and it now has one.

## Finding 5 — The poster store's content is 52% out-of-copyright art

Of 200 Canvas Art Shop titles:

| Share | Source | Note |
|---|---|---|
| **52%** | Public-domain artists | Hokusai, Van Gogh, Goya, Klimt, Waterhouse, Lowry, Blake, Munch, Morris, Vermeer, Botticelli, Modigliani, Schiele, Mucha, Sorolla, Repin, Böcklin… |
| **26%** | Protected / living IP | **Banksy alone is 14%**, plus Peaky Blinders, Star Wars, Marvel, Akira, Totoro, Toy Story, Jaws, Predator, Pink Floyd, Fortnite |
| 8% | Celebrity likeness | "MUGSHOT" series — Elvis, Bowie, Jagger, Cash, Morrison |
| 20% | Generic decor | Highland cows, abstracts, botanicals, kitchen, seascapes |

**The 52% is the lesson and it is free.** A public-domain masterwork gives you the
one thing generated art cannot buy: a subject people already search for by name.
"HOKUSAI, THE GREAT WAVE OFF KANAGAWA" is a keyword with standing demand and zero
origination cost. There are tens of thousands of catalogued PD works — that is a
near-inexhaustible design library you can mine legally, at scale, today.

**The 26% + 8% is a risk they are carrying, not a strategy to copy.** Banksy
actively pursues sellers; celebrity mugshots engage personality/publicity rights;
Ghibli, Disney, Marvel and Lucasfilm all run active takedown programmes. Two of
their own titles ("BANKSY STYLE…", "…NOT BANKSY") show they know it. Copy the
*format* engine and the *PD* content strategy; do not copy the infringing 34%.

## Finding 6 — Format multiplication + a variation price ladder

The poster store multiplies each artwork across product formats exactly the way
the tee stores multiply across garments:

```
 93  CANVAS WALL ART            29  ART FRAMED POSTER
 45  FRAMED WALL ART            11  FLOAT EFFECT CANVAS
 25  CANVAS WALL ARTWORK        11  30MM DEEP FRAMED
```

`EDWARD HOPPER, NIGHTHAWKS` appears as framed poster, float-effect canvas, and
canvas painting print. `BANKSY BOY IN HOT AIR BALLOON` appears three times.
`GOLDFISH, HENRI MATISSE` twice. Same file, four to five listings.

And each listing carries a **size ladder as variations**, which is where "4 SIZES"
in the title comes from:

| Format | Price range | Read |
|---|---|---|
| Framed art poster | £7.99 – £39.99 | entry / traffic driver |
| Canvas wall art | £14.99 – £59.99 | core margin |
| Float-effect canvas | £24.99 – £49.99 | premium |
| Personalised photo canvas | £0.99 – £59.99 | £0.99 opening bid as a rank hack |

The low anchor pulls the "from £7.99" badge in search; the variations capture the
margin. One listing, one photo set, many SKUs.

---

## So what are we doing wrong?

I still can't read your two Claude chats — I have no access to conversation
history, and nothing was published as an artifact, so this is inference from the
symptom (huge catalogue, no conversion) plus what the corpus shows. Five gaps,
in the order I'd fix them:

1. **We're generating ideas; they're generating a grid.** If our pipeline emits
   one row per creative concept, we need ~1,000,000 concepts to reach a million
   listings. They need 20,000. Our unit cost per listing is ~50× theirs.
2. **Titles almost certainly aren't packed to 70–80 characters.** They never miss;
   this is deterministic string assembly, not creative writing.
3. **Sizes and colours are probably separate listings instead of variations.**
   That's both duplicate-listing exposure and a diluted "from £X" badge.
4. **Wrong theme bank.** US-POD niches don't map onto a UK eBay audience buying
   biker, Union Jack, Northern Soul and Spitfire.
5. **No named-subject anchor.** Their poster store gets 52% of its demand from
   subjects people already search by name. Original generated art has to create
   its own demand from nothing.

**Send me ~50 rows of what the current generator emits** (drop them in
`pod/samples/`) and I'll diff them against this corpus rather than inferring.

The build that follows from all of this is in [`README.md`](README.md).

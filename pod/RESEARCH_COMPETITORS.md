# Head to head with the sellers who are converting

eBay UK, 30 Aug 2026. Titles and sold counts copied verbatim from search
pages. Sold counts are what eBay shows on active listings.

## The sellers

| Seller | Scale |
|---|---|
| t-shirt-junky | 170,000+ listings |
| love_tshirts | 130,000+ listings, 63.1K feedback at 99.7% |
| canvasartshop | 92,000 items sold, 99.5% |
| bigboxart | 118,000 items sold |

## Why our 50,740 tees are not converting

Four differences, and all four matter.

### 1. Ours are words. Theirs are pictures.

Every one of our 50,740 is typography on black — `My Nan Is A Bouncer`.
Their sellers are images:

    Colourful Fantasy Wolf Face Mens T-Shirt 100% Cotton
    Blue Cosmic Skull Mens T-Shirt 100% Cotton
    A Fierce Fantasy Dragon Mens T-Shirt 100% Cotton
    Steampunk Scorpion Mens Cotton T-Shirt Tee Top
    A French Bulldog on a Skateboard Mens T-Shirt 100% Cotton
    Megalodon Prehistoric White Shark Dinosaur Mens Sweatshirt
    An Astronaut Cat in Outer Space Mens T-Shirt 100% Cotton
    Gothic Skull and Crow With Arch and Moon Mens T-Shirt

A shopper scrolling a grid of thumbnails sees a picture or a wall of text.
Text only wins if the joke lands in the thumbnail; a wolf face works at any
size. **This is most likely the main reason for the flat response.**

### 2. Their titles are keyword stacks. Ours are sentences.

    BIKER T-SHIRT Motorbike Motorcycle Cafe Racer Chopper Bike Mens Funny Skull Top   151+ sold
    Biker T-Shirt Mens Motorbike Funny Motorcycle Indian Triumph Chopper Cafe Racer
    Skull T-Shirt Mens Biker Tattoo Tribal Viking Demon Gym Heavy Metal Rock Death

Nine near-synonyms in 80 characters, catching every phrasing a buyer might
type. Ours spends the whole title on one phrasing:

    My Nan Is A Bouncer Mens Womens T-Shirt Funny Novelty Gift Tee Top

`Mens Womens T-Shirt Funny Novelty Gift Tee Top` is the same tail on all
50,740, so it adds nothing and eats 46 of the 80 characters. Their tail
changes per design and is made of *subject* words.

### 3. One design becomes eight listings, not one.

Same artwork, different garment — each a separate search:

    Mens T-Shirt · Vest / Tank Top · Hoodie · Sweatshirt / Jumper
    Long Sleeve · Kids / Childrens · Womens Petite Cut · Apron

    Eat Sleep Train Repeat Gym Training Top Mens T-Shirt      £10.48
    Eat Sleep Train Repeat Gym Training Top Mens Hoodie       £23.99
    Northern Soul Keeping the Faith Mens Hoodie               £23.99
    80th Birthday Limited Edition 1946 Cotton Apron           £15.47

Hoodies are £23.99 against £11.99. **We are using one of eight available
slots per design, and the cheapest one.**

### 4. Their subjects already have demand. Ours were invented.

They sell into scenes that people already search: biker, skull, Viking and
Norse, Northern Soul, 2 Tone and ska, Union Jack, gym, fishing, cycling,
hunting, cricket, reggae and Rasta, gothic, pagan, military and regiment,
autism awareness, atheism, vintage-year birthdays.

Ours were built by crossing occupations and hobbies with recipients. Some
of that is real. A lot of it is a search nobody performs.

## Wall art: the finding that changes the plan

canvasartshop's catalogue is overwhelmingly **public domain art**, and its
best sellers are the famous pieces:

    CANVAS WALL ART PRINT BANKSY BUTTERFLY BRAINS GIRL GRAFFITI      151+ sold
    Large Tree Teal Turquoise Leaves Black White Canvas Wall Art     120+ sold
    HOKUSAI, THE GREAT WAVE OFF KANAGAWA - FRAMED ART POSTER          62+ sold
    JAWS VINTAGE MOVIE POSTER CANVAS WALL ART PRINT                   61+ sold
    Peaky Blinders Thomas Shelby CANVAS WALL ART PICTURE PRINT        53+ sold

and the long tail is Hokusai, Waterhouse, Van Gogh, Monet, Turner, Lowry,
Hopper, Caravaggio, Goya, Mucha, Modigliani, Millais, Blake, William Morris,
Shishkin, Sorolla, van Eyck, Jacques-Louis David.

**These are out of copyright and free to reproduce.** We do not need to
generate them, guess at demand, or hope a diffusion model makes something
appealing. The demand already exists — people search "Van Gogh Sunflowers
print" — and the artwork is a download.

### The source is open and verified

The Metropolitan Museum publishes an open-access API, CC0:

    public domain paintings with images        42,579
    Turner                                      1,834
    Rembrandt                                     996
    Hokusai                                       584
    Van Gogh                                      427
    Monet                                         305
    Klimt                                          96
    birds                                      12,307
    Japanese woodblock                          4,601
    maps                                        1,148

Checked one image end to end: *Wheat Field with Cypresses*, Van Gogh 1889,
`isPublicDomain: true`, 4000 × 3184 px — **13.3 × 10.6 inches at 300 dpi**,
so it prints A3 natively and A2 with light upscaling. 8 MB JPEG, free.

The Rijksmuseum and the Art Institute of Chicago publish comparable
open-access sets, which takes the pool past 100,000 works.

**Zero generation cost. Zero GPU time. Zero IP risk. Existing demand.**
Nothing else we have discussed comes close on any of those four.

### What they sell that we must not copy

Banksy, Peaky Blinders, Jaws, Spider-Man, Totoro, Marvel, Elvis, Marilyn,
50 Cent mugshots. Their best seller is a Banksy. Several of their strongest
listings are film and TV property. That is their risk appetite, not ours,
and it is the one place where copying them is the wrong instinct.

Same on the tee side: their sold leaders are The Warriors, Mad Max,
Nostromo/Alien, Monkey Magic, The Prisoner, Kurt Cobain, Pablo Escobar,
The Italian Job, Bullet Club. **We match their formats, not their content.**

## What to do, in order

1. **Public domain art catalogue.** Harvest the Met, Rijksmuseum and Art
   Institute open-access sets. Filter to prints that will sell — paintings,
   Japanese woodblock, botanical plates, bird plates, antique maps. Title
   them the way canvasartshop does: `ARTIST, TITLE - FRAMED ART POSTER
   PAINTING PRINT 4 SIZES`. This is the fastest path to listings that
   convert, and it needs no pod at all.
2. **Re-cut the tee titles.** Same 50,740 designs, keyword-stacked titles
   instead of sentence titles. This is a Revise CSV, costs nothing, and
   tests the title theory against the same artwork.
3. **Garment types.** Every design that sells as a tee also becomes a
   hoodie, vest, sweatshirt, long sleeve, kids and apron. Eight listings per
   design from artwork we already hold, at up to £23.99.
4. **Image-led tee designs.** Wolves, skulls, dragons, Vikings, big cats,
   astronaut animals, steampunk creatures — the subjects both sellers run,
   in our own artwork. This is what the GPU pod is actually for.
5. **Then** the concept grid from `wallart_concepts.json` and the 4,469 UK
   places, which remain good ideas but are slower to prove than 1 and 2.

## Sources

- ebay.co.uk/sch `_ssn=t-shirt-junky` — 60 titles, sold counts
- ebay.co.uk/sch `_ssn=love_tshirts` — 60 titles, sold counts
- ebay.co.uk/sch `_ssn=canvasartshop` — 60 titles, sold counts
- ebay.co.uk/str/bigboxart
- collectionapi.metmuseum.org — counts and one full object verified
- Amazon UK bestsellers returned 503 to automated fetch; corroborated by
  UK retailer best-seller pages naming Van Gogh, Hokusai and Klimt

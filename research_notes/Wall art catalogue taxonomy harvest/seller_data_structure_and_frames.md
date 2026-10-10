# The seller's own competitor dumps, read properly — frames, prices, titles

10 October 2026. Written after being told the titles were in the files and I
had said they were not. They are. This note records what the three MEGA dumps
actually contain, column by column, and three things that change the build:
the frame set, the price ladder, and which competitor is worth copying.

Scripts: `wallart-data/extract_all.py`, `mine_titles.py`, `mine_templates.py`.
Extracted corpus: **13,727,739 rows across 93 CSVs** — displate 15 files /
7,000,890 rows, fy 71 files / 2,979,429 rows, raw800k 7 files / 3,747,420 rows.
Exactly 10.0% of rows in every set carry a title, because a listing is one
parent row plus nine variations (3 colours x 3 sizes).

*(An earlier draft said 9,507,654 rows across 98 CSVs. That was the count
appended by the second extraction run, not the total in the file, and 98 was
the glob count including files that were empty or errored. Verified: 93
distinct files, 93 entries in done.txt, no double-counting.)*

## What I got wrong, and why

The first pass took two columns and reported "Displate has no titles". Three
separate traps, all now handled in `extract_all.py`:

1. **The Fy! files have no header row.** Reading them with one consumed the
   first listing and made every title column read empty. Layout is now
   detected (`*Action(SiteID…` marks a Displate-style header) rather than
   assumed.
2. **Column count varies, 36 to 43.** Their own exporter does not quote
   descriptions containing commas, so `Los Angeles, Us, Geometric Illustration`
   spills across three fields. Rows are now parsed from both ends.
3. **Variation rows have a different shape** — a trailing junk field and no
   `Format`/`Duration` at all. The tail is now found by looking for
   `FixedPrice`, and failing that the first money-shaped field.

I had also checked Displate's *sitemaps* for titles, which genuinely have
none, and wrongly carried that over to the CSVs. Different source, different
answer.

## The frame set — black, white, oak — is already in the data

The parent row declares the variation set. Two different sets are in use:

| `RelationshipDetails` on the parent | parents |
|---|---|
| `Color=Black;White;Oak` + 3 sizes | **121,984** (the Fy! dump) |
| `Color=Black;White - Picture is for illustration;Unframed Print Only` + 3 sizes | 299,994 (the Displate dump) |

So **"white frame and oak frame" is not a new idea to introduce — the Fy! set
already sells exactly Black / White / Oak.** The image URLs carry the frame in
the path, and all three resolve:

    …/art-print-std-portrait-framed-black/<uuid>.jpg
    …/art-print-std-portrait-framed-white/<uuid>.jpg
    …/art-print-std-portrait-framed-oak/<uuid>.jpg

Counted in the dumps: black 244,002 · white 122,006 · oak 121,990 (Fy!), and
black 599,988 · white 299,994 (Displate). The main `PicURL` is always the
black one; the variation rows carry `Color=<name>=<url>`.

**Black has to stay the main image.** It is not a preference: the seller's
team runs a crop tool that finds the dark moulding and cuts everything outside
it (`wallart/size_contract.py` on the wall-art branch says so in as many
words). A white moulding is not dark enough for that tool to find.

### The geometry is an interface, and it is now reproduced exactly

From the size contract, and asserted in `wallart-data/frames.py`:

    canvas     2000 x 2000, wall #EDE9E3
    moulding   outer edge (406, 160) to (1593, 1840)  -> 1188 x 1680
    art area   (447, 201) to (1553, 1799)             -> 1106 x 1598
    prints     A4 2480x3507 · A3 3508x4961 · A2 4961x7015 at 300 dpi

`frames.py` renders black, white and oak on **identical geometry**, so the art
occupies the same pixels whichever frame is shown and the crop tool is
unaffected — only the moulding pixels differ. Verified: the rendered black
mockup's measured frame box is `(406, 160, 1593, 1840)`, matching the
contract exactly. The art is cover-fitted and centre-cropped into the
aperture, never shrunk inside it.

The white moulding needs a 3 px grey lip or it disappears into the #EDE9E3
wall; oak gets faint vertical grain so it reads as timber, not flat tan.

## The price ladder, extracted

Per variation, both dumps agree:

| | A4 | A3 | A2 |
|---|---|---|---|
| Framed (black / white / oak) | **£19.99** | **£24.99** | **£29.99** |
| Unframed print only | £8.99 | £12.99 | £16.99 |

Category 360, condition 1000, quantity 1, location UK, business policies
`1`/`1`/`1` — consistent with the shared facts in `CLAUDE.md`.

Every Displate row carries identical item specifics (Style `Modern`, Colour
`Colorful`, Room `Living Room, Bedroom`, Pattern `Abstract`), so eBay's own
filters do nothing for any of them. That is a gap, not a model to copy.

## The titles — and which competitor to learn from

Counted per listing, not per row (a listing is 10 rows):

| set | titled listings | distinct | repeats | mean length |
|---|---|---|---|---|
| displate | 700,089 | 442,729 | 36.8% | 62 chars |
| **fy** | **297,924** | **282,475** | **5.2%** | 50 chars |
| raw800k | 374,742 | 171,424 | **54.3%** | 74 chars |

Share of titled listings carrying each kind of word:

| | technique words | movement words | colour words | room words |
|---|---|---|---|---|
| displate | 102.5% (just "print") | 3.7% | 7.8% | 0.3% |
| **fy** | **142.6%** | **25.0%** | **31.4%** | **2.5%** |
| raw800k | 109.6% | 10.4% | 9.7% | 0.5% |

Fy!'s vocabulary, as a share of its titles: painting 12.0%, illustration
11.8%, watercolour 5.6%, drawing 2.5%, pastel 1.6%, collage 1.3%, oil 1.3%,
linocut 0.9%, risograph 0.2%. Movements: abstract 9.5%, vintage 7.5%, retro
2.0%, minimalist 1.6%, boho 0.5%. Colours: blue 6.0%, black 4.8%, white 3.6%,
pink 2.8%, gold 1.8%, pastel 1.6%, green 1.4%, purple 1.4%.

**Fy! is the one to copy the method from.** It is also the least formulaic:
its top 18 title skeletons cover only **8.2%** of its distinct titles, against
25.5% for Displate and 28.3% for raw800k. A flatter template distribution is
exactly what a near-duplicate check rewards.

## Two defects in the seller's own raw800k set

Both found in the title skeletons and both worth fixing before any of it is
reused:

- **Truncated mid-word.** `… definition meaning art prin`, `art pri`,
  `art pr`, `art p` — a builder that cut to a character count without
  respecting word boundaries. Thousands of rows.
- **URL fragments in titles.** The skeleton `compress {} a` occurs 635 times:
  `?auto=format%2Ccompress` from an image URL has leaked into the title field.

## Looking at the pictures: the two catalogues are different businesses

32 random images from each, viewed directly rather than measured.

**Fy! is décor.** Linocut birds, Matisse-style cut-paper botanicals,
watercolour coasts, vintage zoological engravings, travel posters with a cream
margin, hard-edge mid-century geometry, naive animal pattern. Repeated
orange-against-blue. Several cream-margin poster layouts. Also a few
**room-mockup photographs** mixed into the image set — those must be excluded
from any learning pass, they are not art.

**Displate is fandom and merch.** In one random sample of 32: a celebrity
portrait (Sting), a TV-series poster (*Suits*), MF DOOM, a cyberpunk character,
Jesus, an Isaiah verse, an Islam flag graphic, a Pornhub-styled "Shaftesbury
Ave" brand parody, stock photographs of a squirrel and the London skyline, and
quote typography. Most of it is unusable for us — likeness, trademark,
franchise, or religion.

That matches the demand evidence exactly: Displate's own search queries are
91.2% named entities (see `displate_catalogue_and_demand.md`). Displate sells
to people who arrive knowing the name of a thing. Fy! sells to people
furnishing a room. **We are in the second business, so Fy! is the reference
and Displate is mainly a negative example.**

UK places do appear in Displate's *supply* (a "Salisbury England" skyline, a
"London United Kingdom" photograph) despite having almost no demand there —
another reminder that supply is not demand.

## There is no "mid" column — checked

The seller said the files have "a title column, there's a mid there as well".
The titles were there and I had missed them. The "mid" was checked the same
way, across every header-bearing CSV:

The File Exchange header carries **36 columns and none of them is a MID**.
The only name containing those letters is `ItemID`, and across all 13,727,739
rows `ItemID`, `CustomLabel` and `StoreCategory` are **completely empty —
0.0% filled**. There is no merchant or media identifier with data in these
dumps.

The most likely referent is the Fy! collection file
`mid-century-modern-art-prints-and-posters.csv`, which is real and carries the
`Color=Black;White;Oak` set like the rest of that dump.

(A handful of rows — 8 to 50 out of 13.7M — show values landing in the wrong
column, e.g. `Modern` under MPN. Those are the unquoted-comma overflow rows,
and at that rate they confirm the parser handles the other 99.9995% correctly.)

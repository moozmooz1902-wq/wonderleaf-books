# Live image style analysis — Fy! (iamfy.co) and Displate

**Method:** the title exports have dead image URLs, so images were resampled from the live sites on
2026-10-08 and **looked at individually with an image-rendering read tool** — not inferred from titles
or filenames. 156 images were viewed: 108 from Fy! across 11 Shopify collections, 48 from Displate
spanning 2013–2026. Per-image notes were written immediately after each viewing batch.

Sources used:
- Fy! — `https://iamfy.co/collections/<handle>/products.json?limit=250` (Shopify JSON, HTTP 200 for all
  11 handles tried) and `https://iamfy.co/collections.json?limit=250`. Live CDN images on
  `cdn.shopify.com`, downloaded at the `_600x` resized variant.
- Displate — `https://sitemaps.displate.com/sitemap-non-licensed-products-index.xml` → monthly product
  sitemaps, which carry `<image:loc>` pointing at live `cdn.displate.com` artwork URLs; product metadata
  (category, tags, orientation) read from `https://displate.com/displate/<id>`.

**One important negative result up front:** Displate's browse pages are behind Cloudflare bot management.
`https://displate.com/browse-collections/popular/<category>` 308-redirects to `/search?q=verified+creators`
and returns a client-rendered shell with zero image URLs; `displate.com/robots.txt` also disallows
`/displates/`. No attempt was made to defeat this. The Displate sample therefore comes from the public
sitemap plus individual product pages, which means it is a **random sample of the non-licensed catalogue,
not a subject-balanced one** — see Gaps.

---

## Q1. What does the art actually look like, by subject group?

### Takeaway

Fy! is a curated, decor-led catalogue with a strong and consistent house look: portrait 3:4, flat
artwork files with no frame or room mockup, warm-neutral or single-flat-colour grounds, restrained
5–8 colour palettes, and a heavy bias toward *handmade-medium artefacts* (visible brush drag, paper
tooth, print mis-registration, cut-paper edges) rather than photographic realism. Displate is the
opposite: a near-unmoderated 5:7 full-bleed marketplace with no shared palette, no margins, a large
black-ground / high-contrast population, and a visible drift from 2013-era pop-art-halftone geek posters
to 2024–26 AI-photoreal hyper-saturated landscapes.

### Group-by-group table

All counts are images actually opened and looked at.

| Group (Fy! handle) | N | Composition | Palette | Medium | Detail | Background | Text | Ratio |
|---|---|---|---|---|---|---|---|---|
| `botanical-art-prints` | 10 | Single centred specimen (4), all-over crop-to-edge (3), row-of-three (1), figure (1). 2/10 carry a printed internal border | 5–8 colours. Sage/forest green, cream, terracotta, cobalt, orange, mustard recur. One strictly 2-ink | Lino/relief print (2), flat vector + riso grain (2), gouache/acrylic on canvas (2), collage (1), photoreal (1), line + watercolour blob (1), flat 3-colour (1) | Polarised: very high (engraving collage, pond scene) or deliberately minimal (one contour line) | Cream/off-white (5), flat mottled colour (3), white (2) | 1/10 (a lino poster with carved art-nouveau caps) | 3:4 except one 0.707 |
| `abstract-art-prints` | 10 | Full-bleed non-representational field (5), inset image with margin (1), subject cropped by frame (3), top-down photo (1) | Two camps: muted 4–6 colour (navy/teal/oatmeal/cream) and full-chroma 15+ (naive folk painting) | Impasto/palette-knife oil (2), acrylic scumble on canvas (2), cut-paper collage (1), flat vector (2), photography (2, one B&W), decorative oil pastiche (1) | Very wide spread; two images have essentially no detail | Flat oatmeal, scraped canvas, pure white, blush | 2/10 (a text-over-impasto slogan; a Bauhaus poster lockup) | 3:4, one 0.707 |
| `animals-art-prints` | 10 | Single centred animal, bottom-anchored and often cropped at the bottom edge (5). Repeating-motif field (2). Scene (2) | Flat-ground portraits use 1 muted ground colour + a warm accent cluster. Scenes run 8–10 | Photoreal-collage (2), flat digital collage w/ paper texture (2), gouache/dry-brush (2), impasto (1), riso-grain screenprint (1), B&W photo (1), licensed line art (1) | High on the photoreal-collage birds; very low on the minimal ones | **Flat single-colour ground is the dominant device** (khaki, dusty teal, salmon, ochre) | 2/10 (a speech bubble; a hand-lettered world map) | 3:4 (7), 1:1 (2), 4:3 (1) |
| `birds-art-prints` | 10 | Single bird centred and bottom-cropped (4), two-bird symmetrical pair (2), inset exhibition panel (1), extreme-minimal (1) | Muted 5–8. Cream, slate blue, rust, coral, sage dominate. Two images are strictly 2-colour | Relief/linocut (2), painted photoreal + collage (2), flat vector gradient (1), digital collage of engravings (1), folk/mid-century collage (2), public-domain engraving scan (1), AI chinoiserie in a poster frame (1) | Bimodal again: feather-by-feather or three flat shapes | Flat cream, chalky teal, layered patterned hills, pure white | 3/10 — incl. the most type-heavy sheet in the whole sample | 3:4 (8), 1:1 (2) |
| `cities-art-prints` | 10 | **Inset image on a sheet with a bottom caption band (4)** — the single most repeated layout. Full-bleed painting (4). Letterform/typographic (1). Photo (1) | Travel-poster group: 4–6 flat inks. Painting group: 10+ high chroma | Flat vector screenprint (2), gouache/oil impasto (2), naive acrylic (1), pen-and-ink (1), brush-and-ink one-colour (1), watercolour + line (1), photo (1), litho scan (1) | High in the ink and vector work; the painterly ones are loose | Cream or white sheet around an inset panel; otherwise full-bleed scene | **8/10** — this is the text-heavy group | 3:4 (8), 0.707 (1), 4:3 (1) |
| `coastal-art-prints` | 10 | **Figure seen from behind, face never shown (5)** — the strongest single convention found. Framing foliage vignette (1). Empty-sky negative space (2) | Terracotta, cream, sage/olive, turquoise, blush. Consistently warm and low-saturation | True watercolour on textured paper (4), gouache (3), flat vector/digital (2), wet-in-wet naive (1) | Low to medium; figures are shapes, not portraits | Bare white paper (3), flat gradient sky (2), full scene (5) | 2/10 (one slogan poster, one "CAPRI / ITALY" caption) | 3:4 (8), 1:1 (1), 0.783 (1) |
| `vintage-art-prints` | 10 | Inset panel + caption (2), all-over repeat (2), flat-black ground with symmetrical subject (2), full-bleed scene (3), photo (1) | Two families: dusty rose/terracotta/cream monochrome, and black-ground with olive/cream/apricot | Period photo (1), flat gouache digital (2), stained-parchment pastiche (1), screenprint w/ engraved hatching (1), single-ink repeat pattern (1), distressed litho + neon type (1), greyscale engraving (1), collage on black (1), Arts-and-Crafts flat (1) | Usually high — "vintage" here means dense ornament | Aged paper, flat black, cream sheet | 5/10 | 3:4 (7), 1:1 (2), 4:3 (1) |
| `art-prints` (generic) | 8 | Inset + text band (2), type-only (1), full-bleed (4), square collage (1) | Mixed; the photoreal-collage bird again uses one flat khaki ground | Impasto oil, flat vector, photoreal collage, mixed-media collage, hand-drawn type, geometric vector | Wide | Flat khaki, linen grey, blush paper, black, oatmeal | 5/8 | 3:4 (7), 1:1 (1) |
| `bestselling-wall-art` | 10 | **Inset panel + serif caption (2)**, full-bleed landscape (4), single subject on plain ground (2), type-only (1), object study (1) | The best-sellers skew *muted*: peach, slate, dusty mauve, terracotta, ice-blue. The two high-chroma entries are gouache paintings | Flat vector landscape (3), gouache (2), charcoal (1), acrylic on board (1), watercolour (1), impressionist oil (1), marker lettering (1) | Mostly medium; flat vector landscapes have almost no texture | Cream sheet, white paper, scraped board | 4/10 | 3:4 (8), 4:3 (2) |
| `illustration-art-prints` | 10 | Interior/scene with high object count (4), single object centred (2), cropped portrait (2), oval vignette (1), flash-sheet grid (1) | Blush pink + green is the signature pairing. 5–10 colours | Flat digital w/ soft airbrush shading (4), tattoo flash linework (1), loose digital brush (1), cut-paper collage (1), dry-brush two-colour (1), decorative flat (2) | High object count, low surface texture | Blush pink, cream plaster texture, flat tan, flat black | 2/10 | 3:4 (8), 1:1 (1), 1.41:1 (1) |
| `watercolor-art-prints` | 10 | Subject cropped by all four edges (3), bottom-left anchored with white above (2), all-over scatter (1), pure abstract bands (2), scene (2) | Sage/eucalyptus greens, indigo/teal, or coral + teal. Two images use only 2 pigments | **Real watercolour artefacts in 6/10** (granulation, hard dried rims, backruns, cold-press tooth, white speckle). Digital airbrush "watercolour" in 2/10. One public-domain scan. One not watercolour at all | Low — this group is the least detailed overall | Pure white paper (6), full-bleed wash (4) | 1/10 (a shop sign) | 3:4 (6), 0.624 (2), 1:1 (1), 0.733 (1) |
| **Displate** (sitemap sample, mixed categories) | 48 | **100% full bleed, 0/48 with any printed margin or inset panel** | No house palette. Large black-ground population (7/48 pure black). High-contrast 2–3 colour lockups common | 2013–15: posterised photo + benday halftone, vector tattoo flash, ink drawing. 2017–21: distressed-texture illustration, public-domain scans, photography, map vectors. 2022–26: AI-photoreal, paper-cut vector, slogan lockups | Extremely wide — from a 4-colour vector leaf tile to a macro frog with per-pore detail | Pure black (7), pure white (4), photograph (6), grunge texture (5), flat colour (rest) | 17/48 | 5:7 uniformly (served 460×640 = 0.719; master 857×1200 = 0.714) |

### Cited findings (first-hand observation)

- **Fy! product JSON carries exactly one image per product** (659 of 660 products sampled across the 11
  collections had `images` length 1). That image is the **flat artwork file** — in all 108 viewed there
  was no frame mockup, no room scene, no watermark, and no shadow. Whatever the catalogue's merchandising
  does, the asset itself is the art alone.
- **Fy! aspect ratios of the supplied image assets** (n=108): 750×1000 ×68, 753×1000 ×13, 1000×1000 ×11,
  1000×750 ×5, 707×1000 ×4, 749×1000 ×2, 624×1000 ×2, 783×1000, 1000×707, 733×1000. That is
  **~79% portrait 3:4, 10% square, 6% landscape, 5% ISO-A (0.707)**.
- **Displate is uniformly 5:7.** All 48 served at 460×640; the product-page master was 857×1200. Nothing
  in the sample deviated.
- **The "flat single colour behind a rendered subject" device** appears in `animals`, `birds` and the
  generic `art-prints` group (all_01, ani_05, bir_01, bir_02, best_05): a photoreal or tightly painted
  animal on a flat khaki, dusty-teal, cream or chalky-teal field. It is the cheapest-looking high-value
  formula in the Fy! sample and recurs across three different collections.
- **The figure-seen-from-behind convention** is near-universal in coastal and strong elsewhere:
  coa_02, coa_03, coa_04, coa_05, coa_07, coa_10, cit_02, all_03, ill_01. Faces are avoided. This both
  sidesteps likeness problems and removes the single hardest thing for a diffusion model to get right.
- **Displate deliberately bleeds type off the plate edge** — and sometimes loses it. In dp_33 the quote
  "I HAVE NOT YET BEGUN TO DEFILE MYSELF" is **cropped on both left and right in the served 5:7 image**,
  losing letters. all_07 on Fy! does the same thing on purpose with "LE MANS". Direct evidence that
  type laid to the edge is a real failure mode in this market, not a theoretical one.
- **Public-domain scans are listed as catalogue items on both sites.** On Fy!: bir_04 (early-19th-c
  hand-coloured parrot engraving with its copperplate caption), cit_06 (1920s Underground litho poster),
  wat_04 (a signed, dated 1916 modernist watercolour). On Displate: dp_13 (a 1942 US patent drawing),
  dp_19 (a 19th-c chromolithograph). This is a meaningful share of what "vintage" means on these sites.
- **Licensed/IP material sits inside ordinary subject collections.** ani_03 is a licensed children's
  character carrying a printed rights credit; best_04 reproduces a Winnie-the-Pooh exchange; on Displate,
  dp_27 (a named video game), dp_38 (a named film), dp_47 (named song lyrics). Do not treat the presence
  of these in the sampled collections as licence to generate similar.

### Inferences

- Fy!'s coherence does not come from one style — the media are genuinely varied — it comes from three
  held constants: **flat artwork file, portrait 3:4, and a restricted warm-neutral palette anchored on
  cream/sage/terracotta**. A generated catalogue could vary medium widely and still read as one shop if
  it held those three.
- Displate has **no house style to copy** and, on the evidence of the 2024–26 slice, is converging on
  AI-photoreal hyper-saturation. Copying it would produce exactly the undifferentiated output the
  wall-art branch already blames for 424k non-selling listings.
- The bimodal detail distribution inside almost every Fy! group (either feather-by-feather or three flat
  shapes, rarely in between) suggests the market rewards a clear commitment either way. The middle —
  moderately detailed, moderately textured — was the least represented register in the sample.

### Gaps

- Fy! collection **handles were sampled, not the whole collection**: 10 products per collection, chosen
  at even intervals through the 250-product listing, so this is a systematic spread but not random.
  Collections return a 250-product cap; actual collection sizes are unknown from this endpoint.
- **`watercolor-art-prints` returned only 141 products** against 250 for the other ten, so that group
  is drawn from a smaller pool.
- Several per-group conclusions rest on 10 images. In particular the "2/10 carry an internal border"
  and "5/10 figure-from-behind" figures are indicative, not measured rates.

---

## Q2. Prompt-ready style specifications per group

Fragments name the medium and its physical artefacts. They are written to be concatenated with a subject
and an aspect-ratio instruction. **None of these describe a specific existing picture**; they describe
recurring, generic craft registers observed across the sample.

### Botanical
1. `two-colour linocut on warm kraft paper, carved gouge marks breaking every stroke, ink sitting unevenly with visible roller mottle, no tonal gradation, registration slightly soft`
2. `flat mid-century shapes with an overall risograph speckle in every fill, no outlines, cream paper ground, subject cropped by the top and bottom edges, five flat inks`
3. `hairline uniform-weight black contour drawing of a single stem, with three loose sage-green watercolour shapes offset behind it, granulating pigment pooled into hard dried rims, bare white paper across the outer quarter of the sheet`
4. `gouache on canvas, visible weave and brush drag, petals filled with hand-drawn pattern — dots, scallops, fine stripes — on a scumbled pale sage ground`

### Abstract
1. `thick impasto oil laid with a palette knife, raised ridges catching light, slab edges left unblended, colour scraped rather than mixed`
2. `cut-paper collage, each shape a different scanned texture — speckled card, gold leaf, hand-painted stripe — torn and cut edges visible, assembled on bare white`
3. `flat geometric planes in five inks on a warm oatmeal ground, hard edges, no gradient, long cast shadows as solid shapes, generous oatmeal margin around the composition`
4. `dry acrylic scumble over canvas weave, broken colour, bare canvas showing through the thin passages, no subject, soft vertical column of lighter tone`

### Animals
1. `tightly rendered animal, fur or feather drawn stroke by stroke with a glossy catchlight in the eye, isolated on a flat single-colour khaki ground with a faint ghosted botanical watermark, subject bottom-anchored and cropped at the lower edge`
2. `flat digital collage, every shape filled with a soft paper grain, no outlines, stylised foliage in four muted greens and a plain sun disc`
3. `chalky gouache dry-brushed over a salmon ground, birds reduced to five flat shapes with a sponged edge, repeated across the field with no focal point`
4. `high-key black-and-white photograph, background blown to pure white so the animal floats with no visible edge, head-on, centred`

### Birds
1. `single-colour relief print, rust ink on warm putty, hand-carved border of triangles and dashes framing the motif, white gouge marks doing all the detail, no mid-tones`
2. `heavy black blockprint on cream, the inked plate edge visible as a soft stained rectangle, the subject a near-solid black mass with scratched white gouges for feathers`
3. `folk collage, hills layered as bands each filled with a different printed pattern — grids, scallops, stippled dots, fine botanicals — birds drawn as banded scallop shapes in black and teal`
4. `flat vector on a vertical gradient sky from pale blue to peach, soft grain shading inside clean shapes, cream cloud forms, five colours`

### Cities
1. `five-ink screenprint look with deliberate off-register grain, strong black shadow shapes, one-point street perspective, cream sky`
2. `brush and ink in a single blue plus a darker navy line, loose gestural marks, large areas of bare cream paper, visible brush ends and scribble`
3. `thick gouache, flat loaded strokes with hard visible edges and no blending, high-chroma facades in pink, yellow, mint and lilac against cobalt water`
4. `impasto oil rooftops, palette-knife slabs for cloud and zinc roof, apricot and dove-grey, horizon placed just above centre`

### Coastal
1. `transparent watercolour on cold-press paper, visible tooth, soft bleeds and backruns, white paper reserved for highlights, terracotta and sage and turquoise, figure seen from behind`
2. `loose watercolour with large areas of bare white paper standing in for sky, pigment pooling at the wet edges, about twelve confident sienna washes making the whole figure`
3. `chalky washed-out gouache, every form a soft-edged patch with no outline, apricot and blush and dusty blue, low contrast`
4. `smooth flat digital render, pastel facades with hand-drawn wobbly white window outlines, flat teal sky gradient occupying the top half completely empty`

### Vintage
1. `single-ink seamless repeat in dusty terracotta on speckled cream paper, pencil-line drawn motifs, no focal point, no margin`
2. `screenprint with fine engraved hatching for feather and cloud detail, five flat inks, coral sky graded to cream`
3. `stained and foxed parchment ground, all black ink, decorative scrolled border, bold brush-ink figure drawing`
4. `flat-black ground with a bilaterally symmetrical subject whose interior is filled with cut-out botanical illustration in blush, coral, olive and cream`

### Illustration
1. `flat digital illustration with soft airbrush shading inside clean shapes, blush-pink ground, pattern on pattern, high object count, no outlines`
2. `traditional tattoo flash: bold uniform black outline, stipple shading, flat fills, specimens laid out in a loose grid on speckled off-white paper`
3. `cut-paper collage with visible paper grain, fibres and scratches in every piece, five flat colours, subject cropped at the top edge`
4. `single object painted in hand-drawn stripes with dry-brush break-up where the bristles skipped, two colours, warm oatmeal ground, centred with a generous margin`

### Watercolour
1. `loose watercolour with granulating pigment pooling at the wet edges, soft bleed into damp paper, white paper showing through, hard dried rims where one wash met another`
2. `pure horizontal wet-into-wet bands with no subject, strong cold-press paper tooth, white speckle where pigment skipped the tooth, bloom edges between bands`
3. `two tonal passes only — a strong sage-green branch in front and a pale ghost branch behind — each leaf a single confident brushstroke with a crisp dried edge, bare white paper across the upper half`
4. `translucent layered washes multiplying where they overlap, coral over teal, granulated dark passages, bands reading as ridges`

### Displate-register (use sparingly — see Q4)
1. `pure black ground, three colours only, high-contrast silhouette with one red accent element`
2. `layered paper-cut landscape, twelve stacked flat bands with soft drop shadows between layers, dusty rose sky, no detail inside any band`

---

## Q3. House-style conventions that recur across subjects

Observed in two or more groups:

1. **Flat artwork file, no frame, no mockup, no shadow.** 108/108 Fy!, 48/48 Displate. **Copy this.**
2. **Portrait 3:4 as the default** on Fy! (~79%), with square used for the decorative folk/collage
   register specifically. **Copy this**, and make square a deliberate sub-format rather than an accident.
3. **Warm-neutral ground as the base layer** — cream, oatmeal, putty, blush, kraft — appearing in every
   single Fy! group. Pure white is used, but mostly for watercolour and line work. **Copy this.**
4. **Restricted palette.** The median Fy! image sits at 5–8 colours; several are strictly 2. The
   high-chroma 15+ images are always *paintings*, where the medium justifies it. **Copy this**, and tie
   chroma to medium rather than letting it float.
5. **Named physical medium artefacts rather than smooth digital finish.** Carve marks, roller mottle,
   canvas weave, paper tooth, dry-brush skip, torn paper edge, riso speckle, mis-registration. This is
   the clearest thing separating Fy! from Displate. **Copy this — it is the highest-value convention here.**
6. **Subject bottom-anchored and cropped by the lower edge**, with the empty space at the top. Seen in
   botanical, animals, birds, coastal, watercolour. **Copy this.**
7. **Figure from behind, face hidden.** Coastal, cities, illustration, generic. **Copy this** — it is
   both a style convention and a practical hedge against face artefacts and likeness risk.
8. **The inset-panel-plus-caption-band sheet**: image inset with ~5% side margins and a 15–28% bottom
   band carrying a place name in letterspaced caps. 10 of 108 Fy! images. **Copy the layout, but see
   Q5 — the type must be composited, not generated.**
9. **Bimodal detail** — commit to either dense or near-empty. **Copy this.**
10. **Do not copy:** Displate's full-bleed-with-no-margin-at-any-size discipline (it demonstrably crops
    type), its black-ground default, and the 2024–26 AI-photoreal hyper-saturated landscape look, which
    is precisely the saturated register the near-duplication problem lives in.

### Margins and safe area

- **Fy! designs with a margin far more often than Displate does.** Of 108 Fy! images, 10 use a formal
  inset panel with a caption band, a further ~8 carry a printed internal border (a coloured band inset
  4–6% all round), and many of the watercolour and line works simply leave 12–25% bare paper. The rest
  are full-bleed.
- **Displate: 0 of 48 had any printed margin or inset panel.** Everything bleeds.
- Practical consequence: a 3:4 Fy!-register asset can safely carry type in a bottom band. A 5:7 Displate
  asset cannot, and dp_33 is the proof.
- Because Fy! is 3:4 and Displate is 5:7, **one master cannot serve both without a crop**. Generating at
  3:4 and centre-cropping to 5:7 removes ~5% of width; any composition relying on edge content or edge-set
  type will break. Generate per-format, or hold all meaningful content inside a 5:7 safe box.

---

## Q4. What FLUX.1 schnell will struggle to render

Ranked by how often the convention appears in the sample, so the cost of each weakness is visible.

**Cannot be relied on at all — composite instead of generating:**

- **Fine lettering.** The exhibition-poster sheet (bir_09) carries six lines of serif copy at four sizes
  plus a transport roundel. The hand-lettered world map (ani_04) is built from *hundreds* of tiny place
  names. The typographic letterform (cit_04) has ~20 hand-lettered place names inside a single letter's
  stroke. The patent scan (dp_13) has numbered callouts and a typewriter caption block. **schnell will
  not produce any of these legibly.** 17/48 Displate and roughly 32/108 Fy! images in the sample contain
  text — this is not a niche problem.
- **Maps with place names.** Both the Fy! typographic map and the two Displate city maps (dp_21 "HAMILTON
  / ON, CANADA", dp_25 "CRETEIL" with coordinates) depend on a correct road network *and* correct
  lettering. Road networks are geometric and place names are text; schnell is weak at both.
- **Coordinates, dates, dimensions, Latin binomials.** vin_07's "CAESALPINIA PULCHERRIMA", dp_41's airport
  IATA tile and lat/long. These are short strings where a single wrong character is obvious.

**Unreliable — expect a high reject rate:**

- **Precise geometry.** The Bauhaus register (abs_05, all_08) needs true straight edges, consistent
  perspective on stair flights, and clean circles. The periodic-table lettering piece (dp_36) and the
  airport diagram (dp_41) need exact rectangles. schnell wobbles on all of these.
- **Recognisable architecture.** cit_09 (a named London store facade), wat_07 (a specific domed skyline),
  cit_03 (an identifiable Art Deco spire), vin_08 (half-timbered European street). schnell produces
  plausible-but-wrong buildings; for the travel-poster register this is sometimes acceptable and
  sometimes fatal, depending on whether the title names the landmark.
- **Repeat patterns that actually tile.** vin_05 and dp_09 are seamless repeats. schnell will produce a
  pattern-*looking* field, not a tileable one.
- **Exact colour counts.** The 2-ink linocut and 3-colour vector registers depend on *not* introducing a
  fourth colour. Prompting a strict ink count is unreliable; post-quantisation is more dependable.
- **Bilateral symmetry.** vin_09's moths and ill_05's oval vignette are near-symmetrical. schnell drifts.

**Should be fine, and is where the value is:**

- Watercolour granulation, wet edges, backruns, paper tooth, white speckle.
- Impasto, palette-knife slabs, canvas weave, dry-brush skip.
- Lino/relief gouge marks, ink mottle, plate-edge staining.
- Riso speckle, halftone, deliberate mis-registration.
- Flat vector landscape bands, layered paper-cut, flat single-colour grounds.
- Animals, birds, botanicals, abstract fields, figures seen from behind.

**Recommended division of labour:** generate the *image panel* with schnell in a chosen medium register,
then composite the caption band, place name and any border as vector type at build time. That reproduces
the most repeated Fy! layout exactly while keeping every string under program control — and it is also
the cheapest defence against near-duplication, since the same panel plus different type is still a
duplicate and will be caught by a panel-level similarity check rather than a title-level one.

---

## Q5. Honest gaps and limits

**What was reached:** all 11 requested Fy! collection handles returned HTTP 200 from the Shopify products
endpoint — `botanical-art-prints`, `abstract-art-prints`, `animals-art-prints`, `birds-art-prints`,
`cities-art-prints`, `coastal-art-prints`, `vintage-art-prints`, `art-prints`, `bestselling-wall-art`,
`illustration-art-prints`, `watercolor-art-prints`. None 404'd, so no handle substitution was needed.

**What was blocked:**
- **Displate category/browse pages.** `https://displate.com/browse-collections/popular/<category>`
  308-redirects to `/search?q=verified+creators`; the destination sets a `__cf_bm` Cloudflare bot-management
  cookie and returns a client-rendered page containing no image URLs. Seven categories were tried
  (floral, abstract, animals, nature, cityscapes, landscapes, minimalistic) — all behaved identically.
  **Recorded as blocked; no attempt was made to work around it.**
- `displate.com/robots.txt` disallows `/displates/` (plural). Individual product pages at `/displate/<id>`
  (singular) are not disallowed and were used for metadata only.
- `sapi.displate.com/artworks/limited` works but returns only the *limited-edition* catalogue, which is
  heavily licensed IP (films, games) and unrepresentative. It was not used for the sample.

**Counts — exactly what was looked at:** 156 images, individually opened and viewed.
108 Fy! (10 per collection except `art-prints` at 8) + 48 Displate.

**Where conclusions rest on few examples — read these with caution:**
- **Every Fy! per-group finding is n=10 or n=8.** Proportions inside a group ("5/10 figure from behind")
  are indicative of a convention, not a measured catalogue rate.
- **The Displate sample is not subject-balanced.** It was drawn randomly from 8 monthly sitemaps spanning
  2013-04 to 2026-10, 6 per month. Because the browse pages were blocked, there was no way to sample by
  category. The resulting 48 span 20+ Displate categories with 1–4 images each, so **no per-subject claim
  about Displate is supportable** — only whole-catalogue observations (full bleed, 5:7, no shared palette,
  era drift) and those rest on 48 images.
- **The era drift claim (pop-art halftone → AI-photoreal)** is based on roughly 6 images per era band.
  The direction was consistent across the bands sampled, but the sample is small.
- **Fy! aspect ratios are the dimensions of the supplied image asset**, not necessarily the printed
  product. Fy! sells multiple print sizes; the mapping from asset ratio to sold ratio was not checked.
- **Medium attributions are visual judgements from a 600px-wide render.** "True watercolour" versus
  "digital watercolour" was called on the presence of paper tooth, granulation and hard dried rims
  (wat_03, wat_05, wat_07, coa_03, coa_05, best_03) versus their absence (wat_01, wat_02). At this
  resolution that distinction is reliable; finer calls — oil versus acrylic, for instance — are not, and
  have been written as "oil/acrylic" where uncertain.
- **Several images in the sample are likely AI-generated already** (bir_09, coa_06, wat_10, dp_37,
  dp_39, dp_43, dp_46 all show the characteristic signatures). Where they do, they are evidence of what
  these sites currently *accept*, not of a human craft tradition to learn from.

**Scope note:** this is a study of style conventions, not of artworks. No artist is named anywhere in
these notes as someone to imitate, and no prompt fragment above describes a specific existing picture.
Where a sampled image carried a rights credit, a licensed character, a film or game title, or song
lyrics, it is flagged in Q1 as an IP risk to avoid rather than a pattern to follow.

**Disk and cleanup:** 156 images were downloaded to
`/tmp/claude-0/-home-user-wonderleaf-books/af9e3fdd-8129-53fc-a69c-916ae3713d2b/scratchpad/livesample/`
— 12 MB (Fy!, `img/`) + 9.7 MB (Displate, `imgdp/`) = **21.7 MB total**. All image files were deleted
after viewing. The per-image observation notes that this document is built from were retained under
`scratchpad/obs/`.

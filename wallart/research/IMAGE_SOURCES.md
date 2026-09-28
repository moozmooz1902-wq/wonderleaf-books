# Free, commercially usable image sources for wall-art print-on-demand (UK seller)

Audit date: 28 Sep 2026. Every count below came from a live API call or a bulk-data download made in this session, unless it is marked *(source's own figure)*. Machine-readable summary: `image_sources.json`. Sample downloads: `samples_pd/` (with `manifest.json` giving the source URL, pixel size and print size for each).

Print sizes: **A3 at 300 dpi = 3508 x 4961 px**, A4 at 300 dpi = 2480 x 3508 px. Viewers usually stand back from wall art, so 200 dpi is acceptable in practice. A3 at 200 dpi = 2339 x 3307 px.

---

## 1. Ranking (usable volume x licence safety)

| # | Source | Licence | Usable images | Typical max px | A3 at 300 dpi? |
|---|---|---|---|---|---|
| 1 | **The Met Open Access** | CC0 | ~490k museum-wide *(Met figure)*; very strong on birds, horses, flowers, landscapes | median 2,670 (range 680-4,759) | Rarely. A4 yes for ~30%; A3 at ~200 dpi |
| 2 | **Smithsonian Open Access** | CC0 | ~73k CC0 art images in SAAM, Asian Art, Cooper Hewitt and Air & Space (millions more are specimens) | median 3,000-5,090 depending on unit | Often (Cooper Hewitt, Asian Art) |
| 3 | **Rijksmuseum** | CC0 / PDM | 386k prints, 48k drawings, 4.9k paintings, 5.3k maps | ~4,000 (IIIF, max area 17.5 MP) | At ~250 dpi |
| 4 | **Art Institute of Chicago** | CC0 | 59,062 public-domain works with an image | median 3,000; 39% are 4,961 or larger (up to 19,601) | 39% yes |
| 5 | **Cleveland Museum of Art** | CC0 | 41,581 | full TIFF median 5,247 | 59% yes (best rate) |

These specialists are just as safe and fill theme gaps:

- **National Gallery of Art, Washington** (CC0): 63,858 images, but the image server (IIIF) delivers at most 4,096 px.
- **Yale Center for British Art** (CC0): best source for Turner, Constable and British horse, hound and fox art; images up to 14k px.
- **Library of Congress**: best for WPA posters and pre-1927 maps; master TIFFs of 4-6k px.
- **Biodiversity Heritage Library**: 320k natural-history plates, around 3k px.
- **Wikimedia Commons**: the largest volume, and famous paintings at gigapixel size, but each file's licence needs checking.

**Not usable commercially:** David Rumsey Map Collection. It is **CC BY-NC-SA 3.0**, so commercial use needs a paid licence.

---

## 2. Counts per theme (public domain or CC0 with an image)

The counts are search hits, so they are upper bounds with some noise, not curated plates. The notes under the table explain how each column was counted.

| Theme | Met (est.) | AIC | Cleveland | NGA | Smithsonian* | Rijks** | YCBA*** | LoC**** | Wikimedia PD-Art | BHL (volumes) |
|---|---|---|---|---|---|---|---|---|---|---|
| birds | 7,520 | 636 | 2,185 | 2,431 | 1,412 | 2,052 | 704 | 7,534 | 19,371 | 5,861 |
| hares/rabbits | 264 | 34 | 45 | 90 | 36 | 391 | 233 | 251 | 2,023 | – |
| foxes | 171 | 60 | 151 | 33 | 57 | 585 | 633 | 2,200 | 3,737 | – |
| horses | 5,552 | 611 | 483 | 1,827 | 510 | 7,009 | 1,740 | 16,284 | 19,476 | 443 |
| cats | 608 | 105 | 83 | 153 | 152 | 873 | – | 2,408 | (noisy) | – |
| dogs | 2,601 | 334 | 253 | 862 | 252 | 4,076 | 541 | 3,191 | 4,227 | 110 |
| cows/cattle | 572 | 158 | 69 | 456 | 250 | 1,259 | 226 | 2,106 | 6,531 | – |
| insects | 563 | 162 | 81 | 132 | 145 | 119 | – | 467 | 3,876 | 3,319 |
| fish | 1,536 | 284 | 356 | 403 | 329 | 1,016 | – | 3,269 | (rate-limited) | 1,224 |
| butterflies | 694 | 71 | 644 | 66 | 60 | 434 | – | 705 | 1,574 | 673 |
| botanical/flowers | 14,896 | 1,160 | 1,799 | 2,899 | 1,764 | 2,573 | 919 | (65, narrow query) | 17,287 | 15,841 |
| landscapes | 5,406 | 1,536 | 1,588 | 4,040 | 6,327 | 16,123 | 4,296 | 54,656 | 136,796 (noisy) | – |
| Hokusai | 427 | 449 | 38 | 0 | 168 | 221 | 2 | 320 | 610 | – |
| Hiroshige | 682 | **1,678** | 241 | 4 | 167 | 248 | – | 475 | 5,997 | – |
| Van Gogh | 23 | 19 | 5 | 23 | 0 | 14 | – | – | 5,582 | – |
| Monet | **0** (restricted) | 46 | 5 | 27 | 0 | 2 | – | – | 5,426 | – |
| Klimt | 12 | 3 | 1 | 6 | 0 | – | – | – | 529 | – |
| Turner | 123 | 166 | 65 | 140 | 1 | – | **4,676** | – | 1,229 | – |
| Constable | ~10 | 12 | 16 | 51 | 7 | – | 613 | – | 1,787 | – |
| travel/railway posters | 0 | 0 | 0 | 0 | 0 | 5,024 (all posters; many in copyright) | – | 947 WPA + 455 travel | (see §5) | – |
| vintage maps | 215 | 26 | 37 | 29 | 59 | 5,288 | 1,767 | **46,259** (pre-1927) | 6,157 | – |
| space/astronomy | 79 | 4 | 23 | 373 | 228 | – | – | 177 | 40 (PD-Art) | – |

How each column was counted:

- **Met:** the number of subject-tag hits, multiplied by the share of a random 20-item sample that was public domain with an image.
- \*\* **Rijksmuseum:** Dutch keyword matches (vogel, haas, vos, paard and so on) on title or description, where an image is available.
- \* **Smithsonian:** counted from the bulk S3 metadata for SAAM, Asian Art (FSG), Cooper Hewitt (1/8 sample x 8) and Air & Space, keeping only media marked CC0.
- \*\*\* **YCBA:** full-text estimates from the LUX API, not filtered by rights.
- \*\*\*\* **Library of Congress:** "online image" hits, which are **mostly photographs**.
- **BHL:** the number of *volumes* dated before 1927 in the archive.org mirror. Each volume holds many plates, and BHL's curated Flickr set alone has **319,661** plates.

**Space/astronomy:** NASA Image Library has Hubble 4,789, JWST 736, galaxy 1,741, nebula 316, planet 7,623 and Moon 20,109 images. Wikimedia has 4.8M files tagged PD-USGov-NASA.

**Maps (generated):** Natural Earth has 177 country polygons at 110m and 258 at 10m, all public domain vectors. OS OpenData offers 24 GB products under OGL, and OSM has worldwide coverage under ODbL.

**Gaps that public domain cannot fill well:**

- Klimt in volume: only ~20 museum images, though ~500 on Commons.
- Railway and travel posters from before 1960 that are **out of copyright in the UK** (see §5).
- Modern-looking animal portraits (for example a fox or hare in a contemporary flat style).
- Specific dog breeds.
- "Cute" nursery animals.

---

## 3. Per-source details (what was tested)

### The Met (collectionapi.metmuseum.org)
- **How to use it:** `search?tags=true&hasImages=true&q=Birds` returns object IDs. Then `objects/{id}` gives `isPublicDomain` and `primaryImage`, which is the original JPG. No key is needed, and the limit is about 80 requests a second.
- **Gotcha:** filters depend on parameter order, and `q` must come last. `q=cat&hasImages=true&isPublicDomain=true` returned 96, while `hasImages=true&isPublicDomain=true&q=cat` returned 36,730.
- **Gotcha:** the Met's Monet paintings (for example 437106 and 438004) come back as `isPublicDomain=false` with no image. The work is public domain, but the Met does not release these images, so do not take them from the Met.
- **Licence:** CC0, and use in any media is allowed. The terms say: *"You must not use The Metropolitan Museum of Art's trademarks or otherwise claim or imply that the Museum ... endorses you."*
- **Sample:** the Great Wave (45434) came back at 3859x2594. That is fine for A4 at 300 dpi and gives A3 at about 200 dpi.

### Smithsonian (api.si.edu)
- **The API key:** `DEMO_KEY` returned **HTTP 429 OVER_RATE_LIMIT** (`x-ratelimit-limit: 10` per hour, already used up by the shared egress IP). **DEMO_KEY is not usable. Get a free api.data.gov key (1,000 requests an hour).**
- **The workaround:** bulk NDJSON on public S3, which needs no key: `https://smithsonian-open-access.s3-us-west-2.amazonaws.com/metadata/edan/{unit}/index.txt`, with 256 files per unit. I downloaded SAAM (52 MB), FSG (27 MB), NASM (11 MB), 1/8 of Cooper Hewitt and 1/32 of Smithsonian Libraries.
- **The rights flag:** each media item has `usage.access == "CC0"` and lists its high-resolution JPEG/TIFF URLs with width and height.
- **Licence:** CC0. The Smithsonian name, logo and sunburst are trademarks and cannot appear on products or suggest endorsement.
- **Sample:** a Hokusai-school "Travelers" (FS-5873_02) at 1877x2537. The unit median is 4,200.

### Rijksmuseum (data.rijksmuseum.nl)
- **How to use it:** the new Linked Art search, for example `search/collection?imageAvailable=true&creator=Katsushika Hokusai`, which needs no key. To reach the image, follow object → `shows` (a VisualItem) → `digitally_shown_by` (a DigitalObject) → `access_point`, which gives `https://iiif.micr.io/{id}/full/max/0/default.jpg`. That is 3 hops per object, so cache the results.
- **Licence:** the rights are on the object as `https://creativecommons.org/publicdomain/zero/1.0/`.
- **Sample:** Hokusai at 3933x4394.

### Art Institute of Chicago (api.artic.edu)
- **How to use it:** POST an Elasticsearch query to `/artworks/search` with `is_public_domain=true`. `thumbnail.width/height` gives the true size of the master image.
- **Gotcha:** the IIIF server sits behind Cloudflare. A plain curl gets a 403 "Just a moment" page, so send an `AIC-User-Agent` header (a custom User-Agent also works). The `full` and `max` size keywords still returned 403, so request `/full/{width},/0/default.jpg`. Large images are served at full size (tested at 10,490 px).
- **Sample:** Hiroshige's Hamamatsu at 3000x2235.

### Cleveland (openaccess-api.clevelandart.org)
- **How to use it:** `?cc0=1&has_image=1`. Use `artists=` for painters, because `q=Gogh` gave 570 noisy hits against 5 real ones.
- **Renditions:** web, print (JPG, up to 3,400 px) and **full (TIFF, median 5,247 px, about 70 MB)**.
- **Terms:** *"Works designated as CC0 do not require attribution ... does not imply endorsement by the CMA, nor does it grant permission to use the CMA's trademarks."*
- **Sample:** "A Hare and a Leg of Lamb" 1969.53. The print JPG is 2557x3400, and the full TIFF is 4137x5500, which is enough for A3.

### National Gallery of Art, Washington
- **How to use it:** download `published_images.csv` (89 MB) and `objects.csv` (82 MB) from `raw.githubusercontent.com/NationalGalleryOfArt/opendata` (the github.com website is blocked by the proxy), and keep rows where `openaccess=1` and `viewtype=primary`.
- **Gotcha:** IIIF delivery is **capped at 4,096 px**. For Monet's "Morning Haze", the CSV lists 5980x4756 but 4096x3258 was delivered.

### Yale Center for British Art
- **How to use it:** IIIF manifests at `manifests.collections.yale.edu/ycba/obj/{id}` show `rights: CC0`. Search through the LUX API with a browser User-Agent, because the website search returns 403 to scripts.
- **Sample:** Turner's "Dort" is available at **14484x9741**.

### Library of Congress
- **How to use it:** `loc.gov/{photos,maps,collections/...}/?fo=json`. Item JSON has `rights_advisory` and a master TIFF.
- **Sample:** WPA "Zion National Park" poster, TIFF at 4246x5742 (73 MB). That is **A3 at 300 dpi**.
- **Rights:** WPA posters say "No known restrictions on publication." But the Canadian Pacific "Travel by train" poster (by Norman Fraser) says **"Rights status not evaluated."** "No known restrictions" is an advisory, not a licence, so filter on the exact advisory string.

### Biodiversity Heritage Library
- **Access:** the API needs a free key, and so does the Flickr API. Without a key: `biodiversitylibrary.org/pageimage/{id}` redirects to an S3 webp of about 2900x3900, and archive.org has `/download/{id}/page/n{N}.jpg` at about 1850x3185.
- **Sample:** Curtis's Botanical Magazine plate 150 (1791). A scanner's thumb shows at the right edge, so expect to crop and clean up.
- **Rights:** public domain for pre-1927 material. Some modern items are CC BY-NC, so check `rights` per item.

### Others
- **NYPL:** the API returns 401 without a free token, and the website search is bot-blocked (Incapsula). One query did succeed: cats, public domain = 442.
- **Paris Musées:** 252,879 "image libre" (CC0) works, per the site. The GraphQL API needs a free token.
- **Openverse:** anonymous use is capped at 240 results. Its links point to Flickr "_b" images of about 1024 px, so use it only for discovery.
- **Wikimedia Commons:** heavily rate-limited (429) from shared IPs; send a descriptive User-Agent and back off. Thumbnails only come in standard widths, so a 2000px request returned 400 while 1920px worked.
  - **Scale:** 2.17M bitmaps tagged PD-Art and 785k tagged PD-old-100. The originals can be huge: Starry Night is 44,567 px and 696 MB.
- **NASA:** images-api.nasa.gov needs no key. The "orig" asset size varies; Webb's Carina image is only 2000 px in the library, and the full-size version is on webbtelescope.org / esawebb.org.
  - **Terms:** NASA material is generally not copyrighted. You cannot use the NASA insignia, "meatball" logo or astronauts' likenesses to imply endorsement. ESA images are CC BY 4.0, which requires attribution.
- **Natural Earth:** public domain, with no attribution needed. The downloads from naciscdn.org worked.
- **OS OpenData:** `api.os.uk/downloads/v1/products` needs no key and lists 24 products. Licence: OGL v3, with the attribution "Contains OS data © Crown copyright and database right 2026".
- **OpenStreetMap:** ODbL. The OSMF Attribution Guideline, for *"Artwork, household goods, and clothing"*, says:

  > *Physical merchandise ... must provide attribution on any packaging, at the point of sale, and, to the extent possible, somewhere on the item itself ... readable and include the URL openstreetmap.org/copyright printed out.*

  So put "© OpenStreetMap contributors · openstreetmap.org/copyright" in small print on the poster **and** in the listing description.
  - **Exemptions:** fewer than 100 features, or an area under 10,000 m².
  - **Tiles:** render your own; do not use the tiles from osm.org.
- **David Rumsey:** the site links `creativecommons.org/licenses/by-nc-sa/3.0`, which is **NonCommercial. Excluded.**

---

## 4. Licence summary for selling printed products

| Source | Sell prints? | Attribution | Must not |
|---|---|---|---|
| Met, AIC, Cleveland, NGA, Rijks, Smithsonian, YCBA, Paris Musées | Yes (CC0) | none | use museum names or logos to suggest endorsement or "official" merchandise; say "from the Met collection" in a way that implies partnership |
| LoC, NYPL | Yes, for items marked "no known restrictions" or public domain | courtesy only | assume "rights not evaluated" means public domain |
| BHL | Yes, for pre-1927 public-domain items | none | use the CC BY-NC items |
| Wikimedia | Per file (PD-Art or PD-old-100 = yes) | only for CC-BY or BY-SA files | trust tags blindly; check the author's death date against the UK term (life + 70 years) |
| NASA | Yes | "Credit: NASA" is advised | use the NASA logo; imply endorsement; use astronaut likenesses |
| Natural Earth | Yes | none | – |
| OS OpenData | Yes (OGL) | "Contains OS data © Crown copyright and database right [year]" | imply OS endorsement |
| OSM | Yes (ODbL) | on the item, the listing and the packaging, with the URL printed | skip it |
| David Rumsey | **No** (BY-NC-SA) | – | – |

Safe listing wording: "Katsushika Hokusai, The Great Wave (c.1831), fine-art reproduction". Avoid "Metropolitan Museum print" or "official", and do not use museum logos.

---

## 5. UK-specific law

1. **Copyright term is life plus 70 years (CDPA s12), not the US rule for works published before 1931.** Something public domain in the US can still be in copyright in the UK. This matters most for:
   - 1920s-50s **railway and travel posters** (LNER, GWR and Southern Railway artists such as Tom Purvis, d. 1959, or Frank Newbould, d. 1951). Artists who died in 1956 or later are still protected. Many originals and rights sit with the Science & Society Picture Library / NRM.
   - Rijksmuseum posters.
   - LoC posters marked "rights not evaluated".
   - Any artist who died after 1955.

   Public domain in the UK for 2026: artists who died in **1955 or earlier**. Monet (d. 1926), Van Gogh, Klimt (d. 1918), Turner, Constable, Hokusai and Hiroshige are all fine.
2. **Photographs and scans of 2D public-domain art.** In *THJ Systems v Sheridan* [2023] EWCA Civ 1354, the Court of Appeal confirmed that the UK originality test is the EU-derived "author's own intellectual creation" test, which needs free and creative choices, and not "skill and labour". A faithful reproduction of a 2D work leaves little room for such choices, so it is unlikely to attract its own copyright.
   - **UK IPO guidance:** its Copyright Notice on digital images (updated 4 Jan 2021) says: *"it seems unlikely that what is merely a retouched, digitised image of an older work can be considered as 'original'."*
   - **Remaining risk:** it is not zero. There is no UK case squarely on museum photographs, some UK institutions (for example the National Portrait Gallery in its 2009 dispute with Wikimedia, and the National Gallery) have claimed rights in reproductions, and website terms of use can bind you as a contract.
3. **Which sources claim copyright in reproductions:** none of the audited museum sources do for their public-domain works; they waive any rights with CC0. The YCBA manifest carries a generic warning that "restrictions may apply". Wikimedia scans taken from Google Art Project, and from institutions that assert rights such as MoMA (Starry Night), are the grey area. For a UK seller the risk is low after *THJ*, but where the same work is available from a CC0 museum, use that version.
4. **Trademarks and passing off:** museum names, the Smithsonian marks, NASA insignia and the "Van Gogh Museum" name are trademarks, so do not put them in titles or tags in a way that suggests origin. Photographs of identifiable people (LoC and NASA images, astronauts) raise passing-off and false-endorsement risk if used in marketing. The UK has no general personality right, but *Irvine v Talksport* and *Fenty v Arcadia* apply.
5. **Modern mapping:** the OS 50-year Crown copyright rule means OS maps published before 1976 are out of Crown copyright. The National Library of Scotland's historic OS scans are a possible extra source for vintage UK maps; they were not tested here, so check NLS's own licence first.

---

## 6. AI fallback pricing (checked 28 Sep 2026)

A3 at 300 dpi is 17.4 MP. Generate at about 1 MP, then upscale 4x to reach roughly 16.8 MP (about 4096 x 4096 for a square image).

| Option | Price | About 1 MP image |
|---|---|---|
| fal.ai **FLUX.1 schnell** | $0.003 per MP (rounded up) | **$0.003** |
| fal.ai Z-Image Turbo | $0.005 per MP | $0.005 |
| fal.ai FLUX.2 | $0.012 per MP | $0.012 |
| fal.ai FLUX.1 dev | $0.025 per MP | $0.025 |
| Bedrock Titan Image G1/V2 (1024, standard) | $0.01 per image | $0.01 |
| Bedrock **Nova Canvas** | $0.04 (1024 standard) / $0.06 (1024 premium or 2048 standard) / $0.08 (2048 premium) | $0.04 |
| Bedrock Stability: Stable Image Core / SD3.5 Large / Stable Image Ultra | $0.04 / $0.08 / $0.14 | $0.04+ |
| Google **Imagen 4 Fast** / Imagen 4 / Imagen 4 Ultra | $0.02 / $0.04 / $0.06 | $0.02 |

The Bedrock and Imagen prices are for us-east-1, taken from the AWS Price List API and the Vertex AI pricing page. The fal.ai prices come from each model's page.

**Upscaling to A3:**

| Option | Price | Cost to A3 |
|---|---|---|
| fal SeedVR upscale | $0.001 per MP | about **$0.017** at 17 MP out |
| fal ESRGAN | $0.00111 per compute-second | under $0.01 |
| fal Recraft Crisp | $0.004 per image | $0.004 (output size limits not checked) |
| fal Clarity (creative) | $0.03 per MP | about $0.03-0.52, depending on whether it bills input or output MP |
| Imagen 4 upscaling (to 4K) | $0.06 | $0.06 |
| Real-ESRGAN run locally | free | GPU or CPU time only |

**Cheapest end-to-end:** FLUX schnell at 1 MP ($0.003) plus SeedVR 4x ($0.017) is about **$0.02 per A3 print file**. Generate only the listing mock-up at listing time ($0.003), and upscale only when an order comes in. **1M listings then cost about $3k** at schnell prices. Check each provider's current output-licence terms before relying on this for commercial use.

---

## 7. Practical pipeline notes
- **Metadata to harvest first:**
  - Met: the API, at about 80 requests a second.
  - AIC: its API.
  - Cleveland: the API, or its GitHub dump.
  - NGA: the CSVs.
  - Smithsonian: the S3 NDJSON.
  - Rijksmuseum: Linked Art.
  - LoC: JSON.

  Store `(source, id, licence flag, width, height, image URL)` and filter on `max(w,h) >= 3300`, which is enough for A3 at about 200 dpi.
- **Print sizes by resolution:**
  - 4,961 px or more: sell A3 or A2 (A2 = 4961x7016 at 300 dpi; about 170 dpi from a 5k image is acceptable for posters).
  - 3,000-4,900 px: sell up to A3 at about 200-250 dpi.
  - Under 3,000 px: sell A4 only, or upscale with Real-ESRGAN, which is free.
- **Scale arithmetic:** there are roughly 300k-500k distinct art images you could legally sell with high confidence. Getting to "millions of listings" means variants of the same image: sizes, frames, crops, colour mats and room mock-ups. Many platforms (Etsy, eBay) penalise near-duplicates, so vary the crop and the theme grouping, not only the size.
- **Duplicates across sources:** the same Great Wave exists at the Met, AIC, Rijks, Smithsonian and on Wikimedia. De-duplicate with a perceptual hash so you don't list 10 near-identical Great Waves.

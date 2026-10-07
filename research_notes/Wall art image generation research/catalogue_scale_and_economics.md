# Catalogue Scale and Economics for Multi-Million-Listing eBay UK Wall Art

Scope note: all figures dated. Official policy/pricing is labelled **[OFFICIAL]**; vendor
pricing pages **[VENDOR]**; seller/trade commentary **[ANECDOTE/TRADE]**; my own arithmetic
**[CALC]**. Research conducted 2026-10-07.

---

## Q1. How do the highest-volume POD sellers structure enormous catalogues? Designs vs listings?

### Takeaway
The structural lever on eBay is the multi-variation listing: one listing can carry up to 250
variations, so a size x frame x colourway matrix collapses into a single listing rather than
multiplying listings. This means a target of "2-3 million **listings**" implies 2-3 million
unique **designs** — a design count larger than Displate's entire decade-old catalogue — whereas
2-3 million **SKUs** is achievable from roughly 100k-200k designs. Which of the two the seller
actually means changes the project by an order of magnitude.

### Cited Findings
- eBay allows up to 250 variations in a single fixed-price listing at no additional fee; a listing
  may use a maximum of 5 variation *specifics* (e.g. Size, Frame Colour) with up to 60 values each,
  and 12 photos per variation at no extra cost — [eBay Trading API variations guide](https://www.developer.ebay.com/api-docs/user-guides/static/trading-user-guide/variations.html) **[OFFICIAL]**
- Exceeding 250 produces the hard error "This listing has too many variations. Reduce the number of
  variations to 250 or less and try again." eBay also counts historical/deleted variants still tied
  to the listing toward the 250 cap, which bites on feed-driven catalogues that churn SKUs —
  [Lengow error documentation](https://help.lengow.com/hc/en-us/articles/29592953618460--eBay-Error-This-listing-has-too-many-variations-Reduce-the-number-of-variations-to-250-or-less-and-try-again) **[TRADE]**
- Multi-variation is only available on Fixed Price listings, not auction-style — [eBay Trading API variations guide](https://www.developer.ebay.com/api-docs/user-guides/static/trading-user-guide/variations.html) **[OFFICIAL]**

### Inferences
- **[CALC]** A realistic wall-art variation matrix — 6 sizes x 4 frame options (unframed, black,
  white, oak) x 2 orientations = 48 SKUs — sits comfortably inside the 250 cap. At 48 SKUs per
  listing, 2.5m SKUs = ~52,000 listings. At 15 SKUs per listing (5 sizes x 3 frames), 2.5m SKUs =
  ~167,000 listings.
- **[CALC]** Conversely, 2.5m *listings* each being one design-with-variations means 2.5m distinct
  designs, and at 48 SKUs each that is 120m SKUs. This is almost certainly not what is wanted.
- **[CALC]** Room targeting ("living room print", "nursery art") and colourway are the two axes that
  tempt sellers into listing duplication rather than variation, because they change the *image* and
  the *keywords*, not just the product attribute. Room targeting in particular cannot be a variation
  axis — it is a keyword/mockup axis — so it is exactly where near-duplicate listings get created.
  This is the structural decision point: room/colourway belongs in the title and gallery of a
  single listing, not in separate listings.

### Gaps
- I found no published breakdown from a named high-volume eBay wall-art seller of their design count
  versus listing count. There is no credible public case study at the 100k+ listing scale for this
  category. Everything in this section is derived from platform mechanics, not from an observed
  competitor catalogue.
- No data on what proportion of large POD sellers use multi-variation versus flat single-SKU
  listings on eBay.

---

## Q2. Displate: scale, bulk series uploading, and how it performs

### Takeaway
**The ~2.5m designs figure in the brief does not check out against Displate's own current
materials, which say "over 1.5 million" designs from "40,000+" artists** — about 37 designs per
artist, not 62. Displate is also a curated single-product marketplace, not a listing-count
marketplace, so it is a weak analogue for eBay listing economics; its useful signal is the
per-design revenue, which is very low.

### Cited Findings
- Displate's own About page states a catalogue of "over 1.5 million" designs; it does **not** state
  an artist count — [Displate About Us](https://displate.com/about-us) **[OFFICIAL]**
- Secondary sources give "40,000+ independent artists" and variously "over 1.4 million",
  "over 1.5 million" and "over 2 million" designs, i.e. the figures are inconsistent across
  snapshots and marketing copy — [Wikipedia: Displate](https://en.wikipedia.org/wiki/Displate);
  [Greenlit Content Displate review](https://greenlitcontent.com/resources/displate-review) **[TRADE]**
- Displate artist commission is quoted as fixed per-size amounts of roughly $4.50 (M), $9.00 (L),
  $14.50 (XL) per sale, rising to ~41% of net price on self-referred traffic —
  [Autokeyworder, 2026](https://autokeyworder.com/blog/ai-income-blueprint-posters) **[ANECDOTE — low-quality source, a POD-tooling blog; treat the commission tiers as indicative only]**
- The same source reports one artist earning $82 from 24 poster sales over Jan-Mar 2026 (~$3.42/sale)
  — [Autokeyworder, 2026](https://autokeyworder.com/blog/ai-income-blueprint-posters) **[ANECDOTE — single unverified data point]**

### Inferences
- **[CALC]** Using Displate's own 1.5m designs and the secondary 40k artists: ~37 designs per artist.
  If a typical artist earns a few hundred dollars a year (consistent with the $82/quarter anecdote),
  revenue per design per year is on the order of **$1-10**. Applied naively to 2.5m designs that
  would be a large number, but the mechanism does not transfer: Displate concentrates demand on a
  curated front page and licensed IP, and eBay does not.
- Displate is a *single product* marketplace (one metal poster, chosen size) — the design:listing
  ratio is 1:1 by construction. It therefore tells us nothing about the variation-collapsing
  question in Q1, and should not be used to justify a listing count.

### Gaps
- **I found no documentation of a Displate bulk/series upload facility and no performance data on
  bulk-uploaded series.** Searches returned bulk-upload docs for other platforms (Merchize,
  DecoNetwork, ShopBase) and a third-party automation tool
  ([LazyMerch Displate upload docs](https://automation-docs.lazymerch.com/upload/displate)) which
  implies bulk uploading is done by scripting the artist UI rather than via an official bulk API.
  I could not verify Displate's official position, per-upload limits, or review/curation throughput.
- No data on how bulk-uploaded Displate series perform relative to hand-curated ones.

---

## Q3. Catalogue size versus sales per listing — diminishing or negative returns?

### Takeaway
There is no public, measured dataset for sales-per-listing versus catalogue size on eBay. The two
substantive pieces of evidence pointing to *negative* returns are (a) the classical catalogue
square-root rule, where profit peaks and then falls as pages are added, and (b) eBay's own stated
position that non-selling listings drag down search relevance **at account level**, which makes
large dead inventory actively harmful rather than merely neutral.

### Cited Findings
- Catalogue square-root/diminishing-returns modelling: in a worked example, profit peaked at
  ~$950,000 at 100 pages and **declined** as pages were added beyond that point — the marginal page
  stops paying for itself — [MineThatData, "Diminishing Returns / Square Root Rule"](https://blog.minethatdata.com/2007/12/diminishing-returns-square-root-rule.html) **[TRADE — print catalogue analytics, pre-2010]**
- Incremental pages past ~48 pages generate only ~30-40% of the sales-per-page of core pages, and
  that ratio keeps falling as total page count rises — [MyTotalRetail, "More Pages, Higher Sales"](https://www.mytotalretail.com/article/more-pages-higher-sales-21227/) **[TRADE]**
- eBay leadership stated at a UK Roadshow (Salford) that **"eBay listings with no sales after 90 days
  may impact search relevance"**, and the reported framing was that such listings adversely affect
  the *whole account's* search relevancy, not just themselves —
  [Frooition, May 2022](https://www.frooition.com/blog/2022/05/are-slow-selling-items-damaging-your-ebay-search-relevance/) **[TRADE reporting an eBay statement — no named eBay spokesperson, no published policy page; treat as credible-but-unofficial]**
- Sell-through rate is described by multiple eBay SEO analysts as one of the strongest Cassini
  signals — a listing that converts earns placement, which earns impressions, which earns sales —
  [Frooition eBay SEO Guide (2026)](https://www.frooition.com/ebay-seo-guide);
  [ZIK Analytics on Cassini](https://www.zikanalytics.com/blog/ebay-cassini/) **[TRADE]**
- eBay has publicly pushed back on the seller folk-remedy of ending and relisting to refresh
  ranking, indicating the algorithm does not reward churn-as-freshness —
  [Value Added Resource](https://www.valueaddedresource.net/is-ebay-end-relist-a-myth/) **[TRADE]**

### Inferences
- **[CALC]** The mechanism that makes POD listing-scaling different from a print catalogue is that
  the marginal cost of a listing is near zero but the marginal cost is *not* the only cost: if
  account-level sell-through is a ranking input, then adding 600,000 non-converting listings to an
  account dilutes the ranking of the listings that *do* convert. The returns curve is therefore
  plausibly not just flattening but turning negative, and the inflection is set by account
  sell-through rather than by any absolute listing count.
- **[CALC]** A testable proxy for the inflection point: track sales per 1,000 active listings per
  account monthly. If that ratio falls faster than listings are added, the account has passed the
  inflection. This is measurable from the seller's own four accounts and is better evidence than
  anything available publicly.

### Gaps
- **No source gives a numeric catalogue size at which eBay sales per listing turns down.** I found
  no study, no eBay statement and no seller dataset quantifying it. Any specific threshold in the
  final report would be fabricated.
- The 90-day/account-relevance claim is from 2022 trade reporting of a verbal statement. I could not
  find it restated on an official eBay help page in 2025-2026. It should be presented with that
  caveat.
- No published sales-rate data for very long-tail (near-zero-search-volume) listings — see Q8.

---

## Q4. Marketplace treatment of near-duplicate and bulk-generated listings (eBay specifically)

### Takeaway
eBay's duplicate listings policy is a bright-line rule that is directly dangerous to this business
model: **more than one fixed-price listing of an identical item from the same seller is prohibited,
including across different usernames and different categories, and "listings that aren't
significantly different" count as duplicates.** Enforcement escalates to account suspension. The
four-account structure does not evade this — cross-username duplication is named in the policy.

### Cited Findings
- **[OFFICIAL]** eBay does not allow "more than one fixed price listing of an identical item at the
  same time from the same seller." The restriction explicitly covers listing an identical item in
  different categories **or using different usernames**, and covers listings that "aren't
  significantly different (such as adding an inconsequential bonus item)" —
  [eBay UK duplicate listings policy (id=4255)](https://www.ebay.co.uk/help/policies/listing-policies/duplicate-listings-policy?id=4255)
- **[OFFICIAL]** Stated exceptions: multiple identical auction-style listings (same start price,
  reserve, title and description, no Buy It Now — and only one un-bid listing is shown to buyers at
  a time); up to 5 fixed-price listings for items fitting multiple devices where each spells out the
  brand/model; eBay's bulk listing tool for many units of the same item; separate listings on
  different eBay sites provided search results are not cluttered —
  [eBay UK duplicate listings policy](https://www.ebay.co.uk/help/policies/listing-policies/duplicate-listings-policy?id=4255)
- **[OFFICIAL]** Enforcement: "removing the listing or other content", "issuing a warning",
  "restricting activity or account suspension" —
  [eBay UK duplicate listings policy](https://www.ebay.co.uk/help/policies/listing-policies/duplicate-listings-policy?id=4255)
- **[OFFICIAL]** Separately, eBay's search and browse manipulation policy bans adding popular
  keywords unrelated to the item and any tactic that could mislead buyers; all words in a listing
  must refer only to the item for sale. Same enforcement ladder up to suspension —
  [eBay UK search & browse manipulation policy (id=4243)](https://www.ebay.co.uk/help/policies/listing-policies/search-browse-manipulation-policy?id=4243)
- Buyers can report listings directly via Report > "Listing practices" > "Search and browse
  manipulation"/"Keyword spamming", and eBay acts once made aware — i.e. enforcement is substantially
  complaint-driven, which means competitor reporting is a live risk at scale —
  [HustleGotReal on the search manipulation policy](https://hustlegotreal.com/faq/ebay/ebay-search-and-browse-manipulation-policy-what-are-sellers-doing-wrong/) **[TRADE]**
- Cassini is described as ranking on three pillars: query relevance, seller performance (defect
  rate, late shipments, cases closed without resolution) and listing quality (item specifics, photos,
  title keywords) — [Frooition eBay SEO Guide (2026)](https://www.frooition.com/ebay-seo-guide) **[TRADE]**

### Inferences
- **[CALC]** The policy's phrase "aren't significantly different" is the whole risk. Two listings of
  the *same design* differing only by frame colour or room-targeted title are plainly not
  significantly different, and a size/frame matrix is exactly what eBay expects to be a
  multi-variation listing. So Q1's structural answer and Q4's compliance answer converge on the same
  recommendation: **variations inside one listing, not separate listings.**
- **[CALC]** Two listings of *different AI-generated designs* are not duplicates under the letter of
  the policy, however visually similar. The exposure is therefore (a) genuinely near-identical
  generations from the same prompt seed family, and (b) the search-manipulation policy, if titles are
  keyword-matrixed across a design set.
- **[CALC]** Spreading duplicates over four accounts is worse than useless: the policy names
  different usernames explicitly, and four linked accounts give eBay four accounts to restrict.

### Gaps
- **I found no eBay statement, policy page or enforcement report specifically addressing
  AI-generated or bulk-generated listings as a category.** There is no public evidence of a named
  eBay crackdown on bulk POD sellers, and no published duplicate-similarity threshold or
  perceptual-hash policy.
- **I found no documentation of eBay search-result deduplication ("Cassini deduplication") as a
  described mechanism.** The Cassini material available is trade SEO commentary, not eBay
  documentation; eBay does not publish Best Match internals. Any claim that Cassini collapses
  near-duplicates into one result would be unsupported.
- No figures on how many listings eBay has removed under the duplicate policy.

---

## Q5. eBay UK shop subscription tiers, 2026 — allowances, overage fees, practical limits

### Takeaway
**Anchor is the only tier that works at this scale, and it is mandatory, not optional.** Anchor
gives unlimited zero-insertion-fee fixed-price listings for £437/month ex VAT; the next tier down
(Featured, 1,500 free then 5p each) would cost over £31,000/month per account at 625k listings.
Across four accounts Anchor is £1,748/month ex VAT (~£20,976/year ex VAT).

### Cited Findings — all **[OFFICIAL]**, from [eBay UK shop fees page (id=4809), last updated 30 September 2026](https://www.ebay.co.uk/help/selling/fees-credits-invoices/store-fees?id=4809)
| Tier | Price/month | Free fixed-price listings | Free 7-day auction listings | Extra fixed-price | Extra auction |
|---|---|---|---|---|---|
| No shop | — | — | — | 30p | 30p |
| Basic | £27 | 250 | 100 | 10p | 15p |
| Featured | £77 | 1,500 | 600 | 5p | 15p |
| Anchor | £437 | **Unlimited** | 1,000 | **Free** | 15p |

- All fees on that page are stated **exclusive of VAT** — [eBay UK shop fees](https://www.ebay.co.uk/help/selling/fees-credits-invoices/store-fees?id=4809) **[OFFICIAL]**
- The page states "Listing and optional listing upgrade fees also apply **each month** for Good 'Til
  Cancelled listings" — i.e. insertion fees on GTC listings recur monthly, they are not one-off —
  [eBay UK shop fees](https://www.ebay.co.uk/help/selling/fees-credits-invoices/store-fees?id=4809) **[OFFICIAL]**
- eBay states the subscription "value" ranges from £105 (Basic) to £1,173 (Anchor) per month if all
  allowances are used — [eBay UK shop fees](https://www.ebay.co.uk/help/selling/fees-credits-invoices/store-fees?id=4809) **[OFFICIAL]**
- Zero-insertion-fee allowances only apply when listing on the site you are registered with (a UK
  seller gets them for listing in the UK) — [Linnworks on UK eBay seller fees](https://www.linnworks.com/?p=3535) **[TRADE]**
- **Selling limits are the harder constraint than fees.** eBay caps the number of items an account
  may list and/or sell per calendar month; new accounts commonly start at 10 items/month, and eBay
  sets higher or lower limits by account, category and risk profile. Active *and* sold listings count
  toward the monthly limit, and **Good 'Til Cancelled listings count toward selling limits and will
  not auto-renew if the limit is reached.** eBay reviews and adjusts limits monthly based on sales
  volume and buyer feedback — [eBay selling limits help page (id=4107)](https://www.ebay.ie/help/selling/listings/selling-limits?id=4107) **[OFFICIAL — eBay IE copy of the help page; the UK copy carries the same policy]**

### Inferences
- **[CALC]** Monthly insertion cost for 625,000 fixed-price listings per account (2.5m / 4 accounts):
  - No shop: 625,000 x £0.30 = **£187,500/month** per account
  - Basic: (625,000 - 250) x £0.10 = **£62,475/month** + £27
  - Featured: (625,000 - 1,500) x £0.05 = **£31,175/month** + £77
  - Anchor: **£437/month**, flat, unlimited
  Anchor is ~71x cheaper than Featured at this volume. There is no decision to make here.
- **[CALC]** Four Anchor shops = £1,748/month ex VAT = £2,097.60/month inc VAT at 20% =
  £20,976/year ex VAT. Against that fixed cost, the catalogue must clear ~£21k/year in contribution
  before anything else is paid — before final value fees, print cost, generation cost or hosting.
- **[CALC]** Anchor's unlimited allowance is only for *fixed-price* listings. Auction-style is capped
  at 1,000 free then 15p each at every tier, so auctions are structurally unavailable at this scale.
  That also closes off the duplicate policy's auction exception (Q4) as a route for duplicates.
- **[CALC]** The practical limit is selling limits, not the subscription. Reaching 625k active
  listings on one account requires eBay to have granted a monthly limit above 625k items, through
  repeated monthly automatic reviews driven by actual sales volume and feedback. A low-sell-through
  catalogue is precisely the profile that does *not* earn limit increases, so the business model
  contains a feedback loop that works against its own scale target.

### Gaps
- **Monthly versus annual shop pricing could not be separated.** The fees page returned the same
  £27/£77/£437 figures for both; eBay UK historically discounted annual subscriptions. I could not
  confirm whether a cheaper annual rate currently exists.
- I could not retrieve eBay UK final value fee rates for the Home/Furniture/Art categories in this
  pass, nor the regulatory operating fee / per-order fee. These are material to unit economics and
  should be looked up before any profit model is built.
- eBay UK abolished selling fees for *private* sellers in 2024; some secondary sources still quote
  "1,000 free listings per month for all UK sellers" and "£0.35 insertion fee", which conflicts with
  the business-seller table above. I could not reconcile the two in this pass — **the table above is
  the business-seller schedule and is the one that applies here**, but the private-seller change
  should be verified separately before quoting any "1,000 free listings" figure.
- No published eBay ceiling on active listings per account above which limits will not be raised.

---

## Q6. Storage, rendering and bandwidth for a multi-million-image catalogue

### Takeaway
Gallery imagery for 2.5m listings is cheap — roughly 1 TB, ~£12/month on Cloudflare R2. Pre-rendering
print-ready files is what breaks the budget: 75-150 TB, $1,100-$2,250/month. The answer is to store
only the generation recipe plus a compressed master, and render print files on demand at order time
(volumes are tiny — one render per sale).

### Cited Findings — Cloudflare R2, from [R2 pricing docs](https://developers.cloudflare.com/r2/pricing/) **[VENDOR]**
- Standard storage **$0.015 per GB-month**; Infrequent Access **$0.01 per GB-month** (30-day minimum
  billing period per object)
- Class A operations (writes: PutObject, CreateMultipartUpload) **$4.50 per million** standard /
  $9.00 IA; Class B operations (reads: GetObject, HeadObject) **$0.36 per million** standard /
  $0.90 IA
- **Egress is free for all storage classes**; IA adds a $0.01/GB retrieval charge
- DeleteObject, DeleteBucket and AbortMultipartUpload are free
- Free tier: 10 GB-month storage, 1m Class A, 10m Class B, unlimited egress

### Inferences
- **[CALC] Gallery/listing images.** An eBay gallery image at ~1600px long edge is ~300-500 KB JPEG.
  2.5m listings x 1 primary image at 400 KB = **1.0 TB** = 1,000 GB x $0.015 = **$15/month**
  (~£12). Even 6 images per listing (mockups, room scenes, detail) = 6 TB = **$90/month**. Storage of
  listing imagery is a rounding error.
- **[CALC] Upload operations.** 2.5m x 6 images = 15m Class A writes = 15 x $4.50 = **$67.50** one-off.
  Also negligible.
- **[CALC] Print-ready files are the cost.** A 300 dpi A1 print is ~7,016 x 9,933 px. As a flattened
  PNG/TIFF that is typically 30-60 MB. 2.5m x 45 MB = **~112 TB** = **$1,680/month** standard R2
  ($1,120/month on IA). Over a year that is $13,440-$20,160 for files that will almost all never be
  printed.
- **[CALC] Therefore: render on demand.** Store (a) the prompt + model + seed + sampler settings
  (a few hundred bytes per design) and (b) the native-resolution generation output as a quality JPEG
  (~1-3 MB at 1024-1536px). 2.5m x 2 MB = 5 TB = **$75/month**. At order time, upscale that master to
  print resolution. At even 1,000 orders/month that is 1,000 upscales — trivial GPU work, a few
  pounds. Pre-rendering is ~22x the storage cost for a file set with a <0.1% hit rate.
- **[CALC] Bandwidth.** R2's free egress removes the usual objection to self-hosting a large image
  set. Note that eBay hosts listing images on its own servers once uploaded (up to 24 images per
  listing at no charge), so after the initial upload the seller serves almost no buyer-facing traffic
  — R2 is an origin/archive, not a CDN under load. **This last point about eBay image hosting is my
  inference from how eBay listings work and was not verified against an eBay page in this pass — it
  should be confirmed.**
- **[CALC] Generation wall-clock, not storage, is the schedule risk.** See Q7.

### Gaps
- I did not find published figures from any seller on actual storage footprints for catalogues at
  this scale, so all the above is modelled from unit prices and standard file sizes rather than
  observed.
- I did not verify eBay's current per-listing image allowance or whether externally hosted images may
  be referenced in listings.
- No data on realistic upscaling cost per print file (model-dependent; depends whether a diffusion
  upscaler or Lanczos/Real-ESRGAN pass is used).

---

## Q7. Cost and throughput of AI image generation at scale

### Takeaway
Rented GPUs put FLUX.1 schnell at roughly **$0.0002-$0.001 per 1 MP image** — 2.5m images for
**$500-$2,500 of GPU time**. Hosted APIs are 3-15x that ($3,500-$7,500 for the same 2.5m) but need no
ops. The binding constraint is wall-clock: one RTX 4090 takes ~2 months to produce 2.5m images, so
parallel GPUs (or a hosted API) are required for any sane schedule.

### Cited Findings
- **RunPod on-demand GPU pricing, page updated 27 September 2026** — RTX 4090 (24 GB):
  **$0.34/hr community / $0.74/hr secure**; L40S (48 GB): $0.79 / $1.09; A100 80 GB PCIe:
  $1.19 / $1.59; H100 80 GB PCIe: $1.99 / $2.89. Serverless is quoted hourly (e.g. H100 $4.79/hr)
  with per-second billing — [RunPod pricing](https://www.runpod.io/pricing) **[VENDOR]**
- **fal.ai FLUX.1 [schnell]: $0.003 per megapixel**, billed rounded up to the nearest megapixel;
  "sub-second response times", 1-4 inference steps, default 4 —
  [fal.ai FLUX schnell](https://fal.ai/models/fal-ai/flux/schnell) **[VENDOR]**
- **Fireworks: $0.00035 per diffusion step = $0.0014 per image** at default settings for FLUX schnell
  — [Fireworks FLUX launch post](https://fireworks.ai/blog/flux-launch) **[VENDOR]**
- On an A100 80 GB, FLUX schnell generates a 1024x1024 image in **~2-4 seconds** at batch size 1,
  FP16 — [JarvisLabs, best GPU for FLUX](https://jarvislabs.ai/ai-faqs/best-gpu-for-flux) **[VENDOR/TRADE benchmark]**
- FLUX.1 schnell needs only 1-4 steps versus dev/pro's ~20-50, which is the source of the cost gap —
  [Replicate FLUX schnell model page](https://replicate.com/black-forest-labs/flux-schnell) **[VENDOR]**
- Licence context confirming the project's existing constraint: schnell is the Apache-2.0 variant;
  this is why it is the correct choice for goods that are sold — consistent with
  [Replicate FLUX schnell](https://replicate.com/black-forest-labs/flux-schnell) **[VENDOR]**

### Inferences
- **[CALC] Per-image cost, rented GPU.** At 2.5 s/image on a $0.34/hr community RTX 4090:
  3,600 / 2.5 = 1,440 images/hr → **$0.00024/image**. On a $1.19/hr A100 at 3 s/image:
  1,200 images/hr → **$0.00099/image**. Batching improves both. Call it **$0.0002-$0.001 per image**.
- **[CALC] 2.5m images, rented GPU.** 2.5m x 2.5 s = 6.25m GPU-seconds = **1,736 GPU-hours**.
  At $0.34/hr = **$590**. At A100 $1.19/hr and 3 s = 2,083 hr = **$2,479**.
- **[CALC] 2.5m images, hosted.** fal.ai at $0.003/MP with 1 MP images = **$7,500**.
  Fireworks at $0.0014/image = **$3,500**. So hosted is 6-13x rented GPU, i.e. the saving from
  self-hosting on 2.5m images is roughly **$3,000-$7,000 one-off** — real, but small next to the
  £20,976/year of eBay Anchor subscriptions (Q5).
- **[CALC] Wall-clock is the real constraint.** 1,736 GPU-hours = **72 days on one GPU**. To finish in
  a week needs ~10 GPUs in parallel; in 24 hours, ~72 GPUs. Hosted APIs absorb this transparently,
  which is a strong argument for using a hosted API for the initial bulk build and rented GPUs only
  for steady-state top-ups.
- **[CALC] Cost per listing, all-in on the image side.** Generation ($0.0004) + storage amortised
  ($75/month / 2.5m = $0.00003/month) ≈ **$0.0005 per design**, versus the eBay Anchor cost of
  £437/month / 625,000 listings = **£0.0007 per listing per month**. Both are negligible per unit —
  which is exactly why the constraint on this business is *not* cost. It is eBay policy (Q4),
  selling limits (Q5) and sell-through dilution (Q3).

### Gaps
- RunPod's own published throughput for FLUX schnell was not available; the 2-4 s/image figure is a
  third-party A100 benchmark and I found no 4090-specific schnell benchmark, so the 2.5 s assumption
  for the 4090 is my interpolation, not a measured figure.
- No figures found for Vast.ai or Replicate per-image pricing in this pass.
- Community-cloud reliability/preemption rates are not published, and they affect effective
  throughput on long bulk runs.

---

## Q8. Is listing low-search-volume long-tail items worth it?

### Takeaway
**I found no reliable data on the sales rate of very long-tail listings — on eBay or elsewhere.**
This is the single biggest evidence gap in the brief, and the report should say so plainly rather
than reason from the "90% of Etsy sellers fail" statistics, which measure shops, not listings.

### Cited Findings
- The widely-circulated "as high as 90% of Etsy shops never get past their first handful of sales"
  figure measures **shops**, not listings, and is an estimate rather than published Etsy data —
  [DEV Community](https://dev.to/black_billi_925ab88fb3cff/why-90-of-etsy-sellers-never-make-it-past-10-sales-and-the-3-things-that-separate-the-ones-who-do-33mm) **[ANECDOTE — explicitly not a listing-level statistic]**
- For shops with large catalogues drawing traffic from hundreds of long-tail queries, the majority of
  the keyword data "simply does not exist in the dashboard" — i.e. platform analytics do not resolve
  long-tail performance, which is itself why this question is hard to answer empirically —
  [InsightAgent Etsy listings guide (2026)](https://www.insightagent.app/guides/etsy-product-listings-data) **[TRADE]**
- POD unit economics for comparison: ~$3-$5 royalty on a ~$20 item with no capital required, and
  ~20 minutes of work per listing when working from existing artwork — the royalty from one upload is
  small but repeats indefinitely — [Closo, "Sell on Printerval in 2026"](https://closo.co/blogs/platform-specific-guides/sell-on-printerval) **[TRADE]**
- Against that, the eBay-side counterweight from Q3: non-selling listings are reported by eBay to
  affect account-level search relevance —
  [Frooition, 2022](https://www.frooition.com/blog/2022/05/are-slow-selling-items-damaging-your-ebay-search-relevance/) **[TRADE reporting eBay]**

### Inferences
- **[CALC]** The long-tail case is sound *only* where the marginal listing has zero negative
  externality. On Amazon KDP or Displate — pure catalogue depth, no account-level ranking penalty —
  a design earning $1/year is worth uploading. On eBay, where account sell-through feeds Best Match,
  a listing earning £0/year is not free: it consumes allowance, counts against selling limits, and
  dilutes the account metric. **The platform, not the product, decides whether the long tail pays.**
- **[CALC]** Break-even sanity check for the proposed structure: four Anchor shops cost £20,976/year
  ex VAT. At a ~£8 contribution per wall-art sale after print and fees, the catalogue must produce
  **~2,622 sales/year (~219/month)** just to cover subscriptions. Spread over 2.5m listings that is
  a required rate of **~0.001 sales per listing per year** — i.e. one sale per 954 listings per year.
  That is a low bar, which is the honest case *for* the strategy; the risk is not the bar's height
  but whether eBay will host 2.5m near-duplicate listings at all (Q4) and whether it will grant the
  selling limits (Q5).
- **[CALC]** The £8 contribution figure is an assumption, not sourced. The break-even above should be
  recomputed once real final value fees and print costs are known.

### Gaps
- **No source found** giving: percentage of eBay listings that never sell; sales rate for listings
  with zero search volume; distribution of sales across a large POD catalogue (e.g. what share of
  revenue the top 1% of designs produces). I searched for Etsy listing-level and eBay listing-level
  data and found only shop-level survival statistics and vendor marketing.
- The internal claim on the wall-art branch that 89% near-duplication explains 424k listings not
  selling is an **internal observation with no external corroboration**; I found nothing published
  that would confirm or refute a near-duplication-to-non-sale link. It should be presented as the
  seller's own measurement, not as an industry finding.

---

## Cross-cutting conclusions for the report writer

1. **The brief's Displate premise needs correcting**: Displate's own site says 1.5m+ designs, not
   2.5m; the 62-designs-per-artist figure derives from an uncorroborated pairing of numbers.
2. **Designs vs listings is the decision that matters.** eBay's 250-variation multi-variation listing
   means size/frame/colourway should collapse into one listing. 2.5m SKUs needs ~50k-170k designs;
   2.5m *listings* needs 2.5m designs and is both harder and more legally exposed.
3. **Cost is not the constraint.** Generation ~$600-$7,500 one-off for 2.5m images; storage ~$75-$90/
   month if print files are rendered on demand. The dominant hard cost is four eBay Anchor shops at
   £20,976/year ex VAT.
4. **Policy and selling limits are the constraints.** eBay's duplicate policy explicitly covers
   different usernames and "not significantly different" listings, with suspension on the enforcement
   ladder; and the account-by-account monthly selling limit must be grown by demonstrated sales,
   which a low-sell-through catalogue does not do.
5. **The returns curve is probably negative, but nobody has published where it turns.** The only
   honest recommendation is to instrument it on the seller's own four accounts (sales per 1,000 active
   listings, monthly) rather than to quote a threshold.

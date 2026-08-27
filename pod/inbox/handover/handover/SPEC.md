# T-SHIRT POD PIPELINE — FULL SPECIFICATION

Everything below is read out of the working code, not from memory. Where a
value is unknown it says so rather than guessing.

---

## 1. PIPELINE ORDER

```
graphics.py          design space: subject x scene x style x palette
   |
rebuild_ledger.py    list EVERY bucket, build used_designs.txt
   |
pick.py --count N    draw N unused designs -> generation_queue.csv
   |
audit.py             29 checks; refuses the run if any fail
   |
pod_sdxl.py          SDXL generation on GPU -> <index>.jpg -> R2 art/raw/
   |
postrun.py --watch   dtf.py + photo_mockup.py -> R2 art/mock/
   |
ebay_graphics.py     -> tshirt_ebay_NN.csv
   |
check_csv.py / no_duplicates.py / global_shuffle.py
```

Fulfilment is separate: `print_tool.py` (GUI) or `order.py` (CLI) pull a
design by custom label and produce the print file.

---

## 2. IMAGE GENERATION

**Model**

| | |
|---|---|
| Base | `stabilityai/stable-diffusion-xl-base-1.0` |
| UNet | `ByteDance/SDXL-Lightning`, `sdxl_lightning_4step_unet.safetensors` |
| Scheduler | Euler, `timestep_spacing="trailing"` |
| Steps | 4 |
| Guidance | 0.0 |
| Refiner | off — Lightning replaces it |
| Resolution | 1024 x 1024 |
| Output | JPEG quality 95, subsampling 0 (`--jpeg`) |

Earlier batches used `Lykon/dreamshaper-xl-1-0` at 30 steps, CFG 7, with the
SDXL refiner at denoise 0.25. Lightning is ~7x faster and measured the same
reject rate, so it replaced it.

**Prompt template**

```
{style_prefix} {subject} {scene}, {composition}, {style}, {palette}, {BASE}
```

`BASE` (appended to every prompt):

```
t-shirt design, subject isolated on pure black, nothing behind it,
bold saturated colour, high contrast, crisp clean edges, vibrant
```

`NEGATIVE` (every prompt):

```
nude, nudity, naked, topless, cleavage, lingerie, bikini, sexual,
suggestive, erotic, revealing clothing,
faded, washed out, muted, desaturated, dull, pastel,
translucent, hazy, wispy, blurry edges,
grey background, light background, white background, border, frame,
panel, backdrop, rectangle, box, full scene, greyscale, text
```

Both must stay inside CLIP's 77-token limit; `audit.py` enforces it
(currently ~72 and ~69 tokens).

**Design space (`graphics.py`)**

| | |
|---|---|
| Subjects | 1,512 across 34 families |
| Scenes | 35 |
| Styles | 16 |
| Total combinations | 3,894,993 |

`design(index)` is deterministic — the same index always yields the same
prompt. That is what makes the ledger work.

Wording that must not return, learned the hard way:

- `"solid black background"` — SDXL paints a literal panel. Use
  `"subject isolated on pure black, nothing behind it"`.
- any fade or dissolve instruction — DTF cannot print a fade.
- scenes containing `"behind"` — they contradict BASE and the model
  resolves the contradiction by painting the thing behind.

---

## 3. PRINT FILE (`dtf.py`)

| | |
|---|---|
| Canvas | 3600 x 4800 px |
| DPI | 300 |
| Artwork margin | 0.80 of canvas |
| `BORDER_MAX` | 90 |
| `SATURATION` | 1.12 |
| Output | RGBA PNG, always — JPEG has no alpha |

**Black-point normalisation.** SDXL cannot output transparency, so "pure
black" arrives as a lifted pedestal around 45-48. Measure the 60th
percentile of the border, subtract it, rescale against the image's own 99.5th
percentile so the artwork keeps its brightness. This one step fixed both the
square-box artefacts and most of the rejections.

**Alpha ramp.** 4 levels then pushed to fully opaque — about 97% solid, 2.3%
partial, and that remainder is one pixel of anti-aliasing. DTF adhesive
powder needs enough ink to grip, so a feathered edge peels after washing.

**QC.** Border luminance measured on the NORMALISED image. Above
`BORDER_MAX` the design is rejected as a light background. Typical batch keep
rate is 83-88%.

---

## 4. MOCKUP (`photo_mockup.py`)

| | |
|---|---|
| Output | 2000 x 2000 JPEG |
| Template | `blank.png`, 1086 x 1448, black tee on white |
| Shirt fills | ~95% of frame |
| Print box | 40% of shirt width |

The square crop must be clamped inside the source image. Cropping
`max(width, height)` around the shirt's centre ran past the edges and PIL
filled out-of-bounds with black, putting black bars down both sides of every
live listing.

---

## 5. PRODUCT AND PRICING

**Variation format** — 10 sizes per listing:

| Size | Price |
|---|---|
| 3-4 Yrs | £8.99 |
| 5-6 Yrs | £11.99 |
| 7-8 Yrs | £11.99 |
| 9-11 Yrs | £11.99 |
| 12-13 Yrs | £11.99 |
| S | £11.99 |
| M | £11.99 |
| L | £11.99 |
| XL | £11.99 |
| 2XL | £11.99 |

**Flat format (`--single`)** — one row, £11.99, size collected through
eBay's personalisation box. Used on accounts with tight listing limits.

Colour is Black only. Garment is 100% cotton, 180gsm, crew neck, short
sleeve, regular fit, machine washable.

The A4 iron-on transfer was dropped — it took listings from 11 variations to
10.

---

## 6. EBAY SETUP

| | |
|---|---|
| Category | 15687 (t-shirts) |
| Shipping profile | `2` |
| Return profile | `1` |
| Payment profile | `1` |
| Location | Manchester |
| Postcode | **blank** — a shared postcode links accounts |
| Format | FixedPrice, GTC |
| Quantity | 1 per listing |
| Condition | 1000 (new) |

**CSV header** (`ebay_graphics.py`):

```
Action(SiteID=UK|Country=GB|Currency=GBP|Version=745|CC=UTF-8),CustomLabel,
*Category,StoreCategory,Relationship,RelationshipDetails,*Title,Subtitle,
*Description,*ConditionID,PicURL,*Format,*Duration,*StartPrice,*Quantity,
*Location,PostalCode,ShippingProfileName,ReturnProfileName,
PaymentProfileName,*C:Size,*C:Colour,C:Brand,*C:Type,*C:Style,C:Department,
*C:Material,C:Sleeve Length,C:Neckline,C:Fit,C:Pattern,C:Size Type,
C:Garment Care,C:Occasion,C:Theme,C:Country/Region of Manufacture,
C:Personalise,C:Personalisation Instructions,C:Handmade,C:Features
```

**Personalisation columns** — taken from a real listing he built by hand and
exported, not guessed:

```
C:Personalise                    = Yes
C:Personalisation Instructions   = TYPE SIZE BELOW, CHOOSE: S,M,L,XL,XXL
*C:Size                          = One Size
*C:Colour                        = Black
C:Handmade                       = (blank)
```

The buyer gets a 250-character free-text box. It takes a minute or two to
appear on a newly created listing — that is not a fault.

**Revise format** for bulk title changes:

```
Action(SiteID=UK|Country=GB|Currency=GBP|Version=745|CC=UTF-8),ItemID,*Title
Revise,137649835318,Sea Turtle Coastal Nautical Bathroom Gift Wall Art Poster Unframed A4 ART PRINT
```

Result rows come back as `Warning` because the account uses business
policies. **Warning rows DO apply.** Only `Failure` does not.

---

## 7. R2 LAYOUT

```
r2:<bucket>/art/raw/<index>.jpg     the generated design
r2:<bucket>/art/mock/<index>.jpg    the listing photo
r2:<bucket>/art/state/              queue + ledger backups
r2:<bucket>/art/csv/                built CSVs
r2:<bucket>/code/                   the code zip
```

One bucket per eBay account:

| Bucket | Public URL |
|---|---|
| tshirt-mockups (store 1) | https://pub-19fad43c12d848caa97d6d53a8695d03.r2.dev |
| tshirt-m12k | https://pub-4b710c8610a84acc8fad1513f48132fd.r2.dev |
| tshirt-km | https://pub-3fd66cede8da49a6bed3678904c8eca6.r2.dev |
| tshirt-us | https://pub-4c63a0303f24460dbff733e45afeac31.r2.dev |
| tshirt-usm | https://pub-ca511edb2cd843008f0b3782a7f6b78a.r2.dev |
| tshirt-roop | https://pub-99a981dc71a04b7cb797533c993c9aae.r2.dev |
| tshirt-mine | https://pub-cc314efd6b1d41fab92fc5f7cd3946b4.r2.dev |

rclone config for R2 — note `provider = Other`, not Cloudflare:

```
rclone config create r2 s3
rclone config update r2 provider Other
rclone config update r2 access_key_id KEY
rclone config update r2 secret_access_key SECRET
rclone config update r2 endpoint https://ACCOUNT_ID.r2.cloudflarestorage.com
rclone config update r2 acl private
rclone config update r2 no_check_bucket true
```

A scoped token returns 403 on `rclone lsd r2:` even when it can read the
buckets. Test with `rclone ls r2:BUCKET --max-depth 1` instead.

---

## 8. DUPLICATE PREVENTION — the hard requirement

No design may ever appear twice, within a store or across stores.

1. `rebuild_ledger.py` is pointed at **every** bucket's `art/raw`, and
   reconstructs `used_designs.txt` from the filenames actually present. R2
   is the source of truth, not any local file.
2. `pick.py` reads that ledger and excludes every index in it. It refuses to
   run without one.
3. `no_duplicates.py` runs before any upload and exits non-zero on failure.

Known bug, not yet fixed: a **failed** `pick.py` run still appends its draw
to `used_designs.txt`. Three failures inflated the ledger from 924,199 to
1,824,199, marking designs used that were never generated. It should only
write on success. Workaround is to rerun `rebuild_ledger.py`.

---

## 9. RUNNING A BATCH

```bash
bash gpucheck.sh                     # real torch allocation on every GPU
export R2_REMOTE=r2:<bucket>/art
python rebuild_ledger.py r2:bucket1/art/raw r2:bucket2/art/raw ...
python pick.py --count N
python audit.py generation_queue.csv          # must say ALL CHECKS PASSED

nohup python postrun.py --bucket $R2_REMOTE --watch 300 --transfers 64 &

for i in 0 1 2 3 4 5; do
  CUDA_VISIBLE_DEVICES=$i nohup python pod_sdxl.py \
    --lightning --jpeg --hires 0 \
    --start $((i*SLICE)) --limit SLICE --tag w$i > w$i.log 2>&1 &
done
nohup python watchdog.py $R2_REMOTE &
```

Start postrun **before** generation so mockups keep pace. Always pass
`--bucket`.

Measured on 6x RTX 4090: **1.3 img/s per worker**, so 440,000 designs in
~17 hours for about $36.

---

## 10. TRAPS THAT HAVE COST REAL TIME

| Trap | Detail |
|---|---|
| Hardcoded `.png` | `--jpeg` broke the print file (JPEG has no alpha) and broke postrun's done-set. Compare by `os.path.splitext(f)[0]`, never by swapping the extension. |
| `already done: 0` | If postrun reports 0 when mockups plainly exist, STOP IT — it is about to rebuild everything. |
| `kept 0` | Means an exception, not a QC threshold. A threshold gives a high reject rate, never a total one. Run `dtf.to_dtf` on one file to see the real error. |
| Missing `--bucket` | postrun silently processes store 1. The tell is a large "already done" when the target should be near zero. |
| Missing `--img-base` | CSVs point at store 1's public URL. **Always inspect the PicURL column before uploading.** |
| `pick.py` writes nothing | On "only N unused designs available" it writes no file, and `audit.py` then passes on the OLD queue. Check the audit's subject count matches the current `graphics.py`. |
| `head -N` on a CSV | Descriptions contain newlines, so line count is not row count. Slice with `csv.reader`. |
| Device node names | `gpucheck.sh` must test a real torch allocation. Nodes are not always numbered from zero, and the old check terminated healthy pods. |

---

## 11. TITLE KEYWORDS

Measured across 669,138 live listings.

T-shirt titles already carry the subject keyword correctly — 100% of dog
breed titles contain "Dog Lover". What they lacked was commercial language:
gift 0%, funny 0%, novelty 5%, unisex 4%, and **"Mens" in 100% with "Womens"
in 0%** on unisex garments.

Wall art was worse: gift 0%, home decor 0%, picture 0%, framed 0%, room
words ~0%, poster 14% — with roughly half of every title spent on palette
and style vocabulary nobody searches (Muted Pastels, Ochre, Industrial Loft).

`retitle_tees.py` and `retitle_art.py` rewrite both into eBay Revise files.
Method: strip the generator's own vocabulary, keep the subject, spend the 80
characters on buyer language.

Competitor pattern worth copying: they stack product nouns — "Wall Art Print
Framed Canvas Picture Poster Decor" — and fill the **Room** item specific,
which is a sidebar filter. Do not claim Canvas or Framed for unframed paper.

---

## 12. NOT SPECIFIED HERE

These are genuinely unknown to me and must come from him:

- **Paper gsm** for the wall art description block
- **Store category IDs** (`StoreCategory` is currently blank)
- **Wall art frame sizes and colours** — the poster generator was built in a
  different project and I have not seen its code
- **Wall art pricing**
- Poster-side prompts, subjects and CSV schema

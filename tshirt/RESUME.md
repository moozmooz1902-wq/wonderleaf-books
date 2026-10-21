# Where this is up to

Branch `claude/dreamy-hopper-cgp4p4`. Everything below is committed.

## Done

**Read the designs.** 22,437 of the 22,485 listings that sold (99.8%) read
by a vision model on a 4090, ~4h, ~$3. `designs_read.jsonl.gz` holds the
printed text, illustration subject, style and layout for each.

**Mined the slogans.** 89 non-overlapping templates covering 40.6% of
slogan sales and 20.7% of all sales, against 7.1% for the eight I first
wrote by hand. `MINED_TEMPLATES.csv`, `TEMPLATE_BANK.json`.

**Vetted them by hand.** `vetted.py` - 41 templates written out in full,
each tagged with the slot type it takes; 15 dropped with the reason
recorded. A mined skeleton carries no grammar, so untyped slotting gave
"I AM A EVIL" and "I LOVE TO GRIZZLY".

**Built the catalogue.** `REPLICA_V5.csv` - 149,680 listings, 118,360 with
a slogan. Titles rebuilt on measured keywords (`KEYWORD_FINDINGS.csv`):
funny 2.12x is in every title, cotton 0.40x removed from all of them.

**Four house looks**, mixed across the catalogue - A 35%, B 30%, D 20%,
C 15%, seeded off source_idx so a listing keeps its look across reruns.

**Real mockup.** `BLANK_TEE.png` - the seller's own product photo
(listing 101812, eBay's 1600px original) with its print patched out.
Placement measured: torso x 292-1312, centre 802, print 46% of torso
width, top edge 60px below the neckline.

**eBay file.** `ebay_file.py` writes UK File Exchange rows. Policies all
named "default", quantity 1, category 15687, GTC fixed price.

**R2.** Bucket `tshirt-m12k`, account M12K, public base
`https://pub-4b710c8610a84acc8fad1513f48132fd.r2.dev`. `r2_upload.py` is
resumable and reports real errors.

## Read first

`ACCESS.md` - what is connected, what is not, and what has already been
tried and failed. RunPod is wired up and needs no setup from the seller.

## Next

1. CPU pod (16 vCPU, 50 GB). NOT a GPU - measured 12.3 designs/sec/core,
   79 KB per JPEG, so 118,360 designs is 2.7 core-hours and 9.5 GB.
2. Upload `tshirt_pack.tgz` to /workspace, then follow `RUN.md`.
3. Render, check `failed 0`, upload, build the eBay file.

## Blocked on the seller

- **Price.** The 9.99 in `ebay_file.py` is a placeholder; the export has no
  price column so it cannot be derived.
- Confirm category 15687 matches their existing listings.
- Whether listings need S-XXL size variations. The current file is
  single-SKU so the format can be proven first.

## Open questions

- The last session ended with "it's taking forever" after the pod was set
  up. Unclear whether that was pod provisioning or the render itself -
  worth getting the actual progress line before assuming the render is
  slow, since it benchmarked at 12.3/sec/core here.
- ~1 in 8 slogans has a weak niche ("EAT SLEEP UNION JACK REPEAT"). Offered
  to add a confidence column so the worst can be cut before listing.
- The 62% of listings with illustrations still need artwork: ~10,000 images
  for 2,517 subjects, ~3h on a 4090, ~$2.50. Not started.

## Things that went wrong, so they are not repeated

- A silent `except Exception` hid a dead Ollama for a full pass of 9,268
  images. Every long-running script now prints the first of each distinct
  error and aborts on a run of failures.
- Template coverage was first reported as 44.3%; sliding the mask along one
  slogan produced four skeletons each claiming the same units. Real figure
  20.7%, via greedy set cover.
- Illustration rate was reported as 83.7% from `main_image` being non-null,
  but 2,821 rows say `text_only` and still name an image. By layout it is
  71.1%.
- dhash first collapsed on garment silhouette rather than artwork; cropping
  to the print area took unique designs from 19,323 to 140,085.
- racer 18.10x / cafe 17.57x / chopper 15.22x are not keyword effects -
  56-78% of each one's units come from three listings.
- Told the seller to rent a 4090 with 150 GB for a job that is Pillow on a
  CPU needing 9.5 GB. Benchmark before specifying hardware.

## 2026-10-06 - the upload set is finished

`EBAY_PARTS_CLEAN.zip` was the file to push AT THAT DATE. **It is
superseded - do not push it.** It holds 115,966 listings at £12.99 with
shipping policy 1, and predates both the variation-set fix for error
21919053 and the title de-duplication.

**The file to push is `EBAY_ONE_FILE.zip`** (7 Oct): 105,573 listings,
527,865 variations, £11.99, shipping policy 2. The 10,393 fewer listings
are redundant copies of titles that still collided after a distinguishing
noun was appended, dropped on the seller's standing instruction - see
PUSH.md. Every one of the 105,573 custom labels was verified to resolve to
both `art/mock/<label>.jpg` and `art/raw/<label>.png` in `tshirt-m12k`.
`PUSH.md` has the order of operations.

Three things were added since the last entry:

- **Illustrations that a DTF transfer can print.** 400 generated, 365
  physically printable, 271 judged good by a vision model, 259 after the IP
  filter; about three in four of those are genuinely good, so roughly 200
  solid designs. `dtf.py` forces flat ink, `judge_illus.py` asks whether the
  result is recognisable, and `ACCESS.md` records why four different pixel
  statistics could not answer that question.
- **13,313 listings composed as picture-over-type**, recoloured per listing
  so one drawing of a motorcycle becomes twelve. Zero repeats on
  picture+layout+palette+slogan.
- **389 listings pulled for trademark or likeness.** Banksy, King Charles,
  Che Guevara, Spitfire, Ducati. 52 of them had clean titles and the brand
  only in the artwork, so they are dropped by SKU as well as by text.

Still open:
- Background panels on roughly one illustration in six. Unsolved in post and
  in prompt; the gate rejects the worst and the rest get through.
- The seller has not yet run `EBAY_TEST_50.csv`.
- A print-size bump of 10-15% was offered once the placement settled at
  mid-chest and has not been answered. The geometry is untouched.

## 2026-10-21 - re-verified before hand-off

Checked, not assumed, before telling the seller to push:

- `EBAY_ONE_FILE.zip` passes `unzip -t`; the CSV re-parses to exactly
  105,573 parent rows, 527,865 variation rows, 633,438 data rows, 30
  columns, 105,573 distinct parent SKUs, zero parents without a PicURL.
- Every variation is £11.99; every parent carries shipping 2 / returns 1 /
  payment 1; parent `RelationshipDetails` is `Size=S;M;L;XL;2XL` and the
  children repeat `*Category`/`*ConditionID`/`*Title`, so the 21919053 fix
  is present in this file.
- 8 listing photos sampled at random from the file: all HTTP 206 from
  `pub-4b710c8610a84acc8fad1513f48132fd.r2.dev`. The bucket is still live
  two weeks on.

**Open conflict the seller must settle: the shipping policy.** This file
uses `2`, on the seller's word recorded in PUSH.md. The repo-root
`CLAUDE.md` states as a shared fact that on EVERY account the shipping,
returns and payment policies are all named `1`. Both cannot be right, and
it is one field. If a test upload returns a business-policy error, flip
`ShippingProfileName` to 1 and nothing else changes.

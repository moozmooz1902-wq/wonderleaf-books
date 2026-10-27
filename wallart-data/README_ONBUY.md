# OnBuy — the files, and the two things that block them

Built 27 Oct 2026. 10,000 listings from `luxvia-art`.

**Read the first section before you upload anything.** The files are built
and checked, but two values in them are placeholders that only your OnBuy
dashboard can supply, and one of them may need OnBuy's permission rather
than a copy-and-paste.

---

## 1. The two blockers

### A. OnBuy wants a barcode for every product, and there are 10,000 of them

OnBuy is a **catalogue** marketplace, not a listing marketplace like eBay.
On eBay you create a listing. On OnBuy you create (or match) a *product* in
OnBuy's shared catalogue, and then put your *offer* against it. New products
normally need a real GS1 barcode — an EAN — and OnBuy's own seller pages say
so plainly.

That does not scale here, and it cannot be worked around by inventing
numbers:

- 10,000 designs is 10,000 products. Buying 10,000 GTINs from GS1 UK is a
  four-figure annual licence, and the full 3.77M catalogue is simply not
  purchasable.
- Made-up or resold barcodes are the fastest way to lose the account, and
  the same reasoning already applies on the Google feed: `web/catalogue/feed.py`
  omits GTIN entirely rather than invent one, because Google's own guidance
  is "submit only if you're sure it's correct".

**The route is the exemption.** OnBuy grants a barcode exemption to sellers
who hold a **UK or EU trademark for their brand**. So:

1. Raise a ticket in the OnBuy seller panel asking for a barcode exemption
   for brand **Walryvo**, for wall art / art prints, explaining that these
   are made-to-order prints produced by you and not manufactured goods.
2. If they ask for the trademark: **NORYMUS LIMITED does not currently hold
   a registered trademark for Walryvo as far as this repo knows.** A UK
   trademark application is £170 for one class through the IPO and takes
   about four months to register, though the application number exists
   immediately. Worth asking OnBuy whether an *application* satisfies them
   before paying for one.

Until that is settled every product row reads `NEEDS-BARCODE-EXEMPTION`,
and `build_onbuy.py --check` refuses the file. That is deliberate: it will
be rejected loudly rather than filed wrongly.

**This is the decision that determines whether OnBuy is viable at all**, so
it is worth raising the ticket before anything else here.

### B. The category ID is not knowable from outside your account

OnBuy's category IDs come from either:

- the **Category Sheet** inside the Product Create Template, or
- `GET /v2/categories` with your API keys.

Neither is reachable from here — the API returns `401 badToken` without your
keys, and the template is behind the dashboard login. So every product row
reads `NEEDS-CATEGORY-ID`.

Guessing was the alternative and it is worse. A guessed ID files 10,000
listings in the wrong department, where they get no traffic and have to be
unpicked one at a time.

**What to send me:** the category row for wall art / art prints from the
Category Sheet — the ID and its path. I put it in `onbuy_plan.json`, re-run,
and the placeholder is gone. One line.

---

## 2. What I need from you, in one list

| | |
|---|---|
| 1 | Your OnBuy **API keys** — consumer key and secret key. Included on the £25 Standard plan. **This is the one that matters most**; see section 6. |
| 2 | Raise the **barcode exemption** ticket for brand Walryvo. The API does not solve this one. |
| 3 | If there are no API keys: the **Product Create Template** spreadsheet (Listing → Add Listing → "Click Here to Find Out More" → Product Create Template URL) and the **category ID** from its Category Sheet. |
| 4 | **Weigh one framed print of each size** (A4, A3, A2) in its packaging. See section 5. |

Item 1 is the big one. **Every column name in the CSV right now is my best
reading of OnBuy's public documentation, not a copy of their template.**
That is the opposite of how the eBay files were built — those copied the
shape of a file eBay had already accepted on your own account, which is why
they came out clean. There is no accepted OnBuy file to copy yet.

Because of that, the data is written out twice:

- `luxvia-art_onbuy_10k_rows.jsonl` — the **data**, with my own field names.
  Every fact OnBuy asks for is in here, independent of any column layout.
- `luxvia-art_onbuy_10k_*.csv` — a **rendering** of that data, using the
  column names in `onbuy_plan.json["columns"]`.

So when the template arrives, correcting the names is editing one block of
`onbuy_plan.json` and re-running. Not a rebuild.

---

## 2b. Where in OnBuy this gets uploaded — and why the CSV is not what goes in

**There is no section you can drop the CSV I built into.** That is worth
stating plainly before the click-path below, because the path leads
somewhere that wants a different file.

OnBuy's bulk route takes **OnBuy's own Product Create Template**, a
spreadsheet with an Explanation tab, a Template tab and a Category Sheet.
My CSV is the same data under my own column names. So the file in
`out/onbuy/` is not the thing that gets uploaded — it is the data that gets
poured into their template once we have it, which is why the template is
item 3 on the list above.

### The click path

From the **Seller Control Panel**:

1. **Listings → Add Listing → "Click Here to Find Out More"**
2. That page carries the **Product Create Template URL**. Download it.
3. Fill in the Template tab. Read the **Explanation** tab first — it is the
   authoritative field list. Use the **Category Sheet** to find the wall-art
   row.
4. Submit it as a **support ticket** through the **Support Centre in the
   Seller Control Panel**, attaching the file with a short message saying
   what it is.
5. Track it under **My Ticket**. Reportedly around **five days**.

It is not a self-serve upload with a progress bar. A person reads it. That
is the whole reason for sending TEST_5 first.

If the Support Centre is down, OnBuy's Seller Terms name
`sellersupport@onbuy.com` as the fallback.

### HOW MUCH TO TRUST THAT PATH

**The menu names are from a third-party guide roughly two and a half years
old, and OnBuy has since rebranded to OnCommerce** — `onbuy.com/gb/sell`
now redirects to `oncommerce.com`. The buttons have probably moved. The
same thing happened on Cloudflare during the website setup, where "Add a
site" had become "Onboard a domain" and the walkthrough had to be corrected
mid-task.

OnBuy's own knowledge base has the current version, as article
`product-create-template` on `seller.onbuy.com`. **That is behind your
login — it 404s from here.** If you can open it, a screenshot of that page
answers this question properly and I will correct this section.

### TWO THINGS FOUND WHILE CHECKING, both of which matter

**1. The Seller Control Panel may already show you the category ID.**
OnCommerce's own seller page says the Control Panel "shows each product's
category ID and fee before it goes live". If that is visible anywhere in
the listing flow, `NEEDS-CATEGORY-ID` can be answered without the template
at all. Worth a look while you are in there.

**2. API product creation has to be switched on for your account first.**
OnBuy's API documentation says products created through the API appear
under **Approve Products** in the Control Panel, and that **live product
creation must be enabled on the account** before the create call works.
So if we go the API route — which section 6 argues we should — that switch
is part of the same request as the barcode exemption, not a separate
discovery later.

---

## 3. The files

In `wallart-data/out/onbuy/`:

| File | What it is |
|---|---|
| `tests/luxvia-art_onbuy_TEST_5.csv` | 5 listings, 50 rows. **Upload this first.** |
| `tests/luxvia-art_onbuy_TEST_25.csv` | 25 listings, 250 rows. Second. |
| `luxvia-art_onbuy_10k.zip` | the real thing — 3 CSVs, 10,000 listings, 100,000 rows, 1.6 MB zipped |

The loose CSVs and the `.jsonl` are not committed (34 MB and 79 MB); they
rebuild in 23 seconds:

```
cd wallart-data
python3 build_onbuy.py --limit 10000 --tag 10k
python3 build_onbuy.py --check out/onbuy --verify-pictures 150
```

### Do the small file first, exactly like eBay

The eBay route was two test files before 3.77M rows, and that is what caught
the variation-picture problem. OnBuy's bulk route is **slower to fail than
eBay's**: the template goes in as a support ticket and is reviewed by a
person, reportedly around five days. A format mistake in a 10,000-listing
file costs five days and a rejection on a brand-new account. A format
mistake in a 5-listing file costs five days and nothing else.

**My recommendation, since you asked:** 10,000 is the right size for the
first real batch — but not the first *upload*. Send TEST_5, get it accepted,
then the 10,000. The remaining 465,660 rendered designs in this bucket alone
are there whenever you want them, and `--limit` is the only thing that
changes.

---

## 4. What is in the 10,000, measured

```
listings 10,000   variant rows 90,000   rows in file 100,000
  theme        6 distinct   creature 34%, botanical 28%, place 25%,
                            stilllife 5%, architecture 4%, celestial 3%
  technique   14 distinct   linocut 9%, pastel 9%, monotype 9%,
                            screenprint 8%, gouache 8%, palette_knife 8%
  palette      5 distinct   duotone 23%, monochrome 21%, complementary 21%,
                            neutral 19%, spectrum 16%
  subject   4410 distinct   most repeated 4x
  colourways       0: 2490  1: 2574  2: 2471  3: 2465
```

You asked for a mix. The theme split lands within a point of the whole
catalogue's — Animals 33% / Flowers 27% / Landscapes 25% as measured on
22 Oct — so this is a fair slice and not a corner of it.

**Near-duplicates: 11 in 10,000, 0.11%.** This is the number that matters
most, because the wall-art branch blames **89% near-duplication** for 424k
eBay listings not selling. Measured the way `CLAUDE.md` requires: on the
256-bit gradient hash of the **cropped artwork**, at the same ≤24-bit
threshold as every audit before it, excluding a design's own colourways.

`luxvia-art` is the one bucket that never had a near-duplicate audit run on
it — there is no `drop_luxvia-art.txt` beside the other three — so this
selection was deduplicated against itself as it was built.

**79 listings were excluded as restricted subjects.** The screen is copied
character for character from `web/catalogue/select.py`: alcohol and tobacco
words in a title. Not a theoretical risk — the third listing the builder
picked before the screen went in was titled *"Ink Wash Beer Print"*.
Marketplace restricted-product screening is automated and reads the title,
and a restricted-product action on a brand-new account is not worth eleven
drinks prints.

**435 were excluded by the 4-per-subject cap**, so no single subject can
dominate.

**All 150 sampled picture URLs came back HTTP 200, `image/jpeg`, over 5 KB.**
30,000 distinct image URLs are referenced in the file.

---

## 5. Decisions I made, and why — overrule any of them

### Framed only. Nine variants, not twelve.

This is the one place the OnBuy file deliberately differs from the eBay one.

Your eBay listings sell an unframed option whose row carries **no picture**,
so eBay falls back to the listing's main image — the black frame. You
approved that on 22 Oct and it matches how your existing listings already
work.

It does not transfer. On a marketplace that shows a picture per variant,
that is a **framed photograph on a product that has no frame** — which is
exactly the mismatch the website was restructured around (see the note at
the top of `web/catalogue/product.py`). And it cannot be fixed here:

- no unframed photograph exists in `luxvia-art`;
- none can be made, because the stored R2 token **cannot write to
  `luxvia-art`** — only to `tshirt-m12k`;
- the raw panel at `luxvia/gen/<SKU>.jpg` is **not** a substitute. It is one
  image per design rather than one per colourway, so it shows the wrong
  colours for three of the four, and it still carries the uncropped bottom
  strip where FLUX scrawls a fake signature. That strip is cropped at render
  time for a legal reason, not a cosmetic one.

So OnBuy launches framed-only, every variant with its own correct
photograph. **This loses the £8.99 entry price**, which is a real cost. Add
unframed the moment a rendered unframed photo exists in this bucket —
`web/catalogue/unframed.py` already does this job for the website and would
need only an R2 write token for `luxvia-art`.

### Brand: Walryvo, not "Unbranded"

The eBay files use `Unbranded`. That cannot work on OnBuy: a catalogue
product needs the real manufacturer brand, and the barcode exemption is
granted on a trademark **for that brand**. "Unbranded" can be neither
trademarked nor exempted. Walryvo is yours, held by NORYMUS LIMITED, and is
the only name here that can carry an exemption.

Say the word if you would rather OnBuy carried a different name.

### One colourway per design

A design exists in four palettes. eBay lists all four, which is right for a
1.9M catalogue. For a first 10,000 it means 10,000 **distinct designs**
instead of 2,500 designs four times over — the widest mix for the same row
count and the lowest near-duplicate reading. The other three colourways are
untouched and available for the next batch.

### Prices are £5 under eBay on every framed size — your instruction, 27 Oct

| | eBay | **OnBuy** |
|---|---|---|
| A4 framed | £24.99 | **£19.99** |
| A3 framed | £29.99 | **£24.99** |
| A2 framed | £34.99 | **£29.99** |

So one design now costs less on OnBuy than on eBay. That is deliberate, and
it is your call on a marketplace you are entering cold.

These prices are read **only** by `build_onbuy.py`. `ebay_plan.json` and
`web/business.config.json` are untouched, so this moved nothing on eBay and
nothing on walryvo.com.

**What it does to the margin.** At OnBuy's 15% commission:

| | Price | Commission | Net | was |
|---|---|---|---|---|
| A4 | £19.99 | £3.00 | **£16.99** | £21.24 |
| A3 | £24.99 | £3.75 | **£21.24** | £25.49 |
| A2 | £29.99 | £4.50 | **£25.49** | £29.74 |

Nobody here knows your print-and-frame cost, so **whether £16.99 on an A4
still clears is your number to check** — I am not going to assume it does.
Breakeven on the £25 + VAT subscription moves from about 1.5 A4 sales a
month to about 1.8, which is not the thing to worry about.

### Unframed: £6.99 / £10.99 / £16.99, recorded but not used

You also asked for £2 off the unframed prices — eBay's £8.99 / £12.99 /
£18.99 becoming £6.99 / £10.99 / £16.99.

**The OnBuy file has no unframed variant**, for the reason in the section
above: no unframed photograph exists in `luxvia-art` and none can be made
from here. So there is no row for those prices to go on yet.

They are stored anyway, as `unframed_when_available` in
`onbuy_plan.json["sizes"]`, so whoever adds the unframed variant does not
have to ask you again. `--check` asserts that none of those three numbers
appears in a framed-only file, so they cannot leak onto a framed row by
accident.

### The delivery weights are estimates, and they are the one number here that was never measured

`A4 0.8 kg, A3 1.3 kg, A2 2.0 kg`, packaged. I have no scale and no
packaging spec, so these are reasoned guesses.

**OnBuy prices delivery off them.** An estimate that is too low is paid for
on every single order, quietly, for as long as it stands. Weigh one of each
size in its packaging and send me three numbers.

### Its own description

`listing_text.description()` — the eBay copy — names the unframed option, so
it would be wrong here. The OnBuy copy is new and says only what the website
says: premium satin art paper, pigment inks, framed behind glazing, made to
order in the UK, dispatch within 3 working days, not hand-painted and not
signed.

No gsm, no "archival", and **no naming of the glazing material** — the first
draft said "shatterproof acrylic rather than glass", which nobody here knows
to be true. The website says "framed behind glazing", and so does this.

---

## 6. What it costs — no per-listing fee, no SKU cap

Checked 27 Oct 2026. **Everything in this section is from third-party
sources and OnBuy's public pages, and the commission table was read from
OnBuy's API on 2 August 2026. Your own seller panel is the authority** — it
shows the real rate against each listing, and promotional subscription
prices change.

### The shape of it is good for this catalogue

| | |
|---|---|
| Per-listing fee | **None.** No insertion fee, no matter how many products. |
| Listing / SKU cap | **None found on any plan.** ChannelEngine's integration guide records "minimum number of SKUs: none", and the Standard plan is described as unlimited listings. |
| Subscription | **Standard £25/month**, Partner £69 (promotional, £129 from Jan 2027), Professional £249. Quoted before VAT. 30-day rolling. |
| Commission | **By category, and wall art lands at 15%** — "Arts, Crafts & Sewing" is 15%, "Furniture" is 15%, "Everything else" is 15%. Minimum £0.25 a sale. |
| Commission base | **The delivered total the buyer pays, INCLUDING postage.** |

This is the opposite of eBay's shape, and it is the right shape for us:
there are no insertion fees to run out of and no selling limits to raise.
**The subscription costs the same whether you list 10,000 or all 3.77M.**
Volume is free; only sales cost anything.

### Margin at the current prices

At 15% commission, free UK delivery (so the commission base is just the
price), on the **reduced OnBuy prices** set on 27 Oct:

| | Price | Commission | Net |
|---|---|---|---|
| A4 framed | £19.99 | £3.00 | **£16.99** |
| A3 framed | £24.99 | £3.75 | **£21.24** |
| A2 framed | £29.99 | £4.50 | **£25.49** |

Before print and frame cost, packaging and postage.

**Breakeven on the subscription is about 1.8 A4 sales a month** (£25 + VAT
= £30 against £16.99 net). That is a low enough bar that the subscription
is not the thing to worry about.

**Do not add a delivery charge to dodge commission — it does not work.**
Commission is charged on the delivered total including postage, so £24.99 +
£4.95 delivery is charged at 15% of £29.94, not of £24.99. Keep delivery
free and the price inclusive, which is the same call
`web/business.config.json` already makes for the website and for the
Merchant Center feed.

For comparison, eBay UK's final value fee on art is around 12.8% plus 30p
an order, so OnBuy is roughly two points worse per sale. Not decisive, and
the absence of insertion fees and selling limits more than covers it at
this catalogue size.

### THE API IS INCLUDED ON THE £25 PLAN, AND THAT CHANGES THE PLAN

OnBuy's own sell page lists "Access to API & integrations" on **Standard**,
not only on the higher tiers. That matters more than any of the fees above,
because the API makes all three of this file's problems go away:

1. `GET /v2/categories` returns the real category tree, so
   `NEEDS-CATEGORY-ID` is answered without waiting for the template.
2. The create-product call rejects a request naming its missing required
   fields, so the field list stops being guesswork — and
   `onbuy_plan.json["columns"]` can be replaced with the real thing.
3. Listings go up programmatically instead of through a spreadsheet
   reviewed by a person over roughly five days. For 10,000 listings that is
   the difference between one afternoon and several weeks, and for 3.77M it
   is the difference between possible and not.

The barcode question does NOT go away — that is OnBuy policy, not a
transport problem, and the exemption in section 1 is still the route.

**So the useful thing to send me is the API credentials**, not the
spreadsheet. Two values from the seller panel: the consumer key and the
secret key. They are account credentials, so treat them as such; put them
in the environment's settings panel rather than in a chat message if that
is available, and a new session will pick them up.

---

## 7. One thing to watch after it goes live

Pictures are served from `pub-6004b56e...r2.dev`, Cloudflare's managed R2
URL. `stores.json` records it answering **Cloudflare error 1015 for 7,142 of
12,834 requests at roughly 70/s**, and 599 of 600 at 48 concurrent and 19/s.

10,000 listings × 3 photographs is **30,000 images** for OnBuy's crawler to
fetch, and it will not ask politely. If listings come back with missing
images, that rate limit is the first thing to check, not the files.

A custom domain in front of the bucket removes the ceiling and costs about
**£8/year**. It was judged not a blocker at eBay's pace; a single bulk
crawler is a different shape of load.

---

## 8. How the files are checked

`build_onbuy.py --check` refuses the upload while anything in it is a
placeholder, and asserts the things that would quietly break it:

- every row is this run's own generated work, by SKU and picture-URL pattern
  — the buckets also hold your existing catalogue, already listed elsewhere
- no duplicate SKUs
- exactly nine variants per listing
- **no variant whose main image is another frame's photograph**
- no variant stranded in a different file from its product row
- every picture URL well formed, and `--verify-pictures N` fetches a sample
- no title over 80 characters, none naming a restricted subject
- no non-positive price, no missing delivery weight

The two `[BLOCK]` lines you will see are the category ID and the barcode.
They are supposed to be there until section 1 is settled.

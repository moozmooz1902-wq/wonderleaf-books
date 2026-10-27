# Barcodes at volume: what they actually cost, and the one lever that matters

Researched 27 Oct 2026, after OnBuy refused the exemption outright. The
brief was "find the cheapest place to buy these for a big inventory, ideally
500,000 listings under $500."

**Short answer: that price does not exist anywhere, and the search for a
cheaper supplier is the wrong search.** GS1 UK is already close to the
cheapest in the world. The money is saved by changing what we ask for, not
by changing who we buy from.

---

## 1. GS1 UK is already the bargain. Shopping around makes it worse.

Same thing — 100,000 numbers — priced by different GS1 member organisations:

| | 100,000 numbers |
|---|---|
| **GS1 UK** | **£425/yr** (from 10 May 2026; was £356) |
| GS1 US | **$10,500 initial, $2,100/yr** |

GS1 US is roughly **twenty times** GS1 UK for the same block. The usual
instinct — shop around, find the cheap jurisdiction — points the wrong way
here, because we already hold the cheap jurisdiction.

GS1 UK's full ladder, ex VAT, effective 10 May 2026:

| Numbers | Price/yr |
|---|---|
| 10 | £25 |
| 100 | £50 |
| 1,000 | £120 |
| 10,000 | £250 |
| **100,000** | **£425** |

On top sits GS1 UK membership, banded on turnover — roughly £50–£130/yr at
our size, and it includes a first block of numbers.

**On joining a cheaper country's GS1:** a prefix carries a country code and
GS1's model is that you license from the organisation where the business is
established. Some will take foreign members, but a UK company trading on a
UK marketplace under a prefix licensed elsewhere is asking a question
nobody needs to ask, for a saving that does not exist — the cheap one is
the one we already qualify for. Not pursued.

---

## 2. GS1 UK appears to stop at 100,000 per prefix

No tier above 100,000 appears anywhere, and even the turnover band for
companies over £1bn is listed as 100,000 numbers. Members can hold **more
than one prefix**, so 500,000 looks like five blocks:

| Numbers | Route | Cost/yr |
|---|---|---|
| 100,000 | one block | **£425** |
| 500,000 | five blocks | **~£2,125** |
| 1,000,000 | ten blocks | **~£4,250** |

**UNVERIFIED, and worth one phone call.** gs1uk.org returns 403 to this
environment and its pricing pages are JavaScript-rendered, so every figure
here comes from search results quoting GS1 UK's own pages rather than from
the pages themselves. Nothing found says whether GS1 UK will sell five
prefixes to one member, or whether a single shorter prefix at a negotiated
price is possible for a catalogue of this shape. **Ask them directly** —
"we are a UK print-on-demand seller needing 100,000–500,000 GTINs, what is
the best structure" is a free question with a potentially four-figure
answer, and volume pricing that is not published often exists.

---

## 2b. THE TRAP THAT COULD MAKE £425 INTO £4,250

**This supersedes the cost estimate given to the seller earlier, which may
be wrong by a factor of eight.** GS1 UK's membership page says:

> Your new annual fee is calculated using either your company's turnover
> **or your current free GTIN-13 allocation**. Should your GTIN-13
> allocation be higher than the amount covered by your turnover range, your
> fee will be based on your GTINs.

Membership is banded, and the bands pair a turnover range with a GTIN
allocation:

| Turnover | GTINs | Fee/yr |
|---|---|---|
| up to £99,999 | 10 | £50 |
| £100,000–£499,999 | 100 | £100 |
| £500,000–£999,999 | 1,000 | £130 |
| … | … | … |
| £50m–£249m | 10,000 | £1,750 |
| over £1bn | 100,000 | **£4,250** |

Read literally, holding **100,000 GTINs puts a member in the £4,250 band
regardless of turnover** — the band that otherwise means a billion pounds
of sales.

**It is not clear whether that clause applies to purchased prefixes or only
to the free allocation included in membership.** If it applied to
purchases, nobody would ever buy the £425 block, which suggests the two are
separate — but "suggests" is not good enough for a decision with a
£3,700/year gap in it.

**Nobody should buy anything until GS1 UK answers this.** The enquiry is
drafted at `onbuy/GS1_ENQUIRY.md`.

---

## 3. THE LEVER: barcodes are priced per VARIANT, not per design

This is where the money is, and it is entirely in our control.

OnBuy requires an EAN on every **variant row**, not every product. Today
each design is offered in three sizes and three frame colours, so **one
design burns nine barcodes**. Change that and the same £425 buys a
different-sized shop:

| Variants per design | Designs inside 100,000 numbers (£425/yr) |
|---|---|
| 9 — three sizes x three frames (today) | **11,111** |
| 3 — three sizes, black frame only | **33,333** |
| 1 — one size, one frame | **100,000** |

**Nine to one is an 89% cut in the barcode bill for the same number of
products on sale.** No supplier negotiation comes close to that.

So the realistic shapes, all-in with membership:

| Shop | Numbers | Cost/yr |
|---|---|---|
| 1,100 designs x 9 variants | 10,000 | **~£350** |
| 11,000 designs x 9 variants | 100,000 | **~£525** |
| 33,000 designs x 3 variants | 100,000 | **~£525** |
| **100,000 designs x 1 variant** | 100,000 | **~£525** |
| 500,000 designs x 1 variant | 500,000 | ~£2,225 |

**£525/year is about $700** — IF section 2b turns out to be benign. If
the allocation clause bites, the same shop is £4,250+ and the whole plan
changes. That one answer decides everything below it, which is why it is
the only thing to do next.

The cost of going to one variant is real: no size or frame choice on the
product page. Worth weighing against nine times the range.

---

## 3b. WHAT $500 ACTUALLY BUYS — the answer to "is this too high"

The sticker shock comes from multiplying by nine, not from GS1's prices.
At **one variant per design**, the same money buys this:

| Spend | GS1 block | Products live on OnBuy |
|---|---|---|
| ~£120 (~$160) | 1,000 | **1,000** |
| ~£250 (~$330) | 10,000 | **10,000** |
| ~£425 (~$565) | 100,000 | **100,000** |

**A 10,000-product OnBuy shop costs about $330 of barcodes.** A
100,000-product shop costs about $565. Both are inside or beside the $500
budget, and both are an order of magnitude more than the 11,000 the
nine-variant structure allows for the same £425.

So the honest answer to "is this too high" is: **no, not if we stop
spending nine barcodes on one design.** £425 was only ever expensive
relative to 11,111 products. Against 100,000 it is half a penny each.

The caveat is still section 2b — if the allocation clause bites, the
100,000 block carries a £4,250 membership and the 10,000 block (£250) is
the one that stays cheap. That is another reason the GS1 call comes first:
it decides which row of this table is real.

---

## 4. The question behind the question: how big should OnBuy be?

Worth stating plainly, because it is the actual decision.

| Channel | Barcodes needed | Status |
|---|---|---|
| eBay | **none** | 3.77M listings built and delivered |
| walryvo.com + Merchant Center | **none** — `feed.py` omits GTIN deliberately, brand + MPN is accepted | live |
| **OnBuy** | **mandatory, no exceptions** | blocked on this |

OnBuy is the only channel charging admission. The 500,000–1,000,000
ambition does not need to live there — it already has two homes where
barcodes cost nothing.

And a brand-new OnBuy account was never going to be handed 500,000
near-identical print-on-demand products anyway: their product team reviews
feeds by hand, and that is the exact shape they reject. The barcode bill is
not the only reason to start smaller.

**Recommendation.** Buy one 100,000 block at £425. Decide the variant
structure against the table in section 3 — one variant gives the widest
range, three is a reasonable compromise. Run it for a quarter. If OnBuy
sells, more blocks are £425 each and come out of revenue. If it does not,
the loss is £525 and the range stays where it already earns.

**Before buying, ask GS1 UK about volume pricing for 100,000–500,000.**
Unpublished tiers are common and the call is free.

---

## 4b. Can an Amazon ASIN be used on OnBuy? No — and the template proves it

Asked 27 Oct. Amazon hands out three identifiers and none of them is a
GTIN, because **nobody issues GTINs except GS1**:

| Amazon gives you | What it is | Usable on OnBuy? |
|---|---|---|
| **ASIN** | Amazon's internal catalogue id | **No** — see below |
| **FNSKU** (X00…) | an FBA warehouse label | **No** — Amazon-internal, not a GTIN |
| **GTIN exemption** | permission to list *without* one | **No** — it waives a number, it does not create one |

The ASIN answer does not need research, because OnBuy's own Product Create
Template settles it. Extracted into `template_spec.json`:

    EAN / UPC        -> Required either EAN or UPC.
    ASIN             -> Preferred

They are **two separate columns with two different requirement levels**.
OnBuy is happy to receive an ASIN and will use it, but it sits alongside
the EAN rather than instead of it. Filling the ASIN column leaves the EAN
column empty, and the EAN column is the one marked Required.

The same goes for MPN, also "Preferred". We already generate an MPN; it has
never been the problem.

**The useful half of this:** Amazon's exemption is real and OnBuy's is not,
which means **Amazon can carry volume at zero barcode cost** where OnBuy
cannot. If the strategy is "list everything", that asymmetry is worth more
than any barcode discount — see section 5.

---

## 5. If another volume marketplace is wanted

Worth knowing: **Amazon does grant GTIN exemptions**, where OnBuy does not.
That is not a recommendation to open an Amazon account — it carries its own
costs and rules — but if the goal is a second marketplace at serious
volume, the exemption route that OnBuy closed is open elsewhere, and worth
researching before spending four figures on barcodes.

---

## What is already built and waiting

`wallart-data/gtin.py` turns a prefix into unlimited unique,
correctly-checksummed EAN-13s, assigns them permanently in a committed map
so none is ever reassigned, and refuses to overflow the prefix. It needs
one thing: the prefix. Everything after that is one command.

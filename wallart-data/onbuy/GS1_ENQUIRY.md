# Enquiry to GS1 UK — send this before buying anything

Drafted 27 Oct 2026. Send to GS1 UK member support (via gs1uk.org contact
or 020 7092 3500) — or just ring them, because question 1 is a
£3,700-a-year question and a phone call answers it in five minutes.

**Why this exists.** The published prices say 100,000 numbers cost £425 a
year. The membership page says the annual fee is set by turnover **or by
GTIN allocation, whichever is higher**, and the 100,000-GTIN band is
£4,250. Those two statements cannot both apply to the same purchase. Until
somebody at GS1 UK says which, the cost of this project is somewhere
between £525 and £4,250 a year and no decision can be made.

Do not guess it from the website. The pages are inconsistent, some are
years old, and the answer is worth more than the call costs.

---

## The email

**Subject:** Licensing 100,000–200,000 GTINs for a UK print-on-demand
catalogue — fee structure question

Hello,

We are a UK limited company (NORYMUS LIMITED, company 17020866, VAT
GB513541030) selling made-to-order framed art prints online. We need to
license a large block of GTINs and would like to get the structure right
before we buy, rather than after.

**What we need**

Our catalogue is digitally created artwork, printed and framed to order.
Each design is sold in several sizes and frame colours, and the marketplace
we are joining requires a distinct EAN on every variant. Realistically that
means **100,000 to 200,000 GTINs**, growing over time.

We are a small company by turnover — the number of products is large, the
revenue is not. That is the core of our question.

**Our questions**

1. **Does holding a large prefix change our membership fee?** Your
   membership page says the annual fee is calculated from turnover *or*
   from our GTIN-13 allocation, whichever is higher. Your additional-numbers
   price list separately shows 100,000 numbers at £425 a year.

   If we buy a 100,000-number prefix on top of a small-turnover membership,
   do we pay roughly £425 plus our existing membership fee — or does the
   allocation move us into the 100,000-GTIN membership band? This is the
   question we most need answered.

2. **What is the best structure for 100,000–200,000 numbers?** Is that
   several 100,000 prefixes, or can a single shorter prefix be issued? Is
   there pricing for volumes above 100,000 that is not on the public list?

3. **Is there anything designed for high-SKU, low-revenue sellers?**
   Print-on-demand and made-to-order businesses carry very large catalogues
   against modest turnover, and the turnover bands do not obviously fit
   that shape. If there is a plan, a rate or a route intended for it, we
   would like to know.

4. **What is the annual commitment?** We understand prefixes holding active
   GTINs renew annually. If our catalogue later shrinks, can a prefix be
   deactivated and the charge stopped?

5. **Lead time** from payment to having the prefix and being able to assign
   numbers.

We would rather buy the right thing once than buy a block, assign numbers
across a live catalogue, and discover the structure was wrong — reassigning
GTINs after products are published is not something we want to do.

Thank you,

[your name]
NORYMUS LIMITED

---

## What each answer means for us

| If GS1 say | Then |
|---|---|
| £425 + small membership, allocation clause does not apply to purchases | Buy 100,000. ~£525/yr. Decide variants from the table in `BARCODE_COSTING.md` §3. |
| Holding 100,000 moves us to the £4,250 band | 100,000 is off the table. Drop to the 10,000 block (~£250) and a ~1,100-design opening range, or go to one variant per design and get 10,000 designs for the same money. |
| There is unpublished volume pricing | Take it, and re-cost §3. |
| There is a high-SKU / POD rate | Ask for it in writing and re-cost everything. |

## Do not buy before the answer

Numbers are assigned permanently — `gtin.py` writes them to a committed map
precisely so none is ever reassigned — so buying the wrong size block and
then migrating is the one expensive mistake available here. A phone call
first costs nothing.

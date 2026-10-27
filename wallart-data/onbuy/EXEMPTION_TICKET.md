# Barcode exemption ticket — to submit via the OnBuy Seller Control Panel

Written 27 Oct 2026. Paste the block below into a support ticket.

## Before you send it — read this bit

**It does not claim you hold a registered trademark, because you do not.**
OnBuy's published line is that they grant barcode exemptions to sellers who
own a UK or EU trademark for their brand. This repo has no record of
NORYMUS LIMITED holding one for Walryvo.

A ticket that claims a trademark you cannot produce gets found out the
moment they ask for the registration number, and it puts the whole account
under suspicion on day one. So the ticket says plainly what you do have —
a registered company, a VAT registration, the brand live on your own domain
— and asks them directly whether a pending application would satisfy them.
That question is the point of the ticket as much as the request is.

If you **do** hold a trademark or have already applied, tell me the number
and I will rewrite it around that, which makes it much stronger.

**Your eBay store trades as "artnoire", not Walryvo.** The link resolves to
`ebay.co.uk/str/artnoire`. That is not a problem, but it would look like
one if the ticket implied the eBay store were branded Walryvo and they
clicked through to a different name. So the ticket offers the store as
evidence of **the products and the trading history**, and keeps Walryvo as
what it is: the brand for your own website and for OnBuy. Say the word if
the two are meant to be the same name and I will rewrite it.

I used the plain `https://www.ebay.co.uk/str/artnoire` rather than the
`ebay.io` short link you sent. Same destination — I followed it — but a
shortener with tracking parameters in a formal ticket reads like marketing,
and some support tools strip or distrust them.

**It discloses that the artwork is AI-generated, and that is deliberate.**
You asked for it and it is the right call: your own website already says
"digitally created" on every product page, so saying something different to
OnBuy would be the one inconsistency worth avoiding. It also *helps* the
argument — no manufacturer means no manufacturer's barcode. I added one
sentence you did not ask for, naming the model and its licence, because
"made with AI" invites exactly one follow-up question — *do you have the
right to sell these?* — and it is better answered before it is asked.

Two other things:

- It asks for **two** things: the exemption, and live product creation
  being switched on. They are the same underlying request — let us create
  products at volume — and OnBuy requires a ticket for the second anyway.
  If you would rather keep it to one ask, delete the section marked
  **Request 2** and send it separately.
- The numbers in it are real and checked: 10,000 designs, nine variants
  each, 90,000 variant barcodes for the first batch alone. Do not round
  them up to sound bigger.

---

## Which ticket category to file it under

**"Product Creation Support (Feeds)"**, and it is a judgement call rather
than an obvious one. The full dropdown, seen 27 Oct, has two plausible
homes for this ticket:

- **Product Creation Support (Feeds)** - the first option.
- **Brand Ownership** - further down, and arguably more precise, since
  OnBuy grants the barcode exemption on the strength of owning the brand.

Product Creation Support wins on two grounds. The ticket's actual question
is "we cannot create products at volume because of the EAN requirement,
what is the route for made-to-order goods" - that is a product-creation
problem that happens to be solved by a brand exemption, not a brand dispute.
And we do NOT hold a trademark: a Brand Ownership queue is likely staffed
to check registration numbers, so filing there leads with our weakest card
and invites a one-line "no trademark, denied" instead of the conversation
the three questions are trying to start. It also covers Request 2, which
Brand Ownership would not.

The ticket now says explicitly that we are happy to be re-routed, so a
wrong guess costs a hop rather than a rejection. If it does come back
declined on the trademark point alone, re-file under **Brand Ownership**
with whatever they asked for.

NOT "Protected Brand Approval or Listing Permissions" - that is for being
allowed to list someone ELSE's gated brand. NOT "Channel Integration API
Queries" - debugging a connection you already have, not being granted
permission to create products.

Worth noting for whoever reads this later: the product-creation option is
named "(Feeds)" and comes FIRST, and the Integrations screen offers feed
imports. OnBuy's mainstream product-creation path is a feed now, not the
spreadsheet - which is why build_onbuy_feed.py exists and why the ticket's
closing paragraph offers the Google Shopping XML.

**GPSR is in that dropdown twice** (GPSR Imports, GPSR Queries), so OnBuy
takes the General Product Safety Regulation seriously. It is probably not
ours: GPSR bites on goods placed on the EU or NORTHERN IRELAND market, and
web/business.config.json sets ships_to to GB, which excludes NI. If OnBuy
sells to NI buyers, or if the shop ever ships to the EU, this needs
checking properly rather than assuming - it carries a named responsible
person and labelling duties.

The full dropdown: Product Creation Support (Feeds), Product Data Change
Requests, One-Time Stock & Price Updates, Product Listing Queries, Order
Queries or Issues, Channel Integration API Queries, Refund fail, VAT
Queries or Issues, Subscription or Invoice Queries, Bank Detail Approval
Queries, Regional Delivery Pricing Request (UK only), GPSR Imports, GPSR
Queries, Bug Report, Brand Ownership, Performance Restrictions
(Suspensions and Withdrawal Holds), Account Verification, Request to
Reactivate Your Account, Business Details Change Requests, Protected Brand
Approval or Listing Permissions.

---

## The ticket

**Subject:** Barcode (EAN) exemption request — brand Walryvo — made-to-order
art prints

Hello,

We are a UK seller preparing to list made-to-order framed art prints and
would like to request a barcode exemption for our own brand, together with
approval to create products at volume.

**Our business**

- Legal entity: NORYMUS LIMITED, company number 17020866, England and Wales
- Registered office: 28 Bedford Square, Leigh, WN7 2AA
- VAT registered: GB513541030
- Brand: Walryvo — our own brand, used on our own website at walryvo.com
- Contact: sales@walryvo.com, 07397 937226
- Intended category: Artwork Prints (9376)
- We already sell these products on eBay UK:
  https://www.ebay.co.uk/str/artnoire

**Why we are asking**

Every item is **printed and framed to order**. Nothing is bought in and
there is no manufacturer: we create the artwork ourselves, print it
ourselves and sell it only under our own brand. These are not manufactured
stock units, and no manufacturer-assigned barcode exists for any of them
because no manufacturer exists.

The designs are **generated by us using AI image generation**, which we
mention because it is relevant to the identifier question rather than
despite it — each design is original to us and exists nowhere else, so
there is nothing to match against an existing catalogue entry. We use
FLUX.1 schnell, which is released under the Apache 2.0 licence and is
licensed for commercial use, so the output is ours to sell. Our listings
state plainly that the work is digitally created, is not a hand-painted
original and is not signed.

**We already sell this exact range on eBay UK**, at
https://www.ebay.co.uk/str/artnoire. eBay does not require a product
identifier for this category and our listings there carry none, which is
the normal position for made-to-order artwork. The products we want to
bring to OnBuy are the same ones, with the same photographs.

The volume is the practical problem. Our opening range on OnBuy is 10,000
designs, out of a catalogue considerably larger than that already live on
eBay. Each is offered in three frame colours and three sizes, which your Product
Create Template requires as nine separate variant rows, each with its own
EAN — **90,000 barcodes for the first upload alone**. Licensing GTINs at
that scale is not a realistic proposition for made-to-order artwork, and we
are not willing to submit invented or reused numbers.

**On the trademark condition**

We understand exemptions are normally granted to sellers holding a
registered UK or EU trademark for their brand. **We do not currently hold a
registered trademark for Walryvo.** We would rather tell you that up front
than have it come up later.

What we can evidence is that this is a real trading business selling its
own original products: a UK registered company with a VAT registration, a
live shop at walryvo.com publishing its company details, VAT number and
consumer policies, and an established eBay UK store selling this same range
at https://www.ebay.co.uk/str/artnoire. Walryvo is the brand we sell under
on our own website and the one we would list under on OnBuy.

Could you tell us:

1. whether a **pending** UK trademark application would satisfy the
   condition, or whether registration must be complete — we are willing to
   file, and it would help to know before we do;
2. whether any other route exists for **print-on-demand or made-to-order**
   goods, where a per-variant GTIN is not meaningful;
3. if an exemption is granted, whether it covers **all variants** of a
   product, since it is the variant rows rather than the parent that
   require the EAN.

**Request 2 — approval to create products in bulk**

Separately, we understand new accounts need live product creation enabled
before products can be created through the API or a feed. Please could you
enable that for our account, or tell us what you need from us first.

We are happy to start with a small test batch of 5–10 products so you can
check the data quality before we send the full range, and we would prefer
to do it that way.

Our product data is already prepared against your Product Create Template,
with the category taken from your Categories tab, and we also have it
available as a Google Shopping XML feed if a scheduled feed import would
suit you better.

If this sits with another team - the brand or catalogue team, for
instance - please pass it on and let us know; we would rather it reached
the right people than be answered quickly.

Thank you,

[your name]
NORYMUS LIMITED / Walryvo

---

## If they say no to the exemption

The fallback order, cheapest first:

1. **File the UK trademark anyway** — £170 for one class at the IPO, about
   four months to registration, application number immediate. Only worth it
   if they confirm a pending application counts, which is question 1.
2. **Ask what the smallest viable GTIN licence is.** GS1 UK sells in
   blocks; if a smaller block plus a narrower opening range (say 500
   designs, framed in one colour and one size, so 500 barcodes rather than
   90,000) gets the account trading, the range can grow once performance
   earns it.
3. **Reduce the variant count.** Nine variants per design is what makes the
   barcode count explode. One size and one frame colour per design turns
   90,000 into 10,000, and a tenth of that for a 1,000-design opening
   range. Worse for buyers, but it is the lever with the most leverage.
4. **Accept that OnBuy is not viable for this catalogue** and put the
   effort into walryvo.com and Merchant Center instead, where the GTIN
   question has already been answered: `web/catalogue/feed.py` omits it
   entirely and Google accepts brand plus MPN for goods with no barcode.

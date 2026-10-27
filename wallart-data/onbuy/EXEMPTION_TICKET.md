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

**Why we are asking**

Every item is **printed and framed to order**. Nothing is bought in, and
there is no manufacturer: we are the producer, and the products are sold
only under our own Walryvo brand. They are not manufactured stock units and
no manufacturer-assigned barcode exists for any of them.

The volume is the practical problem. Our opening range is 10,000 designs.
Each is offered in three frame colours and three sizes, which your Product
Create Template requires as nine separate variant rows, each with its own
EAN — **90,000 barcodes for the first upload alone**, and our wider
catalogue is considerably larger. Licensing GTINs at that scale is not a
realistic proposition for made-to-order artwork, and we are not willing to
submit invented or reused numbers.

**On the trademark condition**

We understand exemptions are normally granted to sellers holding a
registered UK or EU trademark for their brand. **We do not currently hold a
registered trademark for Walryvo.** We would rather tell you that up front
than have it come up later.

What we can evidence is that Walryvo is genuinely our own brand and in
active use: it is a UK registered company with a VAT registration, trading
on its own domain at walryvo.com, with its company details, VAT number and
consumer policies published there.

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

# What is waiting on the seller

Updated 26 Oct 2026. Everything here needs a login, a payment, a judgement
call or a document that Claude does not and should not have. Nothing on
this list is blocked on code.

Ordered by what unblocks the most.

---

## A. walryvo.com is LIVE — done 26 Oct

Nothing in this section is outstanding. Kept as a record of what was done
and by whom, because several of these were the seller's logins and will be
again if anything needs redoing.

| | |
|---|---|
| Nameservers moved to Cloudflare | seller, 17:05 |
| Zone active, all 12 records intact, mail verified | 17:20 |
| Deployed from the seller's Mac | seller, 18:06 |
| walryvo.com + www attached to the Worker | over the API, 18:26 |
| `STRIPE_SECRET_KEY` set, checkout proven live | 18:26 |
| `STRIPE_WEBHOOK_SECRET` set, endpoint enabled | 18:36 |
| Bright black-and-white theme deployed | 18:31 |

Checkout was tested end to end rather than assumed: a real Stripe Checkout
session (`cs_live_...`) was created from a real variant id, HTTP 200. The
key is a RESTRICTED key (`rk_live_`), which is the safer choice and does
carry the scope.

**Three bugs only a real deploy could have found**, all fixed:

1. `site/src/data/*.json` were gitignored, so a fresh checkout would not
   build at all.
2. `cart.astro` used Astro's `define:vars`, the one critical CVE of the
   eleven npm reports that was actually in the shipped site. Replaced with
   data attributes; the other ten are build tooling and do not ship.
3. `wrangler.toml` points `[assets]` at `./dist`, and the adapter does not
   emit a `.assetsignore`, so the compiled server — including the Stripe
   route — would have been published as downloadable files. The build now
   writes that file itself.

And one found by looking at the live site rather than the deploy output:
the first theme deploy rendered walryvo.com as **unstyled HTML**, because
the edge cache held the previous build's page, which names a hashed
stylesheet the deploy had just deleted. The cache key now carries a build
id, so it cannot recur.

## Changing the shop's colours

One word. `web/business.config.json`, the `"theme"` field:

| Name | What it is |
|---|---|
| `ink-black` | black page, white type — **current** |
| `paper-white` | white page, black type |
| `gallery-cream` | the exact cream the mockups are photographed on, so prints have no visible edge |
| `plaster-pink` | warm gallery pink, claret accent |

Change it, then `python3 web/catalogue/build_db.py` and deploy. Nothing else
needs touching: `themes.json` holds the palettes, build_db.py writes
`theme.css`, and every rule in the stylesheet takes its colour from those
tokens. There is no hex value anywhere else.

To add a shade, copy a block in `web/themes.json` and give it a name. Every
preset must define every token — there is no fallback, and a missing one is
an invisible colour rather than an error.

The one token that is not a taste decision is `plate-wall`, the background
behind the big images. Every mockup is a framed print on flat cream,
rgb(237,234,227), baked into the photograph. On a light theme set it to that
exact value and the picture has no edge; on a dark one set it near the page
colour and the print reads as a lit panel on a dark wall.

## B. Quick, and worth doing before Merchant Center sees you

- **Change the SIC code.** Companies House has NORYMUS LIMITED as 96090
  "other service activities", which does not describe selling art prints.
  **47910** (retail via mail order or internet) is the right one. Changed
  on a confirmation statement, which can be filed early for a small fee.
- **Check the VAT name.** Confirm GB513541030 is registered to NORYMUS
  LIMITED at <https://www.gov.uk/check-uk-vat-number>. Google compares the
  VAT record against the site. Thirty seconds.
- **Statement descriptor — seller says it is already set to `WALRYVO`**
  ("i think"), so this is a confirmation rather than a task. Settings →
  Business → Public details. Confirmed 26 Oct that the checkout code sets no
  descriptor, so Checkout falls back to the account default — likely
  NORYMUS. A buyer who sees an unrecognised name on their card statement
  three days later disputes the charge with their bank rather than emailing
  you, and Google's misrepresentation policy expects the shop, the payment
  and the business to line up. Check the public business name and support
  email on the same page read Walryvo and sales@walryvo.com.
- **Finish Stripe account verification.** The dashboard was still prompting.
  Nothing technical is blocked, but payouts are, and Merchant Center wants
  the same documents.
- **Approve the opening 240 designs by eye.** About 4% have clear defects —
  see `web/README.md`. `python3 web/catalogue/sheet.py` builds numbered
  contact sheets, `--drop 22,43,...` removes what is rejected. A morning's
  work and it cannot be automated: the detector does not discriminate.

---

## C. Decisions asked for and never answered

These have been open a while. None is urgent; all of them block something.

1. **Which R2 bucket goes to which eBay account?** Not recorded anywhere.
   Needed before anything else is matched up across the four stores.
2. **The people sweep** (`render/people_sweep.py`, about $1-2 of GPU). 17%
   of panels carry a small distant human figure — roughly 160,000 designs
   and 640,000 listings — which breaks the no-human-figures rule. Not
   portraits; the for-scale kind.
3. **Which end-listing file to use**: `ebay_end/EBAY_END_ALL.csv` (239,449,
   art and tees), `EBAY_END_ART_ONLY.csv` (127,493) or
   `EBAY_END_TEES_ONLY.csv` (111,956).
4. **The t-shirts.** `tshirt/EBAY_ONE_FILE.zip`, 105,573 listings, finished
   since 7 Oct and never uploaded. There is an unsettled shipping-policy
   conflict — the file says profile 2, CLAUDE.md says 1 — that
   `tshirt/EBAY_TEST_3.csv` settles in a single upload.

---

## D. Open from the 26 Oct repricing

- **Did the three files upload cleanly?** 502,443 listings repriced.
- **Was that export the lunar-kms account?** Flat prices were applied as
  instructed. lunar-kms is supposed to run +£10 framed / +£5 unframed. If
  it was lunar, it needs regenerating.
- **A1 SPECIAL SIZE** — 4 rows on one listing, left at £54.99 framed /
  £41.90 unframed because the price list does not cover A1. Give a price
  and it gets set.

---

## Not on this list, because it is done

The website, all 240 products and 12 categories, the logo and banner, every
policy page, the Merchant Center feed (2,160 items, 0 spec problems), the
preflight gate at 19 of 20, the eBay repricing files, and the D1 database
created and seeded. See `CLAUDE.md` for the map.

#!/usr/bin/env python3
"""The Google Merchant Center promotions feed for buy-two-get-one-free.

WHY A SEPARATE FEED. A promotion is not a product attribute. Google reads it
from its own feed, matches it to products by promotion_id, and shows it as a
badge on the listing. Putting a discount in the product feed's price instead
would mean advertising a price the shop does not charge for a single print,
which is the mismatch everything else here is built to prevent.

WHAT THIS IS NOT. It is not a sale price and there is no strikethrough. A
strikethrough needs a base price the shop actually charged for a qualifying
stretch of recent history - Google checks, and a price that was never
charged produces no badge and a false [price]. Every print here is sold at
its normal price; the offer is a genuine free third item.

    python3 promotions.py          # writes promotions.xml next to feed.xml

NOTHING IS SUBMITTED BY THIS SCRIPT. It writes a file.
"""
import datetime as dt, html, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "promotions.xml")

# generic_redemption_code is omitted on purpose: the discount applies
# automatically in the basket and there is no code to type. Offering a code
# that does nothing is a promotion a shopper "can't actually get".
PROMO = {
    "promotion_id": "WALRYVO-3FOR2",
    "product_applicability": "all_products",
    "offer_type": "no_code",
    "long_title": "Buy 2, get 1 free on all prints",
    "promotion_effective_dates": None,   # filled below
    "redemption_channel": "online",
}


def main(days=90):
    cfg = json.load(open(os.path.join(os.path.dirname(HERE),
                                      "business.config.json")))
    start = dt.datetime.now(dt.timezone.utc).replace(microsecond=0)
    end = start + dt.timedelta(days=days)
    # Google wants an explicit window. An open-ended promotion is not
    # something it will show, and a promotion that outlives the seller's
    # intention to honour it is worse than no promotion.
    dates = f"{start.isoformat()}/{end.isoformat()}"

    e = html.escape
    rows = [
        '<?xml version="1.0" encoding="utf-8"?>',
        '<rss version="2.0" xmlns:g="http://base.google.com/ns/1.0">',
        "<channel>",
        f"<title>{e(cfg['brand'])} promotions</title>",
        f"<link>https://{e(cfg['domain'])}/</link>",
        f"<description>Promotions for {e(cfg['brand'])}</description>",
        "<item>",
        f"<g:promotion_id>{e(PROMO['promotion_id'])}</g:promotion_id>",
        f"<g:product_applicability>{PROMO['product_applicability']}</g:product_applicability>",
        f"<g:offer_type>{PROMO['offer_type']}</g:offer_type>",
        f"<g:long_title>{e(PROMO['long_title'])}</g:long_title>",
        f"<g:promotion_effective_dates>{dates}</g:promotion_effective_dates>",
        f"<g:redemption_channel>{PROMO['redemption_channel']}</g:redemption_channel>",
        "</item>",
        "</channel>",
        "</rss>",
    ]
    open(OUT, "w").write("\n".join(rows) + "\n")
    print(f"wrote {OUT}")
    print(f"  {PROMO['long_title']}")
    print(f"  live {start.date()} to {end.date()} ({days} days)")
    print()
    print("NOT SUBMITTED. To use it: Merchant Center -> Marketing ->")
    print("Promotions, add this as a promotions feed, and make sure the")
    print("Promotions programme is enabled for the United Kingdom.")
    print("The offer must be stated on the site while the feed is live -")
    print("it is, on every page and at /delivery#offer.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

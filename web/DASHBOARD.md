# The back office — walryvo.com/admin

Built 31 Oct 2026, because the question "have we had any visitors or orders
yet?" had no answer anywhere.

Live visitors, today's and the fortnight's traffic, where it came from,
which pages, orders, revenue, conversion, and which search engines are
crawling the shop. All of it out of our own database — no Google Analytics,
no third-party script, no tracking cookie, no data leaving the Worker.

---

## Why it had to be built rather than switched on

Three places could have answered it and none of them would:

| | |
|---|---|
| **Cloudflare analytics** | Needs `zone.analytics.read`. The API token in this environment does not carry it, and the dashboard's numbers cannot be read from a Worker anyway. |
| **Merchant Center** | Publishes no read API for engagement. You can look at it in a browser; nothing else can. |
| **The site itself** | Recorded nothing at all. The shop could have had a week of traffic and left no trace. |

So the shop now counts its own.

---

## Three commands, once

From `web/site`, with the repo pulled:

```bash
# 1. Create the three analytics tables in the live database.
npx wrangler d1 execute wallart --remote --file=../catalogue/migrate_analytics.sql

# 2. Set a password for the dashboard. Make it long; it is the only lock.
npx wrangler secret put ADMIN_KEY

# 3. Deploy.
npm run deploy
```

Then open **<https://walryvo.com/admin>** and enter the key.

The key is remembered for 30 days in an HttpOnly cookie, so a phone only
asks once. `https://walryvo.com/admin?key=YOURKEY` also works for a home-
screen shortcut — it swaps the key for the cookie and cleans the URL, so
the key is not left sitting in the address bar.

**Without `ADMIN_KEY` the page refuses to open at all.** There is no
default and no "if unset, allow": the failure mode of that would be
publishing the order history and every visitor's movements to anyone who
guesses a URL.

---

## What each number means

| | |
|---|---|
| **Live** | Distinct visitors in the last five minutes. |
| **Visitors / page views** | A visitor is one person for one day. Views are pages loaded. |
| **Google Shopping** | **The number that answers "is the Merchant Center feed working".** A click from a Google free listing arrives carrying `srsltid` in the URL — that is Google Shopping's own click marker and nothing else sets it. A number above zero here is proof the feed earned a visit, without needing anyone's dashboard but ours. |
| **Checkouts / conversion** | Baskets that reached Stripe, and orders divided by those. This is how you tell "nobody is visiting" apart from "they visit and do not buy" — two problems with completely different fixes. |
| **Crawlers** | Counted per day and batched, so a **lower bound**, not a total. Googlebot-Image fetching photographs is the signal the feed is being processed; it is exactly what the 192 "image not processed" rejections were about. |

---

## Privacy, because the policy had to change

This page used to be able to say "no analytics". It cannot any more, so
`/privacy` was rewritten in the same commit. A policy describing a shop
that no longer exists is the same misrepresentation as a price that does
not match the feed, and it is the kind nobody catches because nobody
rereads their own policy.

What is actually stored, per page view: the path, the time, the referring
site, the country.

What is **not** stored: the IP address. It is hashed together with the user
agent and a salt that changes at midnight UTC, truncated to 16 hex
characters. That tells two people apart today and is useless for telling
who anyone is, or for joining yesterday to today. Rows are deleted after 90
days. No cookie is set, so no consent banner is needed — and the admin
cookie is only ever set for whoever logs in to this page.

---

## How it is built, and the two decisions worth knowing

**Counting happens in `middleware.ts`, above the edge cache.** A page served
from the cache never reaches the route that rendered it, so anything
counted lower down would miss every repeat visitor and every crawl of a
popular page — under-reporting exactly the traffic we are hoping for, in
the one direction nobody would notice.

**Humans get a row each; crawlers get a counter.** One row per human page
view is a handful of writes a day and the detail is worth it. Googlebot
fetching 2,508 products and their photographs is tens of thousands of
requests, and a row apiece would spend the whole D1 write allowance
recording a robot. Crawl counts are also batched inside the isolate and
flushed every 15 seconds or 200 requests, whichever comes first — hence
"lower bound".

Files: `src/lib/analytics.ts` (recording), `src/lib/admin.ts` (auth and
queries), `src/pages/api/admin.ts` (JSON), `src/pages/admin/index.astro`
(the page). The analytics tables are **not** in `seed.sql`'s delete list,
so rebuilding the catalogue never erases the traffic history — the
catalogue can be regenerated and the history cannot.

`preflight.py --live` checks from outside, with no credentials, that an
anonymous request to `/admin` gets nothing, that the page is `noindex`,
that robots.txt disallows it, and that `/api/admin` refuses. That is the
one page on this site where being wrong is a data breach rather than a
disapproval.

# Scaling the shop

Written 26 Oct 2026, after the seller said the intention is eventually to
list "5 million or more" of the generated designs and to run Shopping ads
against them.

The short version: **the hosting is not the constraint, and will not be.
Google's account quota is.** The work below is in that order.

---

## 1. Google's limits, which decide everything else

Checked against Google's own documentation, 26 Oct 2026.

| Limit | Value | Can it be raised? |
|---|---|---|
| **Products per standalone account** | **150,000** | Only by Google, automatically, when the account nears the limit **and meets quality and performance requirements** |
| Items per feed file, per country/language | 5,000,000 | **No. Hard limit.** |
| Feed file size | 4 GB | No |
| Data sources per account | 200 | — |
| Uploads per day, primary source | 100 | — |
| Size of a single item | 200 KB | No |

Read the first row twice. A new standalone Merchant Center account is
capped at **150,000 products**, not millions. The cap lifts on its own, but
only for accounts that are close to it *and* are performing well and
cleanly. There is no form, no payment and no setting that raises it.

So the 5M plan is not blocked by storage or bandwidth. It is gated behind
roughly 150,000 well-behaved listings and a track record. Everything in
this repository that looks like caution - the 240-product launch, the
staged ladder in `catalogue/select.py scale_plan()`, the 20 preflight
checks - is the mechanism for earning that, and it is the only mechanism
there is.

The second row matters later: 5M items per feed file is a hard ceiling, and
the catalogue reaches it as *items*, not products, because each product is
nine feed rows. 150,000 products is already 1.35M rows. **The feed must be
split by country/language and by section well before the product count
looks alarming.**

## 2. Our own limits, and where they actually bite

Measured from the real database, not estimated: 1,220,608 bytes for 240
products and 2,160 variants, indexes included. That is ~5,086 bytes per
product.

| Catalogue | D1 size | Status |
|---|---|---|
| 240 (now) | 1.2 MB | free tier, nothing to do |
| 150,000 (Google's default cap) | ~760 MB | comfortable |
| 1,500,000 | ~7.6 GB | approaching the per-database ceiling |
| 5,000,000 | ~25 GB | **over it - needs sharding** |

**D1's hard limit is 10 GB per database and cannot be raised.** An account
may hold 50,000 databases, so the fix is routine rather than a rewrite:
shard by section (`landscapes`, `animals`, `botanical`, `night-sky`, ...),
bind each as its own D1, and route on the section already present in every
URL - `/c/<section>/<niche>` and, via the product's `section` column,
`/art/<slug>`. The queries do not change; only `getDb()` does.

Do not do this early. A sharded catalogue cannot be queried across shards
in one statement, so anything global - the sitemap, the feed build, "newest
across the whole shop" - has to fan out and merge. That is real complexity
bought for nothing until there are several million products.

**The sitemap needs splitting first, and much sooner.** `sitemap.xml.ts`
calls `allSlugs()`, which is `SELECT slug FROM products` with no limit.
The sitemap standard caps a file at 50,000 URLs, and D1 caps a response
long before a million rows come back. At somewhere around 40,000 products
this breaks, and it breaks silently - a truncated sitemap just means pages
are never indexed. It needs a sitemap index pointing at paged children.
**This is the first thing to fix when the catalogue grows past a few
thousand.**

## 3. What was done on 26 Oct

Both were measured problems at scale, invisible at 240 products.

**Precomputed facet counts.** The navigation shows a count beside every
niche, section, style and colour. That was
`SELECT niche, COUNT(*) FROM products GROUP BY niche`, computed live, which
reads every row in the table on every page view. At 240 products it is
nothing; at a million it is a full scan per request, and D1 bills rows
read, so it would have been simultaneously the slowest query on the site
and the largest line on the bill - for a number that changes only when the
catalogue is rebuilt. It is now a `facet_counts` table written by
`build_db.py`: 38 rows today, and it does not grow with the catalogue,
because a million products still have 53 niches. Verified equal to the live
counts for all five facet kinds before the old query was removed.

**Edge caching of HTML.** Every page renders from D1 on demand. Without a
cache that is a database round trip per view. There is now
`site/src/middleware.ts`, which stores responses in the Workers Cache API -
setting a `Cache-Control` header alone does nothing here, because a Worker
*is* the origin and its response goes straight past Cloudflare's cache.
That trap is worth knowing: the site would have looked cached, the database
would still have been read every time, and the only evidence would have
been the bill.

The TTLs are deliberately short, and `src/lib/cache.ts` explains why. A
cached page showing yesterday's price while the feed carries today's is a
price mismatch, and repeated price mismatches is how a feed earns a
misrepresentation finding rather than a simple disapproval. So:
`max-age=0` for the visitor's own browser, which cannot be purged;
`s-maxage=300` for the shared edge, which can. Policy pages hold an hour.
Cart, checkout, the order page and everything under `/api` are never
cached at all, and the checkout response says `no-store` on its own account
as well - it carries a Stripe session bound to one basket.

**After any price change or reseed, purge:** Cloudflare dashboard →
walryvo.com → Caching → Configuration → Purge Everything.

Verified locally before committing: A4 £24.99, A3 £29.99, A2 £34.99 still
render per variant with `s-maxage=300`; a missing product still returns a
real 404 and is not stored; `/cart` returns `no-store`; preflight unchanged
at 19 of 20, the one failure being the Stripe receipt setting.

## 4. What is NOT worth doing yet

- **Sharding D1.** Not until well past a million products, and Google will
  not have let the catalogue get there first.
- **Read replication.** The market is the UK and the database is near it.
- **An image CDN or resizing service.** R2 egress is free and the images
  are already served immutable through the Worker, cached at the edge.
- **Replacing D1.** It is not the binding constraint and will not be.

## 5. Order of work, when growth actually comes

1. Split the sitemap into an index plus paged children. **Before ~40,000
   products.**
2. Split the feed by section, and by country/language if a second market
   opens. Before 5M *items*, which is ~550,000 products.
3. Page the category listings properly - `byNiche` already takes an offset.
4. Only then consider sharding D1 by section.

Sources: Google Merchant Center quotas and product data specification,
Cloudflare D1 limits and R2/Workers pricing, all read 26 Oct 2026.

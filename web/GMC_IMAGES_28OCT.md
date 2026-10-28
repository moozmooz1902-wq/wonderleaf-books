# "Image not processed" on 192 items — what it was

28 Oct 2026. First Merchant Center sync of walryvo.com: **2,508 products
ingested, 2,316 under review, 192 not approved**, every one of the 192 with
the reason **"Image not processed"**.

## It was not the feed

Checked first, because a malformed feed is the usual answer and it is cheap
to rule out:

    items                      2508   (209 designs x 12 variants)
    titles over 150 chars         0
    descriptions under 20 chars   0
    items with no image           0
    distinct item_group_id      209

Then the images themselves. 120 distinct image URLs, fetched at concurrency
40 with a `Googlebot-Image/1.0` user agent: **120 x HTTP 200**, no rate
limiting, no Cloudflare challenge, correct `content-type: image/jpeg`,
1600x1600 and 1000x1000 — both well over Google's 500x500 minimum. robots.txt
allows the crawler. So the simple explanations were all wrong.

## It was HEAD

`/img/<bucket>/<key>` answered **GET with 200 and HEAD with 500**.

    HEAD  GET   path
    200   200   /
    200   200   /art/st-abbs-charcoal-drawings-00203054
    200   200   /unframed/WA-00093d2a90f2a8fa.jpg
    500   200   /img/luxvia-art/luxvia/gen/listing/WA-0beeb38bcbf5c20a-0-black.jpg

`src/pages/img/[...path].ts` exported `GET` and nothing else, so Astro
answered HEAD with a server error. Crawlers check an image with HEAD before
or instead of downloading it, so the route looked broken to Google and
perfectly healthy to anyone testing it with a browser or with curl's default
GET — which is every test we had.

It also explains the shape of the failure. The static `/unframed/` assets,
served by Workers Assets rather than by that route, answered HEAD correctly
all along; only the R2-served framed photographs were affected.

## The fix

1. `HEAD` is now exported from that route — same status, same headers, no
   body.
2. The Cache API key is now built as an explicit GET request. `cache.put`
   only accepts GET keys, so handing it the HEAD request would have thrown,
   and a throw there is another 500 on an image a crawler is checking.
3. `preflight.py` gained a live check — **"images answer HEAD, not just
   GET"** — over the same 24 sampled images the existing GET check uses. A
   check that only ever sends GET cannot see this class of fault, which is
   the point of adding it.

Verified locally: HEAD now returns `200 image/jpeg`.

## What still has to happen

**The fix is committed, not deployed.** `wrangler deploy` is refused by this
environment's permission classifier, so the deploy is the seller's —
`SETUP_WALKTHROUGH.md` Part 4.

After deploying:

    python3 catalogue/preflight.py --live        # expect the new HEAD check to pass

Then leave Google alone. Google re-crawls images that failed processing for
several days by itself; the documented way to force an earlier refetch is to
change the image URL, which we do not want to do — a product's image URL is
part of its identity and churning it costs the item its history. If the 192
have not cleared a few days after the deploy, that is the point to look
again, and the next thing to check is whether the same 16 designs are
involved or a different set.

## Honest caveat

The HEAD fault is real, it was found on the live site on the same day as the
disapprovals, and it fits the symptom. That is not the same as proof it was
the whole cause. Google does not say which request it made. If the count
drops to zero after the redeploy, this was it; if it does not, the evidence
above still rules out the feed, the image sizes, robots.txt and rate
limiting, which is most of the search space.

# The R2 buckets, as they actually are

Listed 11 Oct 2026 once the token was raised to Admin Read & Write. Object
counts stop at three pages (3,000), which is enough to tell an empty bucket
from a used one; sizes are for those pages only where it says `3,000+`.

## Poster / wall-art buckets - one per eBay account, all already in use

    nebula-m12k         3,000+   1,461 MB   created 2026-06-20
    lunar-kms           3,000+   1,463 MB   created 2026-06-20
    mercury-usm         3,000+   1,449 MB   created 2026-06-16
    posterleaf-store1   3,000+   1,451 MB   created 2026-06-12
    prism-rps           3,000+   1,429 MB   created 2026-06-20
    orbit-uss           3,000+   1,428 MB   created 2026-06-20
    velvet-ars          3,000+   1,415 MB   created 2026-06-20
    luxvia-art            658      885 MB   created 2026-06-18

`luxvia-art` is the odd one - 658 objects where every other store has
3,000+. Worth asking whether that store is deliberately smaller.

## T-shirt side

    tshirt-m12k         3,000+   4,148 MB   live
    tshirt-mockups      3,000+   4,641 MB
    wonderleaf-books    3,000+   3,071 MB
    tshirt-km / -mine / -roop / -us / -usm        all empty

## Why 207 guesses missed them

The seller named the accounts as "Lunar, KMS, Lux, Via Art, Mercury, USM,
Nebula, M12K" and the buckets turned out to be those names **in pairs, run
together**: `lunar-kms`, `luxvia-art`, `mercury-usm`, `nebula-m12k`. Every
guess treated them as separate words. Three more existed that were never
mentioned at all: `orbit-uss`, `prism-rps`, `velvet-ars`.

The lesson is cheap to state and was expensive to learn: guessing names is
not a substitute for listing them. One permission change answered in two
minutes what 207 probes could not.

## What the token can do now

    list buckets     yes
    create buckets   yes   (tested with a throwaway, then deleted)
    delete buckets   yes

So no bucket needs creating by hand. The eight poster buckets already
exist, so generated art goes into them under a prefix rather than into
anything new.

## Connection test, 11 Oct - the S3 side is fully working

`r2_conntest.py` on a pod: put -> get -> delete on `nebula-m12k` all
succeeded, and all eight poster buckets list. Nothing on the S3 side is
blocking.

## What is already in the poster buckets, and the key convention

Sampling four keys from each shows two conventions, and new work must
follow whichever the bucket already uses or the seller's crop tooling and
eBay builder stop matching:

    posterleaf-store1   store1/0000000_framed.jpg  _framed_oak  _framed_white  _raw
    mercury-usm         store2/...                 (same, three frame colours)
    nebula-m12k         store3/0000000_framed.jpg  _raw          (black only)
    velvet-ars          store4/...                 (black only)
    prism-rps           store5/...                 (black only)
    orbit-uss           store6/...                 (black only)
    lunar-kms           store7/...                 (black only)
    luxvia-art          luxvia/abstract/japandi-calm/1-mockup-black.jpg  -oak  -white

So the stores are numbered 1-7 plus Luxvia on its own nested scheme, and
only two of the eight currently carry all three frame colours.

## The existing store plan, from the other branch

`git show origin/claude/hopeful-rubin-u14pgu:wallart/plan.json`

    Luxvia Art    luxvia-art          LX   1,000,000   pic_base ""
    Mercury       mercury-usm         MC     500,000   pic_base ""
    Lunar         lunar-kms           LN     500,000   pic_base ""
    Posterleaf    posterleaf-store1   PL     500,000   pic_base ""
    TOTAL                                  2,500,000

Four stores, 2.5M rows, and **every `pic_base` is empty** - so the public
image URL was never resolved on that branch either. The seller now wants
5M across up to eight buckets, so this plan needs replacing, not extending.

## Still unknown, and not answerable from the S3 API

**The public URL of each bucket, custom domain or not.** Both are a
Cloudflare-API concept and invisible over S3. `wallart/r2_urls.py` on the
other branch already solves this, but it needs a **`CF_API_TOKEN`** -
a Cloudflare API token with Workers R2 Storage permission, separate from
the S3 keys - and the pod probe confirms no such variable is set today.
Until it exists there is no way to know what URL to put in an eBay
listing, or even whether public access is switched on for these buckets.

**Custom domains.** They are a Cloudflare-API concept and invisible here.
The poster listings are already live, so something serves those images
today; if it is a `pub-....r2.dev` host then all eight buckets carry the
`error 1015` rate-limit risk that corrupted 7,142 of 12,834 downloads
during the audit, and every one needs a custom domain before more listings
go up.

## Where the generated block currently sits

`tshirt-m12k/wallart/v1/` - 12,834 panels, 1,808 MB. That is the wrong
bucket; it was the only one writable when the run started. A copy within
R2 is server side and free. `tshirt-m12k/wallart/block1/` holds 476
orphans from before SKUs became content hashes and should be deleted.

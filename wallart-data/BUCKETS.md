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

## Still unknown, and not answerable from the S3 API

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

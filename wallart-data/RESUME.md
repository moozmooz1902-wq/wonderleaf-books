# How to pause and continue

The seller funds this in $100 blocks, so the run has to survive stopping
dead at any moment - including RunPod simply switching the pods off when the
balance hits zero - and pick up from exactly the same place.

## It already does. The bucket is the bookmark.

There is no separate progress file to lose. A panel that exists in R2 is
done; a panel that does not is not. On start, every pod lists the prefix and
drops the jobs it finds, then generates only the rest.

    python3 gen_gated.py --subjects subjects.json --r2-prefix wallart/v1 --resume ...

Two things make that safe, and the first one took a rewrite to get right.

**A SKU says what a design IS, not where it sat in a list.** The first
version numbered jobs by position after a seeded shuffle. That is
reproducible only while the subject list never changes - add one flower and
every SKU after it shifts, so a half-finished run would regenerate
everything it had already paid for. The SKU is now
`WA-<64-bit blake2b of kind|subject|technique|composition|palette>`.

Proven: adding two subjects to a 12,834-job list produced 288 new SKUs and
lost **zero** old ones.

**64 bits, not 32.** The first attempt used crc32 and collided on the very
first run of 12,834 jobs. 2^32 collides past about 65,000, and 937,500 jobs
would collide roughly a hundred thousand times, each one quietly throwing
away a design. There is a collision check in `expand()` that refuses to run
rather than lose work; that check is what caught it.

## Stopping on purpose

    for p in <pod ids>; do curl -X DELETE https://rest.runpod.io/v1/pods/$p; done

Deleting a pod loses nothing: every panel was uploaded as it was made and
the container disk holds nothing that matters. `--max-hours N` also makes a
pod stop itself, so a forgotten pod cannot run all night.

## Starting again after a top-up

Exactly the same command. The pods list the bucket, see what is there, and
carry on. Run `python3 status.py <panels in bucket>` first to see where
things stand and what the next $100 buys.

## What is NOT resumable yet

The CPU stage (`pipeline.py`) rebuilds its listings from whatever panels it
is given, so it is cheap to re-run and does not need resuming. The eBay
upload files are not written yet.

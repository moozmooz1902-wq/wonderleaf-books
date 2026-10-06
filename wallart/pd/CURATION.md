# Curating the public-domain line: where it got to

## What is decided and done

`KEEP_metadata.txt` — **18,000 artworks of the 153,178**, chosen without
touching a single image:

    153,178  curated by curate.py (licence, UK copyright, theme, demand, duplicates)
     55,360  large enough to print A3 at 300 dpi (3,508px) AND scoring 40+
     18,000  kept, with a quota of 818 per theme

The quota matters. Landscapes and city views are a third of the shortlist by
count and the least distinctive by eye; without a cap the survivors would be
mostly those, which is how a catalogue ends up looking like a job lot. Only
famous_masters (3,569) and japanese_woodblock (1,015) are over quota,
because those two have far more high-scoring work than the cap allows and
they are the two most commercial categories in the set.

That alone is an 88% cut and needs no network, no pod and no money.

## What is written but not run: the photometric pass

`quality.py` measures what the metadata cannot see - whether the scan
actually looks good. Contrast between the 5th and 95th luminance
percentiles, share of real blacks, saturation, and distance from neutral
towards the yellow of aged paper. A faded mezzotint passes every metadata
test and is still something nobody wants on a wall.

It is correct and it is cheap. It has not produced a result, and three
attempts is enough for one sitting. Each failed differently and each is
worth recording:

**Run 1 — too slow, and refused.** 4 requests a second against 32 workers,
and 12.6% HTTP 403. The 403s were museums refusing an unrecognised client;
a browser User-Agent is accepted.

**Run 2 — out of disk.** This is the one that matters. 42,305 of the
shortlist carry an IIIF base and were correctly asked for a 400px
rendition. The other 13,055 fell back to `image_url`, which is the archival
master: Cleveland serves `<id>_full.tif`, the Met serves `/original/`.
Downloading those filled a 60 GB volume, raised DecompressionBombWarnings
on 164-megapixel files, and died on `OSError: No space left on device`
after 25 minutes. It read as a hang for an hour and three quarters because
the log only uploaded when the job finished - which it never did.

**Run 3 — silent.** With per-host thumbnail URLs, an in-memory measure that
writes nothing to disk, and a heartbeat that pushes the log to R2 every 60
seconds, the pod ran 26 minutes without the heartbeat ever firing once. Not
diagnosed. The pod reported RUNNING throughout.

## To finish it

    python3 pd/quality.py --fetch --budget 2400 --workers 128 --keep 18000

Needs open outbound network, so it runs on a pod rather than in the Claude
environment, where the museum hosts are not on the allowlist. Expect about
40 minutes and under a pound. The sensible time to do it is when the four
wall-art buckets are connected, because then the output lands somewhere
that can be read directly instead of being posted to a bucket belonging to
another product line.

Until then `KEEP_metadata.txt` is the list to use. It is a defensible cut on
its own; the photometric pass would refine it, not replace it.

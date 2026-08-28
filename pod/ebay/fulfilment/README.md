# Fulfilment: one tool, every store

Paste the custom labels from your orders, get a print file and a shirt image
per order. Same as before — with three things fixed.

## What changed

**1. It no longer matters which bucket a design is in.**
The store list used to be written into both scripts:

```python
BUCKETS = ["https://pub-19fa....r2.dev", "https://pub-4b71....r2.dev"]
```

Adding a store meant editing code on every Mac, and any Mac that missed the
edit reported perfectly good orders as "not recognised". The list now lives in
`sources.json` in R2. Edit that one file and every machine picks it up on its
next order. All stores are searched in parallel, so seven costs about the same
as one, and the answer is cached so a repeat label resolves instantly.

**2. The custom label is used as-is.**
The old code took the first run of digits out of the label:

```python
did = re.search(r"(\d+)", sku).group(1)
```

Fine while every label looked like `GR-0012345`. The current catalogue uses
labels like `bd_16_Dad_0` — that code extracts `16` and fetches a completely
different design. It would have shipped the wrong shirt on the first order
from the new batch. Old numeric labels still work.

**3. The shirt image comes from the right bucket.**
Artwork was searched for across every bucket, but the mockup was always
fetched from the *first* one. Orders from any other store therefore got no
mockup and silently fell back to the artwork flattened on black. Both files
now come from wherever the design actually is.

Also: designs that are already finished 4500×5400 transparent print files —
everything in the current catalogue — are passed straight through instead of
being flattened onto black and re-cut from luminance, which was softening
type that is already crisp.

## Installing on a Mac

Four files in one folder:

```
print_tool.py     the window — double-click this
order.py          the command-line version
wl_lookup.py      shared: finds a label in any store   <- required
halftone.py       optional
```

`wl_lookup.py` is the new one. A machine without it gets a clear message
rather than a stack trace.

## Adding a store

Edit `sources.json`, then put it back:

```bash
rclone copyto sources.json r2:tshirt-mockups/sources.json
```

Every Mac re-reads it within six hours, or immediately on a machine that has
not run the tool that day. Nothing else to do.

```json
{ "name": "store-3", "bucket": "tshirt-s3",
  "base": "https://pub-XXXXXXXX.r2.dev" }
```

`base` is the bucket's **public** URL from Cloudflare → R2 → the bucket →
Settings → Public access. It must be public: the tools deliberately hold no
credentials, so a Mac being stolen or a script being emailed around leaks
nothing.

## Checking it

```bash
python3 order.py --stores          # which stores am I searching?
python3 wl_lookup.py bd_16_Dad_0   # where does this label live?
```

The second prints the store and the exact URL, which is the fastest way to
tell a missing design from a missing bucket.

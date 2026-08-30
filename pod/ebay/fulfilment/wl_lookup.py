"""
wl_lookup.py — find an order's design files, whatever store they live in.

Both order.py and print_tool.py import this, so the lookup is fixed in one
place instead of two.

WHY THIS EXISTS

Both tools had the bucket list written into the script:

    BUCKETS = ["https://pub-19fa....r2.dev", "https://pub-4b71....r2.dev"]

which means adding a store is a code edit on every Mac that runs the tool,
and a Mac that misses the edit silently reports good orders as "not
recognised". With seven stores that is not maintainable.

Now the list lives in ONE file in R2 - sources.json. Edit that once and
every machine picks it up on its next order. The old hardcoded list is kept
only as a last-resort fallback for a machine that is offline when it starts.

TWO BUGS THIS ALSO FIXES

1. The custom label was parsed with re.search(r"(\\d+)", label), which takes
   the first run of digits anywhere in the string. That worked while every
   label looked like GR-0012345. The current catalogue uses labels like
   bd_16_Dad_0, where it extracts "16" and fetches a completely different
   design. The label is now used verbatim first, and digit extraction only
   happens for labels that are genuinely of the old numeric form.

2. The artwork was found by searching every bucket, but the shirt mockup was
   always fetched from the FIRST bucket. So an order from store 2 got its
   artwork from store 2 and no mockup at all - the tool silently fell back to
   flattening the artwork on black. Both files now come from whichever bucket
   actually held the design.
"""

import json, os, re, ssl, sys, time, urllib.request
from concurrent.futures import ThreadPoolExecutor

# One JSON file, in a bucket that will not be deleted, listing every store.
# Adding store 8 = adding four lines to that file. No Mac needs touching.
SOURCES_URL = ("https://pub-19fad43c12d848caa97d6d53a8695d03.r2.dev"
               "/sources.json")

# Used only if sources.json cannot be fetched AND nothing is cached locally,
# i.e. a fresh machine with no internet. Keeps the tool working rather than
# failing outright, but it will not know about newer stores.
FALLBACK = [
    {"name": "tshirt-mockups",
     "base": "https://pub-19fad43c12d848caa97d6d53a8695d03.r2.dev"},
    {"name": "tshirt-m12k",
     "base": "https://pub-4b710c8610a84acc8fad1513f48132fd.r2.dev"},
]

# A plain text file next to this script, one bucket URL per line. Read BEFORE
# sources.json, so a Mac can be pointed at a new store immediately without
# anyone having to upload anything to R2 first. Lines starting with # are
# ignored, so each line can be labelled.
LOCAL_LIST = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          "buckets.txt")

EXTS = ("png", "jpg")
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/120.0 Safari/537.36")

HOME = os.path.expanduser("~/.wonderleaf")
SOURCES_CACHE = os.path.join(HOME, "sources.json")
LABEL_CACHE = os.path.join(HOME, "labels.json")
SOURCES_MAX_AGE = 6 * 3600      # re-fetch the store list twice a day


# --------------------------------------------------------------------------
# HTTPS
# --------------------------------------------------------------------------
# macOS ships Python without its certificate bundle wired up, so every HTTPS
# request fails with CERTIFICATE_VERIFY_FAILED until a separate installer is
# run. Try proper verification first and fall back only if it is unavailable.
#
# The unverified fallback is acceptable HERE and nowhere else: these are
# public images on a known Cloudflare URL. No credentials are sent and
# nothing in the response is secret.
def _contexts():
    out = []
    try:
        import certifi
        out.append(ssl.create_default_context(cafile=certifi.where()))
    except Exception:
        pass
    out.append(ssl.create_default_context())
    loose = ssl.create_default_context()
    loose.check_hostname = False
    loose.verify_mode = ssl.CERT_NONE
    out.append(loose)
    return out


CTXS = _contexts()


def _get(url, timeout=30, method="GET"):
    """Fetch a URL, returning the body, or None if it is not there."""
    req = urllib.request.Request(url, headers={"User-Agent": UA},
                                 method=method)
    for ctx in CTXS:
        try:
            with urllib.request.urlopen(req, timeout=timeout, context=ctx) as r:
                return r.read() if method == "GET" else b""
        except urllib.error.HTTPError:
            return None            # 404/403 - the file is not here
        except Exception as e:
            if "CERTIFICATE" in str(e).upper():
                continue           # try the next context
            return None
    return None


def _load_json(path):
    try:
        with open(path) as fh:
            return json.load(fh)
    except Exception:
        return None


def _save_json(path, data):
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as fh:
            json.dump(data, fh, indent=2)
    except Exception:
        pass                       # a cache that cannot be written is not fatal


# --------------------------------------------------------------------------
# where the designs live
# --------------------------------------------------------------------------
def _local_sources():
    """Buckets listed in buckets.txt beside this script."""
    out = []
    try:
        for line in open(LOCAL_LIST):
            url, _, note = line.partition("#")
            url = url.strip().rstrip("/")
            if url.startswith("http"):
                # The comment after the URL is the store's name, so the
                # "not found in any store" message names stores a person
                # recognises rather than a row of hex.
                out.append({"name": note.strip() or url.split("//")[-1][:18],
                            "base": url})
    except Exception:
        pass
    return out


def sources(refresh=False):
    """
    Every store's public bucket URL.

    Three places, in order: buckets.txt beside this script, then sources.json
    in R2, then the built-in fallback. Anything found locally is searched
    first and is never overwritten by the remote list, so a store can be added
    on one machine straight away.
    """
    local = _local_sources()
    cached = _load_json(SOURCES_CACHE)
    fresh_enough = (cached and not refresh and
                    time.time() - os.path.getmtime(SOURCES_CACHE)
                    < SOURCES_MAX_AGE)
    if fresh_enough:
        return _merge(local, cached)

    body = _get(SOURCES_URL, timeout=10)
    if body:
        try:
            data = json.loads(body)
            entries = data["sources"] if isinstance(data, dict) else data
            entries = [e for e in entries if e.get("base")]
            if entries:
                for e in entries:
                    e["base"] = e["base"].rstrip("/")
                _save_json(SOURCES_CACHE, entries)
                return _merge(local, entries)
        except Exception:
            pass

    return _merge(local, cached or FALLBACK)


def _merge(*lists):
    """Concatenate, keeping order and dropping repeats of the same base."""
    seen, out = set(), []
    for lst in lists:
        for e in lst or []:
            b = e["base"].rstrip("/")
            if b not in seen:
                seen.add(b)
                out.append({**e, "base": b})
    return out


def run_folder(root=None, prefix="Orders"):
    """
    A fresh, dated folder for this batch.

    Both tools used to write into one fixed directory - the GUI into
    ~/Desktop/Print Files - so every batch landed on top of the last one and
    the numbered folders from different orders got mixed together. The name
    carries the date and time to the second, so two runs can never collide
    and the newest batch is obvious in a sorted list.
    """
    import datetime
    root = root or os.path.join(os.path.expanduser("~"), "Downloads",
                                "Wonderleaf Print Files")
    stamp = datetime.datetime.now().strftime("%Y-%m-%d  %H-%M-%S")
    path = os.path.join(root, f"{prefix} {stamp}")
    n = 2
    while os.path.exists(path):          # same second, second window open
        path = os.path.join(root, f"{prefix} {stamp} ({n})")
        n += 1
    os.makedirs(path, exist_ok=True)
    return path


def store_names():
    return [s.get("name", s["base"]) for s in sources()]


# --------------------------------------------------------------------------
# the custom label
# --------------------------------------------------------------------------
def candidate_ids(label):
    """
    Turn an eBay custom label into the filenames it could be stored under.

    The label itself always comes first. Digit extraction is deliberately
    narrow: only a label that is entirely a number, or entirely a short
    prefix plus a number, is treated as the old GR-0012345 form. A greedy
    search would turn bd_16_Dad_0 into 16 and fetch the wrong artwork.
    """
    lab = str(label).strip().strip(",")
    if not lab:
        return []
    out = [lab]

    m = re.fullmatch(r"[A-Za-z]{1,4}[-_]0*(\d+)", lab)
    if m:
        out.append(str(int(m.group(1))))
    elif re.fullmatch(r"0*\d+", lab):
        out.append(str(int(lab)))

    # A size or colour suffix that fulfilment does not care about, e.g.
    # bd_16_Dad_0-XL. Only stripped as a last resort, after the exact label.
    m = re.fullmatch(r"(.+?)[-_](XS|S|M|L|XL|2XL|3XL|4XL|5XL)", lab, re.I)
    if m:
        out.append(m.group(1))

    seen, uniq = set(), []
    for o in out:
        if o not in seen:
            seen.add(o)
            uniq.append(o)
    return uniq


# --------------------------------------------------------------------------
# finding the files
# --------------------------------------------------------------------------
class Design:
    """Where one order's files actually are."""

    def __init__(self, label, did, base, ext, name=""):
        self.label, self.did, self.base, self.ext = label, did, base, ext
        self.store = name

    @property
    def raw_url(self):
        return f"{self.base}/art/raw/{self.did}.{self.ext}"

    @property
    def mock_url(self):
        # Same bucket as the artwork. Fetching this from the first bucket
        # regardless is why store 2 orders never got a real shirt image.
        return f"{self.base}/art/mock/{self.did}.jpg"

    def artwork(self):
        """The print master, in whatever mode it was stored."""
        from PIL import Image
        import io
        body = _get(self.raw_url)
        if not body:
            raise RuntimeError(f"{self.raw_url} vanished between check and fetch")
        return Image.open(io.BytesIO(body))

    def mockup(self):
        """The listing photo, or None if this design never had one."""
        return _get(self.mock_url)

    def __repr__(self):
        return f"<Design {self.label} in {self.store or self.base}>"


def _probe(args):
    base, name, did, ext = args
    url = f"{base}/art/raw/{did}.{ext}"
    return (base, name, did, ext) if _get(url, timeout=15,
                                          method="HEAD") is not None else None


def find(label, extra_base=None):
    """
    Locate one custom label across every store.

    Buckets are probed in parallel with HEAD requests, so seven stores costs
    about the same as one. The bucket that answers is remembered, so the same
    label ordered again resolves with no searching at all.
    """
    ids = candidate_ids(label)
    if not ids:
        return None

    srcs = list(sources())
    if extra_base:
        srcs.insert(0, {"name": "override", "base": extra_base.rstrip("/")})

    # A label seen before: go straight there, but verify - a bucket can be
    # emptied or a design replaced.
    cache = _load_json(LABEL_CACHE) or {}
    hit = cache.get(str(label))
    if hit:
        d = Design(label, hit["did"], hit["base"], hit["ext"],
                   hit.get("store", ""))
        if _get(d.raw_url, timeout=15, method="HEAD") is not None:
            return d
        cache.pop(str(label), None)

    jobs = [(s["base"], s.get("name", ""), did, ext)
            for did in ids for s in srcs for ext in EXTS]
    with ThreadPoolExecutor(max_workers=min(16, len(jobs) or 1)) as pool:
        for res in pool.map(_probe, jobs):
            if res:
                base, name, did, ext = res
                cache[str(label)] = {"base": base, "did": did, "ext": ext,
                                     "store": name}
                _save_json(LABEL_CACHE, cache)
                return Design(label, did, base, ext, name)
    return None


def print_ready(im):
    """
    True if this file is already a finished print file.

    The old SDXL designs were 1024px images on black that had to be upscaled
    and have their background removed. The current t-shirt catalogue is
    rendered straight to 4500x5400 with real transparency, and putting that
    through the same conversion would flatten it onto black and re-derive the
    alpha from luminance - degrading crisp type for no reason.
    """
    return im.mode in ("RGBA", "LA") and min(im.size) >= 2400


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("stores:")
        for s in sources():
            print(f"  {s.get('name','?'):<20} {s['base']}")
        print("\nusage: python3 wl_lookup.py <custom label> [...]")
        raise SystemExit
    for lab in sys.argv[1:]:
        d = find(lab)
        print(f"  {lab:<24} " + (f"{d.store or d.base}  {d.raw_url}"
                                 if d else "NOT FOUND in any store"))

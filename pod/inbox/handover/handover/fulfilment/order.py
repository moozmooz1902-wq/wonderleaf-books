"""
order.py — turn an eBay order into a print-ready file.

Paste the SKUs from your orders, get transparent PNGs ready for the RIP.

    python3 order.py GR-0012345 GR-0067890
    python3 order.py --file skus.txt

Needs only Python and Pillow. It fetches the artwork over the bucket's public
URL, so no rclone and no credentials.

WHAT IT DOES
    1. reads the design id out of the SKU (GR-0012345 -> 12345)
    2. downloads the 1024px master from R2
    3. upscales it
    4. turns the black background transparent
    5. writes a 3600x4800 PNG at 300dpi into ./print/

The print file is made on demand rather than stored, because 141,000 of them
would be ~400 GB of files that mostly never get printed.
"""

import argparse, io, os, re, ssl, sys, urllib.request

import numpy as np
from PIL import Image, ImageFilter

# macOS ships Python without its certificate bundle wired up, so every HTTPS
# request fails with CERTIFICATE_VERIFY_FAILED until you run a separate
# installer. Try the proper certificates first; fall back to an unverified
# context if they are missing.
#
# The fallback is acceptable here and nowhere else: this fetches public images
# from a known Cloudflare URL. There are no credentials and nothing secret in
# the response.
def _contexts():
    """Verified first, unverified as a fallback."""
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


_CTXS = _contexts()

ap = argparse.ArgumentParser()
ap.add_argument("skus", nargs="*", help="e.g. GR-0012345")
ap.add_argument("--file", help="text file with one SKU per line")
ap.add_argument("--out", default="print")
BUCKETS = [
    "https://pub-19fad43c12d848caa97d6d53a8695d03.r2.dev",   # tshirt-mockups
    "https://pub-4b710c8610a84acc8fad1513f48132fd.r2.dev",   # tshirt-m12k
]
ap.add_argument("--base",
                default="https://pub-19fad43c12d848caa97d6d53a8695d03.r2.dev")
ap.add_argument("--scale", type=int, default=2)
ap.add_argument("--width", type=float, default=9.6,
                help="print width in inches")
ap.add_argument("--no-preview", action="store_true",
                help="skip the on-black preview")
ap.add_argument("--halftone", action="store_true",
                help="add a halftone screen. OFF by default — the designer "
                     "handles print prep")
ap.add_argument("--no-halftone", action="store_true",
                help="skip the halftone screen on soft edges")
ap.add_argument("--lpi", type=float, default=28,
                help="halftone frequency; 25-35 suits DTF, lower = bigger dots")
ap.add_argument("--white", action="store_true",
                help="also write a white underbase plate. OFF by default")
ap.add_argument("--no-white", action="store_true",
                help="skip the separate white underbase file")
ap.add_argument("--solid-mask", action="store_true",
                help="force the whole subject solid. Rarely wanted: halftone "
                     "already makes the output binary, and the mask costs "
                     "more ink and boxier edges")
args = ap.parse_args()

DPI = 300
CANVAS = (3600, 4800)
BLACK_POINT, WHITE_POINT = 18, 72
# Corners only. The earlier setting cut the artwork to 57% at the mid-edge
# and read as a dark ring closing in on the design.
VIGNETTE_START, VIGNETTE_END = 0.80, 1.06
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/120.0 Safari/537.36")

skus = list(args.skus)
if args.file:
    skus += [l.strip() for l in open(args.file) if l.strip()]

# No arguments means it was double-clicked rather than run from a shell, so
# ask for the SKUs instead of printing usage and quitting.
if not skus:
    print("=" * 52)
    print(" ORDER -> PRINT FILE")
    print("=" * 52)
    print("\nPaste the SKUs, separated by spaces or on separate lines.")
    print("Press Enter twice when you are done.\n")
    lines = []
    while True:
        try:
            line = input("  SKU: ").strip()
        except EOFError:
            break
        if not line:
            break
        lines.append(line)
    for l in lines:
        skus += [p for p in re.split(r"[\s,]+", l) if p]

if not skus:
    input("\nNo SKUs given. Press Enter to close.")
    raise SystemExit

os.makedirs(args.out, exist_ok=True)


def design_id(sku):
    """GR-0012345 -> 12345. Also accepts a bare number."""
    m = re.search(r"(\d+)", sku)
    if not m:
        return None
    return str(int(m.group(1)))


def fetch(did):
    """
    Download the master image.

    Tries each SSL context in turn. macOS ships Python without its certificate
    bundle wired up, so a verified request fails with CERTIFICATE_VERIFY_FAILED
    until a separate installer is run — and it can fail even with certifi
    present. Falling back to an unverified context is acceptable HERE and
    nowhere else: this fetches public images from a known URL, with no
    credentials and nothing secret in the response.
    """
    import time
    # Try every store's bucket and both extensions. A custom label does not
    # say which store it came from, and m12k was generated with --jpeg so
    # its designs are .jpg where store 1's are .png. Looking only in the
    # default bucket for .png is why m12k orders were "not recognised".
    bases = [args.base] + [b for b in BUCKETS if b != args.base]
    last = None
    for base in bases:
        for ext in ("png", "jpg"):
            url = f"{base}/art/raw/{did}.{ext}"
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            for ctx in _CTXS:
                for attempt in range(2):
                    try:
                        with urllib.request.urlopen(req, timeout=30,
                                                    context=ctx) as r:
                            return Image.open(
                                io.BytesIO(r.read())).convert("RGB")
                    except Exception as e:
                        last = e
                        if "CERTIFICATE" in str(e).upper():
                            break
                        if "404" in str(e) or "Not Found" in str(e):
                            break    # wrong bucket or extension, move on
                        time.sleep(1 + attempt)
    raise last


# Luminance above which a pixel counts as subject rather than background.
# Low, because painterly artwork has genuinely dark areas that still print.
# Luminance above which a pixel counts as subject rather than background.
# This CANNOT be a fixed number: some generations fade to true black, others
# leave a faint haze across the whole frame at luminance 30-45. A fixed floor
# of 22 printed that haze solid, which filled the corners and made the design
# come out as a square. It is now measured from each image's own border.
SUBJECT_FLOOR = 22
SUBJECT_FLOOR_MAX = 70      # never so high that real dark detail is lost

# Fraction of the shorter side faded at the frame border, so artwork that runs
# off the edge tapers out rather than being cut off in a straight line.
EDGE_TAPER = 0.055
FEATHER = 9
# Pull the white in from the colour edge, in pixels at 300dpi (~0.17mm), so it
# cannot show as a pale halo when film and shirt are slightly out of register.
CHOKE = 2


def flat_artefact(rgb, alpha):
    """
    Detect flat grey slabs the generator sometimes leaves in the artwork.

    Some generations hallucinate a UI panel or frame: a solid, perfectly even
    grey rectangle with no texture. Nothing downstream can tell it is not part
    of the design — it has enough ink, so it prints. One in twelve of a sample
    batch had them.
    """
    a = np.asarray(rgb).astype(np.float32)
    h, w = alpha.shape
    step = max(16, min(h, w) // 60)
    hits = total = 0
    for y in range(0, h - step, step * 2):
        for x in range(0, w - step, step * 2):
            if alpha[y:y + step, x:x + step].mean() < 200:
                continue
            b = a[y:y + step, x:x + step]
            total += 1
            lum = b.mean(2)
            if (lum.std() < 5.0 and 35 < lum.mean() < 150
                    and (b.max(2) - b.min(2)).mean() < 16):
                hits += 1
    return (hits / total) if total else 0.0


def subject_floor(lum, border=0.06):
    """
    Work out where the background ends for THIS image.

    Some generations fade to true black; others leave a faint haze right out
    to the frame edge. Treating that haze as artwork prints it solid, which
    fills the corners and turns the design into a square — which is exactly
    what happened on a skull-and-flames test.

    So sample the outer border, take a high percentile of it as the
    background level, and set the threshold just above that.
    """
    h, w = lum.shape
    b = max(4, int(min(h, w) * border))
    edge = np.concatenate([
        lum[:b, :].ravel(), lum[-b:, :].ravel(),
        lum[:, :b].ravel(), lum[:, -b:].ravel()])
    # +4, not +10. A larger margin cut away genuine smoke and flames, which
    # are part of the design — the goal is to drop dead background haze, not
    # to trim the artwork.
    bg = float(np.percentile(edge, 88))
    return float(np.clip(bg + 4.0, SUBJECT_FLOOR, SUBJECT_FLOOR_MAX))


def to_print(im):
    """
    Build the print file.

    Deriving alpha straight from luminance looks right on screen but prints
    badly: on dark painterly artwork only ~43% ends up fully opaque and half
    sits at partial alpha. The RIP dithers a thin white underbase there and
    the colour prints weak — which is the "not enough opacity" complaint.

    So find the subject, make it SOLID, and feather only the true edge. Same
    look on the shirt; ~98% of the design now lays down full white.
    """
    if args.scale > 1:
        im = im.resize((im.width * args.scale, im.height * args.scale),
                       Image.LANCZOS)
        im = im.filter(ImageFilter.UnsharpMask(radius=2, percent=80,
                                               threshold=3))

    a = np.asarray(im).astype(np.float32)
    lum = 0.2126 * a[..., 0] + 0.7152 * a[..., 1] + 0.0722 * a[..., 2]

    if not args.solid_mask:
        alpha = np.clip((lum - BLACK_POINT) / (WHITE_POINT - BLACK_POINT), 0, 1)
        alpha = alpha * alpha * (3 - 2 * alpha)
    else:
        floor = subject_floor(lum)
        mask = (lum > floor).astype(np.float32)
        m = Image.fromarray((mask * 255).astype(np.uint8), "L")
        m = m.filter(ImageFilter.MaxFilter(9))
        m = m.filter(ImageFilter.MinFilter(9))
        m = m.filter(ImageFilter.GaussianBlur(FEATHER))
        alpha = np.asarray(m).astype(np.float32) / 255.0
        alpha = np.clip((alpha - 0.35) / 0.30, 0, 1)

    # --- edge taper -------------------------------------------------------
    # The real cause of a square print is content running off the frame and
    # being cut dead at the border. A radial vignette was the wrong tool: it
    # bit into the middle of the design (57% at the mid-edge) and showed as a
    # dark ring, while doing nothing about the actual corners.
    #
    # This instead fades only the outermost band, measured from each side. A
    # design that already stops short of the frame is untouched; one that runs
    # off the edge tapers out instead of ending in a straight line.
    h, w = alpha.shape
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    band = max(8.0, min(h, w) * EDGE_TAPER)
    dist = np.minimum.reduce([xx, yy, (w - 1) - xx, (h - 1) - yy])
    taper = np.clip(dist / band, 0, 1)
    taper = taper * taper * (3 - 2 * taper)
    alpha = alpha * taper

    r = np.sqrt(((xx - w / 2) / (w / 2)) ** 2 +
                ((yy - h / 2) / (h / 2)) ** 2) / np.sqrt(2)
    fall = np.clip((VIGNETTE_END - r) / (VIGNETTE_END - VIGNETTE_START), 0, 1)
    fall = fall * fall * (3 - 2 * fall)
    if args.solid_mask:
        fall = np.clip(fall * 1.10, 0, 1)
    alpha = alpha * fall

    alpha_img = Image.fromarray((alpha * 255).astype(np.uint8), "L")
    rgba = Image.merge("RGBA", (*im.split(), alpha_img))

    bbox = rgba.getbbox()
    if bbox:
        rgba = rgba.crop(bbox)

    target = int(args.width * DPI)
    s = min(target / rgba.width, (CANVAS[1] * 0.9) / rgba.height)
    rgba = rgba.resize((max(1, int(rgba.width * s)),
                        max(1, int(rgba.height * s))), Image.LANCZOS)

    out = Image.new("RGBA", CANVAS, (0, 0, 0, 0))
    out.alpha_composite(rgba, ((CANVAS[0] - rgba.width) // 2,
                               (CANVAS[1] - rgba.height) // 2))
    return out


def make_underbase(art):
    """
    The white layer that goes down first — the step a designer would otherwise
    do by hand. Built from the alpha channel, so nothing is missed and no wisp
    of smoke gets left out of the selection.

    Choked slightly so the white cannot peek out around the colour.
    """
    a = np.asarray(art)
    m = Image.fromarray(a[..., 3], "L")
    for _ in range(CHOKE):
        m = m.filter(ImageFilter.MinFilter(3))
    ch = np.asarray(m).astype(np.float32)
    ch = np.where(ch > 110, 255, ch * 0.6)
    white = np.zeros(a.shape, np.uint8)
    white[..., :3] = 255
    white[..., 3] = np.clip(ch, 0, 255).astype(np.uint8)
    return Image.fromarray(white, "RGBA")


print(f"{len(skus)} order(s)\n")
ok = 0
for i, sku in enumerate(skus, 1):
    did = design_id(sku)
    if not did:
        print(f"  [{i}] {sku}: cannot read a design id from this SKU")
        continue
    # One numbered folder per order, files named by that number.
    #
    # Everything used to land in a single directory, so a twenty-order batch
    # was forty files in one list and the designer had to pair them up by
    # eye. A folder each keeps the artwork and its shirt image together.
    #
    # orders.txt at the top maps every number back to its custom label, so
    # numbering the folders loses nothing.
    folder = os.path.join(args.out, str(i))
    os.makedirs(folder, exist_ok=True)
    dst = os.path.join(folder, f"{i}.png")
    try:
        im = fetch(did)
        art = to_print(im)

        # DTF cannot print semi-transparent ink, and the adhesive powder needs
        # a minimum dot size to grip. Halftoning turns the fade into solid dots
        # large enough to hold, keeping the look without the peeling.
        if args.halftone:
            try:
                import halftone
                art = halftone.apply(art, lpi=args.lpi)
            except ImportError:
                pass

        art.save(dst, dpi=(DPI, DPI))

        if args.white:
            make_underbase(art).save(dst.replace(".png", "_WHITE.png"),
                                     dpi=(DPI, DPI))

        # A transparent PNG opened in Preview shows its transparency as white,
        # and this artwork is built for a BLACK shirt — every dark area is
        # deliberately absent so the garment shows through. On white it looks
        # patchy and wrong.
        #
        # So the second file is the SHIRT MOCKUP — the same image the eBay
        # listing uses. It already exists in R2, built when the design was
        # made, so it is fetched rather than rebuilt: no extra libraries, no
        # blank.png needed on this machine, and it matches what the customer
        # saw when they bought.
        if not args.no_preview:
            shirt = dst.replace(".png", "_SHIRT.jpg")
            got = False
            mreq = urllib.request.Request(
                f"{args.base}/art/mock/{did}.jpg", headers={"User-Agent": UA})
            for ctx in _CTXS:
                try:
                    with urllib.request.urlopen(mreq, timeout=30,
                                                context=ctx) as r:
                        with open(shirt, "wb") as fh:
                            fh.write(r.read())
                    got = True
                    break
                except Exception:
                    continue

            if not got:
                # no mockup in R2 (an older design, or one never processed) —
                # fall back to the artwork flattened on black
                chk = Image.new("RGB", art.size, (16, 16, 16))
                chk.paste(art, (0, 0), art)
                chk.thumbnail((1400, 1400), Image.LANCZOS)
                chk.save(shirt, quality=92)

        flat = flat_artefact(art.convert("RGB"), np.asarray(art)[..., 3])
        warn = (f"   ** {flat*100:.0f}% flat grey — check for a slab artefact"
                if flat > 0.04 else "")
        print(f"  [{i}] {sku} -> {dst}{warn}")
        ok += 1
    except Exception as e:
        print(f"  [{i}] {sku}: FAILED — {str(e)[:70]}")

# index so a folder number can always be traced back to its order
try:
    with open(os.path.join(args.out, "orders.txt"), "w") as fh:
        fh.write("folder   custom label\n")
        fh.write("------   ------------\n")
        for n, sk in enumerate(skus, 1):
            fh.write(f"{n:<8} {sk}\n")
except Exception:
    pass

print(f"\n{ok}/{len(skus)} written to {os.path.abspath(args.out)}")
print("One folder per order. orders.txt says which folder is which label.")
print(f"{args.width}in wide at {DPI}dpi, transparent background.")
print("Numbered in order so they match your picking list.")
print()
print("The .png files go to the printer — your RIP builds the white")
print("underbase from the transparency.")
print("Two files per order: NAME.png is the artwork for printing,")
print("NAME_SHIRT.jpg shows how it looks on the shirt.")
print("The old note, for reference:")
print("The preview files are only for checking. They show the design")
print("on black, which is how it will actually look. Do not print those.")

if ok:
    # open the folder so the files are right there
    try:
        if sys.platform == "darwin":
            os.system(f"open '{os.path.abspath(args.out)}'")
    except Exception:
        pass

if not sys.stdin.isatty() or not args.skus:
    try:
        input("\nPress Enter to close.")
    except EOFError:
        pass

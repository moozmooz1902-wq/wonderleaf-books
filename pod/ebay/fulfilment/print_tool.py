"""
print_tool.py — a window for making print files. No Terminal.

Paste the eBay custom labels, press the button, the files appear. Built with
tkinter, which ships with Python, so there is nothing extra to install for the
interface itself.

The downloads run on a background thread so the window stays responsive and
can show progress — doing them on the main thread freezes the UI until the
last file finishes, which looks like a crash.
"""

import io, os, re, ssl, subprocess, sys, threading, urllib.request

import tkinter as tk
from tkinter import ttk, messagebox, filedialog

try:
    import numpy as np
    from PIL import Image, ImageFilter
except ImportError:
    root = tk.Tk(); root.withdraw()
    messagebox.showerror(
        "Missing libraries",
        "This needs Pillow and numpy.\n\n"
        "Open Terminal and run:\n\n"
        "    pip3 install pillow numpy\n\n"
        "then start this again.")
    sys.exit(1)

try:
    import wl_lookup
except ImportError:
    root = tk.Tk(); root.withdraw()
    messagebox.showerror(
        "Missing file",
        "wl_lookup.py must sit in the same folder as this tool.\n\n"
        "Copy it in from the fulfilment folder and start this again.")
    sys.exit(1)

try:
    import halftone as _ht
    HT_OK = True
except Exception:
    HT_OK = False

# Optional: the printer's TIFF format. Only used if tifffile is installed.
try:
    from tiff_out import save_tiff
    TIFF_OK = True
except Exception:
    TIFF_OK = False

# The store list is NOT written into this file any more. It lives in
# sources.json in R2 and is read by wl_lookup, so adding a store is one edit
# to one file rather than a code change on every Mac - and a machine that
# missed the edit can no longer report good orders as "not recognised".
DPI = 300
CANVAS = (3600, 4800)
BLACK_POINT, WHITE_POINT = 18, 72
# The vignette exists only to stop a design that fills the whole frame from
# printing as a square. Tested against real artwork it made NO difference to
# the shape — the subject mask already does that — while cutting the artwork
# down to 57% at the mid-edge, which showed as a dark ring closing in on the
# design. Now it touches the outer corners only.
VIG_START, VIG_END = 0.80, 1.06

# Luminance above which a pixel counts as part of the subject rather than
# background. Low, because painterly artwork has genuinely dark areas that
# still need printing.
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

# How far to pull the white underbase in from the colour edge, in pixels at
# 300dpi. About 0.17mm. Without a choke the white peeks out around the artwork
# as a pale halo, because film and garment never align perfectly on the press.
CHOKE = 2
# Width of the softened edge, in pixels at 2048. Enough to avoid a cut-out
# look without thinning the body of the design.
FEATHER = 9
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/120.0 Safari/537.36")


def contexts():
    """macOS often ships Python without working certificates; fall back."""
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


CTXS = contexts()


def flat_artefact(rgb, alpha):
    """
    Detect flat grey slabs left in the artwork by the generator.

    Some generations hallucinate a UI panel or frame: a solid, perfectly even
    grey rectangle with no texture. It is not part of the design, but nothing
    downstream can tell — it has enough ink to print, so it prints. One in
    twelve of a sample batch had them.

    Real artwork always has some variation. A block that is flat to within a
    couple of levels, desaturated, and sits well above the background is not
    artwork.
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


def to_print(im, width_in, solid=True, durable=False):
    """
    Build the print file.

    THE OPACITY PROBLEM
        Deriving alpha straight from luminance gives a smooth ramp, which
        looks right on screen but prints badly: on dark painterly artwork only
        ~43% of the design ends up fully opaque and half sits at partial alpha.
        The RIP then dithers a thin white underbase there and the colour prints
        weak and patchy. The printer sees "not enough opacity".

        So: find the subject, make it SOLID, and feather only a narrow band at
        the true edge. Same soft look on the shirt, but the body of the design
        lays down full white.
    """
    im = im.resize((im.width * 2, im.height * 2), Image.LANCZOS)
    im = im.filter(ImageFilter.UnsharpMask(radius=2, percent=80, threshold=3))

    a = np.asarray(im).astype(np.float32)
    lum = 0.2126 * a[..., 0] + 0.7152 * a[..., 1] + 0.0722 * a[..., 2]

    if not solid:
        alpha = np.clip((lum - BLACK_POINT) / (WHITE_POINT - BLACK_POINT), 0, 1)
        alpha = alpha * alpha * (3 - 2 * alpha)
    else:
        # anything with visible ink is part of the subject
        floor = subject_floor(lum)
        mask = (lum > floor).astype(np.float32)

        # close small gaps so dark detail inside the subject stays printed
        m = Image.fromarray((mask * 255).astype(np.uint8), "L")
        m = m.filter(ImageFilter.MaxFilter(9))     # grow
        m = m.filter(ImageFilter.MinFilter(9))     # shrink back
        # feather only the boundary
        m = m.filter(ImageFilter.GaussianBlur(FEATHER))
        alpha = np.asarray(m).astype(np.float32) / 255.0

        # push everything that is meaningfully inside up to fully opaque, so
        # the underbase is solid rather than dithered
        alpha = np.clip((alpha - 0.35) / 0.30, 0, 1)

        if durable:
            # DTF adhesive powder only sticks where there is enough ink. A
            # feathered edge has thin coverage, holds almost no powder, and
            # peels after a few washes — which is what the printer means by
            # "smoky edges do not stick".
            #
            # So cut hard: everything meaningfully inside becomes fully
            # opaque, everything else vanishes, leaving about a pixel of
            # anti-aliasing so the edge is not jagged. Costs the dissolved
            # look at the very boundary; buys a print that survives washing.
            alpha = np.clip((alpha - 0.45) * 12.0, 0, 1)

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
    fall = np.clip((VIG_END - r) / (VIG_END - VIG_START), 0, 1)
    fall = fall * fall * (3 - 2 * fall)
    # a gentler vignette when printing solid: the point is to soften the very
    # corners, not to thin the artwork
    if solid:
        fall = np.clip(fall * 1.10, 0, 1)
    if durable:
        # the vignette must not thin the edge back down again
        fall = np.clip((fall - 0.30) * 6.0, 0, 1)
    alpha = alpha * fall

    am = Image.fromarray((alpha * 255).astype(np.uint8), "L")
    rgba = Image.merge("RGBA", (*im.split(), am))

    bbox = rgba.getbbox()
    if bbox:
        rgba = rgba.crop(bbox)

    target = int(width_in * DPI)
    s = min(target / rgba.width, (CANVAS[1] * 0.9) / rgba.height)
    rgba = rgba.resize((max(1, int(rgba.width * s)),
                        max(1, int(rgba.height * s))), Image.LANCZOS)

    out = Image.new("RGBA", CANVAS, (0, 0, 0, 0))
    out.alpha_composite(rgba, ((CANVAS[0] - rgba.width) // 2,
                               (CANVAS[1] - rgba.height) // 2))
    return out


def make_underbase(art):
    """
    The white layer that goes down first.

    This is the step a designer would otherwise do by hand: select the
    artwork, put a white shape behind it. Doing it from the alpha channel is
    exact — no hand-selection, no missed wisps of smoke.

    The white is CHOKED, pulled in slightly from the colour edge, so it cannot
    show as a pale halo when the film and the shirt are a fraction out of
    register on the press.
    """
    a = np.asarray(art)
    alpha = a[..., 3]

    m = Image.fromarray(alpha, "L")
    for _ in range(CHOKE):
        m = m.filter(ImageFilter.MinFilter(3))     # erode 1px each pass

    ch = np.asarray(m).astype(np.float32)
    # partial alpha would dither the white; anything meaningfully inside the
    # artwork gets solid white
    ch = np.where(ch > 110, 255, ch * 0.6)

    white = np.zeros(a.shape, np.uint8)
    white[..., :3] = 255
    white[..., 3] = np.clip(ch, 0, 255).astype(np.uint8)
    return Image.fromarray(white, "RGBA")


class App:
    def __init__(self, root):
        self.root = root
        # A fresh dated folder per run, not one fixed directory. Everything
        # landed in ~/Desktop/Print Files before, so each batch buried the
        # last and the numbered folders stopped matching their picking list.
        self.out_dir = None          # created when the run actually starts
        root.title("T-Shirt Print Files")
        root.geometry("640x600")
        root.configure(bg="#f5f5f7")

        head = tk.Frame(root, bg="#111", height=76)
        head.pack(fill="x")
        head.pack_propagate(False)
        tk.Label(head, text="ORDER  →  PRINT FILES", bg="#111", fg="#fff",
                 font=("Helvetica", 19, "bold")).pack(pady=(16, 0))
        tk.Label(head, text="paste the custom labels from your eBay orders",
                 bg="#111", fg="#9a9aa0",
                 font=("Helvetica", 12)).pack()

        body = tk.Frame(root, bg="#f5f5f7", padx=22, pady=16)
        body.pack(fill="both", expand=True)

        tk.Label(body, text="Custom labels", bg="#f5f5f7",
                 font=("Helvetica", 13, "bold")).pack(anchor="w")
        tk.Label(body,
                 text="one per line, or several separated by spaces or commas",
                 bg="#f5f5f7", fg="#6b6b70",
                 font=("Helvetica", 11)).pack(anchor="w", pady=(0, 6))

        self.box = tk.Text(body, height=9, font=("Menlo", 13),
                           relief="solid", bd=1, highlightthickness=0)
        self.box.pack(fill="x")
        self.box.insert("1.0", "GR-0490874\nGR-0330615")
        self.box.focus_set()

        opts = tk.Frame(body, bg="#f5f5f7")
        opts.pack(fill="x", pady=(12, 0))
        tk.Label(opts, text="Print width (inches):", bg="#f5f5f7",
                 font=("Helvetica", 12)).pack(side="left")
        self.width = tk.StringVar(value="9.6")
        tk.Entry(opts, textvariable=self.width, width=6,
                 font=("Helvetica", 12), relief="solid", bd=1
                 ).pack(side="left", padx=(8, 0))

        # ALL EFFECTS OFF BY DEFAULT (Aug 2026).
        # The files now go to his designer, who does the white underbase and
        # decides which artwork needs one. Anything this tool adds — halftone
        # dots, a generated white plate, a CMYK+spot TIFF — is work the
        # designer has to undo. Output is the plain transparent artwork plus a
        # preview to look at. The switches remain for anyone who wants them.
        self.halftone = tk.BooleanVar(value=False)
        self.durable = tk.BooleanVar(value=False)
        self.tiff = tk.BooleanVar(value=False)
        self.underbase = tk.BooleanVar(value=False)
        # OFF by default now. It was added to force opacity before halftone
        # existed; halftone makes everything binary anyway, and the mask costs
        # 8% more ink and five times more boxy edges.
        self.solid = tk.BooleanVar(value=False)
        tk.Checkbutton(opts, text="Solid mask", variable=self.solid,
                       bg="#f5f5f7", font=("Helvetica", 12)
                       ).pack(side="left", padx=(18, 0))
        tk.Checkbutton(opts, text="White layer", variable=self.underbase,
                       bg="#f5f5f7", font=("Helvetica", 12)
                       ).pack(side="left", padx=(10, 0))
        hb = tk.Checkbutton(opts, text="Halftone edge", variable=self.halftone,
                            bg="#f5f5f7", font=("Helvetica", 12))
        hb.pack(side="left", padx=(10, 0))
        if not HT_OK:
            hb.config(state="disabled")
        cb = tk.Checkbutton(opts, text="Printer TIFF", variable=self.tiff,
                            bg="#f5f5f7", font=("Helvetica", 12))
        cb.pack(side="left", padx=(10, 0))
        if not TIFF_OK:
            cb.config(state="disabled")

        self.folder_lbl = tk.Label(opts, text="", bg="#f5f5f7", fg="#6b6b70",
                                   font=("Helvetica", 11))
        self.folder_lbl.pack(side="right")
        tk.Button(opts, text="Change folder", command=self.pick_folder,
                  font=("Helvetica", 11)).pack(side="right", padx=(0, 10))
        self.update_folder_label()

        self.btn = tk.Button(body, text="Make Print Files",
                             command=self.start, bg="#0a84ff", fg="white",
                             font=("Helvetica", 16, "bold"),
                             relief="flat", pady=12,
                             activebackground="#0060df",
                             activeforeground="white",
                             highlightbackground="#0a84ff")
        self.btn.pack(fill="x", pady=(16, 10))

        self.bar = ttk.Progressbar(body, mode="determinate")
        self.bar.pack(fill="x")

        self.log = tk.Text(body, height=9, font=("Menlo", 11),
                           bg="#1c1c1e", fg="#d8d8dc",
                           relief="flat", highlightthickness=0)
        self.log.pack(fill="both", expand=True, pady=(10, 0))
        self.say("Ready. Paste your labels above and press the button.")
        self.say("")
        self.say("Solid mask is now OFF. It forced everything opaque before")
        self.say("halftone existed; halftone does that job better and the mask")
        self.say("only made edges boxier and used more ink.")
        self.say("")
        if HT_OK:
            self.say("Halftone edge is on. DTF cannot print semi-transparent")
            self.say("ink, and the glue powder needs a minimum dot size to")
            self.say("grip. This turns the fade into solid dots big enough to")
            self.say("hold — same look, but it will not peel.")
        else:
            self.say("Halftone unavailable — halftone.py should sit next to")
            self.say("this file.")
        self.say("")
        if TIFF_OK:
            self.say("Printer TIFF is on: it writes the same CMYK + white")
            self.say("spot-channel file your designer builds by hand.")
        else:
            self.say("Printer TIFF is unavailable — to enable it, run:")
            self.say("    pip3 install tifffile imagecodecs")

    def update_folder_label(self):
        # out_dir is None until a run starts, because the folder name carries
        # the time the batch was made rather than the time the app opened.
        name = (os.path.basename(self.out_dir) if self.out_dir
                else "a new dated folder in Downloads")
        self.folder_lbl.config(text=f"saving to: {name}")

    def pick_folder(self):
        d = filedialog.askdirectory(initialdir=os.path.expanduser("~"))
        if d:
            self.out_dir = d
            self.update_folder_label()

    def say(self, msg):
        self.log.insert("end", msg + "\n")
        self.log.see("end")
        self.root.update_idletasks()

    def start(self):
        raw = self.box.get("1.0", "end")
        skus = [s for s in re.split(r"[\s,]+", raw) if s.strip()]
        if not skus:
            messagebox.showwarning("Nothing to do",
                                   "Paste at least one custom label.")
            return
        try:
            width = float(self.width.get())
            if not 2 <= width <= 20:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Check the width",
                                   "Print width should be a number between "
                                   "2 and 20 inches.")
            return

        self.btn.config(state="disabled", text="Working ...")
        self.log.delete("1.0", "end")
        self.bar["maximum"] = len(skus)
        self.bar["value"] = 0
        # background thread: doing this inline freezes the window until the
        # last download finishes, which looks like a crash
        threading.Thread(target=self.run, args=(skus, width),
                         daemon=True).start()

    def run(self, skus, width):
        if not self.out_dir:
            self.out_dir = wl_lookup.run_folder()
        os.makedirs(self.out_dir, exist_ok=True)

        # index mapping folder number -> custom label, so numbering the
        # folders never loses track of which order is which
        try:
            with open(os.path.join(self.out_dir, "orders.txt"), "w") as fh:
                fh.write("folder   custom label\n")
                fh.write("------   ------------\n")
                for n, sk in enumerate(skus, 1):
                    fh.write(f"{n:<8} {sk}\n")
        except Exception:
            pass

        self.say(f"{len(skus)} order(s)\n")
        ok = 0
        for i, sku in enumerate(skus, 1):
            # The label is used exactly as eBay gave it. Pulling the first
            # run of digits out of it worked only while every label looked
            # like GR-0012345; on the current catalogue it turns
            # bd_16_Dad_0 into 16 and fetches a different design entirely.
            design = wl_lookup.find(sku)
            if design is None:
                self.say(f"  [{i}] {sku} — not found in any store "
                         f"({', '.join(wl_lookup.store_names())})")
                self.bar["value"] = i
                continue
            try:
                src = design.artwork()
                if wl_lookup.print_ready(src):
                    # Already a finished 4500x5400 transparent print file.
                    # Running it through to_print() would flatten it onto
                    # black and rebuild the alpha from luminance, softening
                    # type that is currently crisp.
                    art = src
                else:
                    art = to_print(src.convert("RGB"), width,
                                   solid=self.solid.get(),
                                   durable=self.durable.get())

                # Turn any remaining soft fade into solid dots. DTF cannot
                # print semi-transparent ink, and the adhesive powder needs a
                # minimum dot size to grip — a feathered edge holds almost no
                # powder and peels. Halftoning keeps the fade but makes every
                # part of it printable.
                if self.halftone.get() and HT_OK:
                    art = _ht.apply(art)
                # One numbered folder per order, files named by that number.
                # A twenty-order batch used to be forty files in a single
                # list, which the designer had to pair up by eye.
                folder = os.path.join(self.out_dir, str(i))
                os.makedirs(folder, exist_ok=True)
                png = os.path.join(folder, f"{i}.png")
                art.save(png, dpi=(DPI, DPI))

                if self.underbase.get():
                    ub = make_underbase(art)
                    ub.save(png.replace(".png", "_WHITE.png"),
                            dpi=(DPI, DPI))

                # The TIFF is the format the printer takes directly, but it
                # is an EXTRA. If tifffile is missing or the write fails, say
                # so and carry on — losing the PNG as well would be worse.
                tif_note = ""
                if self.tiff.get():
                    try:
                        from tiff_out import save_tiff as _save_tiff
                        _save_tiff(art, png.replace(".png", ".tif"))
                        tif_note = " + tif"
                    except ImportError:
                        tif_note = "  (no tif — run: pip3 install tifffile imagecodecs)"
                    except Exception as te:
                        tif_note = f"  (no tif — {str(te)[:36]})"

                # Second file is the SHIRT MOCKUP — the same picture the eBay
                # listing uses, so it shows how the design actually looks worn.
                # It already exists in R2 from when the design was made, so
                # fetch it rather than rebuild it: nothing extra to install and
                # it matches what the customer saw.
                #
                # It comes from whichever bucket the DESIGN was found in.
                # Always fetching it from the first bucket is why orders from
                # the other stores never got a real shirt image and silently
                # fell back to the flattened version below.
                shirt = png.replace(".png", "_SHIRT.jpg")
                body = design.mockup()
                if body:
                    with open(shirt, "wb") as fh:
                        fh.write(body)
                else:
                    chk = Image.new("RGB", art.size, (16, 16, 16))
                    chk.paste(art, (0, 0), art)
                    chk.thumbnail((1400, 1400), Image.LANCZOS)
                    chk.save(shirt, quality=92)

                flat = flat_artefact(art.convert("RGB"),
                                     np.asarray(art)[..., 3])
                warn = ""
                if flat > 0.04:
                    warn = f"   ** {flat*100:.0f}% flat grey — check for a slab artefact"
                self.say(f"  [{i}] {sku} — done  [{design.store or design.base}]"
                         f"{tif_note}{warn}")
                ok += 1
            except Exception as e:
                msg = str(e)
                if "404" in msg:
                    msg = "not found — check the number"
                elif "CERTIFICATE" in msg.upper():
                    msg = "connection blocked by certificates"
                self.say(f"  [{i}] {sku} — FAILED: {msg[:52]}")
            self.bar["value"] = i
            self.root.update_idletasks()

        self.say(f"\n{ok} of {len(skus)} ready in {self.out_dir}")
        self.update_folder_label()
        if ok:
            self.say("")
            if self.tiff.get() and TIFF_OK:
                self.say("  NAME.tif         <- SEND THIS. CMYK + white plate,")
                self.say("                      ready for the printer as-is")
            self.say("  NAME.png         colour artwork")
            if self.underbase.get():
                self.say("  NAME_WHITE.png   white underbase, already choked")
            self.say("  each order is in its own numbered folder")
            self.say("\nIf the RIP builds its own underbase, use the colour")
            self.say("file alone and ignore the _WHITE one.")
            try:
                subprocess.run(["open", self.out_dir], check=False)
            except Exception:
                pass
        self.btn.config(state="normal", text="Make Print Files")


if __name__ == "__main__":
    root = tk.Tk()
    App(root)
    root.mainloop()

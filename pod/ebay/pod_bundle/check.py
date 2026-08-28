#!/usr/bin/env python3
"""
Preflight: verify everything works BEFORE starting a 2.6 hour render.

    python3 check.py r2:your-bucket/art

Checks deps, fonts, blank, catalogue, rclone, and then does a real end-to-end
round trip: renders one design, uploads both files, reads them back, deletes
them. If this passes, the full run will work.
"""
import os, shutil, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
os.environ.setdefault("BLANK_TEE", os.path.join(HERE, "blank.png"))
OK, BAD = "  [ OK ]", "  [FAIL]"
fails = []


def step(label, fn):
    try:
        detail = fn()
        print(f"{OK} {label}" + (f"  {detail}" if detail else ""))
        return True
    except Exception as e:
        print(f"{BAD} {label}\n         {type(e).__name__}: {e}")
        fails.append(label)
        return False


def main():
    dest = sys.argv[1] if len(sys.argv) > 1 else None
    print("PREFLIGHT\n")

    def deps():
        import PIL, numpy, scipy
        return f"Pillow {PIL.__version__}, numpy {numpy.__version__}, scipy {scipy.__version__}"
    step("python packages", deps)

    def fonts():
        d = os.path.join(HERE, "fonts")
        n = len([f for f in os.listdir(d) if f.endswith(".ttf")])
        if n < 4:
            raise RuntimeError(f"only {n} fonts found in {d}")
        return f"{n} fonts"
    step("fonts", fonts)

    def blank():
        from PIL import Image
        im = Image.open(os.environ["BLANK_TEE"])
        return f"{im.size[0]}x{im.size[1]}"
    step("blank.png", blank)

    def cat():
        import json
        p = os.path.join(HERE, "catalogue.json")
        d = json.load(open(p))
        return f"{len(d):,} designs"
    ok_cat = step("catalogue.json", cat)

    if not dest:
        print("\n  no destination given - skipping the R2 checks")
        print("  usage: python3 check.py r2:your-bucket/art")
        return 1 if fails else 0

    bucket = dest.split("/")[0]

    def rclone_present():
        if not shutil.which("rclone"):
            raise RuntimeError("rclone not installed")
        v = subprocess.run(["rclone", "version"], capture_output=True, text=True)
        return v.stdout.split("\n")[0]
    if not step("rclone installed", rclone_present):
        print("\n  -> install it:  curl https://rclone.org/install.sh | sudo bash")
        return 1

    def bucket_reachable():
        r = subprocess.run(["rclone", "lsf", bucket, "--max-depth", "1"],
                           capture_output=True, text=True, timeout=60)
        if r.returncode != 0:
            raise RuntimeError(r.stderr.strip().split("\n")[-1][:200])
        return f"{bucket} reachable"
    if not step("bucket reachable", bucket_reachable):
        print("\n  -> check the bucket NAME, and that the endpoint / keys are right")
        return 1

    def round_trip():
        import json
        sys.path.insert(0, HERE)
        import render_designs as rd, photo_mockup as pm
        d = json.load(open(os.path.join(HERE, "catalogue.json")))[0]
        tmp = tempfile.mkdtemp()
        png = os.path.join(tmp, "_preflight.png")
        jpg = os.path.join(tmp, "_preflight.jpg")
        art = rd.render(d, os.path.join(HERE, "fonts"))
        art.save(png, compress_level=6)
        pm.build(art, jpg)
        for f, sub in ((png, "raw"), (jpg, "mock")):
            r = subprocess.run(["rclone", "copyto", "--s3-no-check-bucket", f,
                                f"{dest}/{sub}/{os.path.basename(f)}"],
                               capture_output=True, text=True, timeout=180)
            if r.returncode != 0:
                raise RuntimeError("upload failed: " + r.stderr.strip()[:200])
        r = subprocess.run(["rclone", "lsf", f"{dest}/mock"],
                           capture_output=True, text=True, timeout=60)
        if "_preflight.jpg" not in r.stdout:
            raise RuntimeError("uploaded but not visible when listing back")
        return f"design '{d['stem']}' uploaded and read back"
    if step("end-to-end round trip", round_trip):
        print(f"\n  A test image is now at {dest}/mock/_preflight.jpg")
        print("  Open it in your browser to check it looks right, then remove it:")
        print(f"    rclone delete {dest}/mock/_preflight.jpg")
        print(f"    rclone delete {dest}/raw/_preflight.png")

    print()
    if fails:
        print(f"  {len(fails)} check(s) failed: {', '.join(fails)}")
        return 1
    print("  ALL CHECKS PASSED - safe to start the full run:")
    print(f"    nohup python3 run.py --workers 16 --upload {dest} > render.log 2>&1 &")
    print("    tail -f render.log")
    return 0


if __name__ == "__main__":
    sys.exit(main())

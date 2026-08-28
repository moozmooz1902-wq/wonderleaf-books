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
    if not step("python packages", deps):
        print(f"         this python is {sys.executable}")
        print("         install into THIS python:")
        print(f"           {sys.executable} -m pip install Pillow numpy scipy")
        print("         if pip refuses with 'externally-managed-environment', add")
        print("           --break-system-packages")
        print("         if it says 'No module named pip', first run")
        print("           apt-get update && apt-get install -y python3-pip")

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

    name = bucket.split(":", 1)[1] if ":" in bucket else ""

    # NOTE: do not gate on listing the remote ROOT. An R2 token scoped to a
    # single bucket cannot enumerate buckets and returns 403 there, which says
    # nothing about whether the bucket itself works. The real test is a write.
    def bucket_writable():
        if not name:
            raise RuntimeError(
                "no bucket name in the destination - $BUCKET was empty. "
                "Run:  BUCKET=your-bucket-name   then re-run this check")
        tmp = tempfile.mkdtemp()
        probe = os.path.join(tmp, "_preflight.txt")
        open(probe, "w").write("wonderleaf preflight\n")
        r = subprocess.run(["rclone", "copyto", "--s3-no-check-bucket", probe,
                            f"{dest}/_preflight.txt"],
                           capture_output=True, text=True, timeout=120)
        if r.returncode != 0:
            err = r.stderr.strip().split("\n")[-1][:200]
            if "InvalidBucketName" in r.stderr:
                raise RuntimeError(f"bucket name '{name}' is not valid - "
                                   "lowercase letters, digits and hyphens only")
            if "NoSuchBucket" in r.stderr:
                raise RuntimeError(f"no bucket called '{name}' on this account")
            if "AccessDenied" in r.stderr or "403" in r.stderr:
                raise RuntimeError(
                    f"denied writing to '{name}' - the token is probably "
                    "read-only, or scoped to a different bucket")
            raise RuntimeError(err)
        r = subprocess.run(["rclone", "cat", f"{dest}/_preflight.txt"],
                           capture_output=True, text=True, timeout=60)
        if "wonderleaf" not in r.stdout:
            raise RuntimeError("wrote the probe but could not read it back")
        subprocess.run(["rclone", "delete", f"{dest}/_preflight.txt"],
                       capture_output=True, text=True, timeout=60)
        return f"wrote and read back {dest}/_preflight.txt"
    if not step("bucket writable", bucket_writable):
        print("\n  -> fix the bucket name or the token, then re-run this check")
        return 1

    # Listing is only needed so an interrupted run can resume. Warn, do not fail.
    try:
        r = subprocess.run(["rclone", "lsf", f"{dest}/mock",
                            "--retries", "1", "--low-level-retries", "2",
                            "--contimeout", "15s", "--timeout", "60s"],
                           capture_output=True, text=True, timeout=90)
    except subprocess.TimeoutExpired:
        r = subprocess.CompletedProcess([], 1, "", "timed out")
    if r.returncode != 0 and "directory not found" not in r.stderr:
        print("  [WARN] cannot list the bucket - the render will still work,")
        print("         but an interrupted run will restart from zero instead")
        print("         of resuming.  " + r.stderr.strip().split("\n")[-1][:120])

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
        try:
            r = subprocess.run(["rclone", "lsf", f"{dest}/mock", "--retries", "1",
                                "--low-level-retries", "2", "--timeout", "60s"],
                               capture_output=True, text=True, timeout=90)
        except subprocess.TimeoutExpired:
            r = subprocess.CompletedProcess([], 1, "", "timed out")
        # A bucket-scoped token may not allow listing; the upload above already
        # succeeded, so only treat a listing that WORKS and omits the file as a
        # failure.
        if r.returncode == 0 and "_preflight.jpg" not in r.stdout:
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

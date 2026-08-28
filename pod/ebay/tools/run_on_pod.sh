#!/usr/bin/env bash
# Render the t-shirt catalogue on a RunPod CPU box.
#
# NO GPU NEEDED. These designs are typography on black - the whole catalogue
# renders on CPU. Rent the cheapest high-core CPU pod, not a 4090.
#
#   catalogue.json  ->  <id>.png   4500x5400 transparent   (print file, DTF)
#                   ->  <id>.jpg   2000x2000               (eBay listing image)
#
# Both land in R2 under the existing layout, and the local copies are deleted
# once uploaded so a 200GB render fits on a 100GB disk.
#
# Usage on the pod:
#   export R2_BUCKET=tshirt-xxx
#   bash run_on_pod.sh catalogue.json 32
set -euo pipefail

CATALOGUE="${1:?usage: run_on_pod.sh catalogue.json [workers]}"
WORKERS="${2:-$(nproc)}"
OUT_ART="${OUT_ART:-/workspace/art}"
OUT_MOCK="${OUT_MOCK:-/workspace/mock}"
R2_BUCKET="${R2_BUCKET:?set R2_BUCKET}"
UPLOADED="/workspace/.uploaded.txt"

mkdir -p "$OUT_ART" "$OUT_MOCK"
touch "$UPLOADED"

echo "== deps =="
pip install --quiet Pillow numpy scipy

echo "== fonts (SIL Open Font Licence - commercial use permitted) =="
mkdir -p fonts && cd fonts
BASE="https://raw.githubusercontent.com/google/fonts/main"
for f in ofl/anton/Anton-Regular.ttf ofl/bebasneue/BebasNeue-Regular.ttf \
         "ofl/oswald/Oswald%5Bwght%5D.ttf" ofl/archivoblack/ArchivoBlack-Regular.ttf \
         ofl/alfaslabone/AlfaSlabOne-Regular.ttf ofl/staatliches/Staatliches-Regular.ttf; do
  n=$(basename "$f" | sed 's/%5B.*%5D//')
  [ -f "$n" ] || curl -sS -L "$BASE/$f" -o "$n"
done
cd ..

echo "== render + mockup, $WORKERS workers =="
python3 - "$CATALOGUE" "$WORKERS" "$OUT_ART" "$OUT_MOCK" <<'PYEOF'
import json, os, sys, multiprocessing as mp
sys.path.insert(0, "."); sys.path.insert(0, "./generate")
import render_designs as rd
import photo_mockup as pm

cat, workers, out_art, out_mock = sys.argv[1], int(sys.argv[2]), sys.argv[3], sys.argv[4]
designs = json.loads(open(cat).read())

def one(d):
    p_png = os.path.join(out_art, d["design_id"] + ".png")
    p_jpg = os.path.join(out_mock, d["design_id"] + ".jpg")
    if os.path.exists(p_png) and os.path.exists(p_jpg):
        return 0
    art = rd.render(d, "fonts")
    art.save(p_png, compress_level=6)          # print file, DTF
    pm.build(p_png, p_jpg)                     # eBay listing image
    return 1

if __name__ == "__main__":
    with mp.Pool(workers) as pool:
        for i, _ in enumerate(pool.imap_unordered(one, designs, chunksize=32), 1):
            if i % 2000 == 0:
                print(f"  {i:,}/{len(designs):,}", flush=True)
    print("render complete")
PYEOF

echo "== upload to R2 and free the disk =="
# rclone needs provider=Other and --s3-no-check-bucket, per SPEC section 7
find "$OUT_ART" -name '*.png' | xargs -P 16 -I{} sh -c '
  rclone copyto --s3-no-check-bucket "$1" "r2:'"$R2_BUCKET"'/art/raw/$(basename "$1")" -q && rm -f "$1"' _ {}
find "$OUT_MOCK" -name '*.jpg' | xargs -P 16 -I{} sh -c '
  rclone copyto --s3-no-check-bucket "$1" "r2:'"$R2_BUCKET"'/art/mock/$(basename "$1")" -q && rm -f "$1"' _ {}

echo "done. Point build_tee_csv.py --img-base at r2:$R2_BUCKET/art/mock"

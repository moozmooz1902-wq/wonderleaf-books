#!/usr/bin/env bash
# One command on a CPU pod: build the 2.5M wall-art designs, render and upload
# every picture to the four R2 buckets, then build the eBay upload files with
# the real picture URLs and put them in each bucket under ebay-upload/.
#
# Needs these environment variables on the pod (never commit them):
#   R2_ACCOUNT_ID  R2_ACCESS_KEY_ID  R2_SECRET_ACCESS_KEY      (R2 API token, read+write)
# and EITHER a Cloudflare API token so the public picture URLs are found for you:
#   CF_API_TOKEN
# OR the four public URLs (Cloudflare -> R2 -> bucket -> Settings -> Public access):
#   PIC_BASE_LUXVIA_ART  PIC_BASE_MERCURY_USM  PIC_BASE_LUNAR_KMS  PIC_BASE_POSTERLEAF_STORE1
#
#   git clone -b claude/hopeful-rubin-u14pgu https://github.com/moozmooz1902-wq/wonderleaf-books
#   cd wonderleaf-books/wallart && bash pod/run_wallart.sh
#
# Safe to stop and re-run: anything already uploaded is skipped.
set -euo pipefail
cd "$(dirname "$0")/.."
: "${R2_ACCOUNT_ID:?set R2_ACCOUNT_ID}" "${R2_ACCESS_KEY_ID:?set R2_ACCESS_KEY_ID}" "${R2_SECRET_ACCESS_KEY:?set R2_SECRET_ACCESS_KEY}"

WORKERS="${WORKERS:-$(nproc)}"
echo "== 1/6 install"
python3 -m pip install -q pillow boto3

echo "== 2/6 fonts, scripture, map data"
python3 fetch_assets.py

echo "== 3/6 designs (same SKUs as the reviewed catalogue)"
if [ ! -f out/luxvia-art.csv.gz ]; then python3 generate.py; fi
python3 visual_bank.py                     # educational charts + maps
python3 images_bank.py                     # the AI image listings (pictures come from pod/gen_ai.sh)
python3 pd_bank.py                         # public-domain museum art
python3 pod/verify_catalogue.py            # stops here if anything differs from the reviewed build

echo "== 4/6 listing photos (black frame) -> R2   ($WORKERS workers)"
python3 r2_urls.py
i=0
for b in luxvia-art mercury-usm lunar-kms posterleaf-store1; do
  i=$((i+1))
  for f in "out/$b.csv.gz" "out/${b}_visual.csv.gz"; do
    [ -f "$f" ] && python3 publish.py --store "$i" --bucket "$b" --csv "$f" --workers "$WORKERS" --mock-only
  done
done
python3 r2_urls.py --test                 # a real uploaded picture must load from each public URL

echo "== 4b/6 public-domain museum art: download, frame, upload (network bound, ~150k images)"
python3 -m pip install -q requests numpy
python3 pod/fetch_pd.py --all --workers 48

echo "== 5/6 eBay upload files (typography, charts, maps, museum art) -> each bucket's ebay-upload/ folder"
python3 build_ebay.py --source text --source visual --source pd --only-uploaded
python3 build_ebay.py --check
python3 pod/upload_ebay_files.py
echo "eBay files ready: Cloudflare -> R2 -> <bucket> -> ebay-upload/. You can start uploading now."
echo "(The AI animal listings get their own eBay files from pod/gen_ai.sh on the GPU pod.)"

echo "== 6/6 flat print files, A4 at 300dpi -> R2 (art/raw/); upscale for A3/A2 as usual"
i=0
for b in luxvia-art mercury-usm lunar-kms posterleaf-store1; do
  i=$((i+1))
  for f in "out/$b.csv.gz" "out/${b}_visual.csv.gz"; do
    [ -f "$f" ] && python3 publish.py --store "$i" --bucket "$b" --csv "$f" --workers "$WORKERS" --raw-only --print-size A4
  done
done
echo "ALL DONE."

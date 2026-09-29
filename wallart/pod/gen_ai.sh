#!/usr/bin/env bash
# GPU pod: make the AI animal / botanical pictures, upload them to the four R2
# buckets, then build and upload their eBay files.
#
# Pod: any NVIDIA GPU with 24 GB+ (A100 80GB / H100 fastest; RTX 4090 works, slower).
# Same environment variables as run_wallart.sh:
#   R2_ACCOUNT_ID  R2_ACCESS_KEY_ID  R2_SECRET_ACCESS_KEY  and  CF_API_TOKEN (or the PIC_BASE_* URLs)
# Several GPUs or pods? give each one a share:  PART=1/4 bash pod/gen_ai.sh , PART=2/4 ... on the others.
#
#   git clone -b claude/hopeful-rubin-u14pgu https://github.com/moozmooz1902-wq/wonderleaf-books
#   cd wonderleaf-books/wallart && bash pod/gen_ai.sh
set -euo pipefail
cd "$(dirname "$0")/.."
: "${R2_ACCOUNT_ID:?set R2_ACCOUNT_ID}" "${R2_ACCESS_KEY_ID:?set R2_ACCESS_KEY_ID}" "${R2_SECRET_ACCESS_KEY:?set R2_SECRET_ACCESS_KEY}"
PART="${PART:-1/1}"

echo "== 1/5 install (PyTorch comes with the RunPod PyTorch template)"
python3 -m pip install -q pillow boto3 numpy scipy "diffusers>=0.30" transformers accelerate sentencepiece protobuf

echo "== 2/5 fonts, dictionary text"
python3 fetch_assets.py

echo "== 3/5 AI image listings (same SKUs as the reviewed catalogue)"
python3 images_bank.py
python3 pod/verify_catalogue.py _ai

echo "== 4/5 a test batch first: 8 images, check them in Cloudflare before the big run"
python3 r2_urls.py
python3 pod/gen_ai.py --all --limit 8 --part "$PART"
echo "Test images are in each bucket under art/mock/. Starting the full run in 30 s (Ctrl-C to stop)."
sleep 30
python3 pod/gen_ai.py --all --part "$PART"

echo "== 5/5 eBay files for the AI listings whose pictures are uploaded"
python3 build_ebay.py --source ai --only-uploaded
python3 build_ebay.py --check
python3 pod/upload_ebay_files.py
echo "ALL DONE. Files: Cloudflare -> R2 -> <bucket> -> ebay-upload/<bucket>_ai_*.csv"

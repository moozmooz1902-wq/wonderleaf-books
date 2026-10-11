#!/bin/bash
# Launch one shard, community first, secure as fallback. Community is 2.2x
# cheaper per image but regularly answers "no instances currently available",
# so a run that insists on it simply does not start.
N=$1; K=$2
GPUS="NVIDIA RTX A4500,NVIDIA RTX A5000,NVIDIA GeForce RTX 3090,NVIDIA GeForce RTX 4090,NVIDIA L4,NVIDIA RTX 4000 Ada Generation,NVIDIA A40,NVIDIA RTX A6000,NVIDIA L40S"
EXTRA="--batch 4 --width 704 --height 1008 --quant nf4 --retries 2 --part $K/$N --stores stores.json --resume --max-hours 10"
for CLOUD in COMMUNITY SECURE; do
  OUT=$(python3 launch_gen.py --name "wa-v3-$K" --cloud $CLOUD --gpu "$GPUS" --template vbsgwyibn1 \
    --image "runpod/pytorch:2.8.0-py3.11-cuda12.8.1-cudnn-devel-ubuntu22.04" \
    --pip "diffusers transformers accelerate bitsandbytes sentencepiece protobuf hf_transfer easyocr boto3" \
    --script gen_gated.py --jobs gen/subjects.json --ship gen/gen_gated.py --extra "$EXTRA" 2>&1)
  ID=$(printf '%s' "$OUT" | python3 -c "import sys,re;d=sys.stdin.read();m=re.search(r'\"id\": \"([a-z0-9]+)\"',d);print(m.group(1) if m else '')")
  CST=$(printf '%s' "$OUT" | python3 -c "import sys,re;d=sys.stdin.read();m=re.search(r'\"costPerHr\": ([0-9.]+)',d);print(m.group(1) if m else '')")
  if [ -n "$ID" ]; then echo "shard $K/$N  $ID  \$$CST  $CLOUD"; exit 0; fi
done
echo "shard $K/$N  NO CAPACITY"

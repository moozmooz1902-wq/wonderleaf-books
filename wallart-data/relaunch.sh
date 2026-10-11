#!/bin/bash
# Launch one shard, community first, secure as fallback. Community is 2.2x
# cheaper per image but regularly answers "no instances currently available",
# so a run that insists on it simply does not start.
N=$1; K=$2
# Card choice is not about speed, it is about which community hosts have a
# working CUDA runtime. Measured over 16 community pods on 11 Oct:
#     RTX A4500  4/4 worked        RTX 3090  2/2 worked
#     RTX 4090   0/7 CUDA_DEAD     L40S      0/3 CUDA_DEAD
# nvidia-smi answers fine on the dead ones and every /dev/nvidia* node is
# present; torch still cannot init. So 4090 and L40S are excluded from
# community entirely - they bill while producing nothing.
# Two tiers. TIER1 is the four cards proven to init CUDA on community
# hosts. Community capacity on those four is thin - ten shards asked on
# 11 Oct returned eight NO CAPACITY - so TIER2 adds cards that have never
# been tried but are big enough for NF4 (16.1 GB peak) and priced near the
# A4500. An unproven host that cannot init CUDA, or sits behind a
# TLS-intercepting middlebox, now says so and exits in under four minutes,
# which costs about two cents, so trying one is cheaper than idling a shard.
TIER1="NVIDIA RTX A4500,NVIDIA RTX A5000,NVIDIA GeForce RTX 3090,NVIDIA RTX A4000"
TIER2="NVIDIA RTX 4000 Ada Generation,NVIDIA A30,NVIDIA RTX 5000 Ada Generation,NVIDIA L4"
# Hard price ceiling. The A4500 shards run at $0.17-0.19/hr and the whole
# budget is built on that; a card at triple the hourly rate is not three
# times faster, so anything over this is handed back immediately rather
# than quietly tripling the bill. Dollars per image, never dollars per hour,
# is what decides a card - this ceiling just stops an accident.
MAXHR=0.32
# --pool 960000: status.py puts the GPU requirement at 937,500 base images
# (5,000,000 listings, less the 1,250,000 drawn in code, over four
# colourways). The grid is 1,195,035, so the pool takes the first
# 960,000 of it - the target plus 2.4% - and the remaining 235,000 jobs
# stay as spare capacity that a later run can switch on by raising this
# number alone, with nothing regenerated.
EXTRA="--batch 4 --width 704 --height 1008 --quant nf4 --retries 2 --pool 960000 --part $K/$N --stores stores.json --resume --max-hours 10"
for GPUS in "$TIER1" "$TIER2"; do
  CLOUD=COMMUNITY
  OUT=$(python3 launch_gen.py --name "wa-v3-$K" --cloud $CLOUD --gpu "$GPUS" --template vbsgwyibn1 \
    --image "runpod/pytorch:2.8.0-py3.11-cuda12.8.1-cudnn-devel-ubuntu22.04" \
    --pip "diffusers transformers accelerate bitsandbytes sentencepiece protobuf hf_transfer easyocr boto3" \
    --script gen_gated.py --jobs gen/subjects.json --ship gen/gen_gated.py --extra "$EXTRA" 2>&1)
  ID=$(printf '%s' "$OUT" | python3 -c "import sys,re;d=sys.stdin.read();m=re.search(r'\"id\": \"([a-z0-9]+)\"',d);print(m.group(1) if m else '')")
  CST=$(printf '%s' "$OUT" | python3 -c "import sys,re;d=sys.stdin.read();m=re.search(r'\"costPerHr\": ([0-9.]+)',d);print(m.group(1) if m else '')")
  if [ -n "$ID" ]; then
    if [ -n "$CST" ] && [ "$(python3 -c "print(1 if $CST > $MAXHR else 0)")" = "1" ]; then
      curl -sS -X DELETE "https://rest.runpod.io/v1/pods/$ID" >/dev/null
      echo "shard $K/$N  $ID  \$$CST  OVER CEILING $MAXHR - terminated"
      continue
    fi
    echo "shard $K/$N  $ID  \$$CST  $CLOUD"; exit 0
  fi
done
echo "shard $K/$N  NO CAPACITY"

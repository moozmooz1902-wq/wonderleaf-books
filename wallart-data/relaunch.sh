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
# "NVIDIA A30" is NOT a valid gpuTypeId. One invalid name does not get
# skipped: the whole create is rejected with a schema validation error,
# which comes back as a bare LIST rather than an object, so the launcher
# found no id in it and this script printed NO CAPACITY. Five shards sat
# idle for that reason while RTX 4000 Ada was available at $0.20 the
# whole time. Probed one name at a time, 11 Oct: RTX 4000 Ada valid and
# available, RTX 5000 Ada and L4 valid but no instances, A30 not a name.
TIER2="NVIDIA RTX 4000 Ada Generation,NVIDIA RTX 5000 Ada Generation,NVIDIA L4"
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
# subjects.json is fetched by the pod, not carried in its start command:
# at 5,204 subjects it is 90 KB, and the command has a hard limit between
# 60k and 70k characters. seed_assets.py puts it here; re-run that after
# any change to the subject lists or the pods will build the OLD grid.
JOBS_URL="https://pub-4b710c8610a84acc8fad1513f48132fd.r2.dev/wallart/assets/subjects.json"
# PIN diffusers AND transformers. This list was unpinned until 15 Oct and a
# release on PyPI stopped the fleet mid-run: transformers 5.20.0 was uploaded
# at 18:01:01 UTC that day, wa-v3-9 rotated at 18:29 and every pod launched
# after that died before generating anything -
#   ModuleNotFoundError: No module named 'torch.distributed.checkpoint.hf_storage'
# raised under "from diffusers import FluxPipeline", because 5.20.0 imports a
# torch.distributed path this image's torch 2.8.0.dev20250319 does not have.
# Four pods were created and killed in ten minutes before it was read.
#
# The shape of this matters more than the version. Nothing was wrong with the
# repo, the card or the account: an unpinned dependency changed under a run
# that was already going, so the eleven shards launched before 18:01 kept
# working on 5.19.0 while every new one failed - which looks exactly like one
# bad shard until the log is read. An unpinned install means the fleet can
# only be relaunched for as long as upstream does not publish.
#
# 5.19.0 is not a guess: the eleven shards producing at the time were launched
# between 06:33 and 17:39, all of them after 5.19.0 went up on 6 Oct and all
# before 5.20.0, so it is the version the working fleet is measured on.
# diffusers is pinned to the 0.41.0 those same pods report for the same reason.
# The rest of the list is left unpinned because no version of it is known to
# be good; pin each one the same way the first time it breaks.
# CLIP_GATE=0 in the environment turns the people/eyes gate off for every
# shard this script launches. Added 12 Oct when three shards relaunched
# with it came up rejecting 100% of panels while the nine older ones
# stayed at 8-10%; the switch is here so the fleet can keep running at
# the known-good behaviour while that is diagnosed, rather than having
# to choose between a broken gate and no shards.
CLIP="${CLIP_GATE:-1}"
# CLEAN_AT_END=1 in the environment moves the no-text clause to the end of
# the prompt, outside CLIP's 77-token window, for THIS shard only. It is how
# the A/B is run: one shard carries it, fill_shards.sh launches the other
# eleven without it, and the marginal text-reject rates are compared. Never
# set it in fill_shards.sh - a change every shard carries has no control.
CLEAN=""
[ "${CLEAN_AT_END:-0}" = "1" ] && CLEAN=" --clean-at-end"
# STAGGER THE EXPIRY. Every shard ran --max-hours 10, so shards started
# together expired together: ten of the twelve rotated inside fifteen
# minutes at 12:30 on 13 Oct, and the fleet produced 4,044 panels that hour
# against the usual 7,000 while ten pods all downloaded FLUX and worked
# through their retry backlogs at once. The pods were never idle and nothing
# was lost - it is just that the warm-up is paid ten times over in one hour
# instead of spread across ten.
#
# 9.15 to 10.80 hours by shard number spreads the next rotation over about
# an hour and three quarters, and they drift further apart with each cycle
# rather than reconverging.
MAXH=$(python3 -c "print(round(9.0 + $K * 0.15, 2))")
EXTRA="--batch 4 --width 704 --height 1008 --quant nf4 --retries 2 --pool 960000 --part $K/$N --stores stores.json --resume --clip-gate $CLIP --max-hours $MAXH$CLEAN"
for GPUS in "$TIER1" "$TIER2"; do
  CLOUD=COMMUNITY
  OUT=$(python3 launch_gen.py --name "wa-v3-$K" --cloud $CLOUD --gpu "$GPUS" --template vbsgwyibn1 \
    --image "runpod/pytorch:2.8.0-py3.11-cuda12.8.1-cudnn-devel-ubuntu22.04" \
    --pip "diffusers==0.41.0 transformers==5.19.0 accelerate bitsandbytes sentencepiece protobuf hf_transfer easyocr boto3" \
    --script gen_gated.py --jobs gen/subjects.json \
    --jobs-url "$JOBS_URL" --ship gen/gen_gated.py --extra "$EXTRA" 2>&1)
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

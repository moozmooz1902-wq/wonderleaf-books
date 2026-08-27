#!/usr/bin/env bash
# setup.sh — one command from a bare pod to generating.
#
#   export R2_KEY=...  R2_SECRET=...  R2_ACCOUNT=...
#   bash setup.sh
#
# Checks the GPUs FIRST, because a pod with broken CUDA is worth two minutes,
# not two hours. One pod enumerated five GPUs but had no /dev/nvidia0, so
# every worker died at startup after the whole install had been done.

set -uo pipefail
cd /workspace || exit 1

BUCKET="${R2_BUCKET:-r2:tshirt-mockups/art}"
GEN_TOTAL="${GEN_TOTAL:-423000}"

say() { printf '\n=== %s ===\n' "$1"; }

# ---------------------------------------------------------------- GPU first
say "1/6  GPU check"
if ! command -v nvidia-smi >/dev/null; then
    echo "  nvidia-smi missing — this pod has no GPU support. Terminate it."
    exit 1
fi
GPUS=$(nvidia-smi --list-gpus | wc -l)
echo "  nvidia-smi sees $GPUS GPU(s)"

if [ ! -e /dev/nvidia0 ]; then
    echo
    echo "  /dev/nvidia0 IS MISSING."
    echo "  CUDA needs it and the host has not created it. Trying to fix..."
    nvidia-modprobe -c=0 -u 2>/dev/null
    sleep 2
fi

if [ ! -e /dev/nvidia0 ]; then
    echo
    echo "  STILL MISSING. This host is faulty — nothing installed here will"
    echo "  work. TERMINATE this pod and deploy another. Do not continue."
    exit 1
fi
echo "  /dev/nvidia0 present"

if python3 -c "import torch" 2>/dev/null; then
    if ! python3 -c "import torch,sys; sys.exit(0 if torch.cuda.is_available() else 1)" 2>/dev/null; then
        echo
        echo "  torch cannot initialise CUDA on this host. TERMINATE and"
        echo "  deploy another pod. Two minutes lost, not two hours."
        exit 1
    fi
    echo "  torch can reach CUDA"
fi

# ---------------------------------------------------------------- packages
say "2/6  python packages"
if [ ! -d venv ]; then
    python3 -m venv venv --system-site-packages
fi
# shellcheck disable=SC1091
source venv/bin/activate
export HF_HOME=/workspace/hf_cache
pip install -q -U pip
pip install -q diffusers==0.31.0 transformers==4.45.2 accelerate==1.0.1 \
    "safetensors>=0.4.3" sentencepiece protobuf huggingface_hub scipy
echo "  done"

# ---------------------------------------------------------------- rclone
say "3/6  rclone"
if ! command -v rclone >/dev/null; then
    apt-get update -qq >/dev/null 2>&1
    apt-get install -y -qq unzip >/dev/null 2>&1
    curl -s https://rclone.org/install.sh | bash >/dev/null 2>&1
fi
rclone version | head -1

if [ -n "${R2_KEY:-}" ] && [ -n "${R2_SECRET:-}" ] && [ -n "${R2_ACCOUNT:-}" ]; then
    rclone config create r2 s3 >/dev/null
    rclone config update r2 provider Other >/dev/null
    rclone config update r2 access_key_id "$R2_KEY" >/dev/null
    rclone config update r2 secret_access_key "$R2_SECRET" >/dev/null
    rclone config update r2 endpoint \
        "https://${R2_ACCOUNT}.r2.cloudflarestorage.com" >/dev/null
    rclone config update r2 acl "" >/dev/null
    rclone config update r2 no_check_bucket true >/dev/null
    echo "  configured from environment"
else
    echo "  R2_KEY / R2_SECRET / R2_ACCOUNT not set — configure rclone by hand"
fi

if ! rclone lsd "${BUCKET%%/*}" >/dev/null 2>&1; then
    echo "  CANNOT REACH R2. Fix the credentials before going further."
    exit 1
fi
echo "  R2 reachable"

# ---------------------------------------------------------------- state
say "4/6  queue and ledger"
export R2_REMOTE="$BUCKET"
if [ -f generation_queue.csv ] && [ -f used_designs.txt ]; then
    echo "  already present locally"
else
    python state.py restore "$BUCKET" 2>/dev/null
fi

if [ ! -f generation_queue.csv ]; then
    echo
    echo "  No queue in R2 yet. Build one — this is also what protects"
    echo "  against duplicates, so do not skip the ledger step:"
    echo "      python rebuild_ledger.py ${BUCKET}/raw"
    echo "      python pick.py --count ${GEN_TOTAL}"
    echo "      python audit.py generation_queue.csv"
    exit 0
fi
echo "  queue: $(($(wc -l < generation_queue.csv) - 1)) designs"
echo "  ledger: $(wc -l < used_designs.txt) used"

# ---------------------------------------------------------------- verify
say "5/6  pre-flight"
python verify.py 2>/dev/null | tail -2

# ---------------------------------------------------------------- ready
say "6/6  ready"
PER=$(( GEN_TOTAL / (GPUS * 2) ))
cat <<TXT

  This pod has $GPUS GPUs. Launch with the slice for THIS pod —
  the second pod must use different tags or they overwrite each other.

  POD A:
    M="Lykon/dreamshaper-xl-1-0"
    for i in \$(seq 0 $((GPUS-1))); do
      CUDA_VISIBLE_DEVICES=\$i nohup ./venv/bin/python pod_sdxl.py \\
        --model \$M --hires 0 \\
        --start \$((i*$PER)) --limit $PER --tag w\$i > w\$i.log 2>&1 &
    done
    nohup ./venv/bin/python watchdog.py \$R2_REMOTE > watchdog.log 2>&1 &

  POD B: same but  j=\$((i+$GPUS))  and  --start \$((j*$PER)) --tag w\$j

TXT

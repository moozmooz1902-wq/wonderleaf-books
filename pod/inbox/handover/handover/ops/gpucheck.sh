#!/usr/bin/env bash
# gpucheck.sh — is this pod worth setting up?
#
# THE TEST THAT DECIDES IS AN ACTUAL ALLOCATION ON EVERY GPU.
#
# An earlier version failed a pod when /dev/nvidia0 was missing. That was
# right once — a genuinely broken host — but wrong as a rule: device nodes
# are not always numbered from zero, and a pod can be perfectly healthy with
# different numbering. Pods were terminated that would have worked fine.
#
# So the node listing below is INFORMATION ONLY. The verdict comes from
# torch: allocate a tensor on each device and see if it works.

echo "GPU CHECK"
echo

if ! command -v nvidia-smi >/dev/null; then
    echo "  no nvidia-smi — TERMINATE, this pod has no GPU support"
    exit 1
fi

N=$(nvidia-smi --list-gpus | wc -l)
echo "  GPUs reported : $N"
echo "  device nodes  : $(ls /dev/nvidia[0-9]* 2>/dev/null | tr '\n' ' ')"
echo "                  (numbering does not matter — the real test follows)"
echo

PY=""
for c in ./venv/bin/python python3; do
    command -v "$c" >/dev/null 2>&1 && { PY="$c"; break; }
done
if [ -z "$PY" ]; then
    echo "  no python yet — cannot run the real test."
    echo "  Install first, then re-run this before launching."
    exit 0
fi

$PY - "$N" <<'PYEOF'
import sys
try:
    import torch
except ImportError:
    print("  torch not installed yet — install, then re-run this")
    sys.exit(0)

want = int(sys.argv[1])
print(f"  torch         : {torch.__version__}")
print(f"  cuda.is_available: {torch.cuda.is_available()}")
print(f"  device_count  : {torch.cuda.device_count()}")
print()

if not torch.cuda.is_available():
    print("  CUDA WILL NOT INITIALISE — TERMINATE and deploy another.")
    sys.exit(1)

bad = []
for i in range(torch.cuda.device_count()):
    try:
        t = torch.zeros(256, 256, device=f"cuda:{i}")
        t = t + 1
        torch.cuda.synchronize(i)
        free, total = torch.cuda.mem_get_info(i)
        print(f"    cuda:{i}  OK   {total/1e9:.0f} GB, {free/1e9:.0f} free"
              f"   {torch.cuda.get_device_name(i)}")
        del t
    except Exception as e:
        bad.append(i)
        print(f"    cuda:{i}  FAILED  {str(e)[:60]}")

torch.cuda.empty_cache()
print()

if bad:
    print(f"  {len(bad)} GPU(s) cannot be used — TERMINATE and deploy another.")
    sys.exit(1)

if torch.cuda.device_count() < want:
    print(f"  nvidia-smi reports {want} but torch can only use "
          f"{torch.cuda.device_count()}.")
    print("  Launch with the lower number, or terminate and redeploy.")
    sys.exit(1)

print(f"  GOOD POD — all {torch.cuda.device_count()} GPUs allocate and compute.")
print("  Safe to set up.")
PYEOF

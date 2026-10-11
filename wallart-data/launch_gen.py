#!/usr/bin/env python3
"""Create a FLUX generation pod on RunPod and hand it the gen/ bundle.

Two things learned the hard way, both encoded here:

  * Use a runpod/* image, not pytorch/* from Docker Hub. The first attempt
    used pytorch/pytorch:2.4.1-cuda12.1 and the container had still not
    started 22 minutes in - community hosts cache RunPod's own images and
    nothing else, so a 3.6 GB Docker Hub pull happens over the public net.
  * `bash -c`, never `bash -lc`. A login shell re-reads /etc/profile, which
    resets PATH and drops /opt/conda/bin, and then nothing runs at all.

The gen/ directory is shipped inside the start command as a base64 tarball,
because there is no other channel to a fresh pod - no SSH key is held here.

    python3 launch_gen.py --jobs gen/jobs_sample.json --name wallart-sample
"""
import argparse, base64, io, json, os, subprocess, tarfile, sys

API = "https://rest.runpod.io/v1"
IMAGE = "runpod/pytorch:2.4.0-py3.11-cuda12.4.1-devel-ubuntu22.04"
# torch 2.6+ image, needed for diffusers>=0.33 and its bitsandbytes
# PipelineQuantizationConfig, which is how a 24 GB card gets to hold FLUX.
IMAGE_NEW = "runpod/pytorch:2.8.0-py3.11-cuda12.8.1-cudnn-devel-ubuntu22.04"


def curl(method, path, body=None):
    cmd = ["curl", "-sS", "--max-time", "90", "-X", method, f"{API}{path}"]
    if body is not None:
        cmd += ["-H", "Content-Type: application/json", "-d", json.dumps(body)]
    out = subprocess.run(cmd, capture_output=True, text=True).stdout
    try:
        return json.loads(out)
    except Exception:
        return {"_raw": out[:800]}


def bundle(files):
    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode="w:gz") as t:
        for f in files:
            t.add(f, arcname=os.path.basename(f))
    return base64.b64encode(buf.getvalue()).decode()


def start_cmd(b64, jobs, extra, pip=None, script="gen_worker.py"):
    """Run the job ALONGSIDE the image's own /start.sh, never instead of it.

    This is the bug that cost 40 minutes. Overriding dockerStartCmd replaces
    the RunPod image's entrypoint, which is what starts their in-container
    agent. Without the agent the pod never reports a runtime, so `GET /pods`
    shows `runtime: null` for ever and the HTTP proxy has no route to forward
    to - every request to the pod's port 8000 came back 404 from the proxy
    even though the pod said RUNNING. Two pods on two different machines and
    two different clouds behaved identically, which is what gave it away.
    """
    pip = pip or ("'diffusers==0.31.0' 'transformers==4.46.3' 'accelerate==1.1.1' "
                  "'huggingface_hub==0.26.2' sentencepiece protobuf hf_transfer")
    flag = "--subjects" if jobs.endswith("subjects.json") else "--jobs"
    script_line = (f"python3 {script} {flag} {os.path.basename(jobs)} "
                   f"--out /workspace/art {extra}") if jobs else f"python3 {script} {extra}"
    return ["bash", "-c", f"""export PATH=/opt/conda/bin:/usr/local/bin:/usr/bin:/bin:$PATH
mkdir -p /workspace/gen /workspace/art
echo '{b64}' | base64 -d | tar xz -C /workspace/gen
cat > /workspace/run.sh <<'EOS'
export PATH=/opt/conda/bin:/usr/local/bin:/usr/bin:/bin:$PATH
export HF_HUB_ENABLE_HF_TRANSFER=1
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
set -x
( while true; do python3 -m http.server 8000 --directory /workspace >> /workspace/http.log 2>&1; sleep 3; done ) &
nvidia-smi 2>&1 | head -12
ls -l /dev/nvidia* 2>&1 | head
echo "NVIDIA_VISIBLE_DEVICES=$NVIDIA_VISIBLE_DEVICES CUDA_VISIBLE_DEVICES=$CUDA_VISIBLE_DEVICES"
# Wait for the GPU to be usable, not merely present. nvidia-smi answered
# straight away on the last pod while torch still said "CUDA unknown error -
# setting the available devices to be zero", because /dev/nvidia-uvm is
# created later than /dev/nvidia0 and the CUDA runtime needs it. Our run.sh
# starts in parallel with the image's /start.sh, so it can win that race.
# nvidia-modprobe creates the node if it is missing and we are allowed to.
for i in $(seq 1 40); do
  if python3 -c "import torch,sys; sys.exit(0 if torch.cuda.is_available() else 1)" 2>/dev/null; then
    echo "GPU READY after ${{i}} tries"; break
  fi
  [ $i -eq 1 ] && python3 -c "import torch;torch.cuda.init()" 2>&1 | tail -3
  nvidia-modprobe -u -c=0 2>/dev/null
  sleep 5
done
# Say so loudly rather than carrying on. Two community hosts answered
# nvidia-smi correctly and still never gave torch a usable device; without
# this the pod goes on to spend five minutes downloading 24 GB of weights
# before failing, and the watcher cannot tell that apart from a slow start.
python3 -c "import torch,sys; sys.exit(0 if torch.cuda.is_available() else 1)" 2>/dev/null \
  || {{ echo CUDA_DEAD_ON_THIS_HOST; exit 1; }}
# Pinned, because the unpinned install broke twice:
#   diffusers >=0.33 calls torch.accelerator, added in torch 2.6; this image
#   ships torch 2.4.0 and the import dies with AttributeError.
#   transformers 5.x returns BaseModelOutputWithPooling from get_text_features
#   instead of a tensor, which the colour-label pass tripped over earlier.
pip install -q --no-input {pip} 2>&1 | tail -3
python3 -c "import torch,diffusers;print('torch',torch.__version__,'diffusers',diffusers.__version__,'cuda',torch.cuda.is_available())"
cd /workspace/gen
{script_line}
echo GEN_DONE
EOS
nohup bash /workspace/run.sh > /workspace/boot.log 2>&1 &
if [ -x /start.sh ]; then exec /start.sh; else sleep infinity; fi
"""]


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--jobs", default="")
    ap.add_argument("--name", default="wonderleaf-wallart-gen")
    # 24 GB is not enough. The FLUX transformer alone is 11.9B parameters =
    # 23.8 GB in bfloat16, so a 4090 OOMs during the first attention block
    # even with model_cpu_offload. 48 GB cards hold the whole pipeline.
    # Several are listed so RunPod can take whichever has capacity.
    ap.add_argument("--gpu", default="NVIDIA L40S,NVIDIA RTX A6000,NVIDIA A40,"
                                     "NVIDIA L40,NVIDIA A100 80GB PCIe")
    ap.add_argument("--extra", default="--batch 4")
    ap.add_argument("--cloud", default="COMMUNITY", choices=["COMMUNITY","SECURE"])
    ap.add_argument("--image", default=IMAGE)
    ap.add_argument("--pip", default="")
    ap.add_argument("--script", default="gen_worker.py")
    ap.add_argument("--ship", default="")   # extra files for the bundle
    ap.add_argument("--template", default="")
    a = ap.parse_args()

    files = ["gen/gen_worker.py", "gen/prompts.py"] + \
            [f for f in ([a.jobs] + a.ship.split(",")) if f]
    b64 = bundle(files)
    body = {"name": a.name, "imageName": a.image,
            # templateId carries the R2_* credentials the seller put on
            # RunPod. The pod inherits them; this session never holds them.
            **({"templateId": a.template} if a.template else {}), "gpuTypeIds": [g.strip() for g in a.gpu.split(",")],
            "gpuCount": 1, "cloudType": a.cloud,
            "containerDiskInGb": 80, "volumeInGb": 0,
            "ports": ["8000/http"], "dockerStartCmd": start_cmd(b64, a.jobs, a.extra,
                                           a.pip or None, a.script)}
    r = curl("POST", "/pods", body)
    print(json.dumps({k: r.get(k) for k in ("id", "name", "desiredStatus",
                                            "costPerHr", "error", "_raw")}, indent=1))
    if r.get("id"):
        print(f"\nlog:    https://{r['id']}-8000.proxy.runpod.net/boot.log")
        print(f"images: https://{r['id']}-8000.proxy.runpod.net/art/")

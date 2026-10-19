#!/usr/bin/env python3
"""Start CPU pods that build the listing pictures.

CPU, not GPU: this stage is PIL and JPEG encoding, so a graphics card would
be rented and left idle. Measured locally on a real panel - twelve pictures
(four colourways x three frame colours) in 2.2 s, 1.08 MB, so the whole
catalogue is about 580 core-hours and 1.04 TB.

The code is shipped inside the start command as a base64 tarball, the way
launch_gen.py does it, because a fresh pod has no other channel - no SSH key
is held here. Credentials are NOT shipped: R2_ACCOUNT_ID, R2_ACCESS_KEY_ID
and R2_SECRET_ACCESS_KEY come from the RunPod template, which is the only
place they exist.

Each pod takes --part k/N of the 72 half-open key ranges and never writes
outside the bucket a range belongs to, so two pods cannot collide and no
store's pictures can land in another store's bucket.

  python3 launch_render.py --parts 12 --name wa-render --max-hours 10
  python3 launch_render.py --parts 12 --only 1        # just one, to prove it
"""
import argparse, base64, io, json, os, subprocess, sys, tarfile

API = "https://rest.runpod.io/v1"
TEMPLATE = "vbsgwyibn1"
IMAGE = "runpod/base:0.7.0-ubuntu2404"
HERE = os.path.dirname(os.path.abspath(__file__))
FILES = ["render/render_worker.py", "layout.py", "recolour.py", "frames.py",
         "art_border.py", "stores.json"]


def curl(method, path, body=None):
    cmd = ["curl", "-sS", "--max-time", "90", "-X", method, f"{API}{path}"]
    if body is not None:
        cmd += ["-H", "Content-Type: application/json", "-d", json.dumps(body)]
    out = subprocess.run(cmd, capture_output=True, text=True).stdout
    try:
        return json.loads(out)
    except Exception:
        return {"_raw": out[:400]}


def bundle(files):
    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode="w:xz") as t:
        for f in files:
            t.add(os.path.join(HERE, f), arcname=os.path.basename(f))
    return base64.b64encode(buf.getvalue()).decode()


def start_cmd(b64, part, hours, procs, extra=""):
    # Runs ALONGSIDE the image's own /start.sh: replacing the entrypoint kills
    # RunPod's in-container agent, and without it the HTTP proxy has no route
    # and every request to port 8000 comes back 404 while the pod says
    # RUNNING. That cost 40 minutes once already (launch_gen.py:82).
    return ["bash", "-c", f"""export PATH=/opt/conda/bin:/usr/local/bin:/usr/bin:/bin:$PATH
mkdir -p /workspace/r
echo '{b64}' | base64 -d | tar xJ -C /workspace/r
cat > /workspace/run.sh <<'EOS'
export PATH=/opt/conda/bin:/usr/local/bin:/usr/bin:/bin:$PATH
set -x
( while true; do python3 -m http.server 8000 --directory /workspace >/dev/null 2>&1; sleep 3; done ) &
python3 -m pip install -q --no-input --break-system-packages boto3 pillow numpy 2>&1 | tail -2
cd /workspace/r
python3 render_worker.py --part {part} --max-hours {hours} --procs {procs} {extra} --stores stores.json
echo RENDER_EXIT
EOS
nohup bash /workspace/run.sh > /workspace/boot.log 2>&1 &
if [ -x /start.sh ]; then exec /start.sh; else sleep infinity; fi
"""]


# CPU first and by a wide margin, but community CPU capacity is as momentary
# as the GPU kind (fill_shards.sh has the measurements), so there are tiers.
TIERS = [{"computeType": "CPU", "cpuFlavorIds": ["cpu3g", "cpu3c"], "vcpuCount": 16},
         {"computeType": "CPU", "cpuFlavorIds": ["cpu3g", "cpu3c"], "vcpuCount": 8},
         {"computeType": "CPU", "cpuFlavorIds": ["cpu5c", "cpu3c"], "vcpuCount": 8},
         {"computeType": "CPU", "cpuFlavorIds": ["cpu3c"], "vcpuCount": 4}]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--parts", type=int, default=12)
    ap.add_argument("--only", type=int, default=0)
    ap.add_argument("--name", default="wa-render")
    ap.add_argument("--max-hours", type=float, default=10.0)
    # The work is not CPU bound, it is NETWORK bound: one GET and twelve PUTs
    # per panel. Measured on a 16-vCPU pod at one process per vCPU: 8,962
    # panels an hour, which is 30 uploads a second - far short of what the
    # cores could encode. Oversubscribing the pool keeps more requests in
    # flight; the cgroup still caps the CPU, so the only real cost is memory,
    # about 150 MB per child.
    ap.add_argument("--oversub", type=int, default=2)
    ap.add_argument("--hash-only", action="store_true",
                    help="run the hash repair instead of rendering")
    a = ap.parse_args()
    b64 = bundle(FILES)
    print(f"bundle {len(b64):,} chars")
    todo = [a.only] if a.only else range(1, a.parts + 1)
    for k in todo:
        for extra in TIERS:
            # --procs is told to the worker rather than guessed inside it: the
            # pod knows how many vCPU it asked for, the container does not.
            common = {"name": f"{a.name}-{k}", "templateId": TEMPLATE,
                      "imageName": IMAGE, "containerDiskInGb": 30,
                      "volumeInGb": 0, "ports": ["8000/http"],
                      "dockerStartCmd": start_cmd(b64, f"{k}/{a.parts}",
                                                  a.max_hours,
                                                  extra["vcpuCount"] * a.oversub,
                                                  "--hash-only" if a.hash_only
                                                  else "")}
            n = sum(len(x) for x in common["dockerStartCmd"])
            if n > 60000:
                sys.exit(f"start command {n:,} chars - over the pod limit")
            r = curl("POST", "/pods", dict(common, **extra))
            if isinstance(r, dict) and r.get("id"):
                print(f"  {a.name}-{k}  {r['id']}  ${r.get('costPerHr')}/hr  "
                      f"{extra.get('vcpuCount')} vCPU")
                break
        else:
            print(f"  {a.name}-{k}  NO CAPACITY")


if __name__ == "__main__":
    main()

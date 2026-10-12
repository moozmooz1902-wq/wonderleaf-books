#!/usr/bin/env python3
"""Measure how often people and bad eyes actually appear in the live catalogue.

quality_gate.py has existed since 11 Oct and was never wired into the
worker, never shipped to a pod, and never given a threshold - so "no human
figures, and no animal with three eyes" has been resting on prompt wording
and on my own eye over a few contact sheets. That is not a gate.

A threshold cannot be chosen without a measurement, and the measurement
cannot happen here (no torch on this machine), so this runs CLIP over a
random sample of what is actually in the four store buckets and brings
back two things:

  scores.json   the full score distribution for both checks
  worst.jpg     the 48 highest-scoring panels for each check, as a sheet

The sheet is what turns scores into a threshold: look at it, see where the
real failures stop and the false alarms begin, and set the number there.
Recall matters more than precision - a bad listing costs more than a
wasted regeneration - which is the rule calibrate() already encodes.

Nothing is written to the store buckets and nothing is deleted.
"""
import json, subprocess, sys

API = "https://rest.runpod.io/v1"
TEMPLATE = "vbsgwyibn1"
SAMPLE = 3000

SCRIPT = r'''
export PATH=/opt/conda/bin:/usr/local/bin:/usr/bin:/bin:$PATH
mkdir -p /workspace
cat > /workspace/run.sh <<'EOS'
export PATH=/opt/conda/bin:/usr/local/bin:/usr/bin:/bin:$PATH
( while true; do python3 -m http.server 8000 --directory /workspace >/dev/null 2>&1; sleep 3; done ) &
set -x
python3 -m pip install -q --no-input --break-system-packages \
  torch torchvision transformers pillow numpy boto3 2>&1 | tail -3
python3 - <<'EOF'
import os, io, json, random, numpy as np, boto3, torch
from concurrent.futures import ThreadPoolExecutor
from botocore.config import Config
from PIL import Image
from transformers import CLIPModel, CLIPProcessor

HUMAN = {"fail": ["a person standing in the scene",
                  "people walking, human figures",
                  "a human face, a portrait of a man or woman",
                  "a crowd of people"],
         "pass": ["an empty landscape with no people in it",
                  "a deserted village with nobody in the street",
                  "an animal on a plain background",
                  "an abstract pattern with no figures",
                  "a plant or flower study"]}
EYES  = {"fail": ["an animal with three eyes",
                  "an animal with deformed melted eyes",
                  "an animal face that is distorted and wrong",
                  "an animal with mismatched uneven eyes",
                  "a malformed animal with extra facial features"],
         "pass": ["an animal with two normal clear eyes",
                  "a clean well drawn animal portrait",
                  "a simple stylised animal illustration",
                  "an animal seen from behind or in profile"]}

s3 = boto3.client("s3",
    endpoint_url=f"https://{os.environ['R2_ACCOUNT_ID']}.r2.cloudflarestorage.com",
    aws_access_key_id=os.environ["R2_ACCESS_KEY_ID"],
    aws_secret_access_key=os.environ["R2_SECRET_ACCESS_KEY"],
    config=Config(signature_version="s3v4", max_pool_connections=48),
    region_name="auto")
STORES = [("luxvia-art","luxvia/gen/"), ("posterleaf-store1","store1/gen/"),
          ("mercury-usm","store2/gen/"), ("lunar-kms","store7/gen/")]
items=[]
for bkt,pre in STORES:
    tok=None
    while True:
        kw={"Bucket":bkt,"Prefix":pre,"MaxKeys":1000}
        if tok: kw["ContinuationToken"]=tok
        r=s3.list_objects_v2(**kw)
        items+=[(bkt,o["Key"]) for o in r.get("Contents",[]) if o["Key"].endswith(".jpg")]
        if not r.get("IsTruncated"): break
        tok=r["NextContinuationToken"]
print("listed", len(items), flush=True)
random.Random(11).shuffle(items)
items = items[:SAMPLE_N]

def get(it):
    bkt,k=it
    b=s3.get_object(Bucket=bkt,Key=k)["Body"].read()
    return k.rsplit("/",1)[-1][:-4], Image.open(io.BytesIO(b)).convert("RGB")
pairs=[]
with ThreadPoolExecutor(max_workers=32) as ex:
    for i,r in enumerate(ex.map(get, items),1):
        pairs.append(r)
        if i%500==0: print("fetched",i,flush=True)

dev = "cuda" if torch.cuda.is_available() else "cpu"
m = CLIPModel.from_pretrained("openai/clip-vit-large-patch14").to(dev).eval()
p = CLIPProcessor.from_pretrained("openai/clip-vit-large-patch14")
banks={}
for name,bank in (("human",HUMAN),("eyes",EYES)):
    t=p(text=bank["fail"]+bank["pass"],return_tensors="pt",padding=True).to(dev)
    with torch.no_grad():
        f=m.get_text_features(**t); f=f/f.norm(dim=-1,keepdim=True)
    banks[name]=(f,len(bank["fail"]))

skus=[x[0] for x in pairs]
sc={"human":[], "eyes":[]}
B=16
for i in range(0,len(pairs),B):
    ims=[x[1] for x in pairs[i:i+B]]
    with torch.no_grad():
        inp=p(images=ims,return_tensors="pt").to(dev)
        v=m.get_image_features(**inp); v=v/v.norm(dim=-1,keepdim=True)
    for name,(f,nf) in banks.items():
        pr=(100.0*v@f.T).softmax(dim=-1).cpu().numpy()
        sc[name]+= list(pr[:,:nf].sum(axis=1).astype(float))
    if i%480==0: print("scored",i,flush=True)

out={"n":len(skus)}
for name in sc:
    a=np.array(sc[name])
    out[name]={"mean":round(float(a.mean()),4),
               "pct": {str(q): round(float(np.quantile(a,q/100)),4)
                       for q in (50,75,90,95,98,99,99.5)}}
    order=np.argsort(-a)[:48]
    out[name+"_worst"]=[{"sku":skus[int(j)],"score":round(float(a[int(j)]),4)} for j in order]
    cells=[pairs[int(j)][1].resize((300,429),Image.LANCZOS) for j in order]
    sheet=Image.new("RGB",(6*306+6,8*435+6),(255,255,255))
    for n,c in enumerate(cells):
        sheet.paste(c,(6+(n%6)*306, 6+(n//6)*435))
    sheet.save(f"/workspace/worst_{name}.jpg","JPEG",quality=88)
open("/workspace/scores.json","w").write(json.dumps(out,indent=1))
print("SCAN " + json.dumps({k:v for k,v in out.items() if not k.endswith("_worst")}), flush=True)
EOF
echo SCAN_DONE
EOS
nohup bash /workspace/run.sh > /workspace/boot.log 2>&1 &
if [ -x /start.sh ]; then exec /start.sh; else sleep infinity; fi
'''


def curl(method, path, body=None):
    cmd = ["curl", "-sS", "--max-time", "90", "-X", method, f"{API}{path}"]
    if body is not None:
        cmd += ["-H", "Content-Type: application/json", "-d", json.dumps(body)]
    out = subprocess.run(cmd, capture_output=True, text=True).stdout
    try:
        return json.loads(out)
    except Exception:
        return {"_raw": out[:400]}


if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else SAMPLE
    script = SCRIPT.replace("SAMPLE_N", str(n))
    body = {"name": "wallart-qscan", "templateId": TEMPLATE,
            "imageName": "runpod/pytorch:2.8.0-py3.11-cuda12.8.1-cudnn-devel-ubuntu22.04",
            "gpuTypeIds": ["NVIDIA RTX A4000", "NVIDIA RTX A4500",
                           "NVIDIA GeForce RTX 3090", "NVIDIA RTX 4000 Ada Generation"],
            "gpuCount": 1, "cloudType": "COMMUNITY",
            "containerDiskInGb": 60, "volumeInGb": 0,
            "ports": ["8000/http"], "dockerStartCmd": ["bash", "-c", script]}
    r = curl("POST", "/pods", body)
    if isinstance(r, dict) and r.get("id"):
        print(json.dumps({k: r.get(k) for k in ("id", "costPerHr")}, indent=1))
        for f in ("boot.log", "scores.json", "worst_human.jpg", "worst_eyes.jpg"):
            print(f"  https://{r['id']}-8000.proxy.runpod.net/{f}")
        sys.exit(0)
    print("refused:", str(r)[:200])
    sys.exit(1)

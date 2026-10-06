import json, boto3, csv, subprocess, sys
from botocore.config import Config
subprocess.run(["curl","-sS","https://rest.runpod.io/v1/templates","-o","/tmp/t.json"])
e=[x for x in json.load(open("/tmp/t.json")) if x.get("id")=="vbsgwyibn1"][0]["env"]
s3=boto3.client("s3", endpoint_url=f"https://{e['R2_ACCOUNT_ID']}.r2.cloudflarestorage.com",
    aws_access_key_id=e["R2_ACCESS_KEY_ID"], aws_secret_access_key=e["R2_SECRET_ACCESS_KEY"],
    config=Config(retries={"max_attempts":4}), region_name="auto")
B=e["R2_BUCKET"]
def skus(p):
    out,tok=set(),None
    while True:
        kw={"Bucket":B,"Prefix":p,"MaxKeys":1000}
        if tok: kw["ContinuationToken"]=tok
        r=s3.list_objects_v2(**kw)
        out.update(o["Key"].split("/")[-1].rsplit(".",1)[0] for o in r.get("Contents",[]))
        if not r.get("IsTruncated"): return out
        tok=r["NextContinuationToken"]
print("listing art/mock ...", flush=True); mock=skus("art/mock/WLT-")
print("listing art/raw  ...", flush=True); raw=skus("art/raw/WLT-")
print("listing v2       ...", flush=True); v2=skus("v2/WLT-")
rows=[r for r in csv.DictReader(open("FINAL_V7.csv")) if r["slogan"]]
want={f"WLT-{int(r['source_idx']):06d}" for r in rows}
print(f"\nlistings {len(want):,} | mock {len(mock):,} | raw {len(raw):,} | v2 {len(v2):,}", flush=True)
mm, mr = want-mock, want-raw
print(f"missing mockups: {len(mm)}  {sorted(mm)[:5]}", flush=True)
print(f"missing prints : {len(mr)}  {sorted(mr)[:5]}", flush=True)
for sku in sorted(mm):
    if sku in v2:
        s3.copy_object(Bucket=B, Key=f"art/mock/{sku}.jpg",
                       CopySource={"Bucket":B,"Key":f"v2/{sku}.jpg"},
                       ContentType="image/jpeg", MetadataDirective="REPLACE",
                       CacheControl="public, max-age=31536000")
        print(f"  copied {sku}", flush=True)
    else:
        print(f"  {sku}: no v2 source", flush=True)
json.dump({"mock":sorted(mock|(mm&v2)),"raw":sorted(raw)}, open("bucket_state.json","w"))
print("done", flush=True)

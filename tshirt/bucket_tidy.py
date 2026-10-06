#!/usr/bin/env python3
"""Delete the artwork for listings that were pulled, and count what is left.

36 of the illustrated listings are also among the 389 dropped for trademark
or likeness. No eBay row points at them, but the bucket's r2.dev base is
public, so a Spitfire print master sitting there is still published artwork.
It comes down.

Then it counts what the bucket actually holds, which is the only check that
matters before an upload: every listing in the file must have a photo at
art/mock/<SKU>.jpg and a print master at art/raw/<SKU>.png.
"""
import os, sys


def s3():
    import boto3
    from botocore.config import Config
    return boto3.client("s3",
        endpoint_url=f"https://{os.environ['R2_ACCOUNT_ID']}.r2.cloudflarestorage.com",
        aws_access_key_id=os.environ["R2_ACCESS_KEY_ID"],
        aws_secret_access_key=os.environ["R2_SECRET_ACCESS_KEY"],
        config=Config(retries={"max_attempts": 5}), region_name="auto")


def listing(cli, bucket, prefix):
    keys, tok = set(), None
    while True:
        kw = {"Bucket": bucket, "Prefix": prefix, "MaxKeys": 1000}
        if tok:
            kw["ContinuationToken"] = tok
        r = cli.list_objects_v2(**kw)
        keys.update(o["Key"] for o in r.get("Contents", []))
        if not r.get("IsTruncated"):
            return keys
        tok = r["NextContinuationToken"]


def main():
    cli = s3(); B = os.environ["R2_BUCKET"]
    risky = [l.strip() for l in open("risky_skus.txt") if l.strip()]
    gone = 0
    for i in range(0, len(risky), 500):
        batch = [{"Key": f"art/{d}/{s}.{e}"}
                 for s in risky[i:i + 500]
                 for d, e in (("mock", "jpg"), ("raw", "png"))]
        r = cli.delete_objects(Bucket=B, Delete={"Objects": batch, "Quiet": True})
        gone += len(batch) - len(r.get("Errors") or [])
    print(f"removed artwork for {len(risky)} pulled listings ({gone} objects)")

    mock = {k.rsplit("/", 1)[-1][:-4] for k in listing(cli, B, "art/mock/")}
    raw = {k.rsplit("/", 1)[-1][:-4] for k in listing(cli, B, "art/raw/")}
    print(f"art/mock: {len(mock)} photos")
    print(f"art/raw:  {len(raw)} print masters")
    missing = mock ^ raw
    print(f"SKUs with only one of the two: {len(missing)}")
    for s in sorted(missing)[:10]:
        print("   ", s)
    # written back so the eBay file can be diffed against what the bucket
    # really holds, rather than against what the render log claims
    cli.put_object(Bucket=B, Key="art/_MOCK_SKUS.txt",
                   Body=("\n".join(sorted(mock))).encode(),
                   ContentType="text/plain")
    cli.put_object(Bucket=B, Key="art/_RAW_SKUS.txt",
                   Body=("\n".join(sorted(raw))).encode(),
                   ContentType="text/plain")
    cli.put_object(Bucket=B, Key="art/_INVENTORY.txt",
                   Body=f"mock={len(mock)} raw={len(raw)} mismatched={len(missing)}".encode(),
                   ContentType="text/plain")


if __name__ == "__main__":
    main()

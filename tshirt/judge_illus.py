#!/usr/bin/env python3
"""Have a vision model look at every finished print file and say if it is any good.

The mechanical gate in dtf.py catches what cannot physically print - too
little ink, hairlines, a background panel. It cannot catch the other failure,
which is artwork that prints perfectly and is a magenta blob. Four different
pixel statistics were measured against a labelled sample looking for one that
separates "recognisable motorcycle" from "abstract smear"; none of them does,
because it is not a question about pixels. So it is asked as a question about
the picture, by the same qwen2.5vl that read the seller's 22,437 designs.

A second pass added the "panel" question. Four different pixel
statistics were measured looking for one that separates a painted
background rectangle from a design that happens to be solid, and none of
them does - "dragon" and "red car" score identically and only one of them
is wrong. It is a question about the picture, so it is asked as one.

Each design is composited onto black first. The judge should see what a buyer
sees on the shirt, not a cutout on a white page.

    python3 judge_illus.py --prefix illusv2/
"""
import argparse, base64, io, json, os, subprocess, sys, time, urllib.request
from concurrent.futures import ThreadPoolExecutor

OLLAMA = "http://localhost:11434"
MODEL = os.environ.get("MODEL", "qwen2.5vl:7b")

PROMPT = """This is a t-shirt design printed on a black shirt. It is meant to show: {subject}

Return ONLY valid JSON, no other words:
{{"shows": "what you actually see, in a few words",
  "matches": true if what you see is clearly the thing it is meant to show,
  "clean": true if it reads as a deliberate illustration with clear shapes,
           false if it is a smear, a blob, a texture or visual noise,
  "panel": true if the artwork sits on a solid painted rectangle or square
           block of colour, or is a repeating all-over pattern filling a
           rectangle, rather than being cut out against the black shirt,
  "verdict": "good" | "weak" | "unusable"}}

Judge it as a product someone would pay for. A shape that is merely colourful
but not recognisable is "unusable". Be strict."""


def ollama_up():
    try:
        with urllib.request.urlopen(OLLAMA + "/api/tags", timeout=5) as r:
            return [m["name"] for m in json.loads(r.read()).get("models", [])]
    except Exception:
        return None


def ensure_ollama(workers):
    tags = ollama_up()
    if tags is None:
        print("starting ollama...", flush=True)
        env = dict(os.environ, OLLAMA_HOST="0.0.0.0:11434",
                   OLLAMA_NUM_PARALLEL=str(workers))
        log = open("/tmp/ollama.log", "ab")
        subprocess.Popen(["ollama", "serve"], stdout=log, stderr=log,
                         start_new_session=True, env=env)
        for _ in range(60):
            time.sleep(2)
            tags = ollama_up()
            if tags is not None:
                break
        if tags is None:
            sys.exit("ollama would not start - see /tmp/ollama.log")
    if not any(t.split(":")[0] == MODEL.split(":")[0] for t in tags):
        print(f"pulling {MODEL}...", flush=True)
        if subprocess.call(["ollama", "pull", MODEL]) != 0:
            sys.exit("ollama pull failed")
    print("ollama ready", flush=True)


def on_black(png_bytes):
    """What the buyer sees: the transparent print file over the garment."""
    from PIL import Image
    art = Image.open(io.BytesIO(png_bytes)).convert("RGBA")
    out = Image.new("RGB", art.size, (18, 18, 18))
    out.paste(art, (0, 0), art)
    buf = io.BytesIO()
    out.convert("RGB").save(buf, "JPEG", quality=88)
    return base64.b64encode(buf.getvalue()).decode()


def ask(b64, subject):
    body = json.dumps({
        "model": MODEL, "prompt": PROMPT.format(subject=subject),
        "images": [b64], "stream": False, "format": "json",
        "options": {"temperature": 0},
    }).encode()
    req = urllib.request.Request(OLLAMA + "/api/generate", data=body,
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=240) as r:
        return json.loads(json.loads(r.read())["response"])


def s3():
    import boto3
    from botocore.config import Config
    return boto3.client("s3",
        endpoint_url=f"https://{os.environ['R2_ACCOUNT_ID']}.r2.cloudflarestorage.com",
        aws_access_key_id=os.environ["R2_ACCESS_KEY_ID"],
        aws_secret_access_key=os.environ["R2_SECRET_ACCESS_KEY"],
        config=Config(retries={"max_attempts": 5}, max_pool_connections=64),
        region_name="auto")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--prefix", default="illusv2/")
    ap.add_argument("--workers", type=int, default=6)
    a = ap.parse_args()

    ensure_ollama(a.workers)
    cli = s3(); B = os.environ["R2_BUCKET"]

    keys = []
    tok = None
    while True:
        kw = {"Bucket": B, "Prefix": a.prefix + "raw/"}
        if tok:
            kw["ContinuationToken"] = tok
        r = cli.list_objects_v2(**kw)
        keys += [o["Key"] for o in r.get("Contents", [])]
        tok = r.get("NextContinuationToken")
        if not tok:
            break
    print(f"{len(keys)} designs to judge", flush=True)

    done = 0; t0 = time.time()

    def one(key):
        nonlocal done
        slug = key.rsplit("/", 1)[-1][:-4]
        subject = slug.replace("-", " ").strip()
        try:
            body = cli.get_object(Bucket=B, Key=key)["Body"].read()
            v = ask(on_black(body), subject)
            row = {"slug": slug, "subject": subject,
                   "shows": str(v.get("shows", ""))[:80],
                   "matches": bool(v.get("matches")),
                   "clean": bool(v.get("clean")),
                   "panel": bool(v.get("panel")),
                   "verdict": str(v.get("verdict", "")).lower()}
        except Exception as e:
            row = {"slug": slug, "subject": subject, "error": f"{type(e).__name__}: {e}"[:120]}
        done += 1
        if done % 25 == 0:
            print(f"  {done}/{len(keys)}  {done/(time.time()-t0):.1f}/s", flush=True)
        return row

    with ThreadPoolExecutor(max_workers=a.workers) as ex:
        rows = list(ex.map(one, keys))

    err = [r for r in rows if "error" in r]
    if err:
        print(f"{len(err)} failed, first: {err[0]['error']}", flush=True)
    body = "\n".join(json.dumps(r) for r in rows).encode()
    cli.put_object(Bucket=B, Key=f"{a.prefix}_JUDGE.jsonl", Body=body,
                   ContentType="application/x-ndjson")
    from collections import Counter
    print(Counter(r.get("verdict", "ERROR") for r in rows), flush=True)
    cli.put_object(Bucket=B, Key=f"{a.prefix}_JUDGED.txt",
                   Body=f"judged={len(rows)} errors={len(err)}".encode(),
                   ContentType="text/plain")
    print(f"DONE in {(time.time()-t0)/60:.1f} min", flush=True)


if __name__ == "__main__":
    main()

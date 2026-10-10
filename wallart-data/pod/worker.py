#!/usr/bin/env python3
"""Stream competitor art past CLIP and a colour meter. Learn, don't hoard.

Per image it keeps ~40 numbers: the top label on each of seven taxonomy axes
with its score, and the measured colour and composition features. That is about
250 bytes, so the whole 9.1M corpus comes back as ~2 GB of findings instead of
640 GB of pictures. A 1-in-50 random sample keeps its full 768-float embedding
too, which is enough to cluster and to measure near-duplication.

Resumable, because the balance can run out mid-run: work is cut into shards,
a shard's outputs are written and only then is its id appended to done.txt.
A kill at any instant loses at most one shard. Re-running skips what is done.

Parallel: --part k/n takes only the shards where id % n == k, so several pods
share one work list with no coordination and no overlap.

  python3 worker.py --list urls.jsonl --out /workspace/out --part 0/4
"""
import argparse, gzip, io, json, os, time, threading, queue
import numpy as np
from PIL import Image, ImageFile
import requests
from colour import feats
from taxonomy import AXES, prompts

Image.MAX_IMAGE_PIXELS = None
ImageFile.LOAD_TRUNCATED_IMAGES = True
SHARD = 2000
MODEL = "openai/clip-vit-large-patch14"
EMB_KEEP = 50           # keep the full embedding for 1 image in 50


def small(url, src):
    """Ask the CDN to resize: full-size Displate art is 640 KB, this is ~60 KB."""
    sep = "&" if "?" in url else "?"
    return url + sep + ("speedsize=w_384" if src == "displate" else "width=384")


def unwrap(o):
    """transformers 4 returns a tensor from get_*_features; 5 returns an output
    object whose .pooler_output holds the projected features. Support both."""
    import torch as _t
    return o if _t.is_tensor(o) else o.pooler_output


def fetcher(jobs, got, sess):
    while True:
        job = jobs.get()
        if job is None:
            jobs.task_done(); return
        try:
            r = sess.get(small(job["url"], job.get("src", "")), timeout=25)
            if r.status_code == 200 and len(r.content) > 500:
                im = Image.open(io.BytesIO(r.content)); im.load()
                got.append((job, im.convert("RGB")))
        except Exception:
            pass
        jobs.task_done()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--list", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--threads", type=int, default=64)
    ap.add_argument("--batch", type=int, default=160)
    ap.add_argument("--part", default="0/1")
    ap.add_argument("--max-minutes", type=float, default=0, help="stop cleanly after this long")
    a = ap.parse_args()
    pk, pn = (int(x) for x in a.part.split("/"))
    os.makedirs(a.out, exist_ok=True)
    donep = os.path.join(a.out, f"done_{pk}of{pn}.txt")
    done = {l.strip() for l in open(donep)} if os.path.exists(donep) else set()

    import torch
    from transformers import CLIPModel, CLIPProcessor
    dev = "cuda" if torch.cuda.is_available() else "cpu"
    dt = torch.float16 if dev == "cuda" else torch.float32
    model = CLIPModel.from_pretrained(MODEL, torch_dtype=dt).to(dev).eval()
    proc = CLIPProcessor.from_pretrained(MODEL)

    # text side once: 87 prompts, grouped so each axis gets its own softmax
    P = prompts()
    tk = proc(text=[p[2] for p in P], return_tensors="pt", padding=True).to(dev)
    with torch.no_grad():
        T = unwrap(model.get_text_features(**tk))
    T = (T / T.norm(dim=-1, keepdim=True)).to(dt)
    spans, i = {}, 0
    for axis, d in AXES.items():
        spans[axis] = (i, i + len(d)); i += len(d)
    keys = {axis: list(d.keys()) for axis, d in AXES.items()}
    print(f"model on {dev}, {len(P)} prompts, part {pk}/{pn}", flush=True)

    sess = requests.Session()
    ad = requests.adapters.HTTPAdapter(pool_connections=a.threads, pool_maxsize=a.threads)
    sess.mount("https://", ad); sess.mount("http://", ad)

    jobs, got = queue.Queue(maxsize=a.threads * 4), []
    for _ in range(a.threads):
        threading.Thread(target=fetcher, args=(jobs, got, sess), daemon=True).start()

    t0, seen, nsh = time.time(), 0, 0
    metaf = gzip.open(os.path.join(a.out, f"meta_{pk}of{pn}.jsonl.gz"), "at", encoding="utf-8")
    embs_keep, emb_ids = [], []

    def run_shard(sid, lines):
        nonlocal seen
        got.clear()
        for l in lines:
            try:
                jobs.put(json.loads(l))
            except Exception:
                pass
        jobs.join()
        rows = list(got)
        if not rows:
            return 0
        n = 0
        for i0 in range(0, len(rows), a.batch):
            chunk = rows[i0:i0 + a.batch]
            px = proc(images=[im for _, im in chunk], return_tensors="pt")["pixel_values"].to(dev, dtype=dt)
            with torch.no_grad():
                E = unwrap(model.get_image_features(pixel_values=px))
            E = E / E.norm(dim=-1, keepdim=True)
            logits = (E @ T.T).float()
            for j, (job, im) in enumerate(chunk):
                rec = {"id": job.get("id", ""), "s": job.get("src", "")[:2]}
                if job.get("title"):
                    rec["t"] = job["title"]
                for axis, (lo, hi) in spans.items():
                    v = torch.softmax(logits[j, lo:hi] * 100.0, dim=0)
                    top = int(v.argmax())
                    rec[axis[:4]] = keys[axis][top]
                    rec[axis[:4] + "_p"] = round(float(v[top]), 3)
                rec.update(feats(im))
                rec.pop("wh", None)
                metaf.write(json.dumps(rec, ensure_ascii=False) + "\n")
                n += 1
                gi = seen + n
                if gi % EMB_KEEP == 0:
                    embs_keep.append(E[j].float().cpu().numpy().astype(np.float16))
                    emb_ids.append(rec["id"])
        metaf.flush()
        seen += n
        return n

    stop = False
    with open(a.list, encoding="utf-8") as f:
        buf, sid = [], 0
        for line in f:
            buf.append(line)
            if len(buf) < SHARD:
                continue
            cur, lines, buf = sid, buf, []
            mine = (cur % pn == pk)
            sid += 1
            if not mine or str(cur) in done:
                continue
            n = run_shard(cur, lines)
            with open(donep, "a") as df:
                df.write(f"{cur}\n")
            nsh += 1
            el = (time.time() - t0) / 60
            print(f"shard {cur}  +{n}  total {seen:,}  {seen/max(el*60,1):.1f} img/s  {el:.1f} min", flush=True)
            if a.max_minutes and el >= a.max_minutes:
                stop = True; break
    if embs_keep:
        np.save(os.path.join(a.out, f"emb_{pk}of{pn}.npy"), np.stack(embs_keep))
        with open(os.path.join(a.out, f"embids_{pk}of{pn}.txt"), "w") as f:
            f.write("\n".join(emb_ids))
    print(f"DONE part {pk}/{pn}: {seen:,} images, {nsh} shards, "
          f"{(time.time()-t0)/60:.1f} min, stopped_early={stop}", flush=True)


if __name__ == "__main__":
    main()

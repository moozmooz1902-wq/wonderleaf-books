"""Read the text off every design using a vision model on your own GPU.

Runs against an Ollama server (RunPod pod, or anywhere reachable over HTTP).
No Anthropic key, no per-image cost beyond GPU time.

    export VLM_URL=https://<your-pod>-11434.proxy.runpod.net
    python3 read_designs_gpu.py test          # 10 images, check quality first
    python3 read_designs_gpu.py run           # the 22,485 that sold
    python3 read_designs_gpu.py run --all     # all 167,695

Writes designs_read.jsonl, one row per design. Resumable - rerun to continue.
"""
import base64, json, os, sys, threading, time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

URL   = os.environ.get("VLM_URL", "http://localhost:11434").rstrip("/")
MODEL = os.environ.get("VLM_MODEL", "qwen2.5vl:7b")
# Ollama serves requests in parallel; 4-6 keeps a 24GB card busy
WORKERS = int(os.environ.get("VLM_WORKERS", "5"))
IMG   = Path("images")
OUT   = Path("designs_read.jsonl")

PROMPT = """Look at this t-shirt design and report what is printed on it.

Return ONLY valid JSON, no other words:
{"text_lines": ["每 line of text printed on the garment, exactly as written, top to bottom"],
 "has_text": true,
 "main_image": "what is illustrated, in a few words, or null if text only",
 "style": "one of: flat_vector, line_art, cartoon, distressed, photographic, typography_only",
 "layout": "one of: text_only, text_above_image, text_below_image, image_only, badge, two_panel, grid_of_designs"}

If there is no readable text, set text_lines to [] and has_text to false."""


def post(path, body, timeout=180):
    import urllib.request
    req = urllib.request.Request(URL + path, method="POST")
    req.add_header("content-type", "application/json")
    req.data = json.dumps(body).encode()
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read())


def read_one(path):
    b64 = base64.standard_b64encode(path.read_bytes()).decode()
    r = post("/api/generate", {"model": MODEL, "prompt": PROMPT,
                               "images": [b64], "stream": False,
                               "options": {"temperature": 0}})
    txt = r.get("response", "").strip()
    if txt.startswith("```"):
        txt = txt.split("\n", 1)[1].rsplit("```", 1)[0].strip()
    return json.loads(txt)


def targets(all_of_them):
    rows = json.load(open("all.json"))
    done = set()
    if OUT.exists():
        for line in OUT.open():
            try: done.add(json.loads(line)["idx"])
            except Exception: pass
    out = []
    for i, r in enumerate(rows):
        if i in done: continue
        if not all_of_them and r["sold"] == 0: continue
        p = IMG / f"{i:06d}.webp"
        if p.exists(): out.append((i, r, p))
    return out, len(done)


def main(cmd, all_of_them=False):
    rows = json.load(open("all.json"))
    if cmd == "test":
        todo, _ = targets(False)
        todo = todo[:10]
        print(f"testing {MODEL} at {URL}\n")
        for i, r, p in todo:
            t0 = time.time()
            try:
                res = read_one(p)
            except Exception as e:
                print(f"  FAILED {e}"); continue
            print(f"  [{time.time()-t0:.1f}s] {r['title'][:56]}")
            print(f"      reads: {res.get('text_lines')}")
            print(f"      image: {res.get('main_image')}  layout: {res.get('layout')}")
        return

    todo, already = targets(all_of_them)
    print(f"{already:,} already read, {len(todo):,} to go, {WORKERS} workers")
    fh = OUT.open("a", encoding="utf-8")
    lock = threading.Lock()
    t0 = time.time()
    counts = {"ok": 0, "bad": 0, "n": 0}

    def work(job):
        i, r, p = job
        try:
            res = read_one(p)
        except Exception:
            with lock:
                counts["bad"] += 1; counts["n"] += 1
            return
        res.update(idx=i, title=r["title"], sold=r["sold"])
        with lock:
            fh.write(json.dumps(res, ensure_ascii=False) + "\n"); fh.flush()
            counts["ok"] += 1; counts["n"] += 1
            n = counts["n"]
            if n % 100 == 0:
                rate = n / (time.time() - t0)
                print(f"  {n:,}/{len(todo):,}  {rate:.1f}/s  "
                      f"eta {(len(todo)-n)/rate/3600:.1f}h  "
                      f"({counts['bad']} failed)", flush=True)

    with ThreadPoolExecutor(max_workers=WORKERS) as ex:
        list(ex.map(work, todo))
    fh.close()
    print(f"\n{counts['ok']:,} designs read, {counts['bad']:,} failed -> {OUT}")


if __name__ == "__main__":
    c = sys.argv[1] if len(sys.argv) > 1 else ""
    if c in ("test", "run"): main(c, "--all" in sys.argv)
    else: sys.exit(__doc__)

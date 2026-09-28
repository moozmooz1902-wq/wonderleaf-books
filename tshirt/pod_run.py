#!/usr/bin/env python3
"""Read the text off every design. Runs entirely on the pod.

Put this next to t-shirts.csv and run:
    python3 pod_run.py

It makes sure Ollama is up (starting it detached if it is not), downloads the
images, reads each one with the local vision model, and writes
designs_read.jsonl. Resumable - if it stops, just run it again.
"""
import base64, csv, json, os, re, subprocess, sys, threading, time, urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

CSV     = os.environ.get("CSV", "t-shirts.csv")
OLLAMA  = "http://localhost:11434"
MODEL   = os.environ.get("MODEL", "qwen2.5vl:7b")
IMG     = Path("images"); IMG.mkdir(exist_ok=True)
OUT     = Path("designs_read.jsonl")
DL_WORKERS  = 32
VLM_WORKERS = int(os.environ.get("WORKERS", "6"))
SOLD_ONLY   = os.environ.get("ALL", "") == ""      # default: only designs that sold

PROMPT = """Look at this t-shirt design and report what is printed on it.

Return ONLY valid JSON, no other words:
{"text_lines": ["each line of text printed on the garment, exactly as written, top to bottom"],
 "has_text": true,
 "main_image": "what is illustrated, in a few words, or null if text only",
 "style": "one of: flat_vector, line_art, cartoon, distressed, photographic, typography_only",
 "layout": "one of: text_only, text_above_image, text_below_image, image_only, badge, two_panel, grid_of_designs"}

If there is no readable text, set text_lines to [] and has_text to false."""


# ---------------------------------------------------------------- preflight
def ollama_up():
    try:
        with urllib.request.urlopen(OLLAMA + "/api/tags", timeout=5) as r:
            return [m["name"] for m in json.loads(r.read()).get("models", [])]
    except Exception:
        return None


def ensure_ollama():
    """Ollama must be alive AND hold the model, or nothing below works."""
    tags = ollama_up()
    if tags is None:
        print("Ollama is not answering on 11434 - starting it detached...")
        env = dict(os.environ, OLLAMA_HOST="0.0.0.0:11434",
                   OLLAMA_NUM_PARALLEL=str(VLM_WORKERS))
        log = open("/tmp/ollama.log", "ab")
        subprocess.Popen(["ollama", "serve"], stdout=log, stderr=log,
                         start_new_session=True, env=env)
        for _ in range(60):
            time.sleep(2)
            tags = ollama_up()
            if tags is not None:
                break
        if tags is None:
            sys.exit("Ollama would not start. Check /tmp/ollama.log")
        print("Ollama is up.")

    if not any(t.split(":")[0] == MODEL.split(":")[0] for t in tags):
        print(f"{MODEL} is not pulled yet - pulling (this is a few GB)...")
        if subprocess.call(["ollama", "pull", MODEL]) != 0:
            sys.exit(f"ollama pull {MODEL} failed")
    print(f"model ready: {MODEL}")


def smoke_test():
    """Read one real image before committing to 167k of them."""
    sample = sorted(IMG.glob("*.img"))
    if not sample:
        return
    print("smoke test on", sample[0].name, "...", flush=True)
    t0 = time.time()
    try:
        res = read_one(sample[0])
    except Exception as e:
        sys.exit(f"SMOKE TEST FAILED: {type(e).__name__}: {e}\n"
                 f"Nothing else will work until this does. Check /tmp/ollama.log")
    print(f"  ok in {time.time()-t0:.1f}s -> {json.dumps(res, ensure_ascii=False)[:300]}")


# ---------------------------------------------------------------- data
def load_rows():
    junk = "Opens in a new window or tab"
    rows = []
    with open(CSV, encoding="utf-8-sig", newline="") as fh:
        for r in csv.DictReader(fh):
            t = (r.get("Title") or "").replace(junk, "").strip()
            u = (r.get("Image URL") or "").strip()
            try:
                q = int(str(r.get("Sold Quantity") or "0").replace(",", ""))
            except ValueError:
                q = 0
            if t and u:
                rows.append({"title": t, "url": u, "sold": q})
    return rows


def download(rows):
    todo = [(i, r) for i, r in enumerate(rows)
            if (r["sold"] > 0 or not SOLD_ONLY)
            and not (IMG / f"{i:06d}.img").exists()]
    if not todo:
        print("all images already downloaded"); return
    print(f"downloading {len(todo):,} images with {DL_WORKERS} workers...")
    t0 = time.time(); done = [0]; fails = [0]; first_err = []
    lock = threading.Lock()

    def one(job):
        i, r = job
        try:
            req = urllib.request.Request(r["url"], headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=25) as resp:
                (IMG / f"{i:06d}.img").write_bytes(resp.read())
        except Exception as e:
            with lock:
                fails[0] += 1
                if not first_err:
                    first_err.append(f"{type(e).__name__}: {e}  url={r['url'][:120]}")
                    print("  first download error ->", first_err[0], flush=True)
        with lock:
            done[0] += 1
            if done[0] % 2000 == 0:
                rate = done[0] / (time.time() - t0)
                print(f"  {done[0]:,}/{len(todo):,}  {rate:.0f}/s  "
                      f"eta {(len(todo)-done[0])/rate/60:.0f} min  ({fails[0]} failed)",
                      flush=True)

    with ThreadPoolExecutor(max_workers=DL_WORKERS) as ex:
        list(ex.map(one, todo))
    print(f"downloaded in {(time.time()-t0)/60:.1f} min ({fails[0]:,} failed)")


# ---------------------------------------------------------------- vision
def read_one(path):
    b64 = base64.standard_b64encode(path.read_bytes()).decode()
    body = json.dumps({"model": MODEL, "prompt": PROMPT, "images": [b64],
                       "stream": False, "options": {"temperature": 0}}).encode()
    req = urllib.request.Request(OLLAMA + "/api/generate", method="POST", data=body)
    req.add_header("content-type", "application/json")
    with urllib.request.urlopen(req, timeout=300) as r:
        txt = json.loads(r.read()).get("response", "").strip()
    if txt.startswith("```"):
        txt = txt.split("\n", 1)[1].rsplit("```", 1)[0].strip()
    m = re.search(r"\{.*\}", txt, re.S)
    return json.loads(m.group(0) if m else txt)


def analyse(rows):
    done = set()
    if OUT.exists():
        for line in OUT.open():
            try: done.add(json.loads(line)["idx"])
            except Exception: pass
    todo = [(i, r) for i, r in enumerate(rows)
            if (r["sold"] > 0 or not SOLD_ONLY)
            and i not in done and (IMG / f"{i:06d}.img").exists()]
    print(f"\n{len(done):,} already read, {len(todo):,} to go, {VLM_WORKERS} workers")
    if not todo:
        return
    fh = OUT.open("a", encoding="utf-8")
    lock = threading.Lock()
    t0 = time.time(); n = [0]; bad = [0]; streak = [0]; errs = {}
    stop = threading.Event()

    def work(job):
        i, r = job
        if stop.is_set():
            return
        try:
            res = read_one(IMG / f"{i:06d}.img")
        except Exception as e:
            key = f"{type(e).__name__}: {str(e)[:120]}"
            with lock:
                bad[0] += 1; n[0] += 1; streak[0] += 1
                errs[key] = errs.get(key, 0) + 1
                if errs[key] == 1:
                    print(f"  ERROR ({bad[0]} so far): {key}", flush=True)
                # 25 failures in a row means something is broken, not flaky
                if streak[0] >= 25 and not stop.is_set():
                    stop.set()
                    print("\n!! 25 failures in a row - stopping instead of burning "
                          "through the rest. Errors so far:", flush=True)
                    for k, v in sorted(errs.items(), key=lambda x: -x[1]):
                        print(f"   {v:>6,}  {k}", flush=True)
            return
        res.update(idx=i, title=r["title"], sold=r["sold"])
        with lock:
            streak[0] = 0
            fh.write(json.dumps(res, ensure_ascii=False) + "\n"); fh.flush()
            n[0] += 1
            if n[0] % 100 == 0:
                rate = n[0] / (time.time() - t0)
                print(f"  {n[0]:,}/{len(todo):,}  {rate:.1f}/s  "
                      f"eta {(len(todo)-n[0])/rate/3600:.1f}h  ({bad[0]} failed)", flush=True)

    with ThreadPoolExecutor(max_workers=VLM_WORKERS) as ex:
        list(ex.map(work, todo))
    fh.close()
    print(f"\nDONE. {n[0]-bad[0]:,} designs read, {bad[0]:,} failed -> {OUT}")
    if errs:
        print("failure breakdown:")
        for k, v in sorted(errs.items(), key=lambda x: -x[1]):
            print(f"   {v:>6,}  {k}")
    if n[0] - bad[0]:
        print(f"Download {OUT} and send it back.")


if __name__ == "__main__":
    if not Path(CSV).exists():
        sys.exit(f"Put {CSV} next to this script first.")
    ensure_ollama()
    rows = load_rows()
    print(f"{len(rows):,} listings in {CSV}; "
          f"{sum(1 for r in rows if r['sold']>0):,} of them sold at least once")
    download(rows)
    smoke_test()
    analyse(rows)

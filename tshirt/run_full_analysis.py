"""Read every design image via the Batch API and write one fingerprint per design.

    python3 run_full_analysis.py download            # fetch images (32 threads)
    python3 run_full_analysis.py submit [--sold-only]# send batches to Claude
    python3 run_full_analysis.py collect             # poll + write fingerprints.jsonl

Batch API runs asynchronously at 50% cost, so submit and collect are separate
steps - the job survives this session ending.

Auth works two ways, and the script picks whichever is present:
  - ANTHROPIC_API_KEY in the environment, or
  - an API credential stored on the environment, which injects x-api-key at
    the proxy. In that case no key is present in the container at all.
"""
import base64, json, os, sys, time, urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

MODEL = os.environ.get("ANALYSIS_MODEL", "claude-haiku-4-5")
IMG = Path("images"); IMG.mkdir(exist_ok=True)
STATE = Path("batch_state.json")
BATCH_MAX = 10_000          # requests per batch submission

PROMPT = """Analyse this t-shirt design for a print-on-demand catalogue.

Listing title: {title}
Units sold: {sold}

Report only what you can actually see. If it is not a t-shirt design, set
is_design false and leave the rest minimal.

Return ONLY valid JSON:
{{
 "is_design": true,
 "shirt_text": ["each line of text printed on the garment, verbatim, in order"],
 "has_text": true,
 "garment_colour": "black|white|grey|charcoal|olive|navy|natural|other",
 "print_colours": 1,
 "print_style": "one of: flat_silhouette, line_engraving, cartoon, distressed_vintage, photographic, gradient_render, typography_only",
 "layout": "one of: stacked_text, text_over_image, image_over_text, image_only, badge_circle, two_panel, progression_row, mosaic, left_chest",
 "subject": "the main visual element in a few words, or null",
 "niche": "the specific audience, e.g. 'HGV driver' not 'jobs'",
 "hook_type": "one of: in_group_joke, pride_statement, insider_knowledge, pun, nostalgia, milestone, sarcasm, decoration_only",
 "template": "the reusable slogan structure with {{SLOTS}}, or null if no text",
 "typography": {{"faces": "one of: single_sans, sans_plus_serif, script, slab, mixed, none",
                 "case": "uppercase|title|mixed|none"}},
 "model_shot": true,
 "multi_design_grid": false,
 "ip_risk": "none|possible|clear",
 "notes": "one blunt line on what makes it work or why it looks lazy"
}}"""


def rows():
    return json.load(open("all.json"))


def path_for(i):
    return IMG / f"{i:06d}.webp"


def download():
    import requests
    data = rows()
    s = requests.Session()
    ca = "/root/.ccr/ca-bundle.crt"
    if os.path.exists(ca): s.verify = ca
    s.headers["User-Agent"] = "Mozilla/5.0"

    def one(pair):
        i, r = pair
        p = path_for(i)
        if p.exists() and p.stat().st_size > 500: return True
        try:
            resp = s.get(r["url"], timeout=20)
            if resp.status_code == 200 and resp.content:
                p.write_bytes(resp.content); return True
        except Exception:
            pass
        return False

    t0 = time.time(); ok = 0
    with ThreadPoolExecutor(max_workers=32) as ex:
        for n, good in enumerate(ex.map(one, enumerate(data)), 1):
            ok += bool(good)
            if n % 5000 == 0:
                rate = n / (time.time() - t0)
                print(f"  {n:,}/{len(data):,}  {rate:.0f}/s  "
                      f"eta {(len(data)-n)/rate/60:.0f} min", flush=True)
    print(f"downloaded {ok:,} of {len(data):,}")


def media_type(b):
    if b[:4] == b"RIFF": return "image/webp"
    if b[:2] == b"\xff\xd8": return "image/jpeg"
    if b[:8] == b"\x89PNG\r\n\x1a\n": return "image/png"
    return "image/webp"


API = "https://api.anthropic.com/v1"


def call(path, method="GET", body=None, raw=False):
    """Call the API. Sends a key if we have one; otherwise relies on the
    environment's stored API credential injecting x-api-key at the proxy."""
    req = urllib.request.Request(f"{API}{path}", method=method)
    req.add_header("content-type", "application/json")
    key = os.environ.get("ANTHROPIC_API_KEY")
    if key:
        req.add_header("x-api-key", key)
        req.add_header("anthropic-version", "2023-06-01")
    if body is not None:
        req.data = json.dumps(body).encode()
    with urllib.request.urlopen(req, timeout=300) as r:
        return r.read() if raw else json.loads(r.read())


def submit(sold_only=False):
    data = rows()
    idx = [i for i, r in enumerate(data) if (r["sold"] > 0 or not sold_only)]
    idx = [i for i in idx if path_for(i).exists()]
    print(f"submitting {len(idx):,} designs in batches of {BATCH_MAX:,}")

    state = json.loads(STATE.read_text()) if STATE.exists() else {"batches": []}
    done = {b["first"] for b in state["batches"]}

    for start in range(0, len(idx), BATCH_MAX):
        chunk = idx[start:start + BATCH_MAX]
        if chunk[0] in done:
            continue
        reqs = []
        for i in chunk:
            b = path_for(i).read_bytes()
            reqs.append({
                "custom_id": f"d{i}",
                "params": {
                    "model": MODEL, "max_tokens": 1200,
                    "messages": [{"role": "user", "content": [
                        {"type": "image", "source": {"type": "base64",
                         "media_type": media_type(b),
                         "data": base64.standard_b64encode(b).decode()}},
                        {"type": "text", "text": PROMPT.format(
                            title=data[i]["title"], sold=data[i]["sold"])},
                    ]}],
                },
            })
        batch = call("/messages/batches", "POST", {"requests": reqs})
        state["batches"].append({"id": batch["id"], "first": chunk[0], "n": len(chunk)})
        STATE.write_text(json.dumps(state, indent=1))
        print(f"  submitted {batch['id']}  ({len(chunk):,} designs)", flush=True)
    print("all batches submitted. Run `collect` later - results keep for 29 days.")


def collect():
    state = json.loads(STATE.read_text())
    data = rows()
    out = open("fingerprints.jsonl", "a", encoding="utf-8")
    total = bad = 0

    for b in state["batches"]:
        info = call(f"/messages/batches/{b['id']}")
        if info["processing_status"] != "ended":
            print(f"  {b['id']}: {info['processing_status']} - not ready")
            continue
        body = call(f"/messages/batches/{b['id']}/results", raw=True).decode()
        for line in body.splitlines():
            if not line.strip(): continue
            res = json.loads(line)
            if res["result"]["type"] != "succeeded":
                bad += 1; continue
            i = int(res["custom_id"][1:])
            txt = res["result"]["message"]["content"][0]["text"].strip()
            if txt.startswith("```"):
                txt = txt.split("\n", 1)[1].rsplit("```", 1)[0].strip()
            try:
                fp = json.loads(txt)
            except json.JSONDecodeError:
                bad += 1; continue
            fp["idx"] = i
            fp["title"] = data[i]["title"]
            fp["sold"] = data[i]["sold"]
            out.write(json.dumps(fp, ensure_ascii=False) + "\n")
            total += 1
        print(f"  {b['id']}: collected", flush=True)
    out.close()
    print(f"\n{total:,} fingerprints written to fingerprints.jsonl ({bad:,} failed)")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "download": download()
    elif cmd == "submit": submit("--sold-only" in sys.argv)
    elif cmd == "collect": collect()
    else: sys.exit(__doc__)

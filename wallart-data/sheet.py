#!/usr/bin/env python3
"""Contact sheet of competitor art, so a lot of it can be looked at at once.

The scripts measure colour and score labels; this is for the part no metric
covers - what the pictures actually look like.
"""
import io, json, os, random, sys, threading, queue
import urllib.request
from PIL import Image

H = "/tmp/claude-0/-home-user-wonderleaf-books/af9e3fdd-8129-53fc-a69c-916ae3713d2b/scratchpad/harvest2"
src   = sys.argv[1]                      # fy | displate
n     = int(sys.argv[2])
out   = sys.argv[3]
seed  = int(sys.argv[4]) if len(sys.argv) > 4 else 1
cols  = 8
cell  = 300

path = f"{H}/manifest.jsonl" if src == "fy" else f"{H}/displate/displate.jsonl"
rng = random.Random(seed)
# reservoir sample so we do not hold 6.4M lines
pick, k = [], 0
for line in open(path, encoding="utf-8"):
    k += 1
    if len(pick) < n:
        pick.append(line)
    elif rng.random() < n / k:
        pick[rng.randrange(n)] = line
rows = [json.loads(l) for l in pick]

q, got = queue.Queue(), []
def work():
    while True:
        i_d = q.get()
        if i_d is None:
            q.task_done(); return
        i, d = i_d
        u = d.get("img") or d.get("url")
        u += ("&" if "?" in u else "?") + ("speedsize=w_384" if src == "displate" else "width=384")
        try:
            rq = urllib.request.Request(u, headers={"Accept": "image/*"})
            with urllib.request.urlopen(rq, timeout=25) as resp:
                data = resp.read()
            im = Image.open(io.BytesIO(data)).convert("RGB")
            got.append((i, im, d.get("title", "")))
        except Exception:
            pass
        q.task_done()
ths = [threading.Thread(target=work, daemon=True) for _ in range(24)]
for t in ths: t.start()
for i, d in enumerate(rows): q.put((i, d))
q.join()

got.sort()
rowsn = (len(got) + cols - 1) // cols
sheet = Image.new("RGB", (cols * cell, rowsn * cell), (255, 255, 255))
for j, (i, im, t) in enumerate(got):
    im.thumbnail((cell - 8, cell - 8), Image.LANCZOS)
    x = (j % cols) * cell + (cell - im.width) // 2
    y = (j // cols) * cell + (cell - im.height) // 2
    sheet.paste(im, (x, y))
sheet.save(out, "JPEG", quality=86)
print(f"{len(got)} images -> {out}  {sheet.size}")
for j, (i, im, t) in enumerate(got[:200]):
    if t: print(f"  {j:>3} {t[:95]}")

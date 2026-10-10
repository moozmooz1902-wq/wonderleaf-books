#!/usr/bin/env python3
"""Contact sheet of competitor art whose TITLE matches a pattern.

Used to look at what the categories that beat the seller's base watch rate
actually look like - charcoal, sketch, vintage, noir, japanese - rather than
guessing from the word.
"""
import io, json, os, random, re, sys, threading, queue
import urllib.request
from PIL import Image

H = "/tmp/claude-0/-home-user-wonderleaf-books/af9e3fdd-8129-53fc-a69c-916ae3713d2b/scratchpad/harvest2"
pat, n, out = sys.argv[1], int(sys.argv[2]), sys.argv[3]
rx = re.compile(pat, re.I)
cols, cell = 8, 300

rng = random.Random(5)
pick, k = [], 0
for line in open(f"{H}/manifest.jsonl", encoding="utf-8"):
    if not rx.search(line):
        continue
    d = json.loads(line)
    if not rx.search(d.get("title") or ""):
        continue
    k += 1
    if len(pick) < n:
        pick.append(d)
    elif rng.random() < n / k:
        pick[rng.randrange(n)] = d
print(f"{k:,} titles match {pat!r}; sampled {len(pick)}")

q, got = queue.Queue(), []
def work():
    while True:
        it = q.get()
        if it is None:
            q.task_done(); return
        i, d = it
        u = d["url"] + ("&" if "?" in d["url"] else "?") + "width=384"
        try:
            rq = urllib.request.Request(u, headers={"Accept": "image/*"})
            with urllib.request.urlopen(rq, timeout=25) as r:
                got.append((i, Image.open(io.BytesIO(r.read())).convert("RGB"), d.get("title", "")))
        except Exception:
            pass
        q.task_done()
for _ in range(24):
    threading.Thread(target=work, daemon=True).start()
for i, d in enumerate(pick):
    q.put((i, d))
q.join()
got.sort()
rows = (len(got) + cols - 1) // cols
sheet = Image.new("RGB", (cols * cell, max(rows, 1) * cell), (255, 255, 255))
for j, (i, im, t) in enumerate(got):
    im.thumbnail((cell - 8, cell - 8), Image.LANCZOS)
    sheet.paste(im, ((j % cols) * cell + (cell - im.width) // 2,
                     (j // cols) * cell + (cell - im.height) // 2))
sheet.save(out, "JPEG", quality=86)
print(f"{len(got)} images -> {out}")
for j, (i, im, t) in enumerate(got[:24]):
    print(f"  {t[:88]}")

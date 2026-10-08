#!/usr/bin/env python3
"""List a public MEGA folder tree over the API, without downloading anything.

megatools' megals wants an account for this, and megadl has no list-only mode,
so the inventory is read straight from MEGA's client API: request the node list
for the folder handle, then decrypt each node's attributes with the folder key
from the link fragment.
"""
import base64, json, struct, sys, urllib.request, urllib.parse
from Crypto.Cipher import AES

API = "https://g.api.mega.co.nz/cs"

def b64d(s):
    s = s.replace("-", "+").replace("_", "/")
    s += "=" * (-len(s) % 4)
    return base64.b64decode(s)

def a32(b):
    if len(b) % 4:
        b += b"\0" * (-len(b) % 4)
    return list(struct.unpack(">%dI" % (len(b) // 4), b))

def to_bytes(w):
    return struct.pack(">%dI" % len(w), *w)

def dec_attr(attr, key):
    d = AES.new(to_bytes(key), AES.MODE_CBC, b"\0" * 16).decrypt(attr)
    d = d.rstrip(b"\0")
    if not d.startswith(b'MEGA{'):
        return None
    try:
        return json.loads(d[4:].decode("utf-8", "replace"))
    except Exception:
        return None

def api(folder_id, payload):
    url = f"{API}?id=0&n={folder_id}"
    req = urllib.request.Request(url, data=json.dumps(payload).encode(),
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=120) as r:
        return json.loads(r.read().decode())

def walk(link):
    frag = link.split("/folder/", 1)[1]
    fid, _, fkey_b64 = frag.partition("#")
    fid = fid.split("/")[0]
    master = a32(b64d(fkey_b64))
    res = api(fid, [{"a": "f", "c": 1, "r": 1, "ca": 1}])
    nodes = res[0]["f"] if isinstance(res, list) else res["f"]
    out = []
    for n in nodes:
        name, size, typ = None, n.get("s", 0), n.get("t")
        k = n.get("k", "")
        if ":" in k:
            try:
                enc = a32(b64d(k.split(":", 1)[1]))
            except Exception:
                enc = []
            dk = []
            for i in range(0, len(enc), 4):
                blk = enc[i:i + 4]
                if len(blk) < 4:
                    break
                c = AES.new(to_bytes(master), AES.MODE_ECB).decrypt(to_bytes(blk))
                dk += a32(c)
            if typ == 0 and len(dk) >= 8:            # file key folds 32 -> 16
                dk = [dk[0] ^ dk[4], dk[1] ^ dk[5], dk[2] ^ dk[6], dk[3] ^ dk[7]]
            dk = dk[:4]
            if len(dk) == 4 and n.get("a"):
                at = dec_attr(b64d(n["a"]), dk)
                if at:
                    name = at.get("n")
        out.append({"h": n["h"], "p": n.get("p"), "t": typ,
                    "name": name or "(undecrypted)", "size": size})
    return fid, out

for link in sys.argv[1:]:
    fid, nodes = walk(link)
    # rebuild paths
    by = {n["h"]: n for n in nodes}
    def path(n):
        parts, seen = [], set()
        while n and n["h"] not in seen:
            seen.add(n["h"]); parts.append(n["name"]); n = by.get(n.get("p"))
        return "/".join(reversed(parts))
    files = [n for n in nodes if n["t"] == 0]
    dirs  = [n for n in nodes if n["t"] == 1]
    print(f"########## {fid}  ({len(dirs)} folders, {len(files)} files, "
          f"{sum(f['size'] for f in files)/1e9:.2f} GB)")
    ext = {}
    for f in files:
        e = ("." + f["name"].rsplit(".", 1)[-1].lower()) if "." in f["name"] else "(none)"
        ext.setdefault(e, [0, 0]); ext[e][0] += 1; ext[e][1] += f["size"]
    for e, (c, s) in sorted(ext.items(), key=lambda x: -x[1][1]):
        print(f"   {c:>8,} files {s/1e6:>12,.1f} MB  {e}")
    print("   -- top-level --")
    for n in sorted(dirs, key=lambda x: x["name"]):
        if by.get(n.get("p")) is None:
            kids = [f for f in files if f.get("p") == n["h"]]
            print(f"      [D] {n['name']}")
    for f in sorted(files, key=lambda x: -x["size"])[:25]:
        print(f"      {f['size']/1e6:>10,.1f} MB  {path(f)}")
    json.dump(nodes, open(f"/tmp/claude-0/-home-user-wonderleaf-books/"
                          f"af9e3fdd-8129-53fc-a69c-916ae3713d2b/scratchpad/"
                          f"megatools/tree_{fid}.json", "w"))

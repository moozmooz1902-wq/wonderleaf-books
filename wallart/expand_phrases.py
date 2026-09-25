#!/usr/bin/env python3
"""Have Claude write fresh, original wall-art phrases for thousands of micro-niches.

The hand-written banks give ~40-150 phrases per niche - not enough to fill
millions of listings without recolouring the same words. This asks Claude for
~80 new phrases per micro-niche (an audience or venue, in a given tone) through
the Batch API (asynchronous, half price), then writes each micro-niche out as a
normal bank file in banks/niches_ai/, which phrases.py and generate.py pick up
automatically.

    python3 expand_phrases.py plan            list micro-niches + cost estimate, sends nothing
    python3 expand_phrases.py submit          send the batch (needs ANTHROPIC_API_KEY)
    python3 expand_phrases.py collect         fetch results -> banks/niches_ai/*.txt

Options: --model (default claude-opus-5), --per 80 phrases per request,
--limit N to try a small sample first (recommended: --limit 20).
"""
import argparse, json, re, sys, time
from pathlib import Path

from phrases import load_niches, load_slots, norm

HERE = Path(__file__).resolve().parent
BANKS = HERE / "banks"
AI_DIR = BANKS / "niches_ai"
STATE = HERE / "out" / "expand_batch.json"

# per-million-token prices (input, output), batch = half of these
PRICES = {"claude-opus-5": (5.0, 25.0), "claude-sonnet-5": (2.0, 10.0), "claude-haiku-4-5": (1.0, 5.0)}

TONES = {
    "m": "motivational and uplifting",
    "f": "funny, cheeky and warm (British humour, never mean or crude)",
    "h": "heartfelt, sentimental and gift-worthy",
    "s": "practical signage and welcome signs for the venue (house rules, welcome, opening, service lines) with charm",
}

SYSTEM = """You write short text for typography wall art prints sold in the UK (A4/A3 prints, flat vector lettering, no pictures).

Rules for every phrase:
- ORIGINAL wording only. Never quote song lyrics, film or TV lines, poems or authors, and never use brand names, trademarks, sports club names, celebrity names or catchphrases.
- British English spelling and idiom (colour, mum, cosy, favourite).
- 1 to 14 words. Mark natural line breaks for the layout with " / " (for example "Life happens / coffee helps").
- It must make sense printed on a wall with nothing else around it, for the audience and tone given.
- Specific beats generic: use the audience's own vocabulary, in-jokes, tools, places and rituals.
- No profanity, nothing political, nothing that mocks a group.
- Every phrase distinct in wording and structure; do not reuse one template with a word swapped.
- Do not include the clichés listed in the request."""

SCHEMA = {
    "type": "object",
    "properties": {"phrases": {"type": "array", "items": {"type": "string"}}},
    "required": ["phrases"],
    "additionalProperties": False,
}


def slug(s):
    return re.sub(r"[^a-z0-9]+", "_", s.lower()).strip("_")[:60]


def micro_niches():
    """-> list of dicts: id, audience, parent niche, tone, venues."""
    niches = load_niches()
    out = []

    def add(aud, parent, tones, venues=None):
        meta = niches.get(parent)
        if not meta:
            return
        for t in tones:
            out.append({"id": f"ai_{slug(aud)}_{t}", "audience": aud, "parent": parent, "tone": t,
                        "venues": venues or meta["rooms"], "mood": meta["mood"]})

    for line in (BANKS / "audiences.txt").read_text().splitlines():
        if not line.strip() or line.startswith("#"):
            continue
        aud, parent, tones = [x.strip() for x in line.split("|")]
        add(aud, parent, tones)
    slots = load_slots()
    for h in slots["hobby"]:
        add(f"{h[0].lower()} fans ({h[1].lower()}s)", "hobbies", "fh", [h[3], "Man Cave", "Living Room", "Office"])
    for b in slots["breed"]:
        add(f"{b[0]} owners", "pets", "fh")
    for j in slots["job"]:
        add(f"{j[2]} (the {j[3]})", "thank_you_jobs", "fm", [j[3].title(), "Staff Room", "Office"])
    # every venue named in any bank gets its own signage + motivational run
    seen = {m["audience"].lower() for m in out}
    for nid, meta in niches.items():
        if nid.startswith("ai_"):
            continue
        for v in meta["rooms"]:
            if v.lower() not in seen:
                seen.add(v.lower())
                add(f"a {v}", nid, "sm" if nid.startswith(("biz_", "office", "motivation")) else "sh", [v])
    # keep ids unique
    uniq = {}
    for m in out:
        uniq.setdefault(m["id"], m)
    return list(uniq.values())


def examples_for(meta, k=12):
    ex = [p for p in meta["fixed"] if " ~ " not in p][:k]
    return ex


def request_for(m, niches, per):
    parent = niches[m["parent"]]
    avoid = ", ".join(f'"{p.replace(" / ", " ")}"' for p in examples_for(parent, 15))
    user = (f"Audience / market: {m['audience']}\n"
            f"Tone: {TONES[m['tone']]}\n"
            f"Where it will hang: {', '.join(m['venues'][:8])}\n"
            f"Write {per} different phrases.\n"
            f"Clichés already covered - do not repeat these or close variants: {avoid}")
    return {"custom_id": m["id"][:64],
            "params": {"model": ARGS.model, "max_tokens": 8000, "system": SYSTEM,
                       "output_config": output_config(),
                       "messages": [{"role": "user", "content": user}]}}


def output_config():
    oc = {"format": {"type": "json_schema", "schema": SCHEMA}}
    if "haiku" not in ARGS.model:       # effort is not accepted on Haiku 4.5
        oc["effort"] = "low"            # list-writing needs little deliberation
    return oc


def cmd_plan(ms):
    niches = load_niches()
    reqs = [request_for(m, niches, ARGS.per) for m in ms]
    in_tok = sum(len(json.dumps(r["params"])) for r in reqs) / 3.6
    out_tok = len(reqs) * ARGS.per * 16 + len(reqs) * 400      # phrases + JSON + light thinking
    pin, pout = PRICES.get(ARGS.model, (5.0, 25.0))
    cost = (in_tok * pin + out_tok * pout) / 1e6 * 0.5
    by_parent = {}
    for m in ms:
        by_parent[m["parent"]] = by_parent.get(m["parent"], 0) + 1
    print(f"{len(ms):,} micro-niche requests  x {ARGS.per} phrases = ~{len(ms) * ARGS.per:,} new phrases")
    for p, c in sorted(by_parent.items(), key=lambda kv: -kv[1]):
        print(f"  {p:22s} {c:>5}")
    print(f"model {ARGS.model}: ~{in_tok / 1e6:.1f}M input + ~{out_tok / 1e6:.1f}M output tokens "
          f"-> about ${cost:,.0f} at Batch API prices (50% off)")
    print("sample request:\n" + reqs[0]["params"]["messages"][0]["content"])


def client():
    import anthropic
    return anthropic.Anthropic(base_url="https://api.anthropic.com")


def cmd_submit(ms):
    niches = load_niches()
    reqs = [request_for(m, niches, ARGS.per) for m in ms]
    c = client()
    ids = []
    for i in range(0, len(reqs), 10000):
        b = c.messages.batches.create(requests=reqs[i:i + 10000])
        ids.append(b.id)
        print("submitted", b.id, len(reqs[i:i + 10000]))
    STATE.parent.mkdir(exist_ok=True)
    STATE.write_text(json.dumps({"batches": ids, "micro": {m["id"][:64]: m for m in ms}}, indent=1))
    print("Batches usually finish within an hour. Then run: python3 expand_phrases.py collect")


BANNED = re.compile(r"\b(disney|marvel|harry potter|hogwarts|star wars|nike|adidas|coca|pepsi|"
                    r"starbucks|costa|greggs|guinness|jack daniel|lego|barbie|netflix|friends|"
                    r"beatles|queen|oasis|premier league|manchester united|liverpool fc|chelsea|"
                    r"arsenal|keep calm and carry on)\b", re.I)


def clean(p):
    p = re.sub(r"\s+", " ", p.strip().strip('"').strip("“”"))
    p = re.sub(r"\s*/\s*", " / ", p)
    if not p or len(p) > 100 or BANNED.search(p) or len(p.replace(" / ", " ").split()) > 16:
        return None
    return p[:1].upper() + p[1:]


def cmd_collect():
    st = json.loads(STATE.read_text())
    c = client()
    AI_DIR.mkdir(exist_ok=True)
    seen = set()
    for meta in load_niches().values():
        if not meta["id"].startswith("ai_"):
            seen.update(norm(p) for p in meta["fixed"])
    wrote = kept = dropped = 0
    for bid in st["batches"]:
        b = c.messages.batches.retrieve(bid)
        if b.processing_status != "ended":
            print(bid, b.processing_status, "- not finished, try again later"); continue
        for r in c.messages.batches.results(bid):
            if r.result.type != "succeeded":
                continue
            m = st["micro"].get(r.custom_id)
            text = next((x.text for x in r.result.message.content if x.type == "text"), "")
            try:
                phrases = json.loads(text)["phrases"]
            except Exception:
                continue
            good = []
            for p in phrases:
                p = clean(p)
                if p and norm(p) not in seen:
                    seen.add(norm(p)); good.append(p)
                else:
                    dropped += 1
            if not good:
                continue
            parent = load_parent(m["parent"])
            head = [f"name: {m['audience']} ({TONES[m['tone']].split(',')[0]})",
                    f"parent: {m['parent']}",
                    f"noun: {'|'.join(parent['noun'])}",
                    f"rooms: {'|'.join(m['venues'])}",
                    f"mood: {', '.join(m['mood'])}"]
            if parent["occasion"]:
                head.append(f"occasion: {'|'.join(parent['occasion'])}")
            (AI_DIR / f"{r.custom_id}.txt").write_text("\n".join(head) + "\n---\n" + "\n".join(good) + "\n")
            wrote += 1; kept += len(good)
    print(f"wrote {wrote:,} micro-niche banks, {kept:,} new phrases ({dropped:,} dropped as duplicate/unsafe)")
    print("Re-run: python3 generate.py --plan-only  to see the new allocation")


_PARENTS = None


def load_parent(pid):
    global _PARENTS
    if _PARENTS is None:
        _PARENTS = load_niches()
    return _PARENTS[pid]


def main():
    global ARGS
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["plan", "submit", "collect"])
    ap.add_argument("--model", default="claude-opus-5")
    ap.add_argument("--per", type=int, default=80)
    ap.add_argument("--limit", type=int)
    ARGS = ap.parse_args()
    ms = micro_niches()
    if ARGS.limit:
        ms = ms[:: max(1, len(ms) // ARGS.limit)][: ARGS.limit]
    {"plan": lambda: cmd_plan(ms), "submit": lambda: cmd_submit(ms), "collect": cmd_collect}[ARGS.cmd]()


if __name__ == "__main__":
    main()

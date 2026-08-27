# 04 — Metadata playbook

**The governing rule: one listing = one buyer intent.**

Title owns the primary phrase. Tags cover *adjacent* phrases the title does not
contain. The description sells the use case in natural language. Nothing repeats
anything.

Machine-readable limits: [`../data/platform_specs.json`](../data/platform_specs.json).

---

## Redbubble

| Field | Limit | Rule |
|---|---|---|
| Title | **40–50 chars** | Front-load the strongest keyword. Tight, not stuffed. |
| Tags | **15 slots × 50 chars** | Multi-word **phrases**, never single broad words |
| Description | — | Natural language, use cases and gift contexts. **Must not repeat the title verbatim.** |

**Tag mix: 60% specific long-tail / 40% broader category.**

- Good: `vintage 1970s bass tournament shirt`
- Dead: `fishing`

The title keyword does **not** need to also be a tag — the title field is already
weighted heavily. Spend the 15 slots on terms the title doesn't have.

Redbubble's ranking rewards, in order: (1) specific multi-word phrase tags,
(2) a title that matches those tags naturally, (3) a description that does *not*
repeat the title.

**Ban list for this platform:** tag spamming (a named ban reason), trademarked
terms in tags (a named ban reason), and the same design re-uploaded in many
colourways as separate listings.

---

## Etsy

| Field | Limit | Rule |
|---|---|---|
| Title | up to 140 chars | First ~40 characters carry the ranking and display weight |
| Tags | **13 slots × 20 chars** | Use **all 13**. Spaces count. |
| Description | — | Natural language; supports the title, doesn't repeat it |
| Attributes | structured | Fill every one — colour, orientation, style, room |

**Fill the 20 characters.** `hand-painted floral` (19) beats `floral` (6). Every
unused character is lost surface area — Etsy uses tag detail to infer the "vibe"
of a listing, which is itself a ranking input.

**Do not repeat title words in tags.** Title carries the primary phrase; the 13
tags exist to cover *related but different* searches.

**Décor titles must carry a colour word and, where it fits, a room word** — that
is the grammar decorators actually search in:

```
Sage Green Botanical Line Art Print, Set of 3 Minimalist Leaf Wall Art,
Neutral Living Room Decor, Digital Download
```

---

## Amazon Merch on Demand

| Field | Limit | Rule |
|---|---|---|
| Title | **75 chars, enforced** | Over-limit titles get flagged and progressively replaced with an AI rewrite (brand-registered sellers get a 14-day review window) |
| Brand | short | Treat as a keyword slot, not a vanity name |
| Bullets | 2 bullets, **10–255 chars** each | Only the **first ~1,000 bytes across all bullets is indexed** |
| Description | — | Supporting copy |

**~67% of Amazon shoppers are on mobile, where each bullet truncates at about
70–80 characters.** The first 80 characters of bullets 1 and 2 carry nearly all
the SEO and conversion weight.

Bullet structure: **Result → Feature → Proof.** Capitalise the first 2–4 words as
a visual anchor. Highest-intent keywords go first.

Write for **buying intent**, not keyword coverage: product type, who it's for,
the occasion. Not every keyword you could physically fit.

**Never** put a competitor's or any brand's trademarked name in the title,
bullets, description, or backend search terms. Backend keyword stuffing with
brand names is actively reported by rights-holders and is a named violation.

---

## Displate

| Field | Rule |
|---|---|
| Title | Evocative and specific; this is a collector market, name the *feeling* |
| Tags | Subject + style + mood + colour |
| Collection | Group families of work — collections are a browse surface |
| Artist statement | Short; it's part of the premium positioning |

Displate has no published title/tag character limits, but its **artwork** gate is
the strict one — see `02_POSTER_RESEARCH.md` G3 rules. Rejected work cannot be
resubmitted; the system blocks it as a duplicate.

---

## Anti-patterns (all currently present in our generated data)

| Anti-pattern | Why it kills the listing |
|---|---|
| Title = 12 comma-separated keywords | Over Amazon's 75-char limit; unreadable on Etsy; diluted on Redbubble |
| Tags that repeat title words | Wastes every repeated slot; explicitly discouraged on Etsy and Redbubble |
| Single-word tags (`cat`, `space`, `funny`) | Ranks for nothing; competes with millions |
| Description restating the title | Redbubble scores this **down** |
| Same metadata across 40 colourways | Duplicate-spam signature |
| No colour word in a décor title | Invisible to how decorators actually filter |
| No relationship word in a gift title | Invisible to gift search on Amazon and Etsy |
| Brand names in backend search terms | Named trademark violation; account risk |

---

## Generation contract for the model

When the pipeline asks a model for metadata, it must receive **one concept and
one platform** and return exactly:

```json
{
  "platform": "redbubble",
  "title": "≤50 chars, primary phrase front-loaded",
  "tags": ["15 phrase tags, ≤50 chars each, none repeating title tokens"],
  "description": "2–4 sentences, use cases and gift context, no title repetition"
}
```

Never ask one call to produce metadata for all platforms at once — the limits
conflict, and the model averages them into something that violates all four.
`pod/tools/build_prompt.py` emits one call per (concept × platform).

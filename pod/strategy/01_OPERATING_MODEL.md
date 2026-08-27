# 01 — The operating model: six gates

Every concept passes through six gates in order. A concept that fails any gate is
**killed, not repaired by loosening the gate**. This is enforced in code by
`pod/tools/validate_concept.py` against `pod/data/quality_rubric.json`.

```
  DEMAND ──▶ ANGLE ──▶ VISUAL DNA ──▶ PRODUCTION ──▶ METADATA ──▶ IP + DEDUP
   G0         G1           G2             G3            G4           G5/G6
```

---

## G0 — Demand anchor (hard gate)

A concept starts life as a **phrase a buyer types**, never as a theme.

Required fields:

| Field | Meaning |
|---|---|
| `demand.query` | The exact primary search phrase, 2–6 words |
| `demand.cluster` | The family of related phrases it belongs to |
| `demand.adjacent[]` | 8–20 sibling phrases used for tags |
| `demand.evidence` | Where the demand signal came from |
| `demand.est_monthly_volume` | Integer estimate, or null with evidence type `qualitative` |
| `demand.competition` | `low` / `medium` / `high` + result-count estimate |

**Thresholds that the industry converges on:**

- Root keyword ≥ **1,000 monthly searches** (US) for a standalone niche, *or* a
  long-tail ecosystem of 3+ phrases summing to ≥1,000.
- Prefer **< ~2,000–3,000 competing listings** for the exact phrase.
- On Amazon, a niche is viable if top-page listings show BSR in the sellable
  range and are not dominated by established brands with heavy review counts.

**Kill rules:** no query; query is a single generic noun (`cat`, `space`,
`motivation`); competition `high` **and** no differentiating angle at G1.

### Where demand clusters come from
1. Marketplace autocomplete (Etsy, Amazon, Redbubble search box) — free, and it
   is literally a list of what people type.
2. Bestseller / trending pages per platform.
3. Pinterest trending searches — leading indicator for décor and aesthetics.
4. Keyword tools (Merch Informer, Everbee, Sale Samurai, Helium 10) for volume
   and competition numbers.
5. Seasonal calendars — with an **8–10 week lead** before the target date.

---

## G1 — Angle (specificity gate)

> "A design that speaks to French bulldog owners will always outsell a design
> that speaks to dog lovers in general."

The angle is the intersection that makes this listing *not* the other 400,000.

Required: `angle.audience`, `angle.insider_vocab[]`, `angle.emotional_job`.

**The specificity test** — a concept passes only if you can answer all three:
1. **Who exactly** buys this? (Not "people who like nature" — "someone who
   boulders outdoors and knows what a crash pad is".)
2. **What do they call themselves**, in their own vocabulary? Insider language is
   the belonging signal; outsiders don't recognise it, which is the point.
3. **What job does it do?** Identity flag / gift / room décor / collection piece.

**Emotional jobs** (pick exactly one):
`identity_flag`, `in_group_joke`, `gift_for_relationship`, `room_decor`,
`fandom_shrine`, `milestone_marker`, `values_statement`, `nostalgia_hit`.

**Kill rules:** audience is "everyone" or a demographic bucket; the joke or motif
is already the top result for the query; emotional job is unset.

---

## G2 — Visual DNA (anti-slop gate)

The generator must be constrained on **six axes** or it returns the mean.

| Axis | Required content |
|---|---|
| `style_id` | Reference into `poster_style_dna.json` / `tshirt_layout_archetypes.json` |
| `palette` | 3–5 hex values + palette name |
| `composition` | Focal structure, negative space, edge behaviour |
| `typography` | Named type pairing, max 2–3 families, hierarchy |
| `texture` | Grain / halftone / risograph misreg / clean vector / none |
| `avoid[]` | Explicit negative constraints |

**The thumbnail check is part of this gate:** `visual.reads_at_250px` must be
true, and the concept must state *what* carries it at that size (silhouette,
colour block, or one word of type).

**Kill rules:** any axis unset; palette > 6 colours; more than 3 type families;
"detailed intricate highly detailed 8k" style padding, which is exactly the
prompt language that pulls output back to the mean.

---

## G3 — Production

Pulled from `data/platform_specs.json`, not invented per concept.

**Posters**
- Displate: min 2900px short edge, recommended 4000×5600, **1:1.4 ratio**, 300 DPI,
  sRGB, ≤30MB, JPG/PNG/WEBP/AVIF. Keep text ≥200px from every edge. No frames
  drawn inside the artwork. No very dark compositions. No upscaled or grainy art.
- Redbubble art print: 3840×3840 square canvas covers all print sizes; ~6000×8000
  if one file must serve apparel and print. Max 13500×13500 / 300MB. JPEG or PNG
  only. Actual pixel count is what the printer uses — DPI metadata is irrelevant.
- Etsy printable: export the **ratio families** buyers actually frame —
  2:3 (12×18, 24×36), 3:4 (18×24), 4:5 (16×20), 11×14, plus ISO A-series
  (1:1.414) for non-US buyers.

**T-shirts**
- 4500×5400 px, 300 DPI, **transparent** PNG, sRGB, ≤25MB.
- Design must survive on both light and dark garments — either two exports, or a
  palette that works on both.
- No hairlines, no <14pt effective type, no near-invisible gradients — DTG fills
  in fine detail.

**Kill rules:** aspect ratio not in the platform's allowed set; no transparency on
an apparel file; text inside the edge buffer; single export used for both a 1:1.4
metal print and a 2:3 poster.

---

## G4 — Metadata

One listing = **one intent**. Full per-platform rules in `04_METADATA_PLAYBOOK.md`.

Summary of the binding limits:

| Platform | Title | Tags | Body |
|---|---|---|---|
| Redbubble | 40–50 chars, primary phrase front-loaded | 15 × 50 chars, **phrases** | Description must not repeat the title |
| Etsy | up to 140 chars, first ~40 carry the weight | 13 × 20 chars, no title repeats | Description + attributes |
| Amazon Merch | **75 chars max** (enforced) | — (brand + bullets) | 2 bullets, 10–255 chars; first ~80 chars of bullets 1–2 do the work; only first 1,000 bytes indexed |
| Displate | Title + tags + collection | — | Short artist statement |

**Kill rules:** title over the platform limit; any tag duplicating a title token
set; description that restates the title; tag list containing single generic
words in more than 40% of slots.

---

## G5 — IP clearance

See `05_IP_SAFETY.md`. Machine rules in `data/ip_risk_rules.json`.

Every text string that ships — art copy, title, tags, description, **and backend
search terms** — is screened. Trademark risk attaches to the *use in commerce*,
so a clean image with a franchise name in the tags is still an infringement.

**Kill rules:** any denylist hit; any phrase matching a high-risk pattern without
a cleared `ip.screened_against[]` record; "in the style of" a living artist.

---

## G6 — Dedup

- Hard key: `(style_id | layout_id, palette_id, subject_lemma)` must be unique.
- Soft key: normalised title trigram overlap > 0.6 against any existing concept.
- Colourways, garment colours, and sizes are **product options**, never separate
  concepts.

---

## Batch composition

A healthy batch of 50 concepts:

| Share | Type | Rationale |
|---|---|---|
| 50% | **Evergreen** — occupations, breeds, hobbies, botanical, abstract décor | Baseline that pays every month |
| 20% | **Seasonal**, loaded 8–10 weeks early | Predictable demand spikes |
| 20% | **Style-led décor sets** (families of 3 for gallery walls) | Raises average order value |
| 10% | **Trend probes** — short-life aesthetic or humour bets | Cheap options on the upside |

Design décor posters in **families of three**, not singles — gallery-wall
purchasing is a documented buying pattern and multi-print sets carry the highest
average order value in printable wall art.

---

## Cadence

1. **Weekly:** refresh demand clusters from autocomplete + trending + bestseller pages.
2. **Per batch:** generate → validate → kill → produce only survivors.
3. **Day 30 / Day 60:** pull sales by concept. Promote the winning **demand
   cluster** — build 5–10 more concepts inside it. Cull the dead. Never clone the
   winning *image*; that is how you rebuild the duplicate-spam problem.
4. **Quarterly:** re-run the IP screen over the live catalogue — trademarks get
   registered after you list.

## Success metric

Stop counting listings. Track:

```
gate_pass_rate      = concepts passing all 6 / concepts generated   (target 20–40%)
sellers_per_100     = concepts with ≥1 sale in 60d per 100 published
revenue_per_concept = the only number that compounds
```

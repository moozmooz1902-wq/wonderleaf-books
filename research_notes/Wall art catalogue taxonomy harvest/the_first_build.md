# What to build first, and why every line of evidence points at it

10 October 2026. This note exists because four independent pieces of evidence —
gathered by different methods, from different sources — converged on the same
product. That has not happened before in this project.

## The convergence

**Vintage travel posters of named UK places, in the poster-with-margin format,
with the place name set as type rather than drawn.**

| Evidence | Where it came from | Result |
|---|---|---|
| `vintage` beats the base rate | seller's own watchers | 2.30% vs 1.05%, **z = +6.6** |
| UK places beat the base rate | seller's own watchers | 7.91% vs 1.05%, **z = +12.6** on 354 listings |
| The format already exists in our code | `wallart/render.py`, grammar G6 | *"an art panel inside a cream type margin — this is our architecture already"* |
| It is the dominant live form | 24 random Fy! images titled "vintage" | travel posters of Mykonos, Paris, Rome, Taj Mahal, Genoa, Patagonia, Great Britain |

And the seller's own best clean performers are already this exact thing:
*Cap de Formentor Mallorca* (4 watchers), *Sa Calobra Mallorca Cycling* (3),
*Paris-Roubaix* (3), *Sheffield — The Steel City* (5, sixth in the catalogue).

Nothing about it is encumbered. The style is a style; the places are places.

## Why the type being composited matters

The live examples all put the place name in letterspaced caps under the panel.
That is the one thing a diffusion model cannot be trusted with, and the one
thing this repo already does well — `wallart/render.py` draws type to an
asserted size contract. So the division is clean:

- **FLUX draws the panel** — the harbour, the ridge, the pier, no lettering.
- **The renderer sets the name** — exact, legible, every time.
- **The OCR gate rejects** any panel where the model wrote text anyway.

This also means near-duplicate checking must run on the panel, not the title —
confirmed from live data in `first_party_demand_watchers.md`, where the live
catalogue's titles are only 2.1% duplicated while the pictures are the problem.

## The second product: charcoal breed portraits

Same logic, different axis. Of 24 random Fy! images matching
charcoal/sketch/graphite, **nine were dog portraits** — head-and-shoulders in
graphite on white, breed name in small letterspaced caps beneath.

| Evidence | Result |
|---|---|
| `charcoal` | 5.96% vs 1.05% base, **z = +5.9** — the strongest technique in the project |
| `sketch` | 5.26%, **z = +4.4** |
| Enumerable subject list already held | ~400 dog breeds, plus cats, horses, cattle, chickens |
| Grammar | G8, "one object, vast white space, letterspaced caps beneath" |

Again the caption is set type, not drawn. Again nothing is encumbered.

## What NOT to build, on the same evidence

- **Anything funny or cute.** 0.39% and 0.24% against a 1.05% base. 12,731
  slogan listings in the live catalogue earn 50 watchers between them.
- **Anything licensed.** The top twenty watched listings are almost all
  properties — Escher, Banksy, Hockney, Snoopy, Mortal Kombat, The Italian
  Job. They perform, and we cannot have them.
- **Colour-named variants as a volume play.** Colour words in titles do
  nothing: nothing clears z = 3 either way, and `orange` — the complementary
  "house trick" from the supply-side notes — is slightly *below* base at
  0.28%. Colour belongs in the picture, not in the title or the SKU axis.

## Honest status

Everything above rests on watcher counts with a 1.05% base, where the biggest
single signal is 68 listings and the smallest is 5. The σ test keeps the
direction honest but not the magnitude. This is a strong steer for a first
run of a few thousand, measured against real listings — not a licence to
generate a million before anything has been tested.

The image-level learning pass (styles and colour measured from pixels across
the competitor corpus) is still running and is not reflected here.

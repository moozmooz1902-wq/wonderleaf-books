# TikTok Shop strategy — wall-art print sets (UK)

Written 29 Aug 2026. Grounded in live data pulled from the three accounts you sent.

---

## 1. What your benchmark accounts actually show

| Account | Followers | Total likes | Videos | Account age | Likes per video |
|---|---:|---:|---:|---|---:|
| @crush_gallery88 — "Crush Gallery" | 1,496 | 4,445 | 337 | ~6 months | **13** |
| @incase_studios — "IncaseUK" | 1,961 | 22,800 | 271 | ~5 years | **84** |
| @renmaigb — "Luxe Art" | 27 | 22 | 68 | ~4 months | **0.3** |

Read that carefully, because it changes the plan:

- **Crush Gallery is not crushing it.** 337 videos in six months (~2/day) for 1,496
  followers and 13 likes per video. That is a volume machine running at close to
  zero engagement. It may still make money — TikTok Shop conversion doesn't need
  likes — but nothing here proves it does.
- **Luxe Art is a failed account.** 68 videos, 22 total likes. This is what
  spray-and-pray looks like when it doesn't work. Same playbook, no result.
- **IncaseUK is the only real business** — and it breaks the pattern. Five years
  old, *custom* designs, 4,250+ completed orders, an Etsy shop and a WhatsApp
  number in bio. It converts on trust and personalisation, not volume.

**Conclusion:** volume is the entry ticket, not the edge. Two of three accounts
running high-volume generic wall art are flat. Don't copy the account that posts
most; copy the one that *sells* most, and use automation to hit its cadence
without its labour cost.

## 2. Your positioning

Generic "modern wall art" is the losing bucket — it's what Crush Gallery and
Luxe Art both sell. IncaseUK wins on **specificity**. So:

- Pick **one room and one buyer**, not "home decor". E.g. *rented UK flats,
  first-time renters, walls you can't drill.*
- Lead the product on the **constraint you solve**, not the picture:
  no drilling, fits above a standard 3-seater, arrives in one box, under £30.
- Sell the **set**, never the single print. The 3-frame trio is the offer —
  it removes the "what else goes next to it" problem, which is the actual
  reason blank walls stay blank.

## 3. The video format

Three beats, ~9 seconds. This is what the pipeline generates.

| Beat | Time | Job | On-screen text |
|---|---|---|---|
| 1. Hook | 0–2.5s | The bare, disappointing wall. Tension. No product. | The problem, ≤7 words |
| 2. Reveal | 2.5–5.5s | The trio goes up. The change. | The mechanism, ≤7 words |
| 3. Payoff | 5.5–9s | Styled wide shot. Calm, aspirational. | The result, ≤7 words |

Rules that matter more than the visuals:

- **The first 1.5 seconds is the whole game.** If the hook text isn't readable
  and relatable before the viewer's thumb moves, nothing else counts.
- **Never open on the product.** Open on the problem. Product-first videos are
  read as ads and swiped.
- **Always add a trending sound in-app at low volume.** Silent uploads are
  suppressed. The pipeline ships a silent or voiceover track deliberately so you
  add the sound in TikTok — 5 seconds of work, meaningful reach difference.
- **Rotate the angle, not the product.** One product × 20 angles beats
  20 products × 1 angle. Angles live in `config/products.yaml` and the pipeline
  refuses to reuse a (product, angle) pair within 21 days.

## 4. Cadence and the posting workflow

**The constraint you must design around:** you cannot legally auto-post publicly
*and* keep the product link. See `README.md` §"Why this doesn't auto-post" for
the three separate walls. The practical answer:

**Batch weekly, schedule ten days ahead.**

1. Sunday: the GitHub Action builds 7 videos and emails you an artifact.
2. Sunday, ~15 minutes: open TikTok Studio on desktop, upload all 7, tag the
   product on each, set a schedule slot, turn on the AI-content toggle.
3. Monday–Saturday: you touch nothing. Videos post themselves.

That is genuinely hands-off six days a week, and it keeps the Shop link, which
is the only reason the video exists.

**Cadence target: 2–3 per day, every day.** Crush Gallery's ~2/day is the floor
for this category. TikTok Studio schedules 10 days ahead, so one weekly sitting
covers you.

**Posting times (UK):** 7–9am, 12–1pm, 7–10pm. Evening is strongest for home
decor — people scroll on the sofa looking at the wall you're selling to.

## 5. The link problem

You have three options and they are not equal:

1. **Product tag on the video** (best). Requires TikTok Shop seller or approved
   affiliate. Tag it manually when scheduling. Highest conversion by a distance.
2. **Bio link** — what Crush Gallery does (`vt.tiktok.com/...` → TikTok Shop).
   Works, loses most of the traffic to the extra tap.
3. **Pinned comment** with the link. Weakest, but free and instant.

Do (1). Use (3) as a backup on every video regardless — it costs nothing.

## 6. Compliance — the stuff that gets accounts killed

Luxe Art has 27 followers after 68 videos. Accounts in this category do get
throttled, and the causes are boringly consistent:

- **Disclose AI content.** Use the in-app "AI-generated content" toggle, not just
  a hashtag. Undisclosed synthetic media is a removal reason.
- **Never invent claims.** No fake reviews, fake stock counts, fake delivery
  promises, fake discounts. The script writer is explicitly instructed to refuse
  these — don't add them by hand afterwards.
- **Don't post the same video twice.** Duplicate detection is real. The 21-day
  angle cooldown exists for this.
- **Don't run posting bots on a fresh account.** Warm up: 1–2 posts/day for the
  first week, engage from the account like a person, then scale to 3.
- **One account, one niche.** Mixed-topic accounts don't get a stable audience.

## 7. What to measure, and when to kill

Track weekly, not daily. Daily numbers are noise.

| Metric | Healthy | Act if |
|---|---|---|
| Avg. watch time | >55% of length | <40% → hook is failing, rewrite beat 1 |
| Views per video | rising week on week | flat for 3 weeks → change the angle set |
| Click-through to product | >1.5% | <0.5% → the offer or price is wrong, not the video |
| Conversion | >2% of clicks | low with good CTR → listing/photos problem, not TikTok |

**Kill criteria:** if after 60 videos across ≥8 distinct angles you're under
500 views median, the *product* is the problem, not the content. Change the
product before making video 61. Crush Gallery made 337 videos without doing this.

## 8. First 30 days

- **Week 1** — Set up TikTok Shop seller/affiliate. Fill `products.yaml` with
  one product and 15+ angles. Run `--dry-run`, then build 7 real videos.
  Post 1/day manually so you learn what the app does.
- **Week 2** — Go to 2/day via the weekly batch. Add a second product.
- **Week 3** — Read the analytics. Kill the bottom third of angles, write five
  new ones based on which hooks held watch time.
- **Week 4** — 3/day. Pin the link comment on everything. Decide product-level
  keep/kill on the week-1 product using the table in §7.

Do not scale spend before week 3. The pipeline costs pennies per video; the
expensive mistake is 300 videos for a product nobody wants.

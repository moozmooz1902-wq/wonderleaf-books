# TikTok Shop strategy — wall-art print sets (UK)

Written 29 Aug 2026. Grounded in live data pulled from the three accounts you sent.

---

## 1. What your benchmark accounts actually show

| Account | Followers | Total likes | Videos | Account age | Likes per video |
|---|---:|---:|---:|---|---:|
| @crush_gallery88 — "Crush Gallery" | 1,496 | 4,445 | 337 | ~6 months | **13** |
| @incase_studios — "IncaseUK" | 1,961 | 22,800 | 271 | ~5 years | **84** |
| @renmaigb — "Luxe Art" | 27 | 22 | 68 | ~4 months | **0.3** |

**Engagement is a bad proxy for TikTok Shop revenue, and this table proves it.**
Crush Gallery reports 260,000+ sales against 13 likes per video. Both numbers
are real and they do not contradict each other: Shop videos convert on product
intent, not on likes. Someone who taps the pin, buys, and never engages with the
video leaves no trace in the figures above.

So read the table as *reach and engagement only*:

- **Crush Gallery is the model to copy.** ~2 videos/day for six months, generic
  modern wall art, low engagement, very high sales. That is a volume-and-catalogue
  machine, and it works. The lesson is that you do not need a beloved account —
  you need enough shots on goal against enough listings.
- **Luxe Art shows the same playbook failing.** 68 videos, 22 likes, and by all
  appearances no traction. Same category, same approach, no result. The
  difference between it and Crush Gallery is volume and catalogue depth, so
  those are the two variables to push hardest.
- **IncaseUK is a different business** — five years old, custom designs, Etsy and
  WhatsApp in bio. It converts on trust and personalisation. Worth stealing its
  *specificity* in the copy, but its model is not yours.

**Conclusion:** go wide. Maximum listings, maximum videos, ruthless culling of
whatever does not sell. Judge everything on units sold, never on likes — the
metric that would have told you Crush Gallery was failing is the metric that
is wrong.

## 2. Positioning: wide catalogue, narrow hooks

These pull in opposite directions and both are right, at different levels:

- **Catalogue: go wide.** Every listing is an independent shot on goal, and you
  have 100 slots. Crush Gallery wins on breadth, not on taste. Fill the slots.
- **Each individual video: go narrow.** A video that opens on "beautiful wall
  art" stops nobody. A video that opens on *"renting and not allowed to drill"*
  stops the person that is true for. Breadth at the shop level, specificity at
  the video level.

So the offer stays sharp even as the catalogue sprawls:

- Sell the **set**, never the single print. The trio removes the "what goes next
  to it" problem, which is the actual reason blank walls stay blank.
- Lead on the **constraint you solve** — no drilling, fits above a standard
  3-seater, one box, under £30 — not on the picture.
- Let the angle do the targeting. One product against thirty angles reaches
  thirty different people without thirty different listings.

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

**Kill criteria:** judge the *listing*, on units sold, using
`python -m wonderfeed.listings review` (§8). Do not kill on views or likes.
A listing pulling traffic and converting nothing is dead; a listing with no
traffic yet has not been tested. Those need opposite responses, which is the
whole reason that tool exists.

## 8. Listing rotation — working the 100 cap

The cap is the real constraint on this business. A slot holding a listing that
has had twenty videos and no sales is costing you a test you cannot run.

**The loop, weekly:**

1. Export product performance from Seller Center to CSV.
2. `python -m wonderfeed.listings import --csv export.csv`
3. `python -m wonderfeed.listings review`
4. Cull what it flags, delist those in Seller Center, list replacements into the
   freed slots.

**The judgement it applies** — and the distinction that matters most:

| Verdict | Meaning | What to do |
|---|---|---|
| `KEEP` | Sold ≥1 unit in the window | Keep feeding it videos |
| `CULL` | Real traffic, zero units | Dead. The listing converts nothing — free the slot |
| `WATCH` | Barely any traffic, zero units | **Not** dead. Untested. Point more videos at it |
| `TOO EARLY` | Under 14 days live | Leave it alone |
| `NO DATA` | No stats imported | Import a CSV |

`CULL` and `WATCH` look identical on a sales report — both are zero — and they
need opposite responses. Killing a `WATCH` listing throws away a product you
never actually tested; keeping a `CULL` listing burns a slot indefinitely. This
is the single most valuable call the tool makes.

Thresholds live under `listings:` in `settings.yaml`. The default
`cull_after_videos: 15` says: fifteen videos at a product with nothing to show
is enough evidence.

## 9. First 30 days

- **Week 1** — TikTok Shop seller/affiliate set up. List 10–15 products to start
  filling slots. Generate angles in bulk
  (`python -m wonderfeed.angles --product X --count 30 --write`), then build and
  post 1–2/day manually so you learn what the app does.
- **Week 2** — Go to 2–3/day off the weekly batch. Register every listing with
  `listings add`. Push toward 30+ live listings.
- **Week 3** — First real cull cycle: import the CSV, run `review`, delist the
  dead, refill the freed slots. Rewrite angles based on which hooks held watch
  time.
- **Week 4** — 3/day, aiming at the cap. Cull weekly from here on. The catalogue,
  not the account, is the asset you are building.

Do not scale spend before week 3. At ~£0.10/video the content is nearly free;
the expensive mistake is 300 videos pointed at listings you never culled.

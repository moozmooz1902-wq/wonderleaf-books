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

## 3. What to sell — filling 100 slots

Twelve niches ship in `wonderfeed/catalogue.py`, drawn from what recurs across
2026 print-on-demand and Etsy trend reporting: **cars, family, botanical,
identity, music, sport, travel, affirmation, pets, humour, kids, food.** Your
two instincts — family and cars — are both in there and both well supported.

**The rule that decides whether a listing sells: identity beats aesthetics.**
Across print-on-demand, role- and passion-specific designs consistently outsell
generic ones in the same category. So:

| Weak (a category) | Strong (a buyer) |
|---|---|
| "classic car prints" | Mk1 Golf GTI — for the person who actually owned one |
| "family wall art" | first Father's Day, from the baby's point of view |
| "nurse art" | NICU nurse, night shift |
| "botanical prints" | the three plants that survive a north-facing flat |

The right-hand column is what the catalogue generator is instructed to produce.
It is also why one product supports thirty angles: the buyer is specific enough
to have thirty different bad days you can open a video on.

### Intellectual property — read this before listing anything

This is the one that closes shops rather than removing videos. On TikTok Shop an
IP complaint costs violation points, listing removal and withheld balance, and a
pattern of them suspends the seller account — all 100 slots at once. The expected
cost of one risky listing is far higher than it could ever earn.

**The finding that should change your plan: cars are one of the most dangerous
niches, not just the badge.** Vehicle designs are protected by copyright, design
right *and* trademark in the more iconic shapes. A print of a recognisable model
infringes **even with no name, no badge and no logo on it.** Music is the same
story — album covers are copyrighted, and a performer's likeness is separately
protected. Sport carries club badges, kit designs and player likenesses.

So the three niches with the strongest passion-buyer pull are also the three that
can end the business. They are still in the catalogue, but redirected entirely
onto subjects nobody can own:

| Instead of | Sell |
|---|---|
| A Mk1 Golf GTI print | Circuit and rally-stage **layouts** — a track outline is a geographic fact |
| A band or album print | Instruments, waveform art, record-shop culture, your own typography |
| A club or player print | Marathon and cycling **route maps**, climbing topos, city typography |
| Song lyrics | Words you wrote yourself |

That last row catches people out constantly. A "first dance lyrics" print is
copyright infringement, and it looks like the most innocent product in the shop.

**Safest sources, in order** (`python -m wonderfeed.compliance --safe-harbours`):

1. **Your own originals, including AI images you prompted yourself** — without
   naming a living artist or describing a protected design.
2. **Verified public-domain archives** — Biodiversity Heritage Library,
   Rijksmuseum, the Met, Smithsonian Open Access, Library of Congress. Vintage
   botanical plates, old master paintings, antique maps and star charts are a
   genuine goldmine here: free, gorgeous, and provably out of copyright. One
   catch — a museum can restrict commercial use through its **terms of service**
   even where the scan itself carries no copyright, so check the licence per item.
3. **Licensed stock**, with the licence saved.

**On AI-generated art specifically:** you can sell it. UK law recognises
computer-generated works, but for a prompt-only image the ownership is uncertain
and the protection narrow and short — largely untested in court. The practical
consequence is not that you can't sell it; it's that **you probably can't stop
anyone copying it.** Design your moat around catalogue breadth and turnover
rather than around any one image being defensible.

**Screening is automated** — see §7. Nothing reaches `products.yaml` without
passing it, but a word list plus a model review is a filter, not a lawyer. Look
at each concept yourself before you list it.

## 4. The video format

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

## 5. Cadence and the posting workflow

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

## 6. The link problem

You have three options and they are not equal:

1. **Product tag on the video** (best). Requires TikTok Shop seller or approved
   affiliate. Tag it manually when scheduling. Highest conversion by a distance.
2. **Bio link** — what Crush Gallery does (`vt.tiktok.com/...` → TikTok Shop).
   Works, loses most of the traffic to the extra tap.
3. **Pinned comment** with the link. Weakest, but free and instant.

Do (1). Use (3) as a backup on every video regardless — it costs nothing.

## 7. Automated IP screening

Every concept is screened before it can reach `products.yaml`, in two passes:

```bash
python -m wonderfeed.compliance                  # screen products.yaml
python -m wonderfeed.compliance --deep           # add the Claude review pass
python -m wonderfeed.compliance --safe-harbours  # where to source artwork
```

**Pass 1 — blocklist.** Free, instant. Car marques, bands, clubs, franchises,
brands, living people, plus patterns like `Mk2`, "album cover", "official",
"lyrics". A `BLOCK` here is hard: the catalogue generator discards the concept
rather than writing it out.

**Pass 2 — Claude review** (`--deep`, a few pence). Catches what a word list
cannot: a protected design described without being named — "the wedge-shaped 80s
supercar with pop-up headlights" trips no keyword but is still infringing. For
anything it blocks it also suggests a rewrite keeping the same buyer.

Verdicts:

| | Meaning |
|---|---|
| `PASS` | Nothing found. Still your call. |
| `REVIEW` | Something needs a human look — a high-risk niche, or a risky pattern |
| `BLOCK` | Do not list. Rewrite or drop it. |

Tested against deliberate traps: it blocks a Mk1 Golf GTI concept, an Oasis
album reference and a Manchester United print; flags a first-dance-lyrics print
(copyrighted, and it looks innocent); and passes a botanical study. Circuit
layouts come back `REVIEW` rather than `BLOCK` — correct, since the layout is
factual but the niche warrants a look.

**It is a filter, not a lawyer.** It reduces how often you have to think about
this; it does not remove the obligation to look.

## 8. Compliance — the stuff that gets accounts killed

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

## 9. What to measure, and when to kill

Track weekly, not daily. Daily numbers are noise.

| Metric | Healthy | Act if |
|---|---|---|
| Avg. watch time | >55% of length | <40% → hook is failing, rewrite beat 1 |
| Views per video | rising week on week | flat for 3 weeks → change the angle set |
| Click-through to product | >1.5% | <0.5% → the offer or price is wrong, not the video |
| Conversion | >2% of clicks | low with good CTR → listing/photos problem, not TikTok |

**Kill criteria:** judge the *listing*, on units sold, using
`python -m wonderfeed.listings review` (§10). Do not kill on views or likes.
A listing pulling traffic and converting nothing is dead; a listing with no
traffic yet has not been tested. Those need opposite responses, which is the
whole reason that tool exists.

## 10. Listing rotation — working the 100 cap

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

**The one-week rule.** `grace_days` is set to **7**, so a listing is judged
after a week. That is aggressive, and it is only safe because of the
`CULL`/`WATCH` split above: a listing with no traffic after a week lands in
`WATCH`, not `CULL`, so a short window never kills something you simply haven't
tested yet. It only kills listings that got real traffic and converted nobody —
and a week of that is enough.

The one case where 7 days is too tight is if you're posting fewer than about two
videos per listing per week; then most listings sit in `WATCH` forever and the
window does nothing. At 100 listings and 3 videos/day you are posting roughly
one video per listing every five days, so expect a lot of `WATCH` early on.
That is the system telling you the truth: **at 100 listings your bottleneck is
video volume, not culling.**

Other thresholds live under `listings:` in `settings.yaml`. The default
`cull_after_videos: 15` says: fifteen videos at a product with nothing to show
is enough evidence, regardless of age.

## 11. First 30 days

The goal of month one is a **full shop and a working cull loop**, not a viral
video.

- **Week 1 — fill the shelves.** Set up TikTok Shop. Generate the catalogue
  (`python -m wonderfeed.catalogue --count 100 --write`), check every concept
  for trademark risk (§3), and list as many as you can get through. Register
  each with `listings add` as you go. Post 1–2 videos/day by hand to learn the
  app.
- **Week 2 — get to volume.** Weekly batch on. 2–3 videos/day, spread across
  listings rather than concentrated on favourites — an untested listing tells
  you nothing. Keep listing toward the cap.
- **Week 3 — first cull cycle.** Export the CSV, `listings import`,
  `listings review`. Delist everything marked `CULL`, replace with new concepts
  from the unused catalogue. This is the loop you will now run every week.
- **Week 4 — concentrate.** You should have a handful of `KEEP` listings. Point
  `--per-product` at those and let the winners take the volume, while new tests
  fill the slots the culls freed.

Then repeat weekly: import, review, cull, replace, re-point volume at what sells.

Two failure modes to watch for:

- **Spreading too thin.** 100 listings and 3 videos/day means each listing gets
  a video every ~5 days. That is barely enough to generate signal. If everything
  sits in `WATCH` after three weeks, cut the catalogue back and give the
  survivors more shots rather than listing more.
- **Falling in love with a listing.** If `review` says `CULL`, cull it. The slot
  is worth more than the idea. Crush Gallery's advantage is almost certainly
  catalogue breadth plus turnover, not any single design.

At ~£0.10/video the content is nearly free. The expensive mistake is 300 videos
pointed at listings you never culled.

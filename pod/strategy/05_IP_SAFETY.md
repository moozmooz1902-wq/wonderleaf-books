# 05 — IP safety

Not legal advice. This is an operational screen designed to keep accounts alive.
Consult a lawyer for anything genuinely borderline.

## The two rights, and why the distinction matters

| | **Copyright** | **Trademark** |
|---|---|---|
| Protects | Original creative expression — art, photos, illustration, music, text | Brand identifiers — names, logos, catchphrases |
| POD example | Reproducing someone's illustration | Putting a brand or character name on a shirt |
| Duration | Long, then public domain | Indefinite while in use |
| Enforcement | DMCA takedown | Takedown + account termination + damages |

**Trademark is the one that ends accounts**, because it attaches to *use in
commerce* — which includes your title, your tags, your description, and your
**backend search terms**, not just the artwork. A completely original image with a
franchise name in the tags is still an infringement.

## The hard nevers

Never use, in artwork **or** any text field **or** backend keywords:

- Franchise, film, game, or series names
- Character names, real or fictional
- Band names, album titles, lyrics
- Company names, product names, logos, wordmarks
- Registered slogans and catchphrases
- Sports teams, leagues, university names
- Living public figures' names and likenesses (right of publicity)
- Look-alike designs — "close enough to be recognisable" is the legal test, not
  "pixel-identical"
- "In the style of [living artist]"

Platform consequences are consistent across Printful, Printify, Redbubble, Merch
by Amazon and Etsy: takedown for the first offence, **permanent ban for repeats**.

## The doctrine: design the vibe, never the name

This is the whole game for fandom-adjacent demand, which is where the volume is.

| Protected (never) | Vibe equivalent (safe) |
|---|---|
| A specific JRPG title | "retro JRPG energy", "16-bit turn-based nostalgia" |
| A soulslike game name | "soulslike difficulty humour", "you died again" |
| A farming-sim title | "cozy farming-sim aesthetic" |
| A named band | "90s shoegaze", "underground techno", "old-school punk", "sad-girl indie" |
| A named anime | "shonen training arc energy", "magical girl transformation" |
| A named wizarding school | "dark academia magic school aesthetic" |

The audience finds these through *aesthetic* search terms, which is exactly how
Redbubble's browse-led audience shops anyway.

## The zero-risk high-recognition lane: public domain

The single best-performing legitimate substitute for licensed IP. It gives you the
recognition advantage without the risk:

- Fine art out of copyright — Van Gogh, Hokusai, Klimt, Mucha, Monet, Hiroshige,
  Vermeer, Turner
- Scientific and botanical plates — Audubon, Redouté, Haeckel, vintage anatomical
  and celestial charts
- US National Park / WPA poster archive
- Vintage travel, transit and exhibition posters past their term
- Public-domain maps, star charts, patent drawings

**The move is fusion, not reproduction:** a public-domain composition recombined
with a modern motif is both original and instantly recognisable. Displate's
*Starry Night and the Cat* charting in a licensed-IP-dominated top 25 is the
proof.

**Caveat:** verify the term in *your* selling jurisdictions, and note that a
modern **photograph or scan** of a public-domain work can carry its own rights.
Use verified public-domain source scans (Rijksmuseum, Met Open Access, NYPL
Digital Collections, Smithsonian Open Access, Library of Congress).

## Screening procedure

Every text string that ships gets screened — art copy, title, tags, description,
backend terms.

1. **Automated denylist + pattern screen.** `data/ip_risk_rules.json`, enforced by
   `tools/validate_concept.py`. Catches known marks and high-risk shapes.
2. **Manual database check** for any phrase-based design:
   - USPTO — https://tmsearch.uspto.gov/ (US)
   - EUIPO — https://euipo.europa.eu/ (EU)
   - WIPO Global Brand Database (international)
   - **Amazon Brand Registry** before using any tagline or stylised text on Merch
3. **Record the clearance** in `ip.screened_against[]` with a date. Trademarks are
   registered continuously — a phrase clear today may not be clear in six months.
4. **Quarterly re-screen** of the live catalogue.

## Risk tiers

| Tier | Description | Action |
|---|---|---|
| **R0** | Original art, original phrasing, generic vocabulary | Ship |
| **R1** | Common phrase, could plausibly be registered | Database check, record it |
| **R2** | Genre/scene aesthetic adjacent to a franchise | Check that no protected string appears anywhere; ship the vibe only |
| **R3** | Public-domain source | Verify term + verify the scan's own rights |
| **R4** | Any protected name, logo, character, likeness | **Kill** |

The validator refuses to pass any concept at R4, and requires a populated
`ip.screened_against[]` for R1 and R2.

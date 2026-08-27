# POD Data Pool — posters & t-shirts

Research, strategy, and a **machine-readable data pool** for generating
print-on-demand product data that has a chance of selling.

Built to replace "generate hundreds of thousands of rows and hope" with
"generate a few hundred concepts that each survive six gates".

---

## The one-paragraph version

`revenue = listings × E[sales per listing]`. We were scaling the left factor
while the right one sat at zero. Competitor data works when we list from it
because it carries **demand evidence** — a phrase a real buyer typed, on a
listing that already won a search race. Our generated rows carry none of that.
So the fix is not better prose: it is putting a **demand anchor** at the front of
generation and **refusing to emit anything without one** — then constraining the
image model on six visual axes so it stops returning the training-data mean, and
writing metadata against each platform's real limits instead of stuffing keywords.

---

## Layout

```
pod/
├── strategy/
│   ├── 00_DIAGNOSIS.md          Why 100k listings produced nothing — the five failure modes
│   ├── 01_OPERATING_MODEL.md    The six gates, batch composition, cadence, success metrics
│   ├── 02_POSTER_RESEARCH.md    Redbubble / Displate / Etsy / Society6 findings
│   ├── 03_TSHIRT_RESEARCH.md    Amazon Merch / Redbubble / Etsy / TeePublic findings
│   ├── 04_METADATA_PLAYBOOK.md  Per-platform title / tag / description rules
│   └── 05_IP_SAFETY.md          Trademark screen, "design the vibe", public-domain lane
├── data/                        ← THE DATA POOL (this is what you feed the generator)
│   ├── poster_style_dna.json         18 poster styles with full visual DNA
│   ├── tshirt_layout_archetypes.json 14 named t-shirt lockups
│   ├── poster_niches.json            19 poster niches with search grammar + volumes
│   ├── tshirt_niches.json            12 t-shirt niches with specificity ladders
│   ├── palettes.json                 20 named palettes with hex values
│   ├── platform_specs.json           Hard file + metadata limits per platform
│   ├── ip_risk_rules.json            Automated trademark screen
│   └── quality_rubric.json           The gates, thresholds, and denylists
├── schemas/
│   └── concept.schema.json      What one validated concept looks like
└── tools/
    ├── validate_concept.py      Runs the six gates; kills what fails
    ├── build_prompt.py          Assembles render prompts, metadata requests, and lane briefs
    ├── example_concepts.json    4 worked concepts that pass
    └── failing_examples.json    3 concepts that fail the way our old rows fail
```

---

## Quick start

```bash
# 1. Pick a lane and get a generation brief for it
python3 pod/tools/build_prompt.py brief --product tshirt \
    --style tl_specimen_chart --niche nb_hobby

# 2. Hand that brief to the model. It emits concepts against schemas/concept.schema.json.

# 3. Validate. Pass the live catalogue alongside the new batch so dedup can see both.
python3 pod/tools/validate_concept.py live_catalogue.json new_batch.json

# 4. Build image prompts for the survivors
python3 pod/tools/build_prompt.py render survivors.json

# 5. Build ONE metadata request per platform (never all platforms in one call)
python3 pod/tools/build_prompt.py metadata survivors.json --platform redbubble
python3 pod/tools/build_prompt.py metadata survivors.json --platform etsy
```

Stdlib only — no dependencies, nothing to install.

### See the difference immediately

```bash
python3 pod/tools/validate_concept.py pod/tools/example_concepts.json pod/tools/failing_examples.json
```

The three failing rows are deliberately written the way our current pipeline
writes them. Between them they trip 46 kill rules: generic query, no palette,
slop padding in the prompt, wrong pixel dimensions for every target platform,
an 80-character Redbubble title, ten single-word tags of which seven duplicate
the title, a description that restates the title verbatim, a trademark in the
backend search terms, and a near-duplicate recolour of an earlier concept.

---

## The six gates

| Gate | Name | Kills when |
|---|---|---|
| **G0** | Demand anchor | No search phrase, generic query, <8 adjacent phrases, high competition with no differentiator |
| **G1** | Angle | Audience is "everyone", <3 insider terms, specificity rung <2 |
| **G2** | Visual DNA | Unknown style/layout, no palette, empty composition/typography/texture, <3 avoid terms, no thumbnail story, slop padding in the prompt |
| **G3** | Production | Wrong ratio or pixel count for the platform, apparel without transparency, insufficient edge buffer, non-sRGB |
| **G4** | Metadata | Title over limit, wrong tag count, tags duplicating the title, <60% phrase tags, description repeating the title |
| **G5** | IP | Any R4 pattern hit, tier unset or R4, R1/R2 without a recorded screen |
| **G6** | Dedup | Duplicate hard key, >60% title similarity, colourway masquerading as a listing |

**Target gate_pass_rate is 20–40%.** The validator warns above 60% — if almost
everything passes, the gates are being fed pre-filtered data, or they're broken.

---

## The three findings that change what we build

**1. Displate's bestsellers are a trap.** Nineteen of its published 2025 top 25
are licensed IP — Star Wars, Marvel, Elden Ring, Arcane, LotR, One Piece. Any
"study the bestsellers and make more like them" loop walks straight into an IP
takedown. The originals that *did* chart share one profile: **one focal subject,
an extreme named palette, a feeling rather than a scene, total legibility at
thumbnail size.** That profile is in the data pool as `ps_minimal_zen`,
`ps_bold_char_humour`, and `ps_grand_master_fusion`.

**2. The décor market searches in a grammar we weren't writing.**
`[colour] + [style] + [subject] + [format] + [room]`. Our titles described the
design and omitted the colour and the room — the two things a decorator actually
filters on. Gate G4 now deducts for a décor title with no colour word, and for a
gift title with no relationship word.

**3. A phrase without a lockup returns the mean.** We were generating t-shirt
*phrases* and leaving the layout to chance, which is exactly how you get centred
bold text on a blank tee, a hundred thousand times. `tshirt_layout_archetypes.json`
names 14 lockups with slot structure, type rules and colour rules. Every t-shirt
concept must reference one and fill its slots.

---

## What I could not check

I don't have access to your previous chat sessions, so I couldn't read the poster
and t-shirt data generated there — everything here is diagnosed from the
marketplace side plus the symptom you described. **Drop ~50 of those generated
rows into `pod/samples/` and run the validator over them**; it will name the exact
gates they fail rather than leaving it to inference.

Sources for every claim: [`SOURCES.md`](SOURCES.md).

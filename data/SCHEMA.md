# T-Shirt Design Pipeline

Four commands turn a CSV of image links into a written style spec that
grounds generation in your real data.

```
your.csv ──ingest.py──> designs.jsonl  ──analyze.py──> analyzed.jsonl ──distill.py──> STYLE_SPEC.md
           downloads                     Claude reads                   aggregates
           + dedupes                     each image                     + finds winners
```

```bash
export ANTHROPIC_API_KEY=sk-ant-...

cp data/input_template.csv data/my_designs.csv   # fill this in
python3 tools/ingest.py data/my_designs.csv      # download images
python3 tools/analyze.py                         # vision pass, one call per image
python3 tools/distill.py --prompt                # write data/STYLE_SPEC.md
python3 data/check_dataset.py                    # health report, any time
```

Every step is resumable. Images are stored by content hash, analysis is
cached by that hash, so re-running only does the new work.

## Stage 0 — your CSV

Only `image_url` and `title` are required. Everything else sharpens the
result. See `data/input_template.csv`.

| Column | Notes |
|---|---|
| `image_url` | Direct link to the design image. Downloaded and stored locally, since links rot. |
| `title` | The listing title, VERBATIM |
| `listing_url` | For provenance |
| `marketplace` | `merch_amazon`, `etsy`, `redbubble`, `teepublic`, `own_store` |
| `niche` | Be specific: `pediatric nurse`, not `nurse` |
| `price` | |
| `rating` | Star rating, e.g. `4.6` |
| `review_count` | **The single most useful number you can give me** |
| `bsr` | Best Sellers Rank, lower is better |
| `label` | `positive`, or `negative` for designs you think are bad or oversaturated |
| `notes` | One line: why you saved it |

### Why performance data matters so much

`distill.py` scores every design from `rating`, `review_count` and `bsr`,
takes the top third, and writes a **"what the winners do differently"**
section comparing them against the whole set. Without those numbers the
spec can only describe what these designs *look like* — with them it can
tell you which patterns actually sell. Rows with no performance data still
count, they just cannot inform that section.

## Stage 1 — `designs.jsonl`

One row per unique image: `id` (content hash), `image_file`, `title`,
`source_url`, plus whatever CSV fields you filled in. Duplicate artwork
collapses to a single row automatically.

## Stage 2 — `analyzed.jsonl`

What Claude sees in each image, plus a pixel-measured colour palette:

- `shirt_text` — the text printed on the shirt, line by line
- `subject`, `illustration_style`, `layout`, `typography`
- `niche`, `audience_detail`, `hook_type`, `hook_explanation`
- **`title_formula`**, **`slogan_formula`** — the abstract patterns with
  `{SLOTS}`, e.g. `It's a {NOUN} Thing You Wouldn't Understand`. These are
  the reusable part.
- `palette`, `color_count` — measured with Pillow, not guessed, because
  hex codes read off an image by a model are unreliable
- `print_complexity`, `ip_risk`, `quality_notes`

## Stage 3 — `STYLE_SPEC.md`

The distilled answer to "what do these have in common, and what do the
winners do that the rest don't", plus — with `--prompt` — house rules
written from your own best performers.

**This file is the point of the whole exercise.** It persists between
sessions. Nothing you paste into a chat changes my weights; this file is
how the knowledge actually sticks.

## Rules of thumb

- **Depth beats breadth.** 30-50 designs in ONE niche is worth more than
  500 scattered across twenty.
- **Collect losers too.** Set `label` to `negative` on the lazy and
  oversaturated ones. Contrast teaches more than another good example.
- **Never reproduce.** We learn structure — slogan shapes, layout
  conventions, which niches pay — never the artwork or the wording.
  Derivative designs get accounts terminated, and `ip_risk` flags in the
  spec mark designs that are themselves infringing. Those are examples of
  what not to do.

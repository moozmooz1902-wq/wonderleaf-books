# T-Shirt Design Dataset — Schema

One JSON object per line in `designs.jsonl`. Images live in `data/images/`.

The point of this file is NOT to train a model. It is to build up enough
examples that we can write down an explicit **style spec** — the recurring
title structures, slogan formulas, layout conventions and niche angles —
and turn that into a generator prompt (the t-shirt equivalent of
`STORY_PROMPT` in `wonderleaf_web.py`).

So: fields that capture *patterns in words* matter more than the picture.

## Rules of thumb

- **Depth beats breadth.** 30-50 examples inside ONE niche is worth more
  than 500 scattered across twenty niches.
- **Collect losers too.** Set `label: "negative"` on designs you think are
  bad, generic or oversaturated. Contrast teaches more than another good one.
- **Never reproduce.** We learn the pattern, never the artwork or wording.
  Derivative designs get accounts terminated, and plenty of what sells is
  itself infringing.

## Fields

### Required

| Field | Type | Notes |
|---|---|---|
| `id` | string | Short unique slug, e.g. `nurse-coffee-001` |
| `image_file` | string | Filename inside `data/images/`. Save the image — links rot. |
| `title` | string | The listing title, VERBATIM |
| `shirt_text` | string[] | The text printed on the shirt, one array entry per line. Usually differs from the title — this is what we actually generate. |
| `niche` | string | The real unit of this business. Be specific: `pediatric nurse`, not `nurse`. |
| `label` | string | `positive` or `negative` |

### Performance — the field everyone skips

This is the difference between copying *style* and copying *what works*.
A rough gut score is far better than leaving it blank.

| Field | Type | Notes |
|---|---|---|
| `performance.gut_score` | int | 1-5. Your honest guess at how well it sells. |
| `performance.signal_type` | string | `bsr`, `reviews`, `sales_rank`, `seen_repeatedly`, `guess` |
| `performance.value` | string | The actual number or observation, e.g. `BSR 412,000` |

### Strongly recommended

| Field | Type | Notes |
|---|---|---|
| `marketplace` | string | `merch_amazon`, `etsy`, `redbubble`, `teepublic`, `own_store` — decides title limits and listing format |
| `listing_url` | string | For provenance. The saved image is the source of truth. |
| `audience_detail` | string | Who buys it and why |
| `bullets` | string[] | Listing bullets |
| `keywords` | string[] | Tags / search terms |
| `style_tags` | string[] | `typography_only`, `retro_sunset`, `cartoon_mascot`, `minimal_line_art`, `vintage_distressed`, `illustration_plus_text` |
| `layout` | string | `stacked_centered`, `arched_text`, `badge_circle`, `left_chest`, `full_front_scene` |
| `color_count` | int | Print constraints are real |
| `notes` | string | One line: why you saved it, what you'd change |

### Optional

`price`, `product_types` (string[]), `shirt_colors` (string[]),
`date_seen` (YYYY-MM-DD), `publish_date`, `seller`, `ip_flags` (string[]).

## Example row

```json
{
  "id": "example-001",
  "image_file": "example-001.png",
  "title": "EXAMPLE ROW — replace me",
  "shirt_text": ["LINE ONE", "line two"],
  "niche": "example niche",
  "label": "positive",
  "performance": {"gut_score": 3, "signal_type": "guess", "value": ""},
  "marketplace": "",
  "style_tags": ["typography_only"],
  "layout": "stacked_centered",
  "notes": "Delete this row once you add real data."
}
```

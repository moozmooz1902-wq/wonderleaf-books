# T-shirt catalogue research — how to resume

The container is ephemeral. Images and the parsed source file are NOT in git
(too large); both regenerate automatically.

## To pick up in a new session

```bash
cd tshirt
export ANTHROPIC_API_KEY=...          # set in environment settings, not here
python3 run_full_analysis.py download # ~34 min, rebuilds the 167,695 images
# Auth: store ONLY x-api-key as an API credential for api.anthropic.com.
# anthropic-version is sent by the script - it is not a secret.
python3 run_full_analysis.py submit --sold-only   # the 22,485 that sold, ~$40
python3 run_full_analysis.py collect  # writes fingerprints.jsonl
```

`submit` and `collect` are separate because the Batch API is asynchronous and
runs at 50% cost. Results keep for 29 days, so the job survives a session
ending. `all.json` is rebuilt from the seller's CSV by the download step.

## What is already established (measured, not guessed)

- 167,695 listings, 140,085 unique artworks, 218,458 units sold
- 13.4% of designs ever sold; top 1,000 designs are 64% of all sales
- HOUSE SPEC: black garment, 4-5 spot colours, artwork covering 10-25% of the
  chest. That combination measures 5.3-6.3 units/design vs a 1.30 average.
- 29.9% of listings are fit variants (ringer/v-neck/petite/organic/FOTL)
  returning 2.1% of sales
- Only 49 illustrations are needed to cover the whole generated catalogue;
  131,200 of 132,096 designs are pure type and need no artwork

## Known gap this run closes

The 8 templates found so far explain only 7.1% of sales. The shirt text on the
other 92.9% has never been read. That is what `submit` fixes.

## Files

- `render.py` — renders type-led designs to print-ready PNG, free, 3.6/sec
- `cv_analyse.py` — perceptual hash + visual features, free
- `run_full_analysis.py` — download / submit / collect for the Batch API pass
- `MEASURED_FINDINGS.csv` — every measured number with a verdict
- `TEMPLATES.csv` — the 8 template briefs plus the house print spec
- `FINAL_CATALOGUE.csv.gz` — 132,096 generated designs, prioritised

# eBay Research Tools

Market, seller and title analysis for the Wonderleaf platform, built on eBay's
official REST APIs.

Open the app and pick **eBay Research** in the sidebar, or use the package
directly from Python or the command line.

---

## What it does

### Market research
Point it at a search term and it tells you what that market really looks like:

- **Price distribution** including postage — median, quartiles, the full
  histogram, and the outliers worth ignoring.
- **Competition** — how many sellers, how concentrated (Herfindahl index), and
  who owns the first page.
- **Sell-through and velocity** — units sold in 90 days, revenue, units/day,
  and the **price band that actually converts**, which is very often not the
  cheapest one.
- **Asking price vs achieved price** — the gap between what sellers want and
  what buyers pay, with a verdict on which way the market is leaning.
- **Keyword tables** — every word and two-word phrase ranked by how many
  listings use it, split into *mandatory* terms and *long-tail* terms that are
  cheaper to rank for.
- **Gap analysis** — words that appear far more often in **sold** titles than
  in live ones. These are the terms buyers convert on, and they are the single
  most actionable output in the tool.

### Seller research
Give it any seller username and it pulls as much of their live catalogue as the
API will return, then reports:

- Pricing shape, catalogue value, format mix (auction / Buy It Now / Best Offer)
- Postage strategy and free-postage share
- How much of their stock is stale (listed 90+ days — usually a pricing signal)
- Promoted-listing share: are they buying placement?
- Title quality across the catalogue, with **every listing scored worst-first**
  so the quickest wins are at the top
- **Change since your last run** — new listings, listings that vanished
  (usually sold), and every price move

### Title optimiser
Scores a title out of 100 against the live market it competes in, with every
point attributed to a named component and a reason:

| Component | Weight | What it measures |
|---|---|---|
| Length use | 25 | eBay gives you 80 characters; wasting them wastes searches |
| Market keywords | 30 | Coverage of the phrases buyers actually see, share-weighted |
| Attributes | 20 | Colour, size, condition, year, model, quantity |
| Cleanliness | 15 | Filler, hype, repeated words, `L@@K` |
| Differentiation | 10 | Words specific to your item vs boilerplate everyone uses |

It then **builds a replacement title**: your words first, then the highest-value
market terms greedily packed into the remaining characters, and re-scores it so
you can see the delta.

### Compare sellers
Several competitors side by side on identical terms — pricing, title length,
filler use, postage, promotion and top keywords.

---

## Setup

1. Register a free application at
   [developer.ebay.com/my/keys](https://developer.ebay.com/my/keys).
2. Add the keys to Streamlit secrets (**Settings → Secrets**) or your
   environment:

```toml
EBAY_CLIENT_ID     = "YourApp-PRD-xxxxxxxx-xxxxxxxx"   # App ID (Client ID)
EBAY_CLIENT_SECRET = "PRD-xxxxxxxxxxxx-xxxx-xxxx"      # Cert ID (Client Secret)
EBAY_MARKETPLACE   = "EBAY_GB"
```

The **Browse API** (live listings) works immediately. **Marketplace Insights**
(90 days of sold prices) is a limited-release API you apply for separately —
without it every tool still runs, on asking prices only, and says so rather
than quietly presenting them as achieved prices.

---

## Capacity: what actually limits this tool

**eBay counts its daily call allowance against your application keyset, not
your IP address.** This is the single most important thing to understand about
scaling the tool, because it means the obvious lever is the wrong one: a pool
of rotating IP addresses sharing one keyset still stops on exactly the same
call. It would add cost, latency and failure modes for zero extra capacity.

What does raise throughput, in order of effect:

**1. The shared response cache.**
Every response is cached (default 15 minutes). A search another user already
ran is free for everyone else inside that window. On a platform with real
traffic this is by far the largest multiplier — popular searches converge on
one API call.

**2. More keysets.**
Each application registration has its own allowance, and the tool pools them.
Two routes:

```toml
# additional first-party keysets
EBAY_CLIENT_ID_2 = "..."
EBAY_CLIENT_SECRET_2 = "..."

# or a JSON bundle, e.g. per-tenant keys
EBAY_CREDENTIALS = '[{"label":"user-a","client_id":"...","client_secret":"..."}]'
```

The best version of this is **bring-your-own-keys**: users add their own free
developer keys in **Setup → Add your own eBay keyset**, so capacity scales with
the user base and everyone's usage is counted against their own application.
Keys entered this way stay in the browser session and are never written to disk.

**3. Adaptive pacing.**
The send rate halves the moment eBay returns a 429 and walks back up once calls
are clean again (AIMD, the control loop TCP uses). In practice you get throttled
once, briefly, instead of repeatedly.

**4. Keyset failover.**
When a keyset is throttled or spent, the pool hands the *in-flight request* to
another one and the report finishes. It does not restart, and it does not fail.

**5. Budget-aware sampling.**
The tool checks its remaining allowance before a sweep. If the budget is short
it shrinks the sample and tells you, instead of dying halfway through and
leaving you with half a report. A blind catalogue sweep reserves its category
probes up front for the same reason.

**6. Ask eBay.**
They raise allowances for applications showing real usage. That is the supported
route to a bigger ceiling, and it is the one that scales furthest.

You can see all of this live in **Setup → Capacity**: calls left today, per-keyset
status, current send rate, throttle and failover counts.

### Egress proxies

One or more outbound proxies can be configured:

```toml
EBAY_PROXY_URL  = "http://user:pass@host:port"
EBAY_PROXY_URLS = "http://a:8080,http://b:8080"    # ordered failover
```

A list is **failover with health tracking**, so one dead route cannot take the
tool down, and a regional marketplace can be reached from the right country.
It is not a rotation pool: on the API path there is no block to route around,
and disguising traffic would not raise the keyset allowance that is the actual
constraint.

---

## Command line

Useful for batch work and for scheduled trend tracking — run a seller nightly
from cron and each run records a snapshot, so the change reports build
themselves.

```bash
python -m ebay_research.cli market "personalised picture book" --markdown
python -m ebay_research.cli seller wonderleaf_books --max-items 1000 --csv out.csv
python -m ebay_research.cli compare seller_a seller_b --query "picture book"
python -m ebay_research.cli title "Sweet Dreams Little Unicorn" --market "picture book"
python -m ebay_research.cli budget
```

## Python

```python
from ebay_research import EbayClient, load_settings, research_market

client = EbayClient(load_settings(marketplace="EBAY_GB"))
report = research_market(client, "personalised childrens picture book")

for finding in report["findings"]:
    print("-", finding)
```

Every pipeline returns a plain JSON-serialisable dict ending in `findings`: a
list of plain-English sentences. Numbers nobody reads are not research.

---

## Configuration reference

| Variable | Default | Purpose |
|---|---|---|
| `EBAY_CLIENT_ID` / `EBAY_CLIENT_SECRET` | — | Primary application keyset |
| `EBAY_CLIENT_ID_2..9` / `EBAY_CLIENT_SECRET_2..9` | — | Additional keysets |
| `EBAY_CREDENTIALS` | — | JSON list of keysets |
| `EBAY_ENV` | `production` | `production` or `sandbox` |
| `EBAY_MARKETPLACE` | `EBAY_GB` | Marketplace to query |
| `EBAY_CACHE_PATH` | `~/.cache/wonderleaf/…` | SQLite cache, quota ledger and snapshots |
| `EBAY_CACHE_TTL` | `900` | Response cache lifetime, seconds |
| `EBAY_RATE_LIMIT_RPS` | `4.0` | Send-rate ceiling |
| `EBAY_MAX_RETRIES` | `4` | Retries on transient failures |
| `EBAY_TIMEOUT` | `30` | Per-request timeout, seconds |
| `EBAY_PROXY_URL` / `EBAY_PROXY_URLS` | — | Egress proxy, or ordered failover list |
| `EBAY_DAILY_LIMIT_BROWSE` | `5000` | Your Browse allowance, if raised |
| `EBAY_DAILY_LIMIT_INSIGHTS` | `5000` | Your Insights allowance, if raised |

---

## Architecture

```
ebay_research/
  config.py       settings from env or Streamlit secrets
  credentials.py  application keysets and failover between them
  quota.py        persistent daily call ledger and sample planning
  http.py         pacing, adaptive rate control, retries, egress failover
  cache.py        response cache + snapshot history for trends
  client.py       Browse and Marketplace Insights APIs
  models.py       Listing / SoldRecord, parsed once and used everywhere
  titles.py       tokenising, keyword tables, log-odds gap analysis
  analytics.py    price stats, competition, sell-through, price bands
  scoring.py      title scoring and construction
  research.py     pipelines that end in plain-English findings
  export.py       CSV / JSON / Markdown
  ui.py           Streamlit interface
  cli.py          command line
```

The analysis layers are pure Python with no pandas or numpy dependency, so they
are testable on their own and run anywhere. Streamlit is imported only by
`ui.py`.

## Tests

```bash
python -m unittest discover -s tests -t .
```

No network access is required — a fake eBay serves the whole suite, including
throttling, keyset exhaustion, egress failure and budget degradation.

---

## Data use

All data comes from eBay's official APIs under their developer terms. Sold
figures are eBay's own estimates covering the last 90 days. Nothing here
scrapes eBay's website.

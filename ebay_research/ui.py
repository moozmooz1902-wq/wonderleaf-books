"""Streamlit interface for the eBay research tools.

Kept separate from the analysis code so the pipelines stay importable from a
script, a notebook or a cron job without dragging Streamlit in.
"""

from __future__ import annotations

import streamlit as st

from . import export, research, scoring
from .cache import ResponseCache, SnapshotStore
from .client import TOP_LEVEL_CATEGORIES, EbayClient
from .config import MARKETPLACES, load_settings
from .credentials import Credential
from .errors import ConfigError, EbayResearchError, RateLimitError
from .quota import seconds_until_reset

CONDITIONS = {
    "New": "NEW",
    "Used": "USED",
    "Refurbished": "CERTIFIED_REFURBISHED|EXCELLENT_REFURBISHED|SELLER_REFURBISHED",
    "For parts": "FOR_PARTS_OR_NOT_WORKING",
}

BUYING_OPTIONS = {
    "Buy It Now": "FIXED_PRICE",
    "Auction": "AUCTION",
    "Best Offer": "BEST_OFFER",
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _dataframe(rows):
    """Rows to a DataFrame, tolerating an environment without pandas."""
    try:
        import pandas as pd
    except ImportError:
        return None
    return pd.DataFrame(rows)


def _table(rows, caption=None, height=None):
    if not rows:
        st.caption("No data for this section.")
        return
    frame = _dataframe(rows)
    if frame is None:
        st.json(rows[:50])
        return
    st.dataframe(frame, use_container_width=True, hide_index=True, height=height)
    if caption:
        st.caption(caption)


def _money(value, currency):
    if value is None:
        return "—"
    symbol = {"GBP": "£", "USD": "$", "EUR": "€", "AUD": "A$", "CAD": "C$"}.get(currency, "")
    return f"{symbol}{value:,.2f}" if symbol else f"{value:,.2f} {currency}"


def _user_keysets():
    """Keysets this user pasted in — their own eBay developer application.

    Bring-your-own-keys is how a shared platform scales: eBay counts its daily
    allowance per application keyset, so a user with their own keyset gets
    their own budget instead of competing for the platform's.
    """
    return [
        Credential(
            client_id=entry["client_id"],
            client_secret=entry["client_secret"],
            label=entry.get("label", "your keyset"),
            owner=entry.get("owner", "you"),
        )
        for entry in st.session_state.get("user_keysets", [])
    ]


def _get_client(settings_overrides):
    """One client per configuration, reused across reruns."""
    extra = _user_keysets()
    key = tuple(sorted((k, str(v)) for k, v in settings_overrides.items())) + (
        tuple(sorted(c.id for c in extra)),
    )
    cached = st.session_state.get("_ebay_client")
    if cached and cached[0] == key:
        return cached[1]
    settings = load_settings(**settings_overrides)
    client = EbayClient(settings, extra_credentials=extra)
    st.session_state["_ebay_client"] = (key, client)
    return client


def _budget_banner(client):
    """Standing readout of what today's allowance has left."""
    remaining = client.budget("browse")
    if remaining is None:
        return
    keysets = len(client.pool) if client.pool else 0
    total = client.ledger.limit_for("browse") * max(keysets, 1)
    hours = int(seconds_until_reset() // 3600)
    columns = st.columns([3, 1])
    columns[0].progress(
        min(remaining / total, 1.0) if total else 0.0,
        text=f"{remaining:,} of {total:,} API calls left today "
        f"across {keysets} keyset(s) · resets in ~{hours}h",
    )
    if remaining < total * 0.15:
        columns[1].warning("Low", icon="⚠️")


def _show_notices(client):
    for notice in client.notices:
        st.info(notice, icon="📉")


def _show_findings(report):
    st.subheader("What this means")
    for finding in report.get("findings", []):
        st.markdown(f"- {finding}")
    for warning in report.get("warnings", []):
        st.info(warning, icon="ℹ️")


def _price_block(report):
    currency = report.get("currency", "GBP")
    prices = report.get("prices") or {}
    if not prices.get("count"):
        return
    columns = st.columns(5)
    for column, (label, key) in zip(
        columns,
        [
            ("Lowest", "min"),
            ("25th pct", "p25"),
            ("Median", "median"),
            ("75th pct", "p75"),
            ("Highest", "max"),
        ],
    ):
        column.metric(label, _money(prices.get(key), currency))

    histogram = report.get("price_histogram") or []
    if histogram:
        frame = _dataframe(
            [{"band": f"{low:,.0f}–{high:,.0f}", "listings": count} for low, high, count in histogram]
        )
        if frame is not None:
            st.bar_chart(frame.set_index("band"), height=220)
        st.caption(
            f"Distribution of asking prices including postage, in {currency}. "
            "A long right tail usually means a few premium or miscategorised listings."
        )


def _sold_block(report):
    sold = report.get("sold")
    currency = report.get("currency", "GBP")
    if not sold:
        st.warning(
            "No sold-item data. Everything shown is what sellers are **asking**, not "
            "what buyers **paid**. Apply for the Marketplace Insights API at "
            "developer.ebay.com to unlock achieved prices and sell-through.",
            icon="⚠️",
        )
        return

    performance = sold["performance"]
    columns = st.columns(4)
    columns[0].metric("Units sold (90d)", f"{performance['sold_units']:,}")
    columns[1].metric("Sell-through", f"{performance['sell_through_rate']:.0%}")
    columns[2].metric("Est. revenue", _money(performance["estimated_revenue"], currency))
    columns[3].metric("Avg sale price", _money(performance["average_sale_price"], currency))

    trend = sold.get("trend") or []
    if trend:
        frame = _dataframe(trend)
        if frame is not None:
            st.bar_chart(frame.set_index("period_start")[["units"]], height=200)
            st.caption("Units sold per week, oldest first.")

    if sold.get("price_bands"):
        st.markdown("**Sell-through by price band** — where demand actually sits")
        _table(sold["price_bands"])

    if sold.get("winning_terms"):
        st.markdown("**Gap analysis** — words far more common in sold titles than live ones")
        _table(
            sold["winning_terms"],
            caption=(
                "Positive scores mean the word is over-represented among items that "
                "sold. These are the terms to put in your title."
            ),
        )


def _downloads(report, stem):
    st.divider()
    columns = st.columns(3)
    columns[0].download_button(
        "⬇️ Listings CSV",
        data=export.rows_to_csv(report.get("listings", [])),
        file_name=f"{stem}-listings.csv",
        mime="text/csv",
        use_container_width=True,
    )
    columns[1].download_button(
        "⬇️ Brief (Markdown)",
        data=export.report_to_markdown(report),
        file_name=f"{stem}-brief.md",
        mime="text/markdown",
        use_container_width=True,
    )
    columns[2].download_button(
        "⬇️ Full report (JSON)",
        data=export.report_to_json(report),
        file_name=f"{stem}-report.json",
        mime="application/json",
        use_container_width=True,
    )


def _run(label, function, *args, **kwargs):
    """Run a pipeline, turning package errors into readable UI messages."""
    progress = st.progress(0.0, text=label)

    def on_progress(done, total):
        if total:
            progress.progress(min(done / total, 1.0), text=f"{label} — {done}/{total}")

    kwargs["progress"] = on_progress
    client = args[0] if args else None
    if hasattr(client, "reset_notices"):
        client.reset_notices()
    try:
        with st.spinner(label):
            return function(*args, **kwargs)
    except RateLimitError as exc:
        st.error(f"{exc}", icon="🚦")
    except ConfigError as exc:
        st.error(f"{exc}", icon="🔑")
    except EbayResearchError as exc:
        st.error(f"eBay research failed: {exc}", icon="❌")
    except Exception as exc:  # keep the app alive on anything unexpected
        st.error(f"Unexpected error: {exc}", icon="❌")
    finally:
        progress.empty()
    return None


# ---------------------------------------------------------------------------
# Tabs
# ---------------------------------------------------------------------------


def _market_tab(client, sample_size):
    st.markdown(
        "Research a **search term** the way a buyer sees it: who is selling, what "
        "they charge, what actually sells, and which words win the click."
    )
    with st.form("market"):
        query = st.text_input(
            "Search term", placeholder="personalised childrens picture book"
        )
        columns = st.columns(3)
        category = columns[0].selectbox(
            "Category (optional)",
            ["Any"] + [f"{name} ({cid})" for cid, name in TOP_LEVEL_CATEGORIES.items()],
        )
        price_min = columns[1].number_input("Min price", min_value=0.0, value=0.0, step=1.0)
        price_max = columns[2].number_input("Max price", min_value=0.0, value=0.0, step=1.0)
        columns = st.columns(2)
        conditions = columns[0].multiselect("Condition", list(CONDITIONS))
        buying = columns[1].multiselect("Format", list(BUYING_OPTIONS))
        submitted = st.form_submit_button("Research this market", type="primary", use_container_width=True)

    if submitted:
        if not query.strip():
            st.error("Enter a search term.")
            return
        category_ids = None
        if category != "Any":
            category_ids = category.rsplit("(", 1)[1].rstrip(")")
        report = _run(
            "Pulling listings from eBay",
            research.research_market,
            client,
            query.strip(),
            category_ids=category_ids,
            price_min=price_min or None,
            price_max=price_max or None,
            conditions=[CONDITIONS[c] for c in conditions] or None,
            buying_options=[BUYING_OPTIONS[b] for b in buying] or None,
            max_items=sample_size,
        )
        if report:
            st.session_state["market_report"] = report

    report = st.session_state.get("market_report")
    if not report:
        return

    _show_notices(client)
    st.divider()
    st.header(f"'{report['subject']}' on {report['marketplace']}")
    summary = report["summary"]
    columns = st.columns(4)
    columns[0].metric("Live listings", f"{summary['listings_total']:,}")
    columns[1].metric("Sampled", f"{summary['listings_sampled']:,}")
    columns[2].metric("Sellers", f"{report['competition']['sellers']:,}")
    columns[3].metric("Promoted", f"{report['promoted_share']:.0%}")

    _show_findings(report)

    tabs = st.tabs(["Prices", "Sold", "Competition", "Keywords", "Listings"])
    with tabs[0]:
        _price_block(report)
        st.markdown("**Condition mix**")
        _table(report["condition_mix"])
        st.markdown("**Format mix**")
        _table(report["format_mix"])
    with tabs[1]:
        _sold_block(report)
    with tabs[2]:
        competition = report["competition"]
        st.metric("Market concentration (HHI)", competition["hhi"], competition["concentration"])
        _table(competition["top_sellers"], caption="Sellers holding the most listings on this search.")
        st.markdown("**Seller leaderboard**")
        _table(report["sellers"])
    with tabs[3]:
        st.markdown("**Single words** — ranked by how many listings use them")
        _table(report["keywords"])
        st.markdown("**Two-word phrases**")
        _table(report["phrases"])
        st.markdown("**Title shape across the market**")
        _table([report["title_stats"]])
    with tabs[4]:
        _table(report["listings"], height=420)

    _downloads(report, f"market-{report['subject'][:30].replace(' ', '-')}")


def _seller_tab(client, sample_size):
    st.markdown(
        "Point this at **any seller** and it pulls as much of their live catalogue "
        "as the API will give, then reports how they price, how they write titles, "
        "and what has changed since you last looked."
    )
    with st.form("seller"):
        seller = st.text_input("Seller username", placeholder="wonderleaf_books")
        columns = st.columns(2)
        query = columns[0].text_input(
            "Narrow by keyword (optional)",
            help="Much faster and cheaper than a full catalogue sweep.",
        )
        include_sold = columns[1].checkbox("Include sold data", value=True)
        submitted = st.form_submit_button("Research this seller", type="primary", use_container_width=True)

    if submitted:
        if not seller.strip():
            st.error("Enter a seller username.")
            return
        report = _run(
            "Sweeping the seller's catalogue",
            research.research_seller,
            client,
            seller.strip(),
            query=query.strip() or None,
            max_items=sample_size,
            include_sold=include_sold,
        )
        if report:
            st.session_state["seller_report"] = report

    report = st.session_state.get("seller_report")
    if not report:
        return

    _show_notices(client)
    st.divider()
    st.header(f"{report['subject']} on {report['marketplace']}")
    summary = report["summary"]
    identity = report.get("identity") or {}
    columns = st.columns(4)
    columns[0].metric("Listings found", f"{summary['listings_total']:,}")
    columns[1].metric("Sampled", f"{summary['listings_sampled']:,}")
    columns[2].metric("Feedback", f"{identity.get('feedback_score') or '—'}")
    columns[3].metric(
        "Catalogue value", _money(summary.get("catalogue_value"), report["currency"])
    )

    _show_findings(report)

    tabs = st.tabs(
        ["Pricing", "Titles to fix", "Categories", "Sold", "Change over time", "Listings"]
    )
    with tabs[0]:
        _price_block(report)
        st.markdown("**Postage**")
        _table([report["shipping"]["paid_shipping"]] if report["shipping"]["paid_shipping"].get("count") else [])
        st.metric("Free postage share", f"{report['shipping']['free_shipping_share']:.0%}")
        st.markdown("**How long stock has been listed**")
        _table([report["listing_age"]] if report["listing_age"].get("count") else [])
    with tabs[1]:
        st.markdown(
            "Every listing scored against this seller's own market. Worst first — "
            "these are the quickest wins."
        )
        _table(report["weakest_listings"], height=420)
        st.markdown("**Title shape**")
        _table([report["title_stats"]])
    with tabs[2]:
        _table(report["category_mix"])
        if report.get("category_totals"):
            st.markdown("**Listings per top-level category (eBay's own count)**")
            _table(
                [
                    {"category": name, "listings": count}
                    for name, count in report["category_totals"].items()
                ]
            )
    with tabs[3]:
        _sold_block(report)
    with tabs[4]:
        trend = report.get("trend")
        if not trend:
            st.info(
                "This is the first run for this seller. Run it again in a few days "
                "and this tab will show new listings, items that disappeared "
                "(usually sold), and every price move.",
                icon="🕒",
            )
        else:
            columns = st.columns(4)
            columns[0].metric("Listings now", trend["listings_now"], trend["listings_now"] - trend["listings_before"])
            columns[1].metric("New", trend["new_listings"])
            columns[2].metric("Gone", trend["removed_listings"])
            columns[3].metric(
                "Median price",
                _money(trend["median_price_now"], report["currency"]),
            )
            st.markdown("**Biggest price moves**")
            _table(trend["price_changes"])
            st.markdown("**Listings that disappeared** — most will have sold")
            _table(trend["removed_examples"])
    with tabs[5]:
        _table(report["listings"], height=420)

    _downloads(report, f"seller-{report['subject']}")


def _title_tab(client, sample_size):
    st.markdown(
        "Score a title against the market it has to compete in, then rebuild it "
        "from the words that market actually rewards."
    )
    with st.form("title"):
        title = st.text_input(
            "Your title", placeholder="Sweet Dreams Little Unicorn story book"
        )
        market = st.text_input(
            "Search term to benchmark against",
            placeholder="personalised childrens picture book",
            help="The tool pulls live competitor titles for this term and scores yours against them.",
        )
        submitted = st.form_submit_button("Score my title", type="primary", use_container_width=True)

    if submitted:
        if not title.strip():
            st.error("Enter a title to score.")
            return
        market_titles = []
        if market.strip():
            report = _run(
                "Fetching competitor titles",
                research.research_market,
                client,
                market.strip(),
                max_items=min(sample_size, 200),
                include_sold=True,
            )
            if report:
                market_titles = [row["title"] for row in report["listings"]]
                st.session_state["title_market_report"] = report
        st.session_state["title_result"] = scoring.score_title(
            title.strip(), market_titles=market_titles
        )
        st.session_state["title_suggestion"] = scoring.suggest_title(
            [title.strip()], market_titles
        )
        st.session_state["title_market_titles"] = market_titles

    result = st.session_state.get("title_result")
    if not result:
        return

    st.divider()
    score = result["score"]
    st.metric("Title score", f"{score}/100", result["verdict"])
    st.progress(min(score / 100, 1.0))

    for component in result["components"]:
        ratio = component["score"] / component["max"] if component["max"] else 0
        icon = "✅" if ratio >= 0.8 else ("🟡" if ratio >= 0.5 else "🔴")
        st.markdown(
            f"{icon} **{component['name']}** — {component['score']}/{component['max']}  \n"
            f"{component['reason']}"
        )

    if result.get("problems"):
        st.markdown("**Problems**")
        for problem in result["problems"]:
            st.markdown(f"- {problem}")

    if result.get("missing_keywords"):
        st.markdown("**High-value terms you are missing**")
        _table(result["missing_keywords"])

    suggestion = st.session_state.get("title_suggestion")
    if suggestion and suggestion["title"]:
        st.divider()
        st.markdown("### Suggested title")
        st.code(suggestion["title"], language=None)
        st.caption(
            f"{suggestion['length']}/80 characters "
            f"({suggestion['characters_free']} spare). Built from your words first, "
            "then the highest-coverage terms in the live market."
        )
        market_titles = st.session_state.get("title_market_titles") or []
        rescored = scoring.score_title(suggestion["title"], market_titles=market_titles)
        st.metric(
            "Suggested title score",
            f"{rescored['score']}/100",
            f"{rescored['score'] - score:+.1f} vs yours",
        )


def _compare_tab(client, sample_size):
    st.markdown("Put competitors side by side on identical terms.")
    with st.form("compare"):
        raw = st.text_area(
            "Seller usernames, one per line",
            height=120,
            placeholder="seller_one\nseller_two\nseller_three",
        )
        query = st.text_input("Narrow by keyword (optional)")
        submitted = st.form_submit_button("Compare", type="primary", use_container_width=True)

    if submitted:
        sellers = [line.strip() for line in raw.splitlines() if line.strip()]
        if len(sellers) < 2:
            st.error("Enter at least two seller usernames.")
            return
        try:
            with st.spinner(f"Researching {len(sellers)} sellers"):
                st.session_state["comparison"] = research.compare_sellers(
                    client,
                    sellers[:8],
                    query=query.strip() or None,
                    max_items=min(sample_size, 300),
                )
        except EbayResearchError as exc:
            st.error(f"Comparison failed: {exc}", icon="❌")

    comparison = st.session_state.get("comparison")
    if comparison:
        st.divider()
        _table(comparison["sellers"])
        st.download_button(
            "⬇️ Comparison CSV",
            data=export.rows_to_csv(comparison["sellers"]),
            file_name="seller-comparison.csv",
            mime="text/csv",
        )


def _setup_tab(client):
    settings = client.settings
    st.markdown("### Connection")
    columns = st.columns(4)
    columns[0].metric("Marketplace", settings.marketplace)
    columns[1].metric("Environment", settings.environment)
    columns[2].metric("Keysets", len(client.pool) if client.pool else 0)
    egress = client.http.egress_status()
    columns[3].metric(
        "Egress", "Direct" if egress[0]["egress"] == "direct" else f"{len(egress)} route(s)"
    )

    if not client.pool:
        st.error(
            "No eBay API credentials found. Add them to Streamlit secrets "
            "(**Settings → Secrets**) or your environment:",
            icon="🔑",
        )
        st.code(
            'EBAY_CLIENT_ID = "YourApp-PRD-xxxxxxxx-xxxxxxxx"\n'
            'EBAY_CLIENT_SECRET = "PRD-xxxxxxxxxxxx-xxxx-xxxx"\n'
            "\n# more keysets = more daily allowance\n"
            'EBAY_CLIENT_ID_2 = "..."\n'
            'EBAY_CLIENT_SECRET_2 = "..."\n'
            "\n# optional\n"
            'EBAY_MARKETPLACE = "EBAY_GB"\n'
            'EBAY_PROXY_URLS = "http://a:8080,http://b:8080"',
            language="toml",
        )
        st.markdown(
            "Register a free application at "
            "[developer.ebay.com/my/keys](https://developer.ebay.com/my/keys). "
            "The **Browse API** works immediately; **Marketplace Insights** "
            "(90 days of sold prices) is a separate application you apply for."
        )

    # -- capacity ---------------------------------------------------------

    st.divider()
    st.markdown("### Capacity")
    st.caption(
        "eBay counts its daily allowance against your **application keyset**, not "
        "your IP address. More keysets and a warm cache raise capacity; more IP "
        "addresses do not."
    )

    if client.pool:
        _budget_banner(client)
        _table(client.pool.status("browse"), caption="Live status of each keyset.")
        _table(
            client.ledger.snapshot(client.pool.ids),
            caption="Today's usage per keyset and API.",
        )

    with st.expander("Add your own eBay keyset (recommended for heavy use)"):
        st.markdown(
            "Registering your own free developer application gives you your own "
            "daily allowance instead of sharing the platform's. Keys stay in your "
            "browser session — they are never written to disk here."
        )
        with st.form("byok"):
            label = st.text_input("Label", placeholder="my eBay app")
            client_id = st.text_input("App ID (Client ID)")
            client_secret = st.text_input("Cert ID (Client Secret)", type="password")
            if st.form_submit_button("Add keyset", use_container_width=True):
                if not client_id.strip() or not client_secret.strip():
                    st.error("Both the App ID and the Cert ID are required.")
                else:
                    keysets = st.session_state.setdefault("user_keysets", [])
                    keysets.append(
                        {
                            "client_id": client_id.strip(),
                            "client_secret": client_secret.strip(),
                            "label": label.strip() or "your keyset",
                            "owner": "you",
                        }
                    )
                    st.session_state.pop("_ebay_client", None)
                    st.success("Keyset added — it will be used from the next search.")
                    st.rerun()

        if st.session_state.get("user_keysets"):
            for index, entry in enumerate(list(st.session_state["user_keysets"])):
                columns = st.columns([4, 1])
                columns[0].write(f"**{entry['label']}** — …{entry['client_id'][-6:]}")
                if columns[1].button("Remove", key=f"drop-keyset-{index}"):
                    st.session_state["user_keysets"].pop(index)
                    st.session_state.pop("_ebay_client", None)
                    st.rerun()

    # -- diagnostics ------------------------------------------------------

    st.divider()
    st.markdown("### Diagnostics")
    if client.pool and st.button("Run connection test"):
        with st.spinner("Testing"):
            health = client.health()
        st.write(
            {
                "Browse API": "✅ working" if health["browse"] else "❌ unavailable",
                "Marketplace Insights (sold data)": "✅ working"
                if health["insights"]
                else "⚠️ not enabled for this app",
                "Browse calls left today": health.get("browse_calls_left_today"),
            }
        )
        for note in health["notes"]:
            st.info(note)

    stats = client.http.stats
    columns = st.columns(5)
    columns[0].metric("Requests", stats["requests"])
    columns[1].metric("Retries", stats["retries"])
    columns[2].metric("Throttled (429)", stats["throttled"])
    columns[3].metric("Egress failovers", stats["egress_failovers"])
    columns[4].metric("Paced wait", f"{stats['wait_seconds']:.1f}s")

    rate = client.http.adaptive.rate if client.http.adaptive else settings.rate_limit_rps
    st.caption(
        f"Current send rate {rate:.2f} req/s (halves on throttling, recovers "
        f"automatically). Responses are cached for {settings.cache_ttl}s and the "
        "cache is shared, so a search someone already ran costs no allowance."
    )

    if len(egress) > 1 or egress[0]["egress"] != "direct":
        st.markdown("**Egress routes**")
        _table(egress, caption="Ordered failover. A dead route is skipped, not retried forever.")

    st.markdown("### Tracked subjects")
    store = SnapshotStore(settings.cache_path)
    _table(
        store.subjects(limit=50),
        caption="Every subject researched so far, used for trend comparison.",
    )

    if st.button("Clear response cache"):
        ResponseCache(settings.cache_path, ttl=settings.cache_ttl).clear()
        st.success("Response cache cleared. Snapshots and history are kept.")

    with st.expander("How this tool gets its data, and what actually limits it"):
        st.markdown(
            """
This runs on eBay's **official REST APIs** with an OAuth application token:

* **Browse API** — live listings, filterable by seller, category, price,
  condition and format. Every registered developer account has it.
* **Marketplace Insights API** — items sold in the last 90 days. Limited
  release; apply separately. Without it the tools analyse asking prices only
  and say so.

**The limit is the daily call allowance, and eBay counts it per application
keyset — not per IP address.** A pool of rotating IPs sharing one keyset still
stops on the same call, so it would add cost and fragility for no extra
capacity. What genuinely raises throughput, in order of effect:

1. **Shared response cache.** A search someone already ran is free for
   everyone else inside the TTL. On a busy platform this is the largest
   multiplier by far.
2. **More keysets.** Each application has its own allowance. Users adding
   their own free developer keys scale capacity with the user base.
3. **Adaptive pacing.** The send rate halves on the first 429 and recovers,
   so you get throttled once rather than repeatedly.
4. **Budget-aware sampling.** The tool checks its remaining allowance before a
   sweep and shrinks the sample rather than dying halfway through a report.
5. **Ask eBay.** They raise allowances for applications showing real usage —
   that is the supported route to a bigger ceiling.

Multiple **egress proxies** are supported for reliability and for reaching a
regional marketplace from the right country: they are an ordered failover list
with health tracking, so one dead route cannot take the tool down.
            """
        )


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def render():
    """Render the whole eBay research section.  Call from your Streamlit app."""
    st.title("🔎 eBay Research")
    st.caption(
        "Market, seller and title analysis built on eBay's official APIs."
    )

    with st.sidebar:
        st.markdown("### eBay settings")
        marketplace = st.selectbox(
            "Marketplace",
            sorted(MARKETPLACES),
            index=sorted(MARKETPLACES).index(
                load_settings().marketplace
                if load_settings().marketplace in MARKETPLACES
                else "EBAY_GB"
            ),
            format_func=lambda code: f"{MARKETPLACES[code][0]} ({code})",
        )
        sample_size = st.slider(
            "Listings to sample",
            min_value=50,
            max_value=2000,
            value=400,
            step=50,
            help="Bigger samples are more accurate and cost more API calls.",
        )
        rate = st.slider(
            "Requests per second",
            min_value=1.0,
            max_value=10.0,
            value=4.0,
            step=0.5,
            help="Lower this if you ever see throttling.",
        )

    try:
        client = _get_client({"marketplace": marketplace, "rate_limit_rps": rate})
    except ConfigError as exc:
        st.error(str(exc), icon="🔑")
        return

    _budget_banner(client)

    tabs = st.tabs(
        ["Market research", "Seller research", "Title optimiser", "Compare sellers", "Setup"]
    )
    with tabs[0]:
        _market_tab(client, sample_size)
    with tabs[1]:
        _seller_tab(client, sample_size)
    with tabs[2]:
        _title_tab(client, sample_size)
    with tabs[3]:
        _compare_tab(client, sample_size)
    with tabs[4]:
        _setup_tab(client)

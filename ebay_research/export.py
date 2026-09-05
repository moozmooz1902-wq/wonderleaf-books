"""Exports: CSV for spreadsheets, JSON for pipelines, Markdown for humans."""

from __future__ import annotations

import csv
import io
import json


def rows_to_csv(rows):
    """Serialise a list of flat dicts to CSV text (union of all keys)."""
    if not rows:
        return ""
    fieldnames = []
    for row in rows:
        for key in row:
            if key not in fieldnames:
                fieldnames.append(key)
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=fieldnames, extrasaction="ignore")
    writer.writeheader()
    for row in rows:
        writer.writerow({key: row.get(key, "") for key in fieldnames})
    return buffer.getvalue()


def report_to_json(report, indent=2):
    return json.dumps(report, indent=indent, default=str)


def _table(rows, columns):
    if not rows:
        return "_No data._\n"
    header = "| " + " | ".join(label for label, _ in columns) + " |"
    divider = "| " + " | ".join("---" for _ in columns) + " |"
    lines = [header, divider]
    for row in rows:
        cells = []
        for _label, key in columns:
            value = row.get(key, "")
            if isinstance(value, float):
                value = f"{value:,.2f}"
            elif isinstance(value, list):
                value = ", ".join(str(v) for v in value[:5])
            cells.append(str(value))
        lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(lines) + "\n"


def report_to_markdown(report):
    """A shareable brief: findings first, evidence underneath."""
    subject = report.get("subject") or "(no subject)"
    kind = report.get("kind", "report").title()
    currency = report.get("currency", "")
    lines = [
        f"# eBay {kind} Research — {subject}",
        "",
        f"*Marketplace {report.get('marketplace', '')} · generated "
        f"{report.get('generated_at', '')} · prices in {currency}*",
        "",
        "## What this means",
        "",
    ]
    for finding in report.get("findings", []):
        lines.append(f"- {finding}")
    lines.append("")

    for warning in report.get("warnings", []):
        lines.append(f"> ⚠️ {warning}")
    if report.get("warnings"):
        lines.append("")

    prices = report.get("prices") or {}
    if prices.get("count"):
        lines += [
            "## Price distribution (including postage)",
            "",
            _table(
                [prices],
                [
                    ("Count", "count"),
                    ("Min", "min"),
                    ("P25", "p25"),
                    ("Median", "median"),
                    ("P75", "p75"),
                    ("P90", "p90"),
                    ("Max", "max"),
                    ("Mean", "mean"),
                ],
            ),
        ]

    competition = report.get("competition")
    if competition and competition.get("top_sellers"):
        lines += [
            "## Competition",
            "",
            f"{competition['sellers']} sellers · HHI {competition['hhi']} · "
            f"{competition['concentration']}",
            "",
            _table(
                competition["top_sellers"][:10],
                [("Seller", "seller"), ("Listings", "listings"), ("Share", "share")],
            ),
        ]

    if report.get("keywords"):
        lines += [
            "## Keywords buyers see",
            "",
            _table(
                report["keywords"][:25],
                [("Phrase", "phrase"), ("Listings", "listings"), ("Share", "share")],
            ),
        ]

    if report.get("phrases"):
        lines += [
            "## Two-word phrases",
            "",
            _table(
                report["phrases"][:15],
                [("Phrase", "phrase"), ("Listings", "listings"), ("Share", "share")],
            ),
        ]

    sold = report.get("sold")
    if sold:
        performance = sold["performance"]
        lines += [
            "## Sold performance (90 days)",
            "",
            f"- Units sold: **{performance['sold_units']}** "
            f"({performance['units_per_day']}/day)",
            f"- Sell-through rate: **{performance['sell_through_rate']:.1%}**",
            f"- Estimated revenue: **{performance['estimated_revenue']:,.2f} {currency}**",
            f"- Average sale price: **{performance['average_sale_price']}**",
            "",
        ]
        if sold.get("price_bands"):
            lines += [
                "### Sell-through by price band",
                "",
                _table(
                    sold["price_bands"],
                    [
                        ("From", "band_low"),
                        ("To", "band_high"),
                        ("Active", "active"),
                        ("Sold", "sold"),
                        ("STR", "sell_through_rate"),
                    ],
                ),
            ]
        if sold.get("winning_terms"):
            lines += [
                "### Terms that convert",
                "",
                _table(
                    sold["winning_terms"][:15],
                    [
                        ("Phrase", "phrase"),
                        ("Score", "z_score"),
                        ("In sold", "target_count"),
                        ("In active", "background_count"),
                    ],
                ),
            ]

    weakest = report.get("weakest_listings")
    if weakest:
        lines += [
            "## Weakest titles in the catalogue",
            "",
            _table(
                weakest[:15],
                [("Score", "score"), ("Length", "length"), ("Title", "title")],
            ),
        ]

    trend = report.get("trend")
    if trend:
        lines += [
            "## Change since last run",
            "",
            f"- Listings: {trend['listings_before']} → {trend['listings_now']}",
            f"- New: {trend['new_listings']} · Gone: {trend['removed_listings']}",
            f"- Median price: {trend['median_price_before']} → {trend['median_price_now']}",
            "",
        ]
        if trend.get("price_changes"):
            lines += [
                "### Biggest price moves",
                "",
                _table(
                    trend["price_changes"][:10],
                    [
                        ("Title", "title"),
                        ("Was", "was"),
                        ("Now", "now"),
                        ("Change", "change"),
                    ],
                ),
            ]

    lines += [
        "",
        "---",
        "",
        "Data from the eBay Browse and Marketplace Insights APIs. Sold figures cover "
        "the last 90 days and are eBay's own estimates.",
    ]
    return "\n".join(lines)


def score_to_markdown(result):
    """Render a single title score as a readable block."""
    lines = [
        f"**Score {result['score']}/100 — {result['verdict']}**",
        "",
        f"`{result['title']}` ({result['length']}/80 characters)",
        "",
    ]
    for component in result["components"]:
        lines.append(
            f"- **{component['name']}** {component['score']}/{component['max']} — "
            f"{component['reason']}"
        )
    if result.get("problems"):
        lines += ["", "**Problems**"] + [f"- {p}" for p in result["problems"]]
    if result.get("missing_keywords"):
        lines += [
            "",
            "**Missing high-value terms**: "
            + ", ".join(
                f"{m['phrase']} ({m['share']:.0%} of listings)"
                for m in result["missing_keywords"][:8]
            ),
        ]
    return "\n".join(lines)

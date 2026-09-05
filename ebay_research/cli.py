"""Command-line access to the research pipelines.

Useful for batch work and for scheduled trend tracking -- run the same seller
nightly from cron and each run records a snapshot, so the change reports build
themselves.

    python -m ebay_research.cli market "personalised picture book" --markdown
    python -m ebay_research.cli seller wonderleaf_books --max-items 1000 --csv out.csv
    python -m ebay_research.cli title "My Book Title" --market "picture book"
    python -m ebay_research.cli budget
"""

from __future__ import annotations

import argparse
import sys

from . import export, research, scoring
from .client import EbayClient
from .config import MARKETPLACES, load_settings
from .errors import EbayResearchError


def _client(args):
    settings = load_settings(
        marketplace=args.marketplace,
        rate_limit_rps=args.rate,
    )
    return EbayClient(settings)


def _emit(report, args):
    if args.json:
        text = export.report_to_json(report)
    elif args.markdown:
        text = export.report_to_markdown(report)
    else:
        text = "\n".join(f"- {finding}" for finding in report.get("findings", []))
    print(text)
    if args.csv:
        with open(args.csv, "w", encoding="utf-8") as handle:
            handle.write(export.rows_to_csv(report.get("listings", [])))
        print(f"\nListings written to {args.csv}", file=sys.stderr)
    for notice in report.get("warnings", []):
        print(f"! {notice}", file=sys.stderr)


def _common_options(parser, suppress=False):
    """Options accepted both before and after the subcommand.

    On the subcommand copies the defaults are suppressed, so a flag given
    before the subcommand is not silently overwritten by the subparser's own
    default -- argparse's oldest footgun.
    """

    def default(value):
        return argparse.SUPPRESS if suppress else value

    parser.add_argument(
        "--marketplace", default=default(None), choices=sorted(MARKETPLACES),
        help="Marketplace to query (default from EBAY_MARKETPLACE).",
    )
    parser.add_argument(
        "--rate", type=float, default=default(None), help="Requests per second."
    )
    parser.add_argument(
        "--max-items", type=int, default=default(400), help="Listings to sample."
    )
    parser.add_argument(
        "--json", action="store_true", default=default(False),
        help="Print the full JSON report.",
    )
    parser.add_argument(
        "--markdown", action="store_true", default=default(False),
        help="Print a Markdown brief.",
    )
    parser.add_argument(
        "--csv", default=default(None), help="Write sampled listings to this CSV."
    )
    parser.add_argument(
        "--no-sold", action="store_true", default=default(False),
        help="Skip the sold-item lookup.",
    )
    return parser


def build_parser():
    parser = argparse.ArgumentParser(
        prog="ebay_research",
        description="eBay market, seller and title research over the official APIs.",
    )
    _common_options(parser)

    # Repeating the shared options on each subcommand means they work in the
    # natural position too: `market "unicorn book" --markdown`.
    shared = _common_options(argparse.ArgumentParser(add_help=False), suppress=True)
    sub = parser.add_subparsers(dest="command", required=True)

    market = sub.add_parser("market", parents=[shared],
                            help="Research a search term as a market.")
    market.add_argument("query")
    market.add_argument("--category", default=None)
    market.add_argument("--min-price", type=float, default=None)
    market.add_argument("--max-price", type=float, default=None)

    seller = sub.add_parser("seller", parents=[shared],
                            help="Research one seller's catalogue.")
    seller.add_argument("username")
    seller.add_argument("--query", default=None, help="Narrow the sweep by keyword.")

    compare = sub.add_parser("compare", parents=[shared],
                             help="Compare several sellers.")
    compare.add_argument("usernames", nargs="+")
    compare.add_argument("--query", default=None)

    title = sub.add_parser("title", parents=[shared],
                           help="Score a title against a live market.")
    title.add_argument("title")
    title.add_argument("--market", default=None, help="Search term to benchmark against.")

    sub.add_parser("budget", parents=[shared],
                   help="Show today's remaining API allowance.")
    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)
    try:
        client = _client(args)

        if args.command == "budget":
            if not client.pool:
                print(
                    "No eBay credentials configured. Set EBAY_CLIENT_ID and "
                    "EBAY_CLIENT_SECRET (free at developer.ebay.com/my/keys).",
                    file=sys.stderr,
                )
                return 1
            remaining = client.budget("browse")
            print(f"Keysets configured: {len(client.pool)}")
            print(f"Browse calls left today: {remaining:,}")
            print(
                "eBay counts this allowance per application keyset, not per IP "
                "address — add a keyset to raise it."
            )
            for row in client.pool.status("browse"):
                print(
                    f"  {row['keyset']:<20} {row['status']:<10} "
                    f"{row['remaining_today']} left"
                )
            return 0

        if args.command == "market":
            report = research.research_market(
                client,
                args.query,
                category_ids=args.category,
                price_min=args.min_price,
                price_max=args.max_price,
                max_items=args.max_items,
                include_sold=not args.no_sold,
            )
            _emit(report, args)

        elif args.command == "seller":
            report = research.research_seller(
                client,
                args.username,
                query=args.query,
                max_items=args.max_items,
                include_sold=not args.no_sold,
            )
            _emit(report, args)

        elif args.command == "compare":
            result = research.compare_sellers(
                client, args.usernames, query=args.query, max_items=args.max_items
            )
            print(export.rows_to_csv(result["sellers"]))

        elif args.command == "title":
            market_titles = []
            if args.market:
                report = research.research_market(
                    client, args.market, max_items=min(args.max_items, 200)
                )
                market_titles = [row["title"] for row in report["listings"]]
            result = scoring.score_title(args.title, market_titles=market_titles)
            print(export.score_to_markdown(result))
            suggestion = scoring.suggest_title([args.title], market_titles)
            if suggestion["title"]:
                print("\n**Suggested**\n")
                print(suggestion["title"])

        for notice in client.notices:
            print(f"! {notice}", file=sys.stderr)
        return 0

    except EbayResearchError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        return 130


if __name__ == "__main__":
    raise SystemExit(main())

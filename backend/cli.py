"""Command-line entry point for a repeatable Elexon wind analysis."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path
from typing import Sequence
from zoneinfo import ZoneInfo

from .wind_analysis import ElexonDataError, analyze_period


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Fetch Elexon wind actuals and forecasts and calculate as-of accuracy metrics."
    )
    parser.add_argument("--start-date", type=date.fromisoformat, default=date(2026, 1, 1))
    parser.add_argument("--end-date", type=date.fromisoformat, default=date(2026, 1, 31))
    parser.add_argument(
        "--cutoff-hour",
        type=int,
        default=10,
        help="Local hour on the day before delivery (default: 10).",
    )
    parser.add_argument(
        "--timezone",
        default="Europe/London",
        help="IANA timezone for cutoff and delivery dates (default: Europe/London).",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Write the JSON report to this path instead of stdout.",
    )
    parser.add_argument("--timeout", type=float, default=30.0)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.end_date < args.start_date:
        parser.error("--end-date must be on or after --start-date")
    try:
        report = analyze_period(
            args.start_date,
            args.end_date,
            cutoff_hour=args.cutoff_hour,
            cutoff_timezone=ZoneInfo(args.timezone),
            timeout=args.timeout,
        )
    except (ElexonDataError, ValueError, OSError) as exc:
        print(f"Analysis failed: {exc}", file=sys.stderr)
        return 1

    rendered = json.dumps(report, indent=2, ensure_ascii=False) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
        print(f"Wrote report to {args.output}")
    else:
        print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

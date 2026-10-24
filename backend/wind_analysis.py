"""Fetch and evaluate Elexon GB wind actuals and forecast vintages.

The January 2026 WINDFOR feed is hourly while FUELHH is half-hourly. Each
forecast hour is therefore compared with the mean of its two half-hour actual
average-MW observations. The default decision cutoff is a documented pilot
assumption and can be changed by the caller.
"""

from __future__ import annotations

import json
import math
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
from datetime import date, datetime, time, timedelta, timezone
from typing import Any, Iterable
from zoneinfo import ZoneInfo


UTC = timezone.utc
LONDON = ZoneInfo("Europe/London")
DEFAULT_BASE_URL = "https://data.elexon.co.uk/bmrs/api/v1"
DEFAULT_CUTOFF_HOUR = 10


class ElexonDataError(RuntimeError):
    """Raised when Elexon data cannot be retrieved or validated."""


@dataclass(frozen=True)
class Actual:
    start_time: datetime
    generation_mw: float | None
    publish_time: datetime | None


@dataclass(frozen=True)
class Forecast:
    start_time: datetime
    publish_time: datetime
    generation_mw: float | None


@dataclass(frozen=True)
class EvaluationPoint:
    delivery_start: str
    cutoff_local: str
    cutoff_utc: str
    forecast_publish_time: str | None
    forecast_mw: float | None
    actual_mw: float | None
    error_mw: float | None
    absolute_error_mw: float | None
    status: str


def parse_timestamp(value: Any, *, field: str) -> datetime:
    """Parse an ISO-8601 timestamp and normalize it to UTC."""
    if not isinstance(value, str) or not value.strip():
        raise ElexonDataError(f"Expected an ISO-8601 timestamp for {field}.")
    try:
        parsed = datetime.fromisoformat(value.strip().replace("Z", "+00:00"))
    except ValueError as exc:
        raise ElexonDataError(f"Invalid timestamp in {field}: {value!r}") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ElexonDataError(f"Timestamp in {field} has no timezone: {value!r}")
    return parsed.astimezone(UTC)


def _number(value: Any, *, field: str) -> float | None:
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, (float, int)):
        raise ElexonDataError(f"Expected a numeric value for {field}.")
    numeric = float(value)
    if not math.isfinite(numeric):
        raise ElexonDataError(f"Expected a finite value for {field}.")
    return numeric


def _fetch_rows(
    dataset: str,
    params: dict[str, str],
    *,
    base_url: str = DEFAULT_BASE_URL,
    timeout: float = 30.0,
) -> list[dict[str, Any]]:
    query = urllib.parse.urlencode(params)
    url = f"{base_url.rstrip('/')}/datasets/{dataset}/stream?{query}"
    request = urllib.request.Request(
        url,
        headers={"Accept": "application/json", "User-Agent": "Gridbricks-Wind-Pilot/1.0"},
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read(500).decode("utf-8", errors="replace")
        raise ElexonDataError(
            f"Elexon {dataset} request failed with HTTP {exc.code}: {detail}"
        ) from exc
    except (urllib.error.URLError, TimeoutError) as exc:
        raise ElexonDataError(f"Could not reach Elexon {dataset}: {exc}") from exc
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ElexonDataError(f"Elexon {dataset} returned invalid JSON.") from exc

    if not isinstance(payload, list):
        raise ElexonDataError(
            f"Elexon {dataset} returned {type(payload).__name__}; expected a JSON array."
        )
    if any(not isinstance(row, dict) for row in payload):
        raise ElexonDataError(f"Elexon {dataset} returned a non-object row.")
    return payload


def fetch_actuals(
    start_date: date,
    end_date: date,
    *,
    base_url: str = DEFAULT_BASE_URL,
    timeout: float = 30.0,
) -> list[Actual]:
    """Fetch FUELHH wind outturn for inclusive settlement dates."""
    if end_date < start_date:
        raise ValueError("end_date must be on or after start_date")
    rows = _fetch_rows(
        "FUELHH",
        {
            "settlementDateFrom": start_date.isoformat(),
            "settlementDateTo": end_date.isoformat(),
            "fuelType": "WIND",
        },
        base_url=base_url,
        timeout=timeout,
    )
    latest_by_start: dict[datetime, Actual] = {}
    for row in rows:
        if row.get("fuelType") != "WIND":
            raise ElexonDataError("FUELHH returned a row outside the requested WIND filter.")
        start = parse_timestamp(row.get("startTime"), field="FUELHH.startTime")
        published_value = row.get("publishTime")
        published = (
            parse_timestamp(published_value, field="FUELHH.publishTime")
            if published_value is not None
            else None
        )
        actual = Actual(
            start_time=start,
            generation_mw=_number(row.get("generation"), field="FUELHH.generation"),
            publish_time=published,
        )
        previous = latest_by_start.get(start)
        if previous is None or (published is not None and (previous.publish_time is None or published > previous.publish_time)):
            latest_by_start[start] = actual
        elif previous.publish_time == published and previous.generation_mw != actual.generation_mw:
            raise ElexonDataError(
                f"Conflicting FUELHH records share startTime and publishTime: {start.isoformat()}"
            )
    return sorted(latest_by_start.values(), key=lambda item: item.start_time)


def fetch_forecasts(
    publish_from: datetime,
    publish_to: datetime,
    *,
    base_url: str = DEFAULT_BASE_URL,
    timeout: float = 30.0,
) -> list[Forecast]:
    """Fetch WINDFOR forecast vintages within an inclusive publication window."""
    if publish_from.tzinfo is None or publish_to.tzinfo is None:
        raise ValueError("Forecast publication bounds must be timezone-aware")
    if publish_to < publish_from:
        raise ValueError("publish_to must be on or after publish_from")
    rows = _fetch_rows(
        "WINDFOR",
        {
            "publishDateTimeFrom": _format_timestamp(publish_from.astimezone(UTC)),
            "publishDateTimeTo": _format_timestamp(publish_to.astimezone(UTC)),
        },
        base_url=base_url,
        timeout=timeout,
    )
    forecasts: list[Forecast] = []
    for row in rows:
        forecasts.append(
            Forecast(
                start_time=parse_timestamp(row.get("startTime"), field="WINDFOR.startTime"),
                publish_time=parse_timestamp(row.get("publishTime"), field="WINDFOR.publishTime"),
                generation_mw=_number(row.get("generation"), field="WINDFOR.generation"),
            )
        )
    return forecasts


def _format_timestamp(value: datetime) -> str:
    return value.astimezone(UTC).isoformat(timespec="seconds").replace("+00:00", "Z")


def _expected_hour_starts(day: date, tz: ZoneInfo) -> Iterable[datetime]:
    """Yield each UTC hour start in a local calendar day, including DST correctly."""
    start = datetime.combine(day, time.min, tzinfo=tz).astimezone(UTC)
    end = datetime.combine(day + timedelta(days=1), time.min, tzinfo=tz).astimezone(UTC)
    current = start
    while current < end:
        yield current
        current += timedelta(hours=1)


def _decision_cutoff(day: date, hour: int, tz: ZoneInfo) -> datetime:
    previous_day = day - timedelta(days=1)
    return datetime.combine(previous_day, time(hour=hour), tzinfo=tz).astimezone(UTC)


def evaluate(
    start_date: date,
    end_date: date,
    actuals: Iterable[Actual],
    forecasts: Iterable[Forecast],
    *,
    cutoff_hour: int = DEFAULT_CUTOFF_HOUR,
    cutoff_timezone: ZoneInfo = LONDON,
) -> dict[str, Any]:
    """Select as-of forecast vintages, align actuals, and compute error metrics.

    The comparison is hourly: each forecast is matched with the arithmetic mean
    of actual MW observations at the forecast start and 30 minutes later.
    """
    if end_date < start_date:
        raise ValueError("end_date must be on or after start_date")
    if not 0 <= cutoff_hour <= 23:
        raise ValueError("cutoff_hour must be between 0 and 23")

    actual_by_start: dict[datetime, Actual] = {}
    for actual in actuals:
        if actual.start_time.minute not in (0, 30) or actual.start_time.second or actual.start_time.microsecond:
            raise ElexonDataError(f"Unexpected FUELHH interval start: {_format_timestamp(actual.start_time)}")
        previous = actual_by_start.get(actual.start_time)
        if previous is not None and previous != actual:
            raise ElexonDataError(f"Actuals were not deduplicated for {actual.start_time.isoformat()}")
        actual_by_start[actual.start_time] = actual

    forecasts_by_start: dict[datetime, list[Forecast]] = defaultdict(list)
    seen_forecast_versions: dict[tuple[datetime, datetime], float | None] = {}
    for forecast in forecasts:
        if forecast.start_time.minute != 0 or forecast.start_time.second or forecast.start_time.microsecond:
            raise ElexonDataError(f"Unexpected WINDFOR hourly start: {_format_timestamp(forecast.start_time)}")
        key = (forecast.start_time, forecast.publish_time)
        if key in seen_forecast_versions:
            if seen_forecast_versions[key] != forecast.generation_mw:
                raise ElexonDataError("Conflicting WINDFOR rows share delivery and publication timestamps.")
            continue
        seen_forecast_versions[key] = forecast.generation_mw
        forecasts_by_start[forecast.start_time].append(forecast)

    points: list[EvaluationPoint] = []
    status_counts: Counter[str] = Counter()
    errors: list[float] = []
    expected_count = 0

    day = start_date
    while day <= end_date:
        cutoff = _decision_cutoff(day, cutoff_hour, cutoff_timezone)
        for delivery_start in _expected_hour_starts(day, cutoff_timezone):
            expected_count += 1
            eligible = [
                item
                for item in forecasts_by_start.get(delivery_start, ())
                if item.publish_time <= cutoff
            ]
            chosen = max(eligible, key=lambda item: item.publish_time) if eligible else None
            actual_first = actual_by_start.get(delivery_start)
            actual_second = actual_by_start.get(delivery_start + timedelta(minutes=30))

            if chosen is None:
                status = "no_eligible_forecast"
                forecast_value = None
                publication = None
            else:
                forecast_value = chosen.generation_mw
                publication = _format_timestamp(chosen.publish_time)
                if forecast_value is None:
                    status = "forecast_generation_missing"
                elif actual_first is None or actual_second is None:
                    status = "actual_half_hour_missing"
                elif actual_first.generation_mw is None or actual_second.generation_mw is None:
                    status = "actual_generation_missing"
                else:
                    status = "matched"

            actual_value: float | None = None
            error: float | None = None
            absolute_error: float | None = None
            if status == "matched":
                assert chosen is not None and forecast_value is not None
                assert actual_first is not None and actual_second is not None
                first_generation = actual_first.generation_mw
                second_generation = actual_second.generation_mw
                assert first_generation is not None and second_generation is not None
                actual_value = (first_generation + second_generation) / 2
                error = forecast_value - actual_value
                absolute_error = abs(error)
                errors.append(error)

            status_counts[status] += 1
            points.append(
                EvaluationPoint(
                    delivery_start=_format_timestamp(delivery_start),
                    cutoff_local=cutoff.astimezone(cutoff_timezone).isoformat(timespec="minutes"),
                    cutoff_utc=_format_timestamp(cutoff),
                    forecast_publish_time=publication,
                    forecast_mw=forecast_value,
                    actual_mw=actual_value,
                    error_mw=error,
                    absolute_error_mw=absolute_error,
                    status=status,
                )
            )
        day += timedelta(days=1)

    matched_count = len(errors)
    return {
        "period": {"start_date": start_date.isoformat(), "end_date": end_date.isoformat()},
        "decision_rule": {
            "cutoff_hour": cutoff_hour,
            "cutoff_timezone": getattr(cutoff_timezone, "key", str(cutoff_timezone)),
            "description": f"latest WINDFOR publishTime at or before {cutoff_hour:02d}:00 local time on the calendar day before delivery",
        },
        "alignment": "hourly forecast compared with the mean of FUELHH at startTime and startTime + 30 minutes",
        "metrics": {
            "unit": "MW",
            "error_definition": "forecast - actual",
            "matched_pairs": matched_count,
            "expected_hours": expected_count,
            "coverage": matched_count / expected_count if expected_count else 0.0,
            "mae": sum(abs(value) for value in errors) / matched_count if matched_count else None,
            "mean_bias": sum(errors) / matched_count if matched_count else None,
        },
        "status_counts": dict(sorted(status_counts.items())),
        "points": [asdict(point) for point in points],
    }


def analyze_period(
    start_date: date,
    end_date: date,
    *,
    cutoff_hour: int = DEFAULT_CUTOFF_HOUR,
    cutoff_timezone: ZoneInfo = LONDON,
    base_url: str = DEFAULT_BASE_URL,
    timeout: float = 30.0,
) -> dict[str, Any]:
    """Fetch source data for a period and return an as-of evaluation report."""
    if end_date < start_date:
        raise ValueError("end_date must be on or after start_date")
    # Include a three-day lookback so an earlier eligible vintage can still be
    # selected if the prior-day issue is absent. All rows are filtered by the
    # exact per-delivery cutoff inside evaluate().
    publish_from = datetime.combine(
        start_date - timedelta(days=3), time.min, tzinfo=cutoff_timezone
    ).astimezone(UTC)
    publish_to = datetime.combine(
        end_date + timedelta(days=1), time.min, tzinfo=cutoff_timezone
    ).astimezone(UTC)
    actuals = fetch_actuals(start_date, end_date, base_url=base_url, timeout=timeout)
    forecasts = fetch_forecasts(publish_from, publish_to, base_url=base_url, timeout=timeout)
    report = evaluate(
        start_date,
        end_date,
        actuals,
        forecasts,
        cutoff_hour=cutoff_hour,
        cutoff_timezone=cutoff_timezone,
    )
    report["sources"] = {
        "actuals": "Elexon BMRS FUELHH filtered to fuelType=WIND",
        "actual_rows_received": len(actuals),
        "forecasts": "Elexon BMRS WINDFOR filtered by publication-time range",
        "forecast_rows_received": len(forecasts),
        "forecast_publish_window": {
            "from": _format_timestamp(publish_from),
            "to": _format_timestamp(publish_to),
        },
    }
    return report

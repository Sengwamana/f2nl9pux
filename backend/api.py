"""HTTP API exposing the reusable Elexon wind analysis."""

from __future__ import annotations

import os
from datetime import date
from functools import lru_cache
from pathlib import Path
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from .wind_analysis import ElexonDataError, analyze_period


JANUARY_START = date(2026, 1, 1)
JANUARY_END = date(2026, 1, 31)
DEFAULT_TIMEZONE = "Europe/London"

app = FastAPI(
    title="Gridbricks Wind Procurement API",
    description="Elexon GB wind forecast and outturn analysis for January 2026.",
    version="0.1.0",
)

allowed_origins = [
    origin.strip()
    for origin in os.getenv("CORS_ALLOW_ORIGINS", "http://localhost:5173").split(",")
    if origin.strip()
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=False,
    allow_methods=["GET"],
    allow_headers=["Content-Type"],
)

FRONTEND_BUILD = Path(__file__).resolve().parent.parent / "frontend" / "dist"


@lru_cache(maxsize=16)
def _cached_analysis(
    start_date: date,
    end_date: date,
    cutoff_hour: int,
    timezone_name: str,
) -> dict:
    """Cache historical requests to avoid repeatedly downloading the same month."""
    return analyze_period(
        start_date,
        end_date,
        cutoff_hour=cutoff_hour,
        cutoff_timezone=ZoneInfo(timezone_name),
    )


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/analysis")
def get_analysis(
    start_date: date = Query(default=JANUARY_START),
    end_date: date = Query(default=JANUARY_END),
    cutoff_hour: int = Query(default=10, ge=0, le=23),
    timezone_name: str = Query(default=DEFAULT_TIMEZONE, alias="timezone"),
) -> dict:
    if end_date < start_date:
        raise HTTPException(status_code=422, detail="end_date must be on or after start_date")
    if start_date < JANUARY_START or end_date > JANUARY_END:
        raise HTTPException(
            status_code=422,
            detail="The pilot API is limited to delivery dates in January 2026.",
        )
    try:
        ZoneInfo(timezone_name)
    except (ZoneInfoNotFoundError, ValueError):
        raise HTTPException(status_code=422, detail="timezone must be a valid IANA timezone") from None
    try:
        return _cached_analysis(start_date, end_date, cutoff_hour, timezone_name)
    except ElexonDataError as exc:
        raise HTTPException(status_code=502, detail=f"Elexon data unavailable: {exc}") from exc


if FRONTEND_BUILD.is_dir():
    from fastapi.staticfiles import StaticFiles

    app.mount("/", StaticFiles(directory=FRONTEND_BUILD, html=True), name="frontend")


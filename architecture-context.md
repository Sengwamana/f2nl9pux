# Architecture Context

## Status and evidence boundary

The repository contains a Python Elexon analysis module and CLI, a FastAPI HTTP API, a Vite/React TypeScript dashboard, and a multi-stage Docker build. A January 2026 analysis report is also checked in under `data/`. A hosted deployment is not yet created.

## Required technology and target responsibilities

| Element | Status | Intended responsibility |
| --- | --- | --- |
| React frontend | Implemented | `frontend/src/` presents date range/cutoff controls, matched forecast/actual series, timestamps, coverage, and accuracy analysis. |
| Python backend | Implemented | `backend/wind_analysis.py` owns Elexon retrieval and metrics; `backend/cli.py` generates reports; `backend/api.py` exposes FastAPI endpoints. |
| Elexon BMRS `FUELHH` | Integrated | `backend/wind_analysis.py` fetches actual generation filtered to `fuelType=WIND`, then validates and aligns the half-hour records. |
| Elexon BMRS `WINDFOR` | Integrated | `backend/wind_analysis.py` fetches forecast vintages and selects by delivery `startTime` and cutoff-eligible `publishTime`. |
| Docker | Implemented; build not verified in this environment | `Dockerfile` builds React assets and runs FastAPI in one image; `docker-compose.yml` exposes port 8000 and checks `/api/health`. |
| Heroku | Deployment target selected; deployment pending | Single container serves both frontend and API and binds to Heroku's `PORT`; Heroku login, Docker, and a hosted app are unavailable in this environment. |

The challenge mandates React, Python, Docker, and either Vercel or Heroku but does not provide a rationale for those choices. FastAPI and Vite are selected for the API and frontend build/development server. A single-container Heroku topology was selected to keep the browser and API same-origin and simplify deployment.

## Implemented data workflow

The processing must preserve both time axes: delivery (`startTime`) and forecast publication (`publishTime`). For each delivery day, evaluation compares the forecast vintage available by the selected decision cutoff. The project has adopted **10:00 Europe/London on the calendar day before delivery** as a provisional pilot cutoff, based on the “one day before” brief and the observed 09:30Z forecast publication. This is not a confirmed client trading deadline or market gate and should remain configurable/clearly labeled until confirmed.

1. Request FUELHH actuals by inclusive settlement-date range and `fuelType=WIND`; request WINDFOR by publication-time range. This fetch flow is implemented in `backend/wind_analysis.py`.
2. Validate response shape, timestamps, fuel filter, units, and numeric values.
3. Normalize timestamps as timezone-aware instants; use `Europe/London` for the pilot cutoff and show the timezone. January dates are GMT, but preserve source UTC timestamps and do not assume GMT for dates outside January.
4. Filter `FUELHH` to `WIND`; associate forecast and actual rows by delivery interval.
5. Select the latest forecast with `publishTime` no later than the delivery day's provisional 10:00 Europe/London previous-day cutoff.
6. WINDFOR returned hourly `startTime` rows in the January 2026 sample, while FUELHH returned 30-minute rows. For an hourly forecast starting at `t`, pair it with FUELHH at `t` and `t + 30 minutes`; average the two actual average-MW values. Require both actuals; do not interpolate missing data or convert it to zero.
7. Calculate MAE and mean bias (`forecast - actual`) in MW over matched hourly pairs; report sample size and coverage alongside them. Positive bias means the forecast was higher than the matched actual. These are the phase 1 pilot metrics; avoid percentage metrics because they are unstable around low/zero actuals.
8. Emit values and metadata as a JSON report through the CLI or expose the same analysis output through `GET /api/analysis` to the React client.

The workflow is implemented. The API caches identical historical query results in process memory (LRU size 16). Persistent storage, background ingestion, and authentication are not included.

## Data model concepts

The live OpenAPI specification and stream responses were checked during phase 1. Source references: [Elexon FUELHH stream documentation](https://bmrs.elexon.co.uk/api-documentation/endpoint/datasets/FUELHH/stream), [Elexon WINDFOR stream documentation](https://bmrs.elexon.co.uk/api-documentation/endpoint/datasets/WINDFOR/stream), and the [Elexon OpenAPI specification](https://data.elexon.co.uk/swagger/v1/swagger.json).

| Concept | Brief fields | Notes to verify |
| --- | --- | --- |
| Actual wind observation | `startTime`, `generation`, `fuelType`, `publishTime`, `settlementDate`, `settlementPeriod` | OpenAPI describes FUELHH as GB fuel-type generation outturn updated every 30 minutes, with average MW over each 30-minute interval. The `fuelType` query filter is supported. |
| Wind forecast | `startTime`, `publishTime`, `generation` | OpenAPI confirms these fields. Elexon describes forecast generation in MW. The January 2026 API response has hourly delivery start times and multiple forecast vintages; filter the stream by publication-time range. |
| Evaluation pair | hourly delivery time, selected forecast generation, mean of two actual values, selected publication time | Pair hourly forecast with the two half-hour actuals after applying the cutoff; capture included/excluded counts and timestamp provenance. |

### Phase 1 source-response findings

Direct requests to the official API on 2026-10-24 returned:

- `FUELHH/stream?settlementDateFrom=2026-01-01&settlementDateTo=2026-01-31&fuelType=WIND`: 1,488 records, exactly 48 per date, all `WIND`, all with non-null generation. The sample spans `2026-01-01T00:00:00Z` through `2026-01-31T23:30:00Z`.
- `WINDFOR/stream?publishDateTimeFrom=2025-12-25T00:00:00Z&publishDateTimeTo=2026-02-01T00:00:00Z`: 22,192 records in the response. In that sample the delivery start minute is always `:00`; each daily forecast issue carries hourly values.
- Applying the provisional cutoff and hourly alignment yields 744/744 matched forecast hours (24 per delivery day, Jan 1–31). The latest eligible publication for the hourly intervals is available on each date; the selected publication was typically 09:30Z in this sample.
- With those provisional rules, sample MAE is 2,122.81 MW and mean bias is +1,840.30 MW (`forecast - actual`) across 744 hourly pairs. These are exploratory baseline values, not product claims, and must be recalculated by the implemented pipeline.

The implemented pipeline was run for January 1–31, 2026. It fetched 1,488 actual rows and 19,856 forecast rows over a publication window from 2025-12-29 to 2026-02-01, then produced 744 matched hourly points with 100% coverage, MAE 2,122.81 MW, and mean bias +1,840.30 MW. The resulting detailed JSON report is [data/january_2026_analysis.json](data/january_2026_analysis.json). It includes each delivery start, local/UTC cutoff, chosen forecast publication time, values, error, and match status.

Elexon's [generation-by-fuel-type description](https://bmrs.elexon.co.uk/generation-by-fuel-type) warns that renewable outturn values in that report underestimate generation because embedded generation and wind farms without operational meters are excluded. Its [wind forecast description](https://bmrs.elexon.co.uk/wind-generation) says forecasts cover wind farms visible to ESO with operational metering. Present this as Elexon-reported/monitored GB wind, not a complete census of every GB wind generator; confirm source coverage is acceptable for the client before making broader national-generation claims.

## Remaining product/API decisions

- Confirm with the client whether the provisional previous-day 10:00 Europe/London cutoff reflects their real purchase workflow; the app should make it explicit.
- Confirm hourly aggregation of actuals is acceptable given the forecast cadence. Do not duplicate an hourly forecast onto two half-hours and count it twice.
- Consider daily breakdowns or additional forecast lead-time context if procurement users need them.
- Revisit the process-local cache and request strategy if the sample is scaled beyond a single instance.

## Error handling, security, and operations

The analysis module validates upstream payloads and raises actionable data errors; the API maps upstream errors to HTTP 502. The React client presents loading, failure, and partial-coverage states. There are no credentials. Cache is process-local and not shared across instances.

The Docker build and Compose orchestration are present but have not been built or run because Docker is not installed in this environment. A hosted release and production observability are not present. `/api/health` is available as a basic process health endpoint. Direct Python dependencies are pinned in `backend/requirements.txt`; frontend dependencies are locked in `frontend/package-lock.json`. Python transitive dependencies are not yet captured in a fully resolved lockfile.

## Known limitations

- Wind-only data cannot identify total load, non-wind supply, or a complete additional procurement requirement.
- Evaluation results depend on the forecast cutoff, timezone handling, matching policy, and the population of intervals with both forecast and actual data.
- The specified January 2026 window is historical relative to implementation work; API checks confirm forecast and actual data are currently available for the sampled period.
- Elexon's reported renewable outturn excludes some embedded/unmetered generation, so “national” needs this coverage qualification.
- Docker configuration is present but awaits a Docker build/run; Heroku deployment remains outstanding. See [project-overview.md](project-overview.md) for scope and [progress-tracker.md](progress-tracker.md) for status.

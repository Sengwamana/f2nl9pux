# Project Overview

## Background and purpose

Gridbricks is a proposed pilot decision-support web app for a UK energy utility team that procures electricity in the day-ahead market. Renewable output varies with weather, so the team needs to understand the wind forecast available when it makes a purchase decision and how forecast values compare with observed generation.

The brief limits the pilot to national wind generation data from Elexon BMRS. The app is intended to make forecast availability and historical forecast accuracy easier to inspect; it is not described as a complete demand forecasting, market pricing, or dispatch system.

## Objectives and users

| User | Need |
| --- | --- |
| Day-ahead power procurement team | See the latest eligible national wind forecast for relevant delivery intervals and understand the uncertainty in that forecast. |
| Product/customer stakeholders | Review a clear pilot portal and analysis that explains how wind forecast information can inform procurement decisions. |
| Internal technical lead | Review the architecture, data processing, analysis, code, and engineering practices for maintainability and correctness. |

## Requirements

### Explicit business and product requirements

- Focus on purchase decisions made in January 2026.
- Use Great Britain fuel-type actual wind generation from Elexon `FUELHH`, filtered to `fuelType` = `WIND`; Elexon describes it as average MW per 30-minute interval.
- Use Elexon `WINDFOR` forecasts; the brief names `startTime` as delivery time, `publishTime` as forecast creation time, and `generation` as forecast power. Live January 2026 responses were hourly by delivery start, not half-hourly.
- Help users identify the latest forecast available at decision time.
- Quantitatively evaluate forecast accuracy so users can consider error in their decisions.
- Build with a React frontend and Python backend, use Docker, and deploy a sample app to Vercel or Heroku.
- Provide a README with repository contents, startup steps, and deployment link. State AI tool use in the README if AI tools were used.
- Provide a public GitHub repository under an anonymous/random name, an unlisted YouTube demo no longer than 10 minutes, and submit the details through the named challenge form. Verify submitted URLs in incognito mode.
- Keep total assignment effort within 16 hours.

### Functional requirements

1. Present Elexon-reported GB wind forecasts relevant to a day-ahead purchase decision, preserving forecast delivery start and publication time.
2. Present comparable actual generation. For the January sample, aggregate two consecutive half-hour FUELHH average-MW observations to each hourly forecast start using their arithmetic mean.
3. Compare matched hourly forecast and actual values with clearly defined quantitative error measures.
4. Communicate data coverage, missing values, the forecast vintage and decision cutoff used in a comparison.

Items 1–4 express the intended product behavior. The Python source-to-metrics module, CLI, FastAPI endpoints, initial React interface, and Docker configuration are implemented. The Docker image has not yet been built in this environment, and public deployment remains outstanding.

### Non-functional requirements

- Provide a usable, understandable experience for procurement users and a technically reviewable implementation.
- Keep actuals and forecasts traceable to their source and timestamps.
- Handle incomplete or unavailable upstream data without silently treating missing values as zero.
- Protect credentials and configuration if any are introduced.
- Support containerized local execution and a public sample deployment.

These are project quality expectations derived from the brief. Implementation status and verification limits are tracked in [progress-tracker.md](progress-tracker.md).

## Scope, limitations, and assumptions

### In scope

- National wind actuals and forecasts from the two named Elexon datasets.
- January 2026 purchase-decision context.
- A React/Python web application, Docker packaging, sample deployment, quantitative forecast evaluation, and the requested demo/repository/form deliverables.

### Out of scope under the stated data limit

- Demand data, market prices, other generation fuels, individual asset/region analysis, other forecast vendors, weather feeds, or automatic trade execution.
- Calculating the utility's full net procurement requirement. Wind-only data cannot establish that quantity without demand and other supply data.

### Assumptions and unresolved decisions

- The brief does not define the precise decision cutoff. Phase 1 adopts 10:00 Europe/London on the calendar day before delivery as a provisional analysis convention, not an asserted market gate. Confirm the client's actual workflow.
- The live FUELHH stream describes average MW over 30 minutes. The checked January WINDFOR response has hourly `startTime` values; actuals therefore need hourly alignment for a fair comparison. Confirm this aggregation is acceptable to the client.
- Use MAE and mean bias (`forecast - actual`) as the initial accuracy metrics, both in MW, alongside sample count/coverage. This is a documented pilot choice, not a metric specified by the brief. Exclude incomplete hourly actual pairs rather than filling missing values.
- Elexon's generation-by-fuel-type report warns that renewable outturn excludes embedded generation and wind farms without operational meters. Describe results as Elexon-reported/monitored GB wind, not a complete census of all GB wind generation.
- API parameters and payload fields have been verified from the official OpenAPI specification and direct January 2026 responses. Preserve UTC source timestamps; show the provisional decision cutoff in Europe/London. January is GMT, but other periods require daylight-saving-aware conversion.
- No screenshots, visual identity, or existing UI conventions were supplied.

## Terminology

| Term | Meaning in this project |
| --- | --- |
| Delivery interval | A source period identified by `startTime`. FUELHH is half-hourly; the checked WINDFOR sample is hourly. |
| Forecast vintage | A forecast value associated with a publication time; `publishTime` is needed to identify what was known at a decision cutoff. |
| Actual generation | Observed wind generation from `FUELHH` records where `fuelType` is `WIND`. |
| Forecast error | For this pilot baseline, hourly forecast generation minus the mean of the two corresponding half-hour actual MW values. Positive bias means forecast overestimation. |
| Day-ahead decision | The procurement decision made before delivery, described at a high level by the brief; exact market timing is not specified. |

## Acceptance criteria and definition of done

The pilot is ready for review when the implemented product can show the selected hourly forecast as of the stated cutoff and aligned actuals; explain source timestamps and Elexon coverage; calculate the defined hourly MAE and bias; and expose loading, empty, partial-data, and failure states. The React/Python application should run through Docker, be deployed to Vercel or Heroku, and be documented in the README. The public repository, two-part demo video (each part at most five minutes; total at most ten), incognito URL checks, and completed submission form are also required deliverables.

These are acceptance targets, not claims that the work is complete. Current status is in [progress-tracker.md](progress-tracker.md); system boundaries and unknowns are in [architecture-context.md](architecture-context.md).

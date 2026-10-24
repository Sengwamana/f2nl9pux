---
name: uk-wind-procurement-app
description: Build or change the Gridbricks pilot app for UK day-ahead electricity procurement using national Elexon wind forecasts and actuals. Use for product, data, UI, API, or analysis work in this repository.
---

# UK Wind Procurement Pilot

Help build and explain a decision-support web app for the UK utility team buying power through the day-ahead market. The core user need is to see the latest available national wind forecast at the decision point and compare forecasts with observed wind generation quantitatively.

## Fixed scope and constraints

- Frontend: React. Backend: Python. Use Docker. Deployment target requested by the brief: Vercel or Heroku.
- Data scope is national GB wind only, sourced from Elexon BMRS `FUELHH` actual generation (filter `fuelType == WIND`) and `WINDFOR` forecasts. Do not silently add demand, prices, thermal generation, other fuels, external weather, or other vendors.
- Relevant delivery periods are January 2026. FUELHH actuals are average MW per 30-minute interval; the checked January WINDFOR sample has hourly delivery start times. Align each hourly forecast to the mean of the two corresponding half-hour actuals, requiring both actuals and preserving the hourly delivery identity.
- `publishTime` is the forecast creation/availability time; preserve it because forecast vintages matter. The current provisional pilot cutoff is 10:00 Europe/London on the calendar day before delivery. This is an analysis convention, not a confirmed client trading deadline; make it visible and configurable pending confirmation.
- The source data can be revised, incomplete, delayed, or absent. Preserve source timestamps and units, handle gaps explicitly, and distinguish missing observations from zero generation.
- The app supports procurement decisions; it does not issue market orders or calculate a full procurement position. Do not imply that wind forecast error alone equals the utility's required additional purchase.

## Data and analysis guidance

- Verify endpoint schemas and query parameters against current official Elexon BMRS documentation or actual responses before coding against them. Never invent field names, units, pagination behavior, or availability guarantees.
- Join forecast and actual records on aligned delivery time (`startTime`), not on publication time. Since WINDFOR is hourly in the checked January sample and FUELHH is half-hourly, average the two consecutive actual values for each forecast hour. Retain forecast `publishTime` to select an as-of vintage.
- Initial evaluation metrics are MAE and mean bias (`forecast - actual`) in MW with matched-pair coverage. Label positive bias as forecast overestimation. Recalculate metrics from the implemented pipeline; exploratory phase 1 figures are not user claims.
- Define the evaluation population, handling of duplicate forecast vintages, missing pairs, and forecast lead time. Compare actuals against a forecast that would have been available at the stated decision cutoff.
- Report interpretable error measures with units and a clear denominator. Common choices include MAE and bias; if using percentage metrics, explain zero/low-actual handling. Avoid a single aggregate that hides interval or day-to-day variation.
- Show forecast and aligned actual values in MW at the hourly WINDFOR cadence for this sample. Label time zone and daylight-saving behavior. Do not assume API timestamps are local time; inspect and document the source convention.
- Treat historical accuracy as context for uncertainty, not a guarantee for a future interval. Keep claims bounded to the observed January 2026 sample and the selected forecast vintage rule.

## Product implementation

- Inspect repository files and project documentation before changes. Match existing patterns when present; if the repository is still a scaffold, choose the smallest coherent React/Python design that satisfies the requested workflow.
- Keep API acquisition, normalization, vintage selection, metric calculation, and presentation responsibilities distinct. Validate external payloads and return actionable errors for upstream failures, empty periods, and incomplete coverage.
- The main user workflow should make the delivery date/interval understandable, surface the latest eligible forecast, show available actuals for evaluation, and communicate forecast error without implying unsupported procurement quantities.
- Include loading, no-data, partial-data, stale-data, and upstream-error states. Use accessible labels and responsive layouts for chart/table data.
- Document actual behavior and limitations in README and project context docs. Mention use of AI tools in README when AI assisted the implementation, as required by the assignment.
- Do not claim a deployment, public repository, demo video, or form submission exists unless it has actually been completed and verified.

When requirements conflict with current code, preserve the user brief and report the conflict. For domain rules that can change, consult official sources rather than relying on memory.

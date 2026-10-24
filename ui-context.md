# UI Context

## User and primary workflow

The primary user is a UK utility day-ahead procurement team member. Their requested workflow is to understand which national wind forecast was available when making a decision and evaluate the forecast's accuracy against actual generation. The interface is not a full procurement optimizer and must not suggest that wind generation alone determines the amount to buy.

## Requirements versus recommendations

### Explicit requirements

- Make the latest relevant renewable forecast available for day-ahead decision making understandable.
- Quantitatively show forecast accuracy/error.
- Use national wind actuals and forecasts from the named Elexon datasets, focused on January 2026.

### Recommended design direction, not an existing design

The React dashboard is implemented in `frontend/src/App.tsx` and `frontend/src/styles.css`. No brand guide or design reference was provided. The current pilot uses a restrained slate-and-teal palette, dark navigation bar, white metric panels, and explicit historical-data labels; continue to treat these as product choices subject to review:

1. **Decision context:** selected delivery date, hourly delivery range, provisional decision cutoff (10:00 Europe/London on the previous day), and timezone.
2. **Forecast status:** latest eligible forecast publication time and forecast generation for each hourly interval.
3. **Forecast versus actual:** hourly forecast and actual series; actuals are the mean of the two matching half-hour FUELHH average-MW values. Include a table for exact timestamps and values.
4. **Accuracy summary:** MAE and forecast-minus-actual mean bias in MW, sample count/coverage, evaluation window, and selected-vintage rule.
5. **Data quality:** last source retrieval, missing/matched interval counts, stale or partial-data notice, and source links where practical.

The dashboard includes these elements in a single responsive view. The cutoff remains visibly described as provisional.

## Interaction and states

- Allow the user to inspect a delivery date or interval and identify the forecast vintage considered eligible at the displayed cutoff.
- Keep forecast publication time distinct from hourly delivery time in labels and tooltips; make the provisional cutoff visible.
- The frontend implements loading, API error, and partial-coverage states and explains that metrics use matched intervals. A distinct stale-data state is not implemented; API results are cached in process memory.
- Provide table access to chart values and ensure interaction works without a pointer.
- Do not silently change cutoff, timezone, metric definition, or evaluation population when a user changes the date range.

## Visual hierarchy and accessibility

No typography, brand palette, or component library was supplied. The page uses a dark slate header, teal accent, neutral surfaces, consistent borders, and restrained shadows. The chart and table use separate forecast/actual labels and colors. Continue to follow these accessibility recommendations:

- Prioritize delivery date, latest eligible publication, forecast level, and error context over decorative elements.
- Use consistent units and explicit timezone labels; distinguish forecast and actual by both labels and visual treatment, not color alone.
- Use readable contrast, semantic headings, keyboard-accessible controls, focus indicators, chart summaries or data tables, and screen-reader labels.
- Use a responsive layout: desktop can show chart and summary together; narrower screens should stack sections and preserve readable interval tables (horizontal scrolling only when needed).
- Avoid excessive precision and unexplained abbreviations; provide definitions for metrics and forecast error direction.

These are usability recommendations rather than verified existing design rules. Related product boundaries are in [project-overview.md](project-overview.md); implementation status is in [progress-tracker.md](progress-tracker.md).

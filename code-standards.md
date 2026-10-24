# Code Standards

## Current conventions

The repository has a Python analysis module and CLI, a FastAPI HTTP API under `backend/`, and a Vite/React TypeScript frontend under `frontend/`. Keep analysis usable independently of the HTTP layer. No formatter, linter, or automated test configuration is present.

## Repository organization

- Keep frontend and backend responsibilities in clearly separated `frontend/` and `backend/` directories; do not bury data-processing logic in UI components.
- Group React UI by meaningful feature/component responsibility, and keep API access and formatting separate from rendering.
- Keep Python API handlers thin; put Elexon access, schema validation, normalization, forecast-vintage selection, and metrics in focused modules.
- Keep reusable Elexon and analysis logic in `backend/wind_analysis.py`; keep command-line argument parsing and output handling in `backend/cli.py`. Keep FastAPI route handling in `backend/api.py` thin; frontend requests live in `frontend/src/api.ts` and response types in `frontend/src/types.ts`.
- Keep configuration, container files, documentation, and tests in predictable locations. Update the README when directory structure changes.
- Build the Vite app in a Node builder stage and copy only `frontend/dist` into the Python runtime image. Serve the static build from FastAPI after API routes; keep Heroku's configurable `PORT` binding in the container command.

## React and UI code

- Use TypeScript function components and hooks; keep components small and name components/types in `PascalCase` and functions/variables in `camelCase` unless the toolchain imposes another convention. Keep `frontend/package-lock.json` synchronized with its manifest.
- Separate server-data fetching from presentation. Represent loading, empty, partial, and error results explicitly.
- Avoid duplicating date/time or metric calculations across components. Use one tested formatting/analysis boundary and label units/timezone in the UI.
- Keep accessible names, keyboard operation, readable contrast, and responsive behavior in all data displays.

## Python and backend code

- Use `snake_case` for modules, functions, and variables; `PascalCase` for classes. Add type annotations to public functions and domain/data structures.
- Validate external JSON at the boundary. Do not allow loosely typed API payloads to flow into metric calculations unchecked.
- Keep network I/O, domain processing, and HTTP response construction separate. Use explicit timeouts and handle HTTP, parsing, validation, and incomplete-data failures.
- Make timestamps timezone-aware internally; preserve source values or offsets where needed for auditability.
- Use clear exception handling and structured, non-sensitive logs. Do not swallow errors or expose stack traces/secrets in public responses.

## Data and API conventions

- Treat `startTime` as delivery identity and `publishTime` as forecast-vintage time. Keep source timestamps in UTC; use timezone-aware `Europe/London` conversion for the pilot cutoff and UI labels.
- FUELHH provides 30-minute average MW, while the January 2026 WINDFOR sample has hourly delivery timestamps. For an hourly forecast at `t`, use the mean of actual FUELHH values at `t` and `t + 30 minutes`. Require both halves; do not duplicate the forecast onto two rows or interpolate missing values.
- For the current pilot baseline, choose the latest forecast `publishTime <= 10:00 Europe/London` on the calendar day before delivery. This remains a provisional decision cutoff until the client's process is confirmed.
- Define metric names, units, sign convention, evaluation window, and denominator in API output or adjacent documentation. Initial metrics: MAE and mean bias (`forecast - actual`) in MW, with pair count/coverage.
- Never interpret missing generation as zero. Validate numeric values and handle invalid rows explicitly.
- Use consistent JSON field naming and stable, documented error responses in the FastAPI service.

## Dependencies, configuration, and security

- Pin or lock dependencies using the package manager selected during implementation. `frontend/package-lock.json` locks the npm tree; `backend/requirements.txt` pins direct Python packages, but a fully resolved Python lock is still needed for repeatable runtime builds. Avoid adding libraries when standard platform features suffice.
- Keep secrets out of source control, documentation examples, logs, and frontend bundles. Use environment variables for deployment configuration and provide a safe example file with placeholders only.
- Apply least-privilege access if authentication or external credentials become necessary; neither is currently specified.
- Review dependency and container changes for purpose, maintenance, and image size.

## Quality checks and documentation

- Add focused tests for cutoff/vintage selection, UTC/local timezone boundaries, hourly aggregation from two half-hours, incomplete/missing halves, duplicate records, metrics, and API validation when those behaviors are implemented.
- Use the repository's configured formatter, linter, type checks, and build commands. No quality tooling or automated tests are configured yet; record actual commands in the README when added.
- Do not state a check passed unless it was run and its result observed. Document important decisions, assumptions, and changed behavior in the relevant context file.
- Keep this document aligned with actual frameworks, folder paths, tooling, and conventions as the repository evolves.

For AI-specific engineering expectations, see [ai-workflow-rules.md](ai-workflow-rules.md). The current implementation state is tracked in [progress-tracker.md](progress-tracker.md).

# Gridbricks Wind Desk

A pilot dashboard for inspecting Elexon-reported GB wind forecasts available by a configurable day-ahead cutoff and comparing those forecasts with matched wind outturn. This wind-only pilot does not calculate a utility's full procurement requirement.

## Repository guide

- `backend/wind_analysis.py` fetches Elexon `WINDFOR` and `FUELHH` data, selects eligible forecast vintages, aligns hourly forecasts to two half-hour actuals, and computes MAE/bias.
- `backend/cli.py` runs an analysis and writes a JSON report.
- `backend/api.py` serves health and analysis endpoints using FastAPI.
- `backend/requirements.txt` pins the direct Python runtime dependencies; `frontend/package-lock.json` locks the frontend dependency tree.
- `frontend/src/` contains the React dashboard, API client, response types, and styles.
- `frontend/package.json` and `frontend/package-lock.json` define the frontend dependencies and scripts.
- `Dockerfile`, `.dockerignore`, and `docker-compose.yml` build and run the single-container app.
- `data/january_2026_analysis.json` is the Phase 2 January analysis snapshot.
- `project-overview.md`, `architecture-context.md`, `code-standards.md`, `ui-context.md`, `ai-workflow-rules.md`, and `progress-tracker.md` hold persistent project context.
- `.agents/skills/` contains project-specific Codex skills.

## Run locally

Use Python 3.10+ and Node.js 20.19+ or 22.12+.

1. From the repository root, create and install the Python environment:

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r backend/requirements.txt
   ```

2. In one terminal, start the API from the repository root:

   ```bash
   uvicorn backend.api:app --reload --host 0.0.0.0 --port 8000
   ```

3. In another terminal, install and start the frontend:

   ```bash
   cd frontend
   npm ci
   npm run dev
   ```

4. Open the Vite URL printed in the terminal (normally `http://localhost:5173`). Vite proxies `/api` requests to `http://localhost:8000` during development.

The API exposes `/api/health` and `/api/analysis`. Analysis requests are limited to January 2026. Configure comma-separated browser origins with `CORS_ALLOW_ORIGINS` when the frontend is hosted separately.

To regenerate the CLI snapshot from the repository root:

```bash
python -m backend.cli --output data/january_2026_analysis.json
```

The app fetches historical Elexon data on the first API request for a parameter set and caches that result in process memory. The cutoff defaults to 10:00 Europe/London on the day before delivery; this remains a pilot assumption, not a confirmed client market deadline. Hourly forecast actuals are calculated from the mean of the two corresponding half-hour FUELHH average-MW observations. Python transitive dependencies are not yet captured in a fully resolved lockfile.

## Run with Docker

With Docker Engine and the Compose plugin installed, from the repository root:

```bash
docker compose up --build
```

Open `http://localhost:8000`. The container builds the React app and serves it and the API from the same FastAPI process. Docker Compose checks `/api/health` for container health. Stop it with `Ctrl+C`.

## Deployment

The app is configured for deployment on Heroku (container stack) or Vercel. The container serves the API and built frontend from the same process. A public deployment URL was not created in this environment because the Heroku account requires verification/payment info to create apps.

- **Public GitHub repo:** [Sengwamana/f2nl9pux](https://github.com/Sengwamana/f2nl9pux)
- **Deployed app (Vercel):** https://gridbricks-wind-fawn.vercel.app
- **Deployment:** Deployed to Vercel (frontend + API served together). API is limited to January 2026. For container deployment on Heroku, see instructions below.

To deploy to Heroku (container stack), install Docker Engine and the Heroku CLI, make sure your Heroku account can create/run apps, then run these commands from the repository root:

```bash
heroku login
heroku container:login
APP_NAME="choose-a-unique-app-name"
heroku create "$APP_NAME" --stack container
heroku container:push web --app "$APP_NAME"
heroku container:release web --app "$APP_NAME"
heroku open --app "$APP_NAME"
```

Choose an app name that is globally available on Heroku. The app URL is printed after creation and by `heroku open`. Verify it loads, then check the API health endpoint at `https://$APP_NAME.herokuapp.com/api/health`; add the verified public URL here after deployment. The container listens on Heroku's `PORT` environment variable. See [Heroku's container deployment guide](https://devcenter.heroku.com/articles/container-registry-and-runtime) for current platform steps.

## AI tooling

OpenAI Codex assisted with project context, implementation, and documentation. Review the code and analytical assumptions before using the pilot for operational decisions.

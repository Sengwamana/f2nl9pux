# Progress Tracker

Last reviewed: 2026-10-24

Status reflects evidence in the repository at the time of review. A requirement written down is not considered completed work.

## Milestones

| Phase | Status | Dependency / exit evidence |
| --- | --- | --- |
| 1. Confirm product and data rules | In progress | API and initial evaluation rules verified; client confirmation of provisional cutoff and hourly alignment remains open. |
| 2. Build data integration and analysis | Implemented | Fetch, selection, alignment, metrics, CLI, and January output are implemented. Automated checks are not configured. |
| 3. Build React/Python application | Implemented | FastAPI API and React/TypeScript dashboard are in place; frontend build and local API/UI run are verified. |
| 4. Containerize and deploy sample | In progress | Multi-stage Dockerfile and Compose setup are written; Docker build/run and Heroku release await an environment with Docker and authenticated Heroku CLI. |
| 5. Validate and document | In progress | README and six context docs reviewed; internal Markdown links resolve and frontend production build succeeds. Docker/runtime verification remains blocked by unavailable tooling. |
| 6. Demo and submission | Pending | Working app, public repo, deployment URL, recorded video, and access checks. |

## Work items

| Status | Task | Dependency / evidence |
| --- | --- | --- |
| Completed | Capture supplied challenge scope in project context docs | User-provided brief. |
| Completed | Create project-specific Codex skills | `.agents/skills/` contains product, documentation, and pitch/review skills. |
| Completed | Verify Elexon stream parameters, response fields, actual units/cadence, and January data coverage | Official OpenAPI spec and direct API requests on 2026-10-24; see [architecture-context.md](architecture-context.md). |
| In progress | Use provisional 10:00 Europe/London previous-day cutoff; confirm against actual client workflow | This is an analysis assumption, not a verified market gate or buyer deadline. |
| Completed | Define provisional hourly alignment, MAE/bias sign, and missing-pair handling | Documented baseline: average two half-hour actuals; require both; MAE and forecast-minus-actual bias in MW. |
| Completed | Implement Elexon actual and forecast fetch layer | `backend/wind_analysis.py`; direct January run completed. |
| Completed | Implement forecast-vintage selection, interval matching, and accuracy metrics | Provisional cutoff, hourly alignment, MAE/bias; CLI output has 744 matched pairs. |
| Completed | Build the web application layer | FastAPI API and React UI implemented; frontend production build completed successfully. |
| Pending | Add automated checks for cutoff, DST, alignment, missing data, and metrics | No test framework or tests exist yet. |
| Completed | Generate January 2026 analysis output | `data/january_2026_analysis.json`; 100% hourly coverage under the documented pilot assumptions. |
| Completed | Implement FastAPI analysis and health endpoints | `backend/api.py`; January-only validation, configurable cutoff/timezone, in-process result cache, upstream error mapping. |
| Completed | Implement React wind dashboard | `frontend/src/`; date/cutoff filters, metrics, trend chart, interval table, loading/error/partial states. |
| Completed | Add repository README and AI tool disclosure | `README.md` documents directories, local startup, API, deployment status, and Codex use. |
| Completed | Add Docker and Compose configuration | Multi-stage `Dockerfile`, `.dockerignore`, and `docker-compose.yml` build the UI, serve same-origin UI/API, bind `PORT`, and define a health check. Build/run not verified because Docker is unavailable. |
| Pending | Deploy a sample app to Heroku | Provider selected and release steps documented; Docker and authenticated Heroku CLI are unavailable in this environment. |
| In progress | Complete README deployment details | Directory guide, local startup, and AI disclosure are present; add verified URL after deployment. |
| Pending | Publish a public GitHub repository with anonymous/random name | No local Git repository or remote is present at this workspace path; no public repository URL is verified. |
| Pending | Record customer and technical segments within time limits (10 minutes total) | Dashboard implementation and phase 2 analysis exist; live portal/container runtime is not verified. |
| Pending | Verify all submitted URLs in incognito mode | Public repo, deployed app, and unlisted video URLs. |
| Pending | Submit required details through the named challenge form | All required artifacts and URLs. |

## QA and deployment status

- Frontend production build: **Passed** — `cd frontend && npm run build` (TypeScript project build and Vite production bundle).
- Local app run: **Passed** — API started with Uvicorn at `http://localhost:8000`; `/api/health` returned HTTP 200. Vite frontend at `http://localhost:5173` returned HTTP 200. The analysis API returned 744/744 matched hours, 100% coverage, MAE 2,122.81 MW, and mean bias +1,840.30 MW.
- Automated tests/lint: **Not configured or run** — no test, formatter, or lint setup exists. The January CLI analysis was executed as the phase 2 data job, not as a test suite.
- Phase 1 source checks: **Completed** — official OpenAPI plus direct `FUELHH`/`WINDFOR` requests; 1,488 half-hour actuals and 744/744 hourly forecast/actual pairs under the provisional cutoff.
- Phase 2 data pipeline: **Implemented and run** — `python3 -m backend.cli --output data/january_2026_analysis.json`; output contains 744 matched points, 100% coverage, MAE 2,122.81 MW, bias +1,840.30 MW.
- Docker configuration: **Present** (`Dockerfile`, `.dockerignore`, `docker-compose.yml`); image build/runtime **Not verified**, Docker executable unavailable.
- Deployment: **No Heroku app created or URL available**; Heroku CLI executable unavailable and authentication not established.
- Documentation: **Reviewed** — all six context documents and README are present; internal Markdown file links resolve. README has local run instructions, directory guide, Heroku steps, and AI disclosure; deployed URL is outstanding.
- Git: **No repository metadata at this workspace path** — `git status` reports this directory is not a Git repository; no public repo URL is verified.
- Python dependency reproducibility: **Partial** — direct requirements are pinned; transitive resolution is not locked.
- Video, public repository, incognito URL checks, and form submission: **Not evidenced**.

## Risks and open questions

- The 10:00 Europe/London previous-day cutoff is only a pilot convention; the client may use another decision time.
- WINDFOR is hourly in the January 2026 response while FUELHH is half-hourly; the client should accept the hourly alignment approach.
- Elexon generation-by-fuel type reporting excludes embedded generation and wind farms without operational meters, so the dataset does not represent every GB wind generator.
- Wind generation alone is insufficient to calculate the complete additional electricity procurement requirement.
- The exploratory MAE/bias values depend on these provisional evaluation rules and must be recomputed by the eventual application.
- The 16-hour time limit is a challenge constraint; scope should prioritize the core forecast-vintage and accuracy workflow.

## Next actions

1. Build and launch `docker compose up --build` in an environment with Docker installed.
2. Authenticate the Heroku CLI, create the container app, push/release the `web` image, and record its verified URL in the README.
3. Confirm the provisional cutoff and hourly alignment with the intended buyer workflow before presenting analysis as operational guidance.
4. Lock the full Python dependency tree before relying on repeatable production image builds.
5. Initialize or attach the intended Git repository, then publish the requested anonymous public repository.
6. Record the customer/technical demo and complete URL access checks and submission form.

Acceptance criteria are summarized in [project-overview.md](project-overview.md); technical unknowns are in [architecture-context.md](architecture-context.md).

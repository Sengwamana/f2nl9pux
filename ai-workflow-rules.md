# AI Workflow Rules

Use these rules for Codex and other AI coding assistants working on this repository. They complement, and do not replace, human review.

## Before changing code

1. Read [project-overview.md](project-overview.md), [architecture-context.md](architecture-context.md), [code-standards.md](code-standards.md), and [ui-context.md](ui-context.md), plus the relevant section of [progress-tracker.md](progress-tracker.md).
2. Inspect the current files, configuration, dependency manifests, tests, and Git state. Confirm whether requested behavior already exists.
3. Restate the relevant acceptance criteria and identify any missing information. Make a reasonable, low-risk assumption when possible and document it; ask only when an ambiguity blocks a correct implementation.

## Research and implementation

- Use focused changes that preserve the selected React/Python architecture and existing conventions. Do not rewrite unrelated parts of the application.
- Verify Elexon endpoint schemas, query parameters, units, timezone behavior, and historical availability using official documentation or observed responses. The supplied brief names `FUELHH`, `WINDFOR`, `fuelType`, `startTime`, `publishTime`, and `generation`; it does not settle all schema or operational details.
- Do not invent market cutoffs, data fields, procurement rules, datasets, UI requirements, completed features, or analysis results. Separate confirmed requirements, proposed choices, assumptions, and unknowns.
- Preserve delivery interval and forecast publication time. Make the forecast-vintage eligibility rule explicit and prevent future publications from leaking into an as-of evaluation.
- Keep secrets, credentials, tokens, and sensitive environment values out of outputs, source control, screenshots, logs, and frontend code.
- Review generated code for correctness, validation, security, maintainability, and unnecessary complexity before considering the task done.

## Bugs and features

- For bugs, reproduce or trace the failure from source and available evidence, identify the affected behavior, then make a narrow correction and cover the relevant edge case.
- For features, trace the flow through the data boundary, backend behavior, frontend state, and user-visible documentation. Implement empty, partial, and failure states as appropriate.
- Do not modify application behavior for a documentation-only request.

## Verification and reporting

- Run the relevant existing tests, build, lint, type checks, or manual checks after code changes, unless the user requests otherwise or a check cannot run. Report the exact checks run and observed outcomes; do not imply success when a check was skipped or failed.
- Do not claim deployment, public access, API integration, repository publication, video creation, or form submission without direct verification.
- Update relevant context docs when behavior, architecture, conventions, or project status changes. Record significant decisions and unresolved issues in the appropriate document.
- In the final report, summarize changed files and behavior, verification evidence, remaining assumptions/risks, and any uncompleted acceptance criteria.

Keep this workflow aligned with the product scope in [project-overview.md](project-overview.md) and technical boundaries in [architecture-context.md](architecture-context.md).

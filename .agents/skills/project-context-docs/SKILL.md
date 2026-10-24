---
name: project-context-docs
description: Create or maintain Gridbricks project knowledge documents from the product brief and verified repository evidence. Use when asked to document project context, architecture, code/UI conventions, AI workflow, or progress.
---

# Project Context Documentation

Create a concise, reliable project knowledge base for this repository. The source request is the user's supplied Gridbricks challenge brief and its companion instructions in the attached `Pasted text.txt` when available. Inspect the current repository before documenting it; do not treat plans as implementation facts.

## Required files

Create or update these exact root filenames unless the repository already has an established project-context documentation directory:

- `project-overview.md`: purpose, business objectives, target users, requirements, scope, constraints, terminology, acceptance criteria, and definition of done.
- `architecture-context.md`: verified architecture, component responsibilities, stack, data flow, processing, models, errors, security, Docker/deployment, decisions, and limitations. Use Mermaid only for actual or explicitly planned architecture.
- `code-standards.md`: repository-specific React/Python practices, structure, naming, API conventions, validation, quality checks, security, dependencies, and docs.
- `ui-context.md`: user workflows, screens, navigation, data displays, states, responsive behavior, visual hierarchy, accessibility, and confirmed design choices. Mark recommendations as such.
- `ai-workflow-rules.md`: read docs and inspect code first; make focused changes; verify API assumptions; protect secrets; report only checks actually run; update affected docs; review generated code; give a practical workflow for feature, bug, test, and reporting tasks.
- `progress-tracker.md`: milestone/task status, dependencies, QA, deployment, docs, risks, deliverables, acceptance criteria, and next steps. Use Markdown checklists/tables and mark status based on evidence.

## Evidence rules

- Separate explicit requirements, confirmed implementation, proposed decisions, assumptions, and unresolved questions.
- The product scope is a React frontend and Python backend for a UK utility's national wind day-ahead decision support, using Elexon BMRS `FUELHH` actuals filtered to `WIND` and `WINDFOR` forecasts, focused on January 2026. Preserve forecast `publishTime` and delivery `startTime`; verify timestamp, unit, and endpoint details from official Elexon documentation or repository evidence.
- Do not state that the repository has code, tests, Docker, deployment, public GitHub repository, YouTube demo, or form submission unless the repository or reliable evidence confirms it. On an empty or partial scaffold, mark implementation status honestly.
- Do not invent exact procurement cutoffs, market rules, API payload fields, architectural components, or UI design. Record missing choices as assumptions or open questions.
- Preserve useful existing documentation, avoid duplication, use relative links between the six documents, and keep each document specific to this project.

## Review before completion

Check that all six files exist, required topics are covered, links resolve, statements are consistent with one another and repository evidence, and current versus planned work is clear. Do not modify application code to complete a documentation request. Report missing evidence, assumptions, and discovered repository inconsistencies plainly.

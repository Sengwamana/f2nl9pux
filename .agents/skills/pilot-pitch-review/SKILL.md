---
name: pilot-pitch-review
description: Prepare the Gridbricks pilot walkthrough, customer pitch, or internal technical handoff from verified app behavior and repository evidence. Use for demo scripts, video outlines, architecture walkthroughs, and submission readiness.
---

# Pilot Pitch and Technical Handoff

Help present the Gridbricks UK wind day-ahead procurement pilot to two audiences: the utility procurement team and an internal technical lead. Anchor every claim in the running app, source code, measured analysis, or documented requirements.

## Deliverable shape from the brief

- A single unlisted YouTube video, maximum 10 minutes total.
- Part 1: customer-facing portal and analysis pitch, with an initial overview no longer than 5 minutes.
- Part 2: technical review and knowledge transfer covering architecture, design, analysis, codebase, and engineering practices, with an initial overview no longer than 5 minutes.
- A public GitHub repository with an anonymous/random repository name, plus a README covering the repository files/directories, how to start the app, and the Vercel or Heroku app link.
- Submission through the named challenge form. URLs submitted in the form must be opened in incognito mode to verify access.

## Prepare from evidence

- Inspect the current implementation, README, project context docs, analysis outputs, and deployment status before drafting a demo. Clearly separate delivered behavior from roadmap or mock data.
- For the customer segment, lead with the buyer's operational question: what wind generation forecast was available for each delivery interval at decision time, and how did that forecast compare with actual generation? Show the key workflow, relevant evidence, and decision value without claiming the application calculates a complete procurement position.
- Explain forecast vintage (`publishTime`), delivery interval (`startTime`), actuals, coverage, and error measures in plain language. State the evaluation period and limitations. Do not present retrospective accuracy as certainty about future wind generation.
- For the technical segment, trace the real data path from Elexon BMRS actuals (`FUELHH`, `WIND`) and forecasts (`WINDFOR`) through backend processing/API to the React interface. Explain only components that exist or explicitly label planned components.
- Use a timed outline that allocates time to both segments and leaves room for transitions; ensure neither segment exceeds five minutes and total runtime stays under ten minutes.
- Include a concise technical review map: repository directories, key files, processing rules, error handling, tests/checks actually run, Docker usage, deployment, and known limitations.
- Do not claim a public repo, deployed app, unlisted video, incognito access verification, or form submission has happened unless verified. Do not submit the form or publish/ upload material on the user's behalf without an explicit request to perform that external action.

If a required artifact is missing, prepare a truthful outline or checklist and identify the exact prerequisite rather than fabricating demo details.

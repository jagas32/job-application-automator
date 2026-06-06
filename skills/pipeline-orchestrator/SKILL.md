---
name: pipeline-orchestrator
description: Run the full job-application pipeline end to end — job-analyzer → resume-tailorer → cover-letter-writer → linkedin-message. Use when Jason provides a job description and wants all deliverables.
---

# Pipeline Orchestrator

## Input
- A job description in `inputs/` (ask Jason which one if multiple are new)
- Base resume in `inputs/` (stop and ask if missing)

## Pipeline
Run stages in order; each consumes the previous stage's JSON. Load only the SKILL.md for the current stage (token efficiency).

| # | Stage | Skill | Output |
|---|-------|-------|--------|
| 1 | Analyze | skills/job-analyzer | job-analysis.json |
| 2 | Tailor | skills/resume-tailorer | resume.md, resume-changes.json |
| 3 | Letter | skills/cover-letter-writer | cover-letter.md |
| 4 | Outreach | skills/linkedin-message | linkedin-messages.md |

All outputs go to `outputs/<company>-<role>/` (kebab-case, e.g., `outputs/acme-senior-pm/`).

## Orchestration Rules
1. Create the output folder before stage 1.
2. **Checkpoint after stage 1**: if `flags` in job-analysis.json is non-empty (e.g., unmet hard requirements), surface them to Jason before continuing.
3. Validate each stage's JSON output exists and parses before starting the next stage; on failure, retry the stage once, then stop and report.
4. **Voice check (final step)**: read all three deliverables together; fix any tone inconsistencies so resume, letter, and messages sound like one person.
5. Finish with a summary: files produced, keywords incorporated/unmatched, and any `notes_for_jason`.

## Partial Runs
- "Just the resume" → stages 1–2.
- "Redo the cover letter" → reuse existing job-analysis.json + resume.md, run stage 3 only.

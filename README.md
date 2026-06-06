# Job Application Automator

An agentic pipeline that turns a job description + base resume into a complete, ATS-optimized application package — tailored resume, cover letter, and LinkedIn outreach — in one run.

```
job description ──┐
                  ├─► job-analyzer ─► resume-tailorer ─► cover-letter-writer ─► linkedin-message
base resume ──────┘        │                │                    │                     │
                   job-analysis.json    resume.md          cover-letter.md    linkedin-messages.md
```

## Key Features

- **Four-stage skill pipeline** — each stage is a standalone `SKILL.md` with a defined JSON contract; the orchestrator chains them and validates output between stages.
- **ATS keyword optimization** — keywords extracted verbatim from the posting, woven into the resume only where truthful, with unmatched keywords reported instead of fabricated.
- **Anti-fabrication by design** — every skill enforces a hard rule: no invented experience, titles, dates, or metrics. Gaps are flagged to the user, never papered over.
- **One brand voice** — a final voice-check pass ensures resume, letter, and messages read like the same person: confident, specific, achievement-driven, zero clichés.
- **Built-in QA** — JSON schema validation, cover letter word-count bounds (250–350), LinkedIn character limits (600/300) verified programmatically every run.
- **Token-efficient orchestration** — compact intermediate JSON, file references instead of re-pasted content, only one skill loaded per stage.

## How to Run

> **Note:** Base resume kept private for security. Examples use anonymized sample data.

### Option 1 — Cowork (full AI pipeline)

1. Drop a job description and your base resume into `inputs/`.
2. Ask Claude: *"Run the full pipeline on `inputs/<job-file>.md` using the orchestrator."*
3. Collect deliverables from `outputs/<company>-<role>/`.

Partial runs work too: *"just the resume"* (stages 1–2) or *"redo the cover letter"* (stage 3 only).

### Option 2 — CLI runner

```bash
# Scaffold + validate (no API key needed)
python3 scripts/run_pipeline.py inputs/sample_job_description.md --dry-run

# Full run via Claude API (requires ANTHROPIC_API_KEY)
python3 scripts/run_pipeline.py inputs/sample_job_description.md

# Single stage, custom resume
python3 scripts/run_pipeline.py inputs/job.md --resume inputs/your_resume.md --stage analyze

# Re-validate an existing output folder
python3 scripts/run_pipeline.py inputs/sample_job_description.md --stage validate
```

| Stage | Skill | Output |
|-------|-------|--------|
| 1. analyze | `skills/job-analyzer` | `job-analysis.json` |
| 2. tailor | `skills/resume-tailorer` | `resume.md`, `resume-changes.json` |
| 3. letter | `skills/cover-letter-writer` | `cover-letter.md` |
| 4. linkedin | `skills/linkedin-message` | `linkedin-messages.md` |

## Example Output (validated run)

Main example: a fictional sample posting — *AI Automation Specialist, BrightOps Solutions (remote, $18–25/hr)*, in `inputs/sample_job_description.md` — run end to end into `outputs/brightops-ai-automation-specialist/`:

- 8 files generated across the 4 stages, all JSON valid
- 16 of 19 ATS keywords incorporated verbatim; 2 unmatched keywords reported (not fabricated)
- Cover letter: 264 words, mission-specific hook, ends with the project link the posting requests
- 4 LinkedIn texts (recruiter + hiring manager, full message + connection note), all under platform limits

## Tech Stack

| Layer | Tools |
|-------|-------|
| AI orchestration | Claude Cowork, Agent Skills, pipeline orchestrator pattern |
| Data contracts | Structured JSON between stages |
| CLI runner | Python 3 (stdlib argparse; optional `anthropic` SDK for API mode) |
| Inputs | Markdown / txt / docx job descriptions and resumes |
| QA | Programmatic JSON validation, word/char limit checks |

## Portfolio Value

This project demonstrates core agentic-workflow patterns: skills as composable units with explicit JSON contracts, an orchestrator with checkpoints and retry rules, human-in-the-loop flag surfacing (unmet requirements stop the line, not the truth), and hybrid execution — the same skill files drive both a conversational Cowork run and a headless API run from the CLI. It's the third project in a series (Auto-Marketing Pipeline, Data Report Automator, Smart File Organizer) applying one architecture to a new domain.

---

*Built by Jason Gasso — [github.com/jagas32](https://github.com/jagas32)*

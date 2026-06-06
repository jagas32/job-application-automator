# Job Application Automator

**Status: COMPLETE (2026-06-06)** — pipeline built, validated end-to-end on a sample posting.

## Overview & Goal
Input: a job description + Jason's resume. Output: a tailored resume, cover letter, and LinkedIn outreach message — consistent in voice, optimized for the specific role and ATS keywords.

## Folder Structure
```
inputs/      Job descriptions and base resume (md/txt/pdf)
outputs/     Generated deliverables, one subfolder per application: outputs/<company>-<role>/
skills/      Pipeline skills (each has a SKILL.md)
examples/    Reference examples of good outputs
scripts/     Helper scripts (parsing, file conversion)
docs/        Project documentation
```

## Key Conventions
- **Structured JSON**: skills pass data between stages as JSON (see each SKILL.md for its schema). Job analysis output is the contract consumed by all downstream skills.
- **Brand voice consistency**: one professional voice across resume, cover letter, and LinkedIn message — confident, specific, achievement-driven. No clichés ("passionate", "team player"), no fabricated experience.
- **Token efficiency**: keep intermediate JSON compact; reference files by path instead of re-pasting content; only load the skill needed for the current stage.

## How to Run the Pipeline
1. Drop the job description into `inputs/` (and base resume if not already there).
2. Invoke `skills/pipeline-orchestrator/SKILL.md` — it runs the stages in order:
   job-analyzer → resume-tailorer → cover-letter-writer → linkedin-message
3. Find deliverables in `outputs/<company>-<role>/`.

Individual stages can be run standalone by following the relevant SKILL.md.

### CLI Runner (alternative)
```bash
python3 scripts/run_pipeline.py inputs/<job>.md                  # full run (needs ANTHROPIC_API_KEY)
python3 scripts/run_pipeline.py inputs/<job>.md --dry-run        # plan only, no API calls
python3 scripts/run_pipeline.py inputs/<job>.md --stage validate # QA an existing output folder
python3 scripts/run_pipeline.py inputs/<job>.md --stage tailor --resume inputs/my_base_resume.md
```
The runner derives the `outputs/<company>-<role>/` slug from the posting, surfaces analysis flags after stage 1, and finishes with programmatic validation (JSON validity, 250–350 word letter, 600/300 char LinkedIn limits).

## Project Status

- 5 skills complete: job-analyzer, resume-tailorer, cover-letter-writer, linkedin-message, pipeline-orchestrator
- Base resume in `inputs/my_base_resume.md`; sample posting in `inputs/sample_job_description.md`
- Validated run: `outputs/brightops-ai-automation-specialist/` — 8 files, all QA checks passing (16/19 ATS keywords incorporated, 2 unmatched reported honestly)
- CLI runner tested in dry-run and validate modes
- Next ideas: docx export of tailored resume, application tracker (xlsx), interview-prep skill

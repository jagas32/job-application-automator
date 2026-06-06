---
name: linkedin-message
description: Write short LinkedIn outreach messages (recruiter + hiring manager variants) from job-analysis.json and the tailored resume. Fourth stage of the application pipeline.
---

# LinkedIn Message

## Input
- `outputs/<company>-<role>/job-analysis.json`
- `outputs/<company>-<role>/resume.md`

## Process
1. Identify Jason's single strongest hook for this role (top skill match or standout achievement).
2. Draft two variants:
   - **Recruiter**: name the exact role, one-line credential, ask about process/next steps.
   - **Hiring manager**: one specific point of interest in their team/product (from `company_signals`), one relevant achievement, soft ask for a conversation.
3. Draft a connection-request note (≤300 chars) for each variant.

## Output
`outputs/<company>-<role>/linkedin-messages.md` containing all four texts, clearly labeled.

```json
{
  "hook_used": "",
  "recruiter_chars": 0,
  "hiring_manager_chars": 0
}
```
(append as `linkedin-meta.json`)

## Rules
- Full messages ≤600 characters; connection notes ≤300 characters (LinkedIn limit).
- First sentence must be specific to the company/role — no generic openers ("I came across your profile…").
- No desperation, no flattery, exactly one ask per message.
- Brand voice consistent with resume and cover letter.

---
name: job-analyzer
description: Parse a job description into structured JSON — role facts, required/preferred skills, ATS keywords, company signals. First stage of the application pipeline; its output is consumed by all downstream skills.
---

# Job Analyzer

## Input
A job description file from `inputs/` (md, txt, or pdf — extract text first if pdf).

## Process
1. Extract role facts: title, company, location, seniority, comp if listed.
2. Classify requirements as **required** vs **preferred** (use the posting's own wording; infer from emphasis if unlabeled).
3. Pull ATS keywords: exact phrases for hard skills, tools, certifications. Keep the posting's spelling/casing.
4. Capture company signals: mission, values, tone of the posting, recent context if stated.
5. Note red flags or gaps worth flagging to Jason (e.g., requirements he may not meet).

## Output Schema
Write to `outputs/<company>-<role>/job-analysis.json`:

```json
{
  "company": "",
  "role": "",
  "location": "",
  "seniority": "",
  "required_skills": [""],
  "preferred_skills": [""],
  "ats_keywords": [""],
  "responsibilities": [""],
  "company_signals": { "mission": "", "values": [""], "tone": "" },
  "flags": [""]
}
```

## Rules
- Keep JSON compact — no prose fields longer than one sentence (token efficiency).
- Never invent details not in the posting.
- `ats_keywords` should be deduplicated and verbatim from the posting.

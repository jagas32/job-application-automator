---
name: cover-letter-writer
description: Write a tailored cover letter from job-analysis.json and the tailored resume. Third stage of the application pipeline.
---

# Cover Letter Writer

## Input
- `outputs/<company>-<role>/job-analysis.json`
- `outputs/<company>-<role>/resume.md`

## Process
1. Pick the 2–3 strongest matches between Jason's experience and `required_skills`/`responsibilities` — these are the letter's spine.
2. Hook (1st paragraph): why this role at this company, referencing one specific `company_signals` item. No "I am writing to apply…".
3. Body (1–2 paragraphs): one concrete achievement per key match, with metrics from the resume. Show, don't claim.
4. Close: brief, confident call to action.
5. Match the posting's tone (from `company_signals.tone`) while keeping the brand voice.

## Output
- `outputs/<company>-<role>/cover-letter.md`
- Append to `outputs/<company>-<role>/cover-letter-meta.json`:

```json
{
  "matches_highlighted": [""],
  "company_signal_used": "",
  "word_count": 0
}
```

## Rules
- 250–350 words, 3–4 paragraphs max.
- Only claim what the resume supports — no fabrication.
- Brand voice: confident, specific, warm; zero clichés ("passionate", "dream job", "perfect fit").
- Address a named hiring manager if the posting includes one; otherwise "Dear <Team> Hiring Team".

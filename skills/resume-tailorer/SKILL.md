---
name: resume-tailorer
description: Tailor the base resume to a specific job using job-analysis.json. Reorders, rewrites, and keyword-optimizes without fabricating. Second stage of the application pipeline.
---

# Resume Tailorer

## Input
- `outputs/<company>-<role>/job-analysis.json` (from job-analyzer)
- Base resume from `inputs/`

## Process
1. Map each required skill in the analysis to evidence in the base resume. Note unmatched requirements.
2. Rewrite the summary/headline to mirror the role title and top 3 required skills.
3. Reorder and rewrite bullets: lead with experience most relevant to `responsibilities`; weave in `ats_keywords` verbatim where truthful.
4. Quantify achievements wherever the base resume supports it (metrics, scale, impact).
5. Cut or compress low-relevance content to keep length at 1–2 pages.

## Output
- `outputs/<company>-<role>/resume.md` — the tailored resume
- `outputs/<company>-<role>/resume-changes.json`:

```json
{
  "keywords_incorporated": [""],
  "keywords_unmatched": [""],
  "sections_reordered": [""],
  "bullets_rewritten": 0,
  "notes_for_jason": [""]
}
```

## Rules
- **Never fabricate** experience, titles, dates, or metrics. Unmatched keywords go in `keywords_unmatched`, not into the resume.
- Brand voice: confident, specific, achievement-driven; active verbs; no clichés.
- ATS-safe formatting: standard section headings, no tables/graphics.

#!/usr/bin/env python3
"""Job Application Automator — CLI pipeline runner.

Runs the 4-stage pipeline (analyze -> tailor -> letter -> linkedin) on a job
description + base resume.

Modes:
  - API mode (ANTHROPIC_API_KEY set): each stage loads its SKILL.md as
    instructions and calls Claude to generate the deliverable.
  - Dry-run / validate mode (no key needed): scaffolds the output folder and/or
    QA-checks existing outputs (JSON validity, word counts, char limits).

Usage:
  python3 scripts/run_pipeline.py inputs/job.md
  python3 scripts/run_pipeline.py inputs/job.md --resume inputs/my_base_resume.md
  python3 scripts/run_pipeline.py inputs/job.md --stage analyze
  python3 scripts/run_pipeline.py inputs/job.md --dry-run
  python3 scripts/run_pipeline.py inputs/job.md --stage validate
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MODEL_DEFAULT = "claude-sonnet-4-6"

STAGES = [
    # (name, skill dir, primary output, extra outputs)
    ("analyze", "job-analyzer", "job-analysis.json", []),
    ("tailor", "resume-tailorer", "resume.md", ["resume-changes.json"]),
    ("letter", "cover-letter-writer", "cover-letter.md", ["cover-letter-meta.json"]),
    ("linkedin", "linkedin-message", "linkedin-messages.md", ["linkedin-meta.json"]),
]
STAGE_NAMES = [s[0] for s in STAGES] + ["all", "validate"]


def slugify(text: str) -> str:
    return re.sub(r"-+", "-", re.sub(r"[^a-z0-9]+", "-", text.lower())).strip("-")


def guess_slug(job_text: str, job_path: Path) -> str:
    """Best-effort <company>-<role> slug from the posting; fall back to filename."""
    company = role = None
    m = re.search(r"^\*\*Company:\*\*\s*(.+)$", job_text, re.M)
    if m:
        company = m.group(1).strip()
    m = re.search(r"^#\s+(.+)$", job_text, re.M)
    if m:
        role = re.sub(r"\(.*?\)", "", m.group(1)).strip()
    if company and role:
        # drop corporate suffixes for a tighter slug
        company = re.sub(r"\b(inc|llc|ltd|corp|solutions|technologies)\b\.?", "", company, flags=re.I)
        return slugify(f"{company} {role}")
    return slugify(job_path.stem)


def read_skill(skill_dir: str) -> str:
    p = ROOT / "skills" / skill_dir / "SKILL.md"
    if not p.exists():
        sys.exit(f"ERROR: missing skill file {p}")
    return p.read_text(encoding="utf-8")


def call_claude(model: str, system: str, prompt: str) -> str:
    try:
        import anthropic
    except ImportError:
        sys.exit("ERROR: API mode needs the SDK: pip install anthropic")
    client = anthropic.Anthropic()
    resp = client.messages.create(
        model=model,
        max_tokens=4096,
        system=system,
        messages=[{"role": "user", "content": prompt}],
    )
    return "".join(b.text for b in resp.content if b.type == "text")


def extract_block(text: str, kind: str) -> str:
    """Pull a fenced ```kind block; fall back to the whole response."""
    m = re.search(rf"```{kind}\n(.*?)```", text, re.S)
    return m.group(1).strip() if m else text.strip()


def run_stage(name: str, out_dir: Path, job_text: str, resume_text: str, model: str) -> None:
    _, skill_dir, primary, extras = next(s for s in STAGES if s[0] == name)
    skill = read_skill(skill_dir)
    analysis = (out_dir / "job-analysis.json")
    context = [f"JOB DESCRIPTION:\n{job_text}"]
    if name != "analyze" and analysis.exists():
        context.append(f"JOB ANALYSIS JSON:\n{analysis.read_text(encoding='utf-8')}")
    if name == "tailor":
        context.append(f"BASE RESUME:\n{resume_text}")
    if name in ("letter", "linkedin"):
        tailored = out_dir / "resume.md"
        context.append(f"TAILORED RESUME:\n{tailored.read_text(encoding='utf-8')}"
                       if tailored.exists() else f"BASE RESUME:\n{resume_text}")

    files = ", ".join([primary] + extras)
    prompt = (
        "\n\n---\n\n".join(context)
        + f"\n\n---\n\nFollow the skill instructions exactly. Produce: {files}. "
          "Return each file in its own fenced code block, preceded by a line "
          "'FILE: <name>'. JSON files must be valid JSON. Never fabricate "
          "experience, titles, dates, or metrics."
    )
    print(f"  -> calling Claude ({name})...")
    text = call_claude(model, skill, prompt)

    # split response into named file blocks
    blocks = re.findall(r"FILE:\s*(\S+)\s*\n```[a-z]*\n(.*?)```", text, re.S)
    written = set()
    for fname, body in blocks:
        if fname in [primary] + extras:
            (out_dir / fname).write_text(body.strip() + "\n", encoding="utf-8")
            written.add(fname)
    if primary not in written:  # fallback: whole response is the primary file
        kind = "json" if primary.endswith(".json") else "markdown"
        (out_dir / primary).write_text(extract_block(text, kind) + "\n", encoding="utf-8")
        written.add(primary)
    print(f"     wrote: {', '.join(sorted(written))}")


def validate(out_dir: Path) -> bool:
    ok = True

    def check(cond: bool, label: str) -> None:
        nonlocal ok
        print(f"  [{'PASS' if cond else 'FAIL'}] {label}")
        ok = ok and cond

    for j in sorted(out_dir.glob("*.json")):
        try:
            json.loads(j.read_text(encoding="utf-8"))
            check(True, f"{j.name} is valid JSON")
        except json.JSONDecodeError as e:
            check(False, f"{j.name} invalid JSON: {e}")

    letter = out_dir / "cover-letter.md"
    if letter.exists():
        words = len(letter.read_text(encoding="utf-8").split())
        check(150 <= words <= 400, f"cover letter {words} words (target 250-350)")

    li = out_dir / "linkedin-messages.md"
    if li.exists():
        text = li.read_text(encoding="utf-8")
        for block in re.split(r"^## ", text, flags=re.M)[1:]:
            title = block.splitlines()[0].strip()
            body = re.search(r"\n\n(.+?)\n\n\*\(", block, re.S)
            if not body:
                continue
            n = len(body.group(1).strip())
            limit = 300 if "Connection" in title else 600
            check(n <= limit, f"linkedin '{title[:40]}' {n}/{limit} chars")

    required = [s[2] for s in STAGES]
    missing = [f for f in required if not (out_dir / f).exists()]
    check(not missing, f"all stage outputs present"
          + (f" (missing: {', '.join(missing)})" if missing else ""))
    return ok


def main() -> None:
    ap = argparse.ArgumentParser(description="Run the job application pipeline.")
    ap.add_argument("job", help="job description file (md/txt)")
    ap.add_argument("--resume", default="inputs/my_base_resume.md")
    ap.add_argument("--stage", choices=STAGE_NAMES, default="all")
    ap.add_argument("--outputs", default=None, help="override output folder")
    ap.add_argument("--model", default=MODEL_DEFAULT)
    ap.add_argument("--dry-run", action="store_true",
                    help="scaffold + plan only, no API calls")
    args = ap.parse_args()

    job_path = Path(args.job)
    if not job_path.is_absolute():
        job_path = ROOT / job_path
    if not job_path.exists():
        sys.exit(f"ERROR: job description not found: {job_path}")
    job_text = job_path.read_text(encoding="utf-8")

    resume_path = Path(args.resume)
    if not resume_path.is_absolute():
        resume_path = ROOT / resume_path
    if not resume_path.exists():
        sys.exit(f"ERROR: base resume not found: {resume_path}")
    resume_text = resume_path.read_text(encoding="utf-8")

    slug = guess_slug(job_text, job_path)
    out_dir = Path(args.outputs) if args.outputs else ROOT / "outputs" / slug
    out_dir.mkdir(parents=True, exist_ok=True)
    print(f"Output folder: {out_dir.relative_to(ROOT) if out_dir.is_relative_to(ROOT) else out_dir}")

    if args.stage == "validate":
        sys.exit(0 if validate(out_dir) else 1)

    stages = [s[0] for s in STAGES] if args.stage == "all" else [args.stage]
    if args.dry_run:
        print("Dry run — plan:")
        for name in stages:
            _, skill_dir, primary, extras = next(s for s in STAGES if s[0] == name)
            print(f"  {name}: skills/{skill_dir} -> {', '.join([primary] + extras)}")
        print("No API calls made. Set ANTHROPIC_API_KEY and rerun without --dry-run.")
        return

    if not os.environ.get("ANTHROPIC_API_KEY"):
        sys.exit("ERROR: ANTHROPIC_API_KEY not set. Use --dry-run, or run the "
                 "pipeline conversationally in Cowork instead.")

    for name in stages:
        print(f"Stage: {name}")
        run_stage(name, out_dir, job_text, resume_text, args.model)
        if name == "analyze":
            flags = json.loads((out_dir / "job-analysis.json").read_text(encoding="utf-8")).get("flags", [])
            if flags:
                print("  Flags from analysis (review before applying):")
                for f in flags:
                    print(f"   - {f}")

    print("\nValidation:")
    sys.exit(0 if validate(out_dir) else 1)


if __name__ == "__main__":
    main()

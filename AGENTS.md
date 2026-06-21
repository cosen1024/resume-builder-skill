# Repository instructions

## Scope

The distributable product is `resume_skill/`.

- `reference/` and `template/` are local research material. Do not copy their content into the
  published skill unless provenance and licensing have been checked.
- `HANDOFF.md` records implementation context. User-facing instructions belong in `README.md`
  and `resume_skill/SKILL.md`.

## Runtime

On this Mac, all rendering and Python verification commands must use:

```bash
/opt/homebrew/bin/python3.13
```

Do not use Anaconda Python for WeasyPrint and do not replace WeasyPrint with Chrome headless PDF.

## Change workflow

1. Read `resume_skill/SKILL.md` and the relevant file under `resume_skill/references/`.
2. Add or update a regression test in `resume_skill/evals/test_resume_skill.py` for behavior changes.
3. Keep the Markdown data format backwards compatible unless the change is explicitly documented.
4. Render all five templates after layout changes.
5. Keep generated HTML/PDF files under `/tmp` or `output/`; do not add them to the repository.

## Required verification

```bash
/opt/homebrew/bin/python3.13 -m unittest resume_skill/evals/test_resume_skill.py -v
/opt/homebrew/bin/python3.13 \
  /Users/cosen/.codex/skills/.system/skill-creator/scripts/quick_validate.py \
  resume_skill
```

For template changes, additionally render `resume_skill/assets/resume.example.md` with
`compact`, `classic`, `modern`, `timeline`, and `minimal`, then inspect the PDFs visually.

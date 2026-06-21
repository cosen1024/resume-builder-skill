# Repository instructions

## Scope

The distributable product is `resume_skill/`. Keep user-facing installation and usage guidance in
`README.md`, `README.en.md`, and `resume_skill/SKILL.md`.

## Runtime

Use a Python 3 interpreter with the packages from `requirements.txt` installed. In commands below,
`${PYTHON_BIN:-python3}` represents that interpreter.

## Change workflow

1. Read `resume_skill/SKILL.md` and the relevant reference file.
2. Add or update a regression test for behavior changes.
3. Keep the Markdown data format backward compatible unless explicitly documented.
4. Render all five templates after layout changes.
5. Keep generated HTML and PDF files out of version control.

## Required verification

```bash
${PYTHON_BIN:-python3} -m unittest resume_skill/evals/test_resume_skill.py -v
${PYTHON_BIN:-python3} \
  "${CODEX_HOME:-$HOME/.codex}/skills/.system/skill-creator/scripts/quick_validate.py" \
  resume_skill
```

For template changes, render `compact`, `classic`, `modern`, `timeline`, and `minimal`, then inspect
the resulting PDFs visually.

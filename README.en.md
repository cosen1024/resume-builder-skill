# resume-builder

English | [简体中文](README.md)

`resume-builder` is a Chinese resume-generation Skill for Codex and Claude Code. It keeps resume
content in an editable `resume.md`, then uses Jinja templates, offline CSS, and WeasyPrint to
produce searchable A4 PDFs.

## Preview

The bundled fictional example uses the `compact` template with the `teal` accent and an optional
photo. All names, schools, companies, contact details, projects, and metrics are demonstration data.

![Compact resume example with photo](docs/images/resume-compact-photo.png)

Source: [`resume_skill/assets/resume.example.md`](resume_skill/assets/resume.example.md)

```bash
/opt/homebrew/bin/python3.13 \
  resume_skill/scripts/render.py \
  resume_skill/assets/resume.example.md \
  --template compact \
  --accent teal \
  --out output/kusen-compact-photo.pdf
```

## Features

- One Markdown content source with five interchangeable layouts.
- Offline rendering without Typora, browser printing, CDNs, or remote fonts.
- Chinese campus and experienced-hire writing guidance using STAR/XYZ and quantified outcomes.
- CSV and xlsx import using a simple three-column schema.
- Optional photo, preset accents, and custom `#rrggbb` colors.
- JD-oriented rewriting and keyword-gap analysis without inventing experience or metrics.
- ATS-oriented `classic` layout plus `compact`, `modern`, `timeline`, and `minimal` visual options.
- Privacy-first import: identity numbers are excluded from generated metadata by default.

## Templates

| Template | Intended use |
|---|---|
| `compact` | Stable, dense, single-column Chinese technical resumes |
| `classic` | Conservative black-and-white output and ATS parsing |
| `modern` | Colored sidebar for internet and product roles |
| `timeline` | Chronological presentation for experience-heavy candidates |
| `minimal` | Low-density, restrained visual style |

Accents: `blue`, `teal`, `wine`, `ink`, `purple`, `green`, `orange`, or a six-digit hex color.
`classic` intentionally remains black and white.

## Requirements

This repository is verified on macOS Apple Silicon with:

```bash
/opt/homebrew/bin/python3.13
```

Install dependencies:

```bash
/opt/homebrew/bin/python3.13 -m pip install --break-system-packages -r requirements.txt
```

On the maintainer's machine, Anaconda Python conflicts with WeasyPrint's glib/pango libraries.
Chrome headless PDF output is also intentionally unsupported.

## Quick start

Convert the bundled CSV example:

```bash
/opt/homebrew/bin/python3.13 \
  resume_skill/scripts/csv_to_md.py \
  resume_skill/assets/resume.example.csv \
  -o output/resume.md
```

Render it:

```bash
/opt/homebrew/bin/python3.13 \
  resume_skill/scripts/render.py \
  output/resume.md \
  --template compact \
  --accent teal \
  --out output/resume.pdf
```

The accepted Markdown schema is documented in
[`field-schema.md`](resume_skill/references/field-schema.md).

## Install as a Skill

Codex:

```bash
mkdir -p ~/.codex/skills
ln -s "$(pwd)/resume_skill" ~/.codex/skills/resume-builder
```

Claude Code:

```bash
mkdir -p ~/.claude/skills
ln -s "$(pwd)/resume_skill" ~/.claude/skills/resume-builder
```

Example prompt:

```text
Use $resume-builder to create a concise Chinese campus resume for a backend engineering role
from my real experience.
```

## Tests

```bash
/opt/homebrew/bin/python3.13 -m unittest \
  resume_skill/evals/test_resume_skill.py -v

/opt/homebrew/bin/python3.13 \
  ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py \
  resume_skill
```

Template changes must also be visually checked by rendering all five layouts.

## Repository scope

The distributable product is `resume_skill/`. The root `reference/`, `template/`, and `output/`
directories are local research or generated artifacts and are excluded from publication.

See [`RELEASE_REVIEW.md`](RELEASE_REVIEW.md) for the independent review checklist, release
governance notes, and a ready-to-use AI review prompt.

## Release notes

- External resume projects were studied only for general layout principles. Their author data,
  example resumes, icons, and template source are not part of this Skill.
- The demo avatar is an original SVG created for this repository.
- The project and original demo avatar are released under the [MIT License](LICENSE).

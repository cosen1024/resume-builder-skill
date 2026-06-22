# resume-builder

English | [简体中文](README.md)

`resume-builder` is a reusable resume-generation Skill for Codex, Claude Code, and other AI agents
that can read `SKILL.md` and run local scripts. It is optimized for Chinese typography while also
supporting English and bilingual resume content.

It handles both content improvement and deterministic rendering from one Markdown source into
searchable, selectable A4 PDFs.

![High-resolution compact PDF preview with an optional avatar](preview/resume-compact.png)

All names, schools, companies, projects, awards, and figures in the preview are fictional.
The avatar demonstrates optional photo placement; remove the `photo` field for a photo-free version.

## Highlights

- **End-to-end workflow**: collect experience, polish content, select a layout, and export PDF
- **Truth-first writing**: ask for missing context and metrics without inventing claims
- **STAR / XYZ rewriting**: turn duty lists into action- and outcome-oriented bullets
- **JD tailoring**: extract keywords, identify gaps, and adjust wording and section order
- **Multiple hiring scenarios**: campus, experienced, backend, AI, frontend, product, and operations
- **Flexible input**: conversation, Markdown, CSV, and xlsx
- **Five A4 layouts**: `compact`, `classic`, `modern`, `timeline`, and `minimal`
- **Optional photos and colors**: four photo-capable layouts, seven presets, and custom colors
- **Offline and searchable output**: no CDN, remote fonts, or online resume service required
- **Privacy-aware defaults**: sensitive identity fields are excluded from the resume body

## Installation

### Recommended: ask an AI agent to install it

Give the repository and this prompt to a Skill-compatible agent:

```text
Install resume-builder from this repository:
https://github.com/cosen1024/resume-builder-skill.git

Install the complete resume_skill folder and preserve its agents, assets,
references, scripts, and evals directories. Do not copy only SKILL.md.
```

The complete directory structure is required because rendering depends on bundled templates, CSS,
scripts, and writing references.

### Manual Codex installation

```bash
git clone https://github.com/cosen1024/resume-builder-skill.git
cd resume-builder-skill
mkdir -p ~/.codex/skills
cp -R resume_skill ~/.codex/skills/resume-builder
```

### Manual Claude Code installation

```bash
git clone https://github.com/cosen1024/resume-builder-skill.git
cd resume-builder-skill
mkdir -p ~/.claude/skills
cp -R resume_skill ~/.claude/skills/resume-builder
```

### Other AI agents

Copy the complete `resume_skill/` folder into the agent's Skill directory. If the agent has no
standard Skill directory, point it to `resume_skill/SKILL.md` and allow it to run the local commands
under `scripts/`. Keep `assets/` and `references/` intact.

## Python dependencies

PDF rendering uses WeasyPrint:

```bash
python3 -m pip install -r requirements.txt
```

Here, `python3` means the interpreter where these dependencies are installed. Replace it with the
appropriate interpreter for your virtual environment or operating system.

## Usage

After installation, describe the task naturally. No special prefix or symbol is required:

```text
Use resume-builder to create a concise campus resume for a backend engineering role from my real experience.
```

```text
Use resume-builder to polish this English resume without inventing experience or metrics.
```

```text
Use resume-builder to tailor my resume to this job description and list matched and missing keywords.
```

```text
Use resume-builder to render this resume with both the compact and classic templates.
```

## Templates

| Template | Style | Recommended use | Photo |
|---|---|---|---|
| `compact` | Dense, stable single column | Technical roles and content-heavy resumes | Yes |
| `classic` | Black-and-white, ATS oriented | Broad applications and conservative industries | Yes |
| `modern` | Colored sidebar | Internet, product, and operations roles | Yes |
| `timeline` | Chronological rail | Candidates with many internships or projects | No |
| `minimal` | Restrained whitespace | Short, carefully edited resumes | Yes |

Available accents:

```text
blue / teal / wine / ink / purple / green / orange / #rrggbb
```

`classic` always remains black and white.

## Quick installation check

Use this command only to verify that dependencies, templates, and PDF rendering work:

```bash
python3 resume_skill/scripts/render.py \
  resume_skill/assets/resume.example.md \
  --template compact \
  --accent teal \
  --out resume.pdf
```

For real use, ask the agent to create or update `resume.md` from your own material, then render it
with the same script.

## Skill structure

```text
resume_skill/
├── SKILL.md                         # Agent workflow and invocation rules
├── agents/
│   └── openai.yaml                  # OpenAI/Codex UI metadata
├── scripts/
│   ├── csv_to_md.py                 # CSV/xlsx to Markdown
│   └── render.py                    # Markdown to HTML/PDF
├── references/
│   ├── field-schema.md              # Data format and field mapping
│   ├── role-presets.md              # Role-specific content priorities
│   ├── templates-guide.md           # Layout, color, and photo selection
│   ├── visual-design-system.md      # Typography and layout rules
│   └── writing-principles.md        # STAR, metrics, and ATS guidance
├── assets/
│   ├── resume.example.csv           # Fictional spreadsheet example
│   ├── resume.example.md            # Fictional Markdown example
│   ├── examples/demo-avatar.png     # Photo-layout example
│   ├── styles/resume-base.css       # Shared print styles
│   └── templates/                   # Five HTML/CSS layouts
│       ├── compact/
│       ├── classic/
│       ├── modern/
│       ├── timeline/
│       └── minimal/
└── evals/
    └── test_resume_skill.py         # Regression tests
```

## Limitations

- Spreadsheet import supports `.csv` and `.xlsx`, but not legacy `.xls`
- Markdown parsing is limited to the headings, entries, and inline syntax documented here
- Current output formats are HTML and PDF; DOCX export and a web editor are not included
- JD matching and rewriting are performed by the invoking agent, not by a standalone scorer

## Tests

```bash
python3 -m unittest resume_skill/evals/test_resume_skill.py -v
```

## License

[PolyForm Noncommercial License 1.0.0](LICENSE)

Personal study, research, education, and other noncommercial uses are permitted. Commercial use
requires separate permission. Because commercial use is restricted, this project is source-available
rather than Open Source Initiative approved open source.

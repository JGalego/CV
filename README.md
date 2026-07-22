# CV

Curriculum Vitae, built from a single structured data source.

![latex](images/latex.jpg)

## How this works

The CV content lives in [`data/resume.json`](data/resume.json), a
[JSON Resume](https://jsonresume.org/schema/)-based schema extended with a
few custom sections (`badges`, `talks`, `meta`). Text fields use a small
markup dialect — `[text](url)`, `**bold**`, `*italic*`, `` `code` `` — defined
in [`scripts/richtext.py`](scripts/richtext.py).

[`scripts/build.py`](scripts/build.py) renders that data through the Jinja2
templates in [`templates/`](templates/) to produce every output format from
one source:

| File | Purpose |
|---|---|
| `cv_en.tex` / `cv_en.pdf` | Human-facing LaTeX/PDF, same visual design as before |
| `cv_en.md` | Markdown, for GitHub rendering or pasting into other tools |
| `llms.txt` | Plain-text version, easy for LLMs/agents/ATS systems to parse |
| `data/resume.json` | The structured source of truth itself — also a valid machine-readable export |

CI ([`.github/workflows/build-cv.yml`](.github/workflows/build-cv.yml))
regenerates and commits all four on every push to `main`.

## Editing the CV

Edit `data/resume.json` (not the generated `.tex`/`.md`/`.txt` files —
those are overwritten by the build). Then run:

```bash
pip install -r scripts/requirements.txt
python3 scripts/build.py
```

This regenerates `cv_en.tex`, `cv_en.md` and `llms.txt`. Compiling
`cv_en.tex` to a PDF requires a LaTeX distribution with `lualatex`
(TeX Live with `roboto`, `fontawesome`, `marvosym`); CI does this
automatically, so a local LaTeX install is only needed to preview the PDF
before pushing:

```bash
latexmk -lualatex cv_en.tex
```

## Editing templates

Changing the visual design or output layout means editing the templates in
[`templates/`](templates/), not `data/resume.json`:

- `resume.tex.j2` — LaTeX template (uses `\VAR{ }` / `\BLOCK{ }` Jinja
  delimiters so they don't clash with LaTeX's own `{ }` braces)
- `resume.md.j2` — Markdown template
- `resume.txt.j2` — plain-text/`llms.txt` template

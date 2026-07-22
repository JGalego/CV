#!/usr/bin/env python3
"""
Build cv_en.tex, cv_en.md and llms.txt from data/resume.json.

Usage:
    python3 scripts/build.py

The generated cv_en.tex is then compiled to cv_en.pdf by latexmk/lualatex
(done in CI; see .github/workflows/build-cv.yml).
"""

import json
from collections import defaultdict
from pathlib import Path

import jinja2

import richtext

ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = ROOT / "data" / "resume.json"
TEMPLATES_DIR = ROOT / "templates"

OUTPUTS = {
    "resume.tex.j2": ROOT / "cv_en.tex",
    "resume.md.j2": ROOT / "cv_en.md",
    "resume.txt.j2": ROOT / "llms.txt",
}


def load_data():
    with open(DATA_FILE, encoding="utf-8") as f:
        data = json.load(f, object_pairs_hook=dict)

    skills_by_name = defaultdict(list)
    for skill in data.get("skills", []):
        skills_by_name[skill["name"]].append(skill)
    data["skills_by_name"] = skills_by_name

    return data


def tex_filter(text):
    return richtext.latex_ordinal(richtext.to_latex(text))


def make_env(fmt):
    if fmt == "latex":
        env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(str(TEMPLATES_DIR)),
            block_start_string=r"\BLOCK{",
            block_end_string="}",
            variable_start_string=r"\VAR{",
            variable_end_string="}",
            comment_start_string=r"\#{",
            comment_end_string="}",
            trim_blocks=True,
            lstrip_blocks=True,
            autoescape=False,
        )
        env.filters["tex"] = tex_filter
        env.filters["texurl"] = richtext.latex_escape_url
    else:
        env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(str(TEMPLATES_DIR)),
            trim_blocks=True,
            lstrip_blocks=True,
            autoescape=False,
        )
        env.filters["md"] = richtext.to_markdown
        env.filters["txt"] = richtext.to_text
    return env


def build():
    data = load_data()

    for template_name, out_path in OUTPUTS.items():
        fmt = "latex" if template_name.endswith(".tex.j2") else "other"
        env = make_env(fmt)
        template = env.get_template(template_name)
        rendered = template.render(**data)
        out_path.write_text(rendered, encoding="utf-8")
        print(f"wrote {out_path.relative_to(ROOT)} ({len(rendered)} bytes)")


if __name__ == "__main__":
    build()

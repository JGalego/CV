"""
Tiny markup dialect used throughout data/resume.json so that a single piece of
text can be rendered as LaTeX, Markdown or plain text.

Supported inline markup:
    [text](url)   -> hyperlink
    **text**      -> bold
    *text*        -> italic
    `text`        -> monospace / code

Anything else is literal text. Unicode (emoji, subscripts/superscripts such as
H2 written as "H₂") is passed through untouched in every format, which
keeps the source text renderer-agnostic without needing LaTeX math mode.
"""

import re

# Order matters: links first, then bold before italic (** vs *), then code.
_TOKEN_RE = re.compile(
    r"(?P<link>\[(?P<link_text>[^\]]+)\]\((?P<link_url>[^)]+)\))"
    r"|(?P<bold>\*\*(?P<bold_text>.+?)\*\*)"
    r"|(?P<italic>\*(?P<italic_text>.+?)\*)"
    r"|(?P<code>`(?P<code_text>[^`]+)`)"
)

_LATEX_SPECIAL = {
    "&": r"\&",
    "%": r"\%",
    "$": r"\$",
    "#": r"\#",
    "_": r"\_",
    "{": r"\{",
    "}": r"\}",
    "~": r"\textasciitilde{}",
    "^": r"\textasciicircum{}",
    "\\": r"\textbackslash{}",
}
_LATEX_ESCAPE_RE = re.compile("|".join(re.escape(c) for c in _LATEX_SPECIAL))

# Minimal escaping for the {url} argument of \href (must not touch : / . etc.)
_LATEX_URL_SPECIAL = {"%": r"\%", "#": r"\#", "&": r"\&", "_": r"\_"}
_LATEX_URL_ESCAPE_RE = re.compile("|".join(re.escape(c) for c in _LATEX_URL_SPECIAL))


def latex_escape(text):
    return _LATEX_ESCAPE_RE.sub(lambda m: _LATEX_SPECIAL[m.group(0)], text)


def latex_escape_url(url):
    return _LATEX_URL_ESCAPE_RE.sub(lambda m: _LATEX_URL_SPECIAL[m.group(0)], url)


def _render_plain(text, fmt):
    return latex_escape(text) if fmt == "latex" else text


def render(text, fmt):
    """Render a richtext string as 'latex', 'markdown' or 'text'."""
    if text is None:
        return ""

    out = []
    pos = 0
    for m in _TOKEN_RE.finditer(text):
        if m.start() > pos:
            out.append(_render_plain(text[pos:m.start()], fmt))

        if m.group("link"):
            link_text, url = m.group("link_text"), m.group("link_url")
            if fmt == "latex":
                out.append(r"\href{%s}{%s}" % (latex_escape_url(url), latex_escape(link_text)))
            elif fmt == "markdown":
                out.append("[%s](%s)" % (link_text, url))
            else:
                out.append("%s (%s)" % (link_text, url))
        elif m.group("bold"):
            bold_text = m.group("bold_text")
            if fmt == "latex":
                out.append(r"\textbf{%s}" % latex_escape(bold_text))
            elif fmt == "markdown":
                out.append("**%s**" % bold_text)
            else:
                out.append(bold_text)
        elif m.group("italic"):
            italic_text = m.group("italic_text")
            if fmt == "latex":
                out.append(r"\textit{%s}" % latex_escape(italic_text))
            elif fmt == "markdown":
                out.append("*%s*" % italic_text)
            else:
                out.append(italic_text)
        elif m.group("code"):
            code_text = m.group("code_text")
            if fmt == "latex":
                out.append(r"\texttt{%s}" % latex_escape(code_text))
            elif fmt == "markdown":
                out.append("`%s`" % code_text)
            else:
                out.append(code_text)

        pos = m.end()

    if pos < len(text):
        out.append(_render_plain(text[pos:], fmt))

    return "".join(out)


def to_latex(text):
    return render(text, "latex")


def to_markdown(text):
    return render(text, "markdown")


def to_text(text):
    return render(text, "text")


_ORDINAL_RE = re.compile(r"\b(\d+)(st|nd|rd|th)\b")


def latex_ordinal(text):
    """Superscript ordinal suffixes for LaTeX output, e.g. '1st' -> '1$^{st}$'."""
    return _ORDINAL_RE.sub(lambda m: "%s$^{%s}$" % (m.group(1), m.group(2)), text)

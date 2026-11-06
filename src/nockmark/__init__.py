"""nockmark: annotated code fragments for Sphinx and MyST.

The HTML counterpart of the LaTeX package nockmark
(https://github.com/sigilante/nockmark).  Add "nockmark" to a Sphinx
project's extensions (or a Jupyter Book's sphinx.extra_extensions) and use
one directive, in Markdown pages and in notebook Markdown cells:

    ```{nockmark}
    :language: nock
    %% heading Static sites: the code travels with the literal
    [8 [1 0]
      8 {{[1 <B>]|s1}}
      {{9 2 0 1|s2}}]
    %% note s1 literal formula: a `Form` carrying `nockToSki` *B*
    %% note s2 opcode 9 pulls the `Form`: `app` runs its code
    %% skip
    <B> = [6 [5 [0 7] 4 0 6] [0 6]
        {{9 2 [0 2] [4 0 6] 0 7|s3}}]
    %% below s3 the arm is copied from the subject by `[0 2]`
    %% rule
    %% heading Dynamic site: a formula built from data
    [2 [0 1] {{~[1 4] [1 0 1]|d1}}]
    %% below d1 autocons builds a plain cell: `app` hands it to `nockI`
    ```

Code lines are kept verbatim, indentation included.  In them:

* ``{{code|name}}`` is a solid box named ``name``; ``{{~code|name}}`` is
  dashed.  The name is optional when no note refers to the box.
* ``<B>`` is a metavariable, set in italics (``:meta: off`` to disable).

Lines starting with ``%%`` are layout commands:

* ``%% heading <text>``, ``%% rule``, ``%% skip``;
* ``%% note <box> <text>``: a note in the right column, with an arrow
  to the end of the box's line;
* ``%% below <box> <text>``: a note set under the box.

Note and heading text takes ``code``, *emphasis* and **strong**.

HTML output is a CSS grid (``static/nockmark.css``, added to every page),
highlighted with the project's Pygments lexers, including any registered with
``app.add_lexer``.  LaTeX output is the nockmark environment; the package
ships nockmark.sty and adds it to the LaTeX build.
"""

__version__ = "0.1.0"

import html
import os
import re

from docutils import nodes
from docutils.parsers.rst import Directive, directives
from pygments import lex
from pygments.lexers import get_lexer_by_name
from pygments.token import STANDARD_TYPES
from pygments.util import ClassNotFound
from sphinx.highlighting import lexer_classes as sphinx_lexer_classes
from sphinx.highlighting import lexers as sphinx_lexers

_HERE = os.path.dirname(os.path.abspath(__file__))

BOX = re.compile(r"\{\{(~?)(.*?)(?:\|([A-Za-z][\w-]*))?\}\}")
META = re.compile(r"<([A-Za-z][\w-]*)>")
INLINE = re.compile(r"`([^`]+)`|\*\*([^*]+)\*\*|\*([^*]+)\*")


class NockmarkError(Exception):
    pass


# ------------------------------------------------------------------ parse

def parse_line(text):
    """Split a code line into ('code', s) and ('box', dashed, s, name) pieces."""
    pieces, pos = [], 0
    for m in BOX.finditer(text):
        if m.start() > pos:
            pieces.append(("code", text[pos:m.start()]))
        pieces.append(("box", m.group(1) == "~", m.group(2), m.group(3)))
        pos = m.end()
    if pos < len(text):
        pieces.append(("code", text[pos:]))
    return pieces


def visible_len(s, meta):
    return len(META.sub(r"\1", s) if meta else s)


def parse(body, meta=True):
    """Body lines -> a list of items:
    ('heading', text) ('rule',) ('skip',)
    ('line', pieces, {box name: column}, [side notes], [below notes])."""
    items, boxes = [], {}
    for raw in body:
        if raw.lstrip().startswith("%%"):
            cmd = raw.lstrip()[2:].strip()
            word, _, rest = cmd.partition(" ")
            if word == "heading":
                items.append(("heading", rest.strip()))
            elif word in ("rule", "skip"):
                items.append((word,))
            elif word in ("note", "below"):
                name, _, text = rest.strip().partition(" ")
                if name not in boxes:
                    raise NockmarkError(f"note for unknown box {name!r}")
                line = boxes[name]
                (line[3] if word == "note" else line[4]).append((name, text.strip()))
            else:
                raise NockmarkError(f"unknown command %% {word}")
            continue
        pieces = parse_line(raw.rstrip())
        cols, col = {}, 0
        for p in pieces:
            if p[0] == "box" and p[3]:
                if p[3] in boxes:
                    raise NockmarkError(f"box name {p[3]!r} used twice")
                cols[p[3]] = col
            col += visible_len(p[-2] if p[0] == "box" else p[1], meta)
        line = ["line", pieces, cols, [], []]
        for name in cols:
            boxes[name] = line
        items.append(line)
    return items


# ------------------------------------------------------------------ HTML

def _css_class(tok):
    while tok not in STANDARD_TYPES:
        tok = tok.parent
    return STANDARD_TYPES[tok]


def highlight(s, lexer, meta):
    """HTML for a code span: Pygments classes, metavariables in italics."""
    out = []
    parts = META.split(s) if meta else [s]
    for i, part in enumerate(parts):
        if i % 2:
            out.append(f'<var class="nm-meta">{html.escape(part)}</var>')
            continue
        if not part:
            continue
        if lexer is None:
            out.append(html.escape(part))
            continue
        for tok, val in lex(part, lexer):
            val = val.rstrip("\n") if part[-1:] != "\n" else val
            if not val:
                continue
            cls = _css_class(tok)
            esc = html.escape(val)
            out.append(f'<span class="{cls}">{esc}</span>' if cls else esc)
    return "".join(out)


def inline_html(text):
    out, pos = [], 0
    for m in INLINE.finditer(text):
        out.append(html.escape(text[pos:m.start()]))
        if m.group(1):
            out.append(f"<code>{html.escape(m.group(1))}</code>")
        elif m.group(2):
            out.append(f"<strong>{html.escape(m.group(2))}</strong>")
        else:
            out.append(f"<em>{html.escape(m.group(3))}</em>")
        pos = m.end()
    out.append(html.escape(text[pos:]))
    return "".join(out)


def render_html(items, lexer, meta):
    rows = []
    for it in items:
        kind = it[0]
        if kind == "heading":
            rows.append(f'<div class="nm-heading">{inline_html(it[1])}</div>')
        elif kind == "rule":
            rows.append('<div class="nm-rule"></div>')
        elif kind == "skip":
            rows.append('<div class="nm-skip"></div>')
        else:
            _, pieces, cols, side, below = it
            code = []
            for p in pieces:
                if p[0] == "code":
                    code.append(highlight(p[1], lexer, meta))
                else:
                    _, dashed, s, name = p
                    cls = "nm-box nm-dashed" if dashed else "nm-box"
                    ident = f' data-nm="{html.escape(name)}"' if name else ""
                    code.append(f'<span class="{cls}"{ident}>{highlight(s, lexer, meta)}</span>')
            arrow = '<span class="nm-arrow" aria-hidden="true"></span>' if side else ""
            note = "<br>".join(inline_html(t) for _, t in side)
            rows.append(
                f'<div class="nm-line"><code class="nm-code">{"".join(code)}</code>{arrow}</div>'
                f'<div class="nm-note">{note}</div>'
            )
            for name, text in below:
                rows.append(
                    f'<div class="nm-below" style="padding-left: {cols[name]}ch">'
                    f'<span class="nm-text">{inline_html(text)}</span></div>'
                )
    # The outer .highlight picks up the theme's Pygments colours; the grid is
    # the inner div, so the theme's own .highlight rules don't reach it.
    return ('<div class="nockmark-wrap highlight"><div class="nockmark">'
            + "".join(rows) + "</div></div>")


# ------------------------------------------------------------------ LaTeX

_TEX = {"\\": r"\textbackslash{}", "{": r"\{", "}": r"\}", "$": r"\$", "&": r"\&",
        "#": r"\#", "_": r"\_", "%": r"\%", "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}"}


def tex(s):
    return "".join(_TEX.get(c, c) for c in s)


def tex_code(s, meta):
    parts = META.split(s) if meta else [s]
    return "".join(r"\nkmeta{" + tex(p) + "}" if i % 2 else tex(p).replace(" ", r"\ ")
                   for i, p in enumerate(parts))


def inline_tex(text):
    out, pos = [], 0
    for m in INLINE.finditer(text):
        out.append(tex(text[pos:m.start()]))
        if m.group(1):
            out.append(r"\texttt{" + tex(m.group(1)) + "}")
        elif m.group(2):
            out.append(r"\textbf{" + tex(m.group(2)) + "}")
        else:
            out.append(r"\emph{" + tex(m.group(3)) + "}")
        pos = m.end()
    out.append(tex(text[pos:]))
    return "".join(out)


def render_latex(items, meta, indent_width=2):
    out = [r"\begin{center}", r"\begin{nockmark}"]
    for it in items:
        kind = it[0]
        if kind == "heading":
            out.append(r"  \nkheading{" + inline_tex(it[1]) + "}")
        elif kind == "rule":
            out.append(r"  \nkrule")
        elif kind == "skip":
            out.append(r"  \nkskip{0.3}")
        else:
            _, pieces, cols, side, below = it
            first = pieces[0][1] if pieces and pieces[0][0] == "code" else ""
            lead = len(first) - len(first.lstrip(" "))
            body, stripped = [], False
            for p in pieces:
                if p[0] == "code":
                    s = p[1] if stripped else p[1][lead:]
                    if s:
                        body.append(r"\nk{" + tex_code(s, meta) + "}")
                else:
                    _, dashed, s, name = p
                    cmd = r"\nkdynamic" if dashed else r"\nkstatic"
                    body.append(cmd + "{" + (name or "nm@anon") + "}{" + tex_code(s, meta) + "}")
                stripped = True
            step = lead / indent_width
            out.append(rf"  \nkline[{step:g}]{{" + "".join(body) + "}")
            for name, text in side:
                out.append(r"  \nknote{" + name + "}{" + inline_tex(text) + "}")
            for name, text in below:
                out.append(r"  \nknotebelow{" + name + "}{" + inline_tex(text) + "}")
    out += [r"\end{nockmark}", r"\end{center}"]
    return "\n".join(out)


# ------------------------------------------------------------------ directive

def _lexer(lang):
    """The lexer for lang: one the project registered with app.add_lexer
    first, then any Pygments knows; None for plain text."""
    if lang in ("none", "text"):
        return None
    if lang in sphinx_lexers:
        return sphinx_lexers[lang]
    if lang in sphinx_lexer_classes:
        return sphinx_lexer_classes[lang]()
    try:
        return get_lexer_by_name(lang)
    except ClassNotFound:
        return None


class NockmarkDirective(Directive):
    has_content = True
    option_spec = {
        "language": directives.unchanged,
        "meta": lambda a: directives.choice(a, ("on", "off")),
        "caption": directives.unchanged,
        "class": directives.class_option,
    }

    def run(self):
        meta = self.options.get("meta", "on") == "on"
        lang = self.options.get("language", "nock")
        lexer = _lexer(lang)
        try:
            items = parse(list(self.content), meta)
        except NockmarkError as e:
            return [self.state_machine.reporter.error(
                f"nockmark: {e}", line=self.lineno)]
        container = nodes.container(classes=["nockmark-figure"] + self.options.get("class", []))
        container += nodes.raw("", render_html(items, lexer, meta), format="html")
        container += nodes.raw("", render_latex(items, meta), format="latex")
        if "caption" in self.options:
            cap, _ = self.state.inline_text(self.options["caption"], self.lineno)
            para = nodes.paragraph("", "", *cap, classes=["nm-caption"])
            container += para
        return [container]


def _config_inited(app, config):
    # Assign rather than append: newer Sphinx hands out copies of list values.
    config.html_static_path = [*config.html_static_path, os.path.join(_HERE, "static")]
    config.latex_additional_files = [*config.latex_additional_files,
                                     os.path.join(_HERE, "nockmark.sty")]


def setup(app):
    app.add_directive("nockmark", NockmarkDirective)
    app.connect("config-inited", _config_inited)
    app.add_css_file("nockmark.css")
    app.add_latex_package("nockmark")
    return {"version": __version__, "parallel_read_safe": True,
            "parallel_write_safe": True}

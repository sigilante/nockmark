# nockmark

Annotated code fragments for LaTeX, drawn with TikZ: lines of code with solid
or dashed boxes around spans, notes in a right-hand column with arrows, notes
set under a box, headings and dotted dividers. Made for Nock, which has no
layout of its own, but any monospaced code works. pdfLaTeX, XeLaTeX and
LuaLaTeX.

![An annotated Nock fragment drawn with nockmark](https://raw.githubusercontent.com/sigilante/nockmark/master/doc/example.png)

```latex
\usepackage{nockmark}
...
\begin{nockmark}
  \nkheading{Static sites}
  \nkline{\nk{[8 [1 0]}}
  \nkline[1]{\nk{8 }\nkstatic{s1}{[1 \nkmeta{B}]}}
  \nknote{s1}{literal formula: a \texttt{Form} carrying its code}
  \nkrule
  \nkheading{Dynamic site}
  \nkline{\nk{[2 [0 1] }\nkdynamic{d1}{[1 4] [1 0 1]}\nk{]}}
  \nknotebelow{d1}{autocons builds a plain cell}
\end{nockmark}
```

Extracted from Figure 1 of *Nock in SKI* (Davis 2027). The manual is
`doc/nockmark.tex`.

## LaTeX

Copy or symlink `tex/nockmark.sty` next to your document, or install it into
your TeX tree with `l3build install`.

## Sphinx, MyST and Jupyter Book

### Install

```sh
pip install nockmark
```

or the current source:

```sh
pip install git+https://github.com/sigilante/nockmark
```

nockmark needs Python 3.9 or later and pulls in Sphinx (5 or later), docutils
and Pygments.

### Enable it

In a Sphinx project's `conf.py`:

```python
extensions = ["nockmark"]
```

In a Jupyter Book 1.x `_config.yml`:

```yaml
sphinx:
  extra_extensions:
    - nockmark
```

The directive works in MyST Markdown pages and in notebooks' Markdown cells
(a plain Sphinx project reads Markdown through `myst-parser`; Jupyter Book
already includes it), and in reStructuredText as `.. nockmark::`.
The extension adds `nockmark.css` to every HTML page, and for a PDF/LaTeX build
it copies the bundled `nockmark.sty` into the LaTeX output and loads it, so
nothing needs installing in the TeX tree. Directives render when the site is
built; a notebook opened live in Jupyter shows the Markdown source.

### The directive

````markdown
```{nockmark}
:language: nock
:caption: Count-up decrement.
%% heading Static sites
[8 [1 0]
  8 {{[1 <B>]|s1}}
  {{9 2 0 1|s2}}]
%% note s1 a literal formula: the battery *B*
%% note s2 pull arm 2 of the core and run it
%% rule
%% heading Dynamic site
[2 [0 1] {{~[1 4] [1 0 1]|d1}}]
%% below d1 autocons builds a plain cell, interpreted at run time
```
````

Options:

| Option | Values | |
|---|---|---|
| `:language:` | a lexer name; default `nock` | Highlighting. Any Pygments lexer, or one the project registers with `app.add_lexer` (so a Nock or Hoon lexer is picked up). `none` or `text`, or a name no lexer knows, gives plain text. |
| `:meta:` | `on` (default), `off` | Whether `<B>` is a metavariable. |
| `:caption:` | text | A caption under the block; inline markup allowed. |
| `:class:` | class names | Extra classes on the outer container. |

Body syntax:

- Code lines are kept verbatim, indentation included.
- `{{code|name}}` is a solid box, `{{~code|name}}` a dashed one. The name is
  optional when no note refers to the box; a name may be used only once per
  block.
- `<B>` (a letter, then letters, digits, `_` or `-`) is a metavariable, set in
  italics. `:meta: off` leaves it as written.
- Lines starting `%%` are layout:
  - `%% heading <text>`: a heading;
  - `%% rule`: a dotted divider;
  - `%% skip`: vertical space;
  - `%% note <box> <text>`: a note in the right column, with an arrow from the
    end of the box's line;
  - `%% below <box> <text>`: a note set under the box.
- A note must come after the line holding its box. Note and heading text takes
  `` `code` ``, `*emphasis*` and `**strong**`.

Keep to one `note` per code line: notes on the same line share one cell of the
right column. Put the other boxes on lines of their own, or use `below`.

In the browser the notes move under their lines on narrow screens. An error in
the body (an unknown command, a note for an unknown box, a box name used twice)
is reported as an error in the build output, at the directive's line, and
the block is left out.

## Python without Sphinx

The parser and both renderers are plain functions in `nockmark`
(`src/nockmark/__init__.py`). Importing the module needs Sphinx installed, which
`pip install nockmark` takes care of.

- `parse(lines, meta=True)` takes the directive body as a list of strings (one
  per line, no `:option:` lines) and returns a list of items: `("heading",
  text)`, `("rule",)`, `("skip",)` or `["line", pieces, columns, notes,
  below_notes]`. It raises `nockmark.NockmarkError` for an unknown `%%`
  command, a note for an unknown box, or a repeated box name.
- `render_html(items, lexer, meta)` returns an HTML string. `lexer` is a
  Pygments lexer instance (for example from
  `pygments.lexers.get_lexer_by_name`) or `None` for no highlighting. Pass the same `meta` as to
  `parse`.
- `render_latex(items, meta, indent_width=2)` returns a `nockmark` environment
  inside `center`, for a document that loads `nockmark.sty`. Leading spaces
  become `\nkline` indent steps of `indent_width` spaces.

```python
from importlib.resources import files

import nockmark

block = """\
%% heading Static site
[8 [1 0] 8 {{[1 <B>]|s1}} 9 2 0 1]
%% note s1 a literal formula: the battery *B*
%% rule
[2 [0 1] {{~[1 4] [1 0 1]|d1}}]
%% below d1 autocons builds a `cell`
"""

items = nockmark.parse(block.splitlines())
print(nockmark.render_html(items, None, True))   # None: no highlighting
print(nockmark.render_latex(items, True))

css = (files("nockmark") / "static" / "nockmark.css").read_text()
```

Output (the HTML is one line):

```html
<div class="nockmark-wrap highlight"><div class="nockmark"><div class="nm-heading">Static site</div><div class="nm-line"><code class="nm-code">[8 [1 0] 8 <span class="nm-box" data-nm="s1">[1 <var class="nm-meta">B</var>]</span> 9 2 0 1]</code><span class="nm-arrow" aria-hidden="true"></span></div><div class="nm-note">a literal formula: the battery <em>B</em></div><div class="nm-rule"></div><div class="nm-line"><code class="nm-code">[2 [0 1] <span class="nm-box nm-dashed" data-nm="d1">[1 4] [1 0 1]</span>]</code></div><div class="nm-note"></div><div class="nm-below" style="padding-left: 9ch"><span class="nm-text">autocons builds a <code>cell</code></span></div></div></div>
```

```latex
\begin{center}
\begin{nockmark}
  \nkheading{Static site}
  \nkline[0]{\nk{[8\ [1\ 0]\ 8\ }\nkstatic{s1}{[1\ \nkmeta{B}]}\nk{\ 9\ 2\ 0\ 1]}}
  \nknote{s1}{a literal formula: the battery \emph{B}}
  \nkrule
  \nkline[0]{\nk{[2\ [0\ 1]\ }\nkdynamic{d1}{[1\ 4]\ [1\ 0\ 1]}\nk{]}}
  \nknotebelow{d1}{autocons builds a \texttt{cell}}
\end{nockmark}
\end{center}
```

The HTML needs the stylesheet, which ships in the package as
`nockmark/static/nockmark.css` (read it with `importlib.resources` as above, or
copy it from `src/nockmark/static/`). Highlighting uses Pygments token classes
inside an outer `.highlight`, so add a Pygments style, e.g.
`pygments.formatters.HtmlFormatter().get_style_defs(".highlight")`. The wheel
also ships `nockmark/nockmark.sty` for the LaTeX side.

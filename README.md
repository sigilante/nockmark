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

```sh
pip install nockmark
```

Add `nockmark` to `extensions` in `conf.py`, or to `sphinx.extra_extensions` in a
Jupyter Book's `_config.yml`. Then, in a Markdown page or a notebook's Markdown
cell:

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

Code lines are kept verbatim. `{{code|name}}` is a solid box, `{{~code|name}}` a
dashed one (the name is optional when no note refers to it); `<B>` is a
metavariable (`:meta: off` to disable). Lines starting `%%` are layout:
`heading`, `rule`, `skip`, `note <box> <text>` (right column, with an arrow) and
`below <box> <text>` (under the box). Note text takes `` `code` ``, `*emphasis*`
and `**strong**`. Highlighting uses any lexer the project registers, so a Nock or
Hoon lexer added with `app.add_lexer` is picked up.

The same block builds to the LaTeX environment in a PDF build; the Python
package ships `nockmark.sty` and adds it to the LaTeX output. In the browser the
notes move under their lines on narrow screens. Directives render when the site
is built; a notebook opened live in Jupyter shows the Markdown source.

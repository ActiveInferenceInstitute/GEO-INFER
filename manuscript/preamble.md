# LaTeX Preamble

This file contains project-local LaTeX additions consumed by the template
renderer, which injects it verbatim immediately before `\begin{document}` in
`output/pdf/_combined_manuscript.tex`. Keep it minimal until the manuscript
needs additional math, table, or figure support.

```latex
\usepackage{amsmath}
\usepackage{amssymb}
\usepackage{geometry}
\usepackage{graphicx}
\usepackage{booktabs}
\usepackage{longtable}
\usepackage{array}
\usepackage{hyperref}
\usepackage[capitalise,noabbrev]{cleveref}
\usepackage{natbib}
```

## Float placement

LaTeX's defaults reserve a whole page for any float taller than
`\topfraction` (0.7) of the text block, and let a float claim a page of its
own once it fills `\floatpagefraction` (0.5) of one. All three evidence
figures therefore landed on pages carrying a single caption and roughly 300
characters of text against 1,800-2,000 on an ordinary page. Raising
`\topfraction` lets a tall float sit at the top of a text page; raising
`\floatpagefraction` means LaTeX opens a float page only for a float that
nearly fills one.

These parameters alone were not enough for the module inventory: at one column
of 45 legible rows it came to 0.90 of the text block and still cleared the
raised threshold. The generator now lays that figure out in two panels and
refuses, in `_assert_leaves_room_for_text`, to write any figure whose float
would exceed `\floatpagefraction` — so the settings below and the drawn size
are held in agreement rather than one being tuned against the other.

```latex
\renewcommand{\topfraction}{0.9}
\renewcommand{\bottomfraction}{0.9}
\renewcommand{\textfraction}{0.08}
\renewcommand{\floatpagefraction}{0.85}
```

## Breakable monospace spans

Pandoc emits inline code as `\texttt{...}`, which cannot break. The renderer
rewrites long monospace spans to a breakable macro, but only when it can
decode Pandoc's serialised body: a span containing `--` reaches the `.tex` as
`-\/-`, whose backslash puts it outside that decoder's contract, and the span
stays unbreakable. Six of the seven commands in the verification table carry a
`--` flag, and all six ran into the neighbouring Status column; the seventh,
which has no such flag, was rewritten by the renderer and broke cleanly.

Measuring first keeps the change to the spans that need it: a span narrower
than a sixth of the line is boxed once and shipped unchanged, and only a wide
one is re-typeset through `\seqsplit`, which adds break opportunities without
inserting a character, so the printed command still copies as one string. At
the full 430pt line that threshold is about twelve monospace characters, close
to the sixteen-character threshold the renderer applies to the spans it can
decode; inside a narrow table column it scales down with the column, which is
where the unbreakable spans actually overflow.

```latex
\IfFileExists{seqsplit.sty}{\usepackage{seqsplit}}{\newcommand{\seqsplit}[1]{#1}}
\newsavebox{\GIttbox}
\protected\def\texttt#1{%
  \begingroup\ttfamily
  \sbox\GIttbox{#1}%
  \ifdim\wd\GIttbox>0.15\linewidth\seqsplit{#1}\else\usebox\GIttbox\fi
  \endgroup}
```

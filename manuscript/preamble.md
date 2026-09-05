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
own once it fills `\floatpagefraction` (0.5) of one. The two half-height
evidence figures therefore landed on pages carrying a single caption and
roughly 300 characters of text against 1,800-2,000 on an ordinary page.
Raising `\topfraction` lets a tall float sit at the top of a text page;
raising `\floatpagefraction` means LaTeX opens a float page only for a float
that nearly fills it — which the full-page 45-module inventory does and the
smaller figures do not.

```latex
\renewcommand{\topfraction}{0.9}
\renewcommand{\bottomfraction}{0.9}
\renewcommand{\textfraction}{0.08}
\renewcommand{\floatpagefraction}{0.85}
```

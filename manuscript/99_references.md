# References {#sec:references}

Bibliography lives in [`manuscript/references.bib`](references.bib) and is read
by Pandoc during PDF render. Citations in the manuscript must resolve to real
entries in that file; repository-derived counts and captions are not
substitutes for external scientific references.

The generator audits that relationship on every run. It parses
`references.bib`, scans the resolved manuscript for citation keys — excluding
cross-reference labels such as figure and table references, which share the
`@` sigil — and fails the build when a citation has no entry. An entry that no
section cites is reported by name on every run, and can be promoted to a build
failure through the bibliography policy in `manuscript/config.yaml`.

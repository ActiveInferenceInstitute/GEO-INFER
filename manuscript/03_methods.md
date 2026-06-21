# Methods {#sec:methods}

## Manuscript Construction Method

Use the manuscript scaffold to summarize the module registry, ACT/BAYES/MATH foundations, repo-wide contracts, and current verification commands from ISA and TODO.

## Evidence Promotion

Future manuscript claims should be promoted in this order:

1. Identify the source file, test, generated artifact, or external reference.
2. Add or verify the project-local gate that reproduces the claim.
3. Move volatile values into generated manuscript variables when they can change across runs.
4. Add prose only after the supporting evidence path is stable.

## Template Compliance

Each section file has one H1 label, no unresolved citations, and no generated-value tokens until a project-local token producer exists.

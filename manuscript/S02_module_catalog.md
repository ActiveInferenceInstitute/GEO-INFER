# Supplemental Module Catalog {#sec:module_catalog}

The catalog is the per-module companion to the theme map in
[@sec:system_context] and the measured inventory in
[@tbl:module_inventory]. Where those surfaces group the framework, this
catalog enumerates it: one prose entry per module, in alphabetical order,
each stating what the module is for, what its public interface exposes, and
how its test surface is shaped. The repository ships
`{{GEO_MODULE_COUNT}}` modules at the commit this manuscript was generated
from.

[@tbl:module_catalog_index] is the catalog's index. Each row names one
measured module, the declared theme it belongs to, a one-line purpose taken
from the module's own `README.md`, its counted non-empty Python source
lines, and its test-file count. The entries that follow the table expand
each row into prose; they are authored from the module's public interface —
the symbols its package exports in `__init__.py` — its test census, and its
declared theme role. They reference no figures, and every quantity the
catalog states is measured by the same inventory pass that produces this
manuscript's other numbers.

{{GEO_MODULE_TABLE}}

: The module catalog index at commit `{{RESEARCH_COMMIT}}`: one row per
measured module with its declared theme, purpose, and measured source and
test surfaces. The rows are alphabetical and self-contained, so a row can be
read on its own or as the index into the prose entries below. The purpose
column quotes the module's own README; the LOC and Tests columns are the
same measurements the inventory figure and the module inventory table
publish.
{#tbl:module_catalog_index}

Read the catalog alongside the theme map rather than instead of it: theme
membership is a statement about the kind of claim a module is responsible
for, while the entries below are statements about what each module actually
exposes and verifies. An entry can be read on its own — each begins with the
module's full name — or in sequence, where the alphabetical order makes the
shared shape of the module contract visible: every module is a package with
a public interface, a test tree, and a theme.

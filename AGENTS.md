# GEO-INFER Agent Instructions

Use this file as the repository-level operating contract for automated agents working in GEO-INFER.

## Cold Start (agent orientation)

New to this repo? In order:

1. **What this is**: a multi-module geospatial inference monorepo (uv workspace, Python 3.11+); see [README.md](README.md) "What's inside".
2. **Module map**: [README.md Module Index](README.md#module-index) (source/test counts per module) and [GEO-INFER-INTRA/docs/modules/index.md](GEO-INFER-INTRA/docs/modules/index.md) (conceptual catalog).
3. **Where to change what**: module behavior in `GEO-INFER-*/src/` (owning package); cross-module docs in `GEO-INFER-INTRA/docs/`; tests/validation in `GEO-INFER-TEST/`.
4. **Health in one command**: `uv run python GEO-INFER-TEST/rewrite_readme_agents.py --check` (generated-signpost drift) plus the validators under Standard Commands.
5. **Backlog with acceptance lines**: [TODO.md](TODO.md).

## Repository Scope

- Root path: repository root (`.`; resolve it from the checkout in use)
- Modules: `GEO-INFER-ACT`, `GEO-INFER-AG`, `GEO-INFER-AGENT`, `GEO-INFER-AI`, `GEO-INFER-ANT`, `GEO-INFER-API`, `GEO-INFER-APP`, `GEO-INFER-ART`, `GEO-INFER-BAYES`, `GEO-INFER-BIO`, `GEO-INFER-CIV`, `GEO-INFER-CLIMATE`, `GEO-INFER-COG`, `GEO-INFER-COMMS`, `GEO-INFER-DATA`, `GEO-INFER-ECON`, `GEO-INFER-EDU`, `GEO-INFER-EMERGENCY`, `GEO-INFER-ENERGY`, `GEO-INFER-EXAMPLES`, `GEO-INFER-FOREST`, `GEO-INFER-GIT`, `GEO-INFER-HEALTH`, `GEO-INFER-INSURANCE`, `GEO-INFER-INTRA`, `GEO-INFER-IOT`, `GEO-INFER-LOG`, `GEO-INFER-MARINE`, `GEO-INFER-MATH`, `GEO-INFER-METAGOV`, `GEO-INFER-NORMS`, `GEO-INFER-OPS`, `GEO-INFER-ORG`, `GEO-INFER-PEP`, `GEO-INFER-PLACE`, `GEO-INFER-REQ`, `GEO-INFER-RISK`, `GEO-INFER-SEC`, `GEO-INFER-SIM`, `GEO-INFER-SPACE`, `GEO-INFER-SPM`, `GEO-INFER-TEST`, `GEO-INFER-TIME`, `GEO-INFER-TRANSPORT`, `GEO-INFER-WATER`
- Package manager: `uv`
- Python target: 3.11+

## Required Workflow

1. Inspect the relevant module before editing.
2. Keep functionality in the owning module under `src/`.
3. Keep scripts and examples as thin orchestration surfaces.
4. Update README.md and AGENTS.md when behavior, commands, exports, or dependencies change.
5. Run the narrowest relevant test first, then the repo contract validators.

## Standard Commands

```bash
uv sync --all-packages --all-extras
python -m compileall GEO-INFER-*/src GEO-INFER-*/examples
uv run python GEO-INFER-TEST/validate_repo_contracts.py --strict-source-language
uv run python GEO-INFER-TEST/validate_logging_hygiene.py
uv run python GEO-INFER-TEST/validate_documentation.py --strict
uv run python GEO-INFER-TEST/validate_skills.py --check-xrefs
uv run python manuscript/generate_research_artifacts.py
uv run python GEO-INFER-TEST/run_unified_tests.py --category unit
uv run python GEO-INFER-TEST/run_unified_tests.py --category integration
uv run python GEO-INFER-TEST/run_unified_tests.py --category performance
uv run python GEO-INFER-TEST/run_unified_tests.py --h3-migration
uv run python GEO-INFER-TEST/validate_test_contracts.py --strict
uv run python GEO-INFER-TEST/validate_model_contracts.py --strict --seed 42
uv run python GEO-INFER-TEST/run_model_audit.py --seed 42 --reproducible
uv run --with 'ruff>=0.15.6,<0.16' ruff check GEO-INFER-*/src --select F821,F823,E721,E722
uv run python GEO-INFER-TEST/rewrite_readme_agents.py --check
```

## Modular Hygiene Contract

- Use root `pyproject.toml`, `uv.lock`, and `.python-version` as the shared uv environment contract.
- Sync the shared workspace with `uv sync --all-packages --all-extras`.
- Keep module behavior in the owning `GEO-INFER-*` package under `src/`; keep scripts and examples as orchestration surfaces.
- Treat `manuscript/generate_research_artifacts.py` as the only producer of manuscript variables, figure captions, figure registries, and resolved manuscript copies; never hand-edit ignored `output/`.
- Keep every module's local test inventory above the minimum release gate of four pytest files.
- Put planned work in root `TODO.md` or a tracked issue; do not leave task markers in module source or tests.
- Use module loggers in libraries and configure handlers only from CLI entrypoints.

## Documentation Contract

Agent-facing documentation must be operational: current paths, commands, package names, public exports, test surfaces, and failure triage. Do not advertise planned APIs in AGENTS.md; use issues, roadmaps, or implementation status files for future work.

## Documentation Workflow

- Put conceptual, cross-module, and user-facing guidance in
  `GEO-INFER-INTRA/docs/`.
- Keep module READMEs focused on the current filesystem, imports, dependencies,
  and verification commands; they are generated from tracked repository facts.
- Keep `SKILL.md` action-oriented and synchronized with real public APIs.
- Validate relative documentation links and generated signposts before handoff.
- Preserve existing work from other agents in a shared checkout; inspect the
  diff before staging generated documentation.

## Documentation and Release Gate

- Run `uv run python GEO-INFER-TEST/rewrite_readme_agents.py` after changing tracked module files, public exports, tests, or validation commands.
- Treat the generated README/AGENTS diff as a review surface: it should reflect the intended source, test, dependency, and signpost changes only.
- Before integrating to `main`, run the strict repository, test, model, skill, source-hygiene, unit, integration, performance, and H3 gates and record any environment-only setup warnings separately from repository failures.

<!-- gitnexus:start -->
# GitNexus — Code Intelligence

This project is indexed by GitNexus as **GEO-INFER** (65872 symbols, 93814 relationships, 300 execution flows). Use the GitNexus MCP tools to understand code, assess impact, and navigate safely.

> Index stale? Run `node .gitnexus/run.cjs analyze` from the project root — it auto-selects an available runner. No `.gitnexus/run.cjs` yet? `npx gitnexus analyze` (npm 11 crash → `npm i -g gitnexus`; #1939).

## Always Do

- **MUST run impact analysis before editing any symbol.** Before modifying a function, class, or method, run `impact({target: "symbolName", direction: "upstream"})` and report the blast radius (direct callers, affected processes, risk level) to the user.
- **MUST run `detect_changes()` before committing** to verify your changes only affect expected symbols and execution flows. For regression review, compare against the default branch: `detect_changes({scope: "compare", base_ref: "main"})`.
- **MUST warn the user** if impact analysis returns HIGH or CRITICAL risk before proceeding with edits.
- When exploring unfamiliar code, use `query({search_query: "concept"})` to find execution flows instead of grepping. It returns process-grouped results ranked by relevance.
- When you need full context on a specific symbol — callers, callees, which execution flows it participates in — use `context({name: "symbolName"})`.
- For security review, `explain({target: "fileOrSymbol"})` lists taint findings (source→sink flows; needs `analyze --pdg`).

## Never Do

- NEVER edit a function, class, or method without first running `impact` on it.
- NEVER ignore HIGH or CRITICAL risk warnings from impact analysis.
- NEVER rename symbols with find-and-replace — use `rename` which understands the call graph.
- NEVER commit changes without running `detect_changes()` to check affected scope.

## Resources

| Resource | Use for |
|----------|---------|
| `gitnexus://repo/GEO-INFER/context` | Codebase overview, check index freshness |
| `gitnexus://repo/GEO-INFER/clusters` | All functional areas |
| `gitnexus://repo/GEO-INFER/processes` | All execution flows |
| `gitnexus://repo/GEO-INFER/process/{name}` | Step-by-step execution trace |

## CLI

| Task | Read this skill file |
|------|---------------------|
| Understand architecture / "How does X work?" | `.claude/skills/gitnexus/gitnexus-exploring/SKILL.md` |
| Blast radius / "What breaks if I change X?" | `.claude/skills/gitnexus/gitnexus-impact-analysis/SKILL.md` |
| Trace bugs / "Why is X failing?" | `.claude/skills/gitnexus/gitnexus-debugging/SKILL.md` |
| Rename / extract / split / refactor | `.claude/skills/gitnexus/gitnexus-refactoring/SKILL.md` |
| Tools, resources, schema reference | `.claude/skills/gitnexus/gitnexus-guide/SKILL.md` |
| Index, status, clean, wiki CLI commands | `.claude/skills/gitnexus/gitnexus-cli/SKILL.md` |

<!-- gitnexus:end -->

#!/usr/bin/env python3
"""Rewrite tracked README.md and AGENTS.md files from repository facts.

The generated files are intentionally compact and operational. They avoid
roadmap language and only describe the current filesystem, package metadata,
test entry points, and public symbols discoverable from Python source files.
"""

from __future__ import annotations

import ast
import argparse
import subprocess
import sys
import tomllib
import warnings
from dataclasses import dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
MODULE_PREFIX = "GEO-INFER-"
MAX_SYMBOLS = 20


@dataclass
class ModuleInfo:
    name: str
    path: Path
    package: str
    description: str
    version: str
    dependencies: list[str]
    source_files: int
    test_files: int


def git_ls_files() -> list[Path]:
    result = subprocess.run(
        ["git", "ls-files"],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=True,
    )
    return [REPO_ROOT / line for line in result.stdout.splitlines() if line]


def read_pyproject(module_dir: Path) -> dict:
    pyproject = module_dir / "pyproject.toml"
    if not pyproject.exists():
        return {}
    return tomllib.loads(pyproject.read_text(encoding="utf-8"))


def requirement_lines(module_dir: Path, limit: int = 12) -> list[str]:
    requirements = module_dir / "requirements.txt"
    if not requirements.exists():
        return []
    lines: list[str] = []
    for line in requirements.read_text(encoding="utf-8", errors="ignore").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        lines.append(stripped)
        if len(lines) >= limit:
            break
    return lines


def discover_modules() -> dict[str, ModuleInfo]:
    modules: dict[str, ModuleInfo] = {}
    for module_dir in sorted(REPO_ROOT.glob(f"{MODULE_PREFIX}*")):
        if not module_dir.is_dir():
            continue
        pyproject = read_pyproject(module_dir)
        project = pyproject.get("project", {})
        package = str(project.get("name", module_dir.name.lower())).replace("-", "_")
        modules[module_dir.name] = ModuleInfo(
            name=module_dir.name,
            path=module_dir,
            package=package,
            description=str(project.get("description", module_dir.name)),
            version=str(project.get("version", "unversioned")),
            dependencies=requirement_lines(module_dir),
            source_files=len(list((module_dir / "src").glob("**/*.py"))),
            test_files=len(list((module_dir / "tests").glob("**/test_*.py"))),
        )
    return modules


def module_for(path: Path, modules: dict[str, ModuleInfo]) -> ModuleInfo | None:
    try:
        relative = path.relative_to(REPO_ROOT)
    except ValueError:
        return None
    if not relative.parts:
        return None
    return modules.get(relative.parts[0])


def tracked_doc_files() -> tuple[list[Path], list[Path]]:
    files = git_ls_files()
    readmes = sorted(path for path in files if path.name == "README.md")
    agents = sorted(path for path in files if path.name == "AGENTS.md")
    return readmes, agents


def direct_contents(directory: Path) -> tuple[list[str], list[str], list[str]]:
    dirs = sorted(
        child.name + "/"
        for child in directory.iterdir()
        if child.is_dir() and child.name not in {".git", ".venv", "__pycache__"}
    )
    py_files = sorted(child.name for child in directory.glob("*.py"))
    other_files = sorted(
        child.name
        for child in directory.iterdir()
        if child.is_file()
        and child.name not in {"README.md", "AGENTS.md"}
        and child.suffix != ".py"
    )
    return dirs[:24], py_files[:24], other_files[:24]


def public_symbols(directory: Path) -> list[str]:
    symbols: list[str] = []
    for py_file in sorted(directory.glob("*.py")):
        if py_file.name.startswith("test_"):
            continue
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", SyntaxWarning)
                tree = ast.parse(py_file.read_text(encoding="utf-8", errors="ignore"))
        except SyntaxError:
            continue
        for node in tree.body:
            if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
                if node.name.startswith("_"):
                    continue
                kind = "class" if isinstance(node, ast.ClassDef) else "function"
                symbols.append(f"`{py_file.name}:{node.name}` ({kind})")
                if len(symbols) >= MAX_SYMBOLS:
                    return symbols
    return symbols


def purpose_for(path: Path, module: ModuleInfo | None) -> str:
    rel = path.parent.relative_to(REPO_ROOT)
    if rel == Path("."):
        return "Repository root for the GEO-INFER geospatial inference framework."
    if module and path.parent == module.path:
        return module.description.rstrip(".") + "."
    parts = rel.parts
    folder = parts[-1].replace("_", " ").replace("-", " ")
    if module:
        return f"{folder.title()} workspace within `{module.name}`."
    return f"{folder.title()} workspace within GEO-INFER."


def test_command(path: Path, module: ModuleInfo | None) -> str:
    if path.parent == REPO_ROOT:
        return "uv run python GEO-INFER-TEST/run_unified_tests.py --category unit"
    if module and path.parent == module.path:
        return f"uv run python GEO-INFER-TEST/run_unified_tests.py --module {module.name.removeprefix(MODULE_PREFIX)}"
    if "tests" in path.parent.parts:
        rel = path.parent.relative_to(REPO_ROOT)
        return f"uv run python -m pytest {rel}"
    if module:
        return f"uv run python GEO-INFER-TEST/run_unified_tests.py --module {module.name.removeprefix(MODULE_PREFIX)}"
    return "uv run python GEO-INFER-TEST/validate_repo_contracts.py --skip-import-smoke"


def validation_commands(path: Path, module: ModuleInfo | None) -> str:
    """Return the validation command block for a documentation file."""
    commands: list[str] = []
    if module and module.name == "GEO-INFER-TEST":
        commands.append("uv sync --all-packages --all-extras")
    commands.append(test_command(path, module))
    return "\n".join(commands)


def module_readme_notes(path: Path, module: ModuleInfo | None) -> str:
    """Return implemented module-specific README notes for module roots."""
    if not module or path.parent != module.path:
        return ""
    if module.name == "GEO-INFER-TEST":
        return """
## Strict Testing Contracts

- `src/geo_infer_test/testing.py` exports deterministic RNG, local filesystem,
  HTTP, SQLite, and service fixtures plus finite/probability/matrix/model and
  visualization-manifest assertions.
- `validate_test_contracts.py --strict` validates every module inventory,
  primary marker, forbidden pytest control, syntax tree, and behavior-test
  docstring.
- `validate_model_contracts.py` checks representative ACT model contracts;
  `run_model_audit.py` emits finite statistics, a PNG visualization, SHA-256
  sidecars, and a deterministic manifest.
"""
    if module.name == "GEO-INFER-ACT":
        return """
## Implemented H3 Active Inference Contracts

- ACT uses `inferactively-pymdp==1.0.3` through
  `geo_infer_act.utils.pymdp_adapter` for categorical H3 active-inference
  runtime paths. H3 runtime cells are validated with real `h3>=4.5.0,<5`.
- Flat H3 APIs remain available through `GenerativeModel.enable_h3_spatial`,
  `GenerativeModel.update_h3_beliefs`, `ActiveInferenceModel.infer_over_h3_grid`,
  `SpatialActiveInferenceAgent.step`, and `simulate_h3_lattice`.
- Research trace APIs are available through
  `GenerativeModel.compute_h3_cell_diagnostics`,
  `ActiveInferenceModel.trace_over_h3_grid`,
  `ActiveInferenceModel.trace_over_nested_h3_grid`,
  `SpatialActiveInferenceAgent.trace_step`, and
  `SpatialActiveInferenceAgent.trace_nested_step`.
- Nested H3 APIs are opt-in through `enable_nested_h3_spatial`,
  `update_nested_h3_beliefs`, `infer_over_nested_h3_grid`,
  `SpatialActiveInferenceAgent.step_nested`, and
  `MultiAgentModel.simulate_nested_h3_lattice`.
- H3 diagnostics use `H3CellDiagnostics`, `H3EdgeDiagnostics`,
  `H3LevelDiagnostics`, and `SpatialInferenceTrace`; nested results use
  `NestedH3LevelSummary`, `NestedH3BeliefUpdateResult`, and
  `NestedH3GridInferenceResult` from `geo_infer_act`.
- Nested runner mode is enabled with `RunConfig.parameters["nested_h3"] = True`
  and emits `data/h3_hierarchy.csv`, `data/nested_h3_diagnostics.json`,
  `data/nested_h3_parent_child_diagnostics.csv`, and
  `visualizations/nested_h3_hierarchy_map.html`.
- Flat and nested H3 runner outputs include pymdp diagnostics in
  `data/pymdp_h3_diagnostics.json`, `data/pymdp_policy_posteriors.csv`, and
  `visualizations/pymdp_policy_free_energy.html`.
- Flat and nested H3 runner outputs also include
  `data/spatial_inference_trace.json`, `data/spatial_research_statistics.json`,
  `data/h3_cell_diagnostics.csv`, `data/h3_edge_diagnostics.csv`,
  `visualizations/h3_belief_flux_map.html`, `visualizations/h3_policy_surface.html`,
  `visualizations/h3_policy_transitions.html`,
  `visualizations/h3_spatial_autocorrelation.html`,
  `visualizations/h3_entropy_free_energy_phase.html`, and
  `visualizations/spatial_inference_research_report.html`.
- Research-profile runs are opt-in through
  `RunConfig.parameters["research_profile"] = True` or
  `geo-infer-act-run --research-profile`; they keep real H3 geometry and
  `inferactively-pymdp==1.0.3` while using deterministic offline spatial
  fields that avoid collapsed policy and entropy traces.
- Generate the deterministic four-run gallery with
  `uv run python GEO-INFER-ACT/examples/spatial_active_inference_gallery.py`.
  The supported runtime is `uv run`; system Python may contain older pymdp
  distributions and is not a valid H3 runtime contract.

```python
import numpy as np
from geo_infer_act import ActiveInferenceModel, GenerativeModel

model = GenerativeModel("categorical", {"state_dim": 4, "obs_dim": 4})
model.enable_nested_h3_spatial([7, 8, 9], cells=["89283082803ffff"])

agent = ActiveInferenceModel(model_type="categorical")
agent.set_generative_model(model)
result = agent.infer_over_nested_h3_grid(
    {model.h3_cells[0]: np.array([1.0, 0.0, 0.0, 0.0])},
    return_result=True,
)
trace = agent.trace_over_nested_h3_grid(
    {model.h3_cells[0]: np.array([1.0, 0.0, 0.0, 0.0])},
    grid_result=result,
)
```

Nested validation command:

```bash
uv run pytest GEO-INFER-ACT/tests/unit/test_nested_h3_active_inference.py -q
uv run python GEO-INFER-TEST/validate_h3_active_inference_contract.py
uv run python GEO-INFER-TEST/validate_act_geospatial_contract.py
```
"""
    if module.name == "GEO-INFER-SPACE":
        return """
## Implemented Nested H3 Contracts

- `geo_infer_space.nested.NestedH3Grid` builds real `h3>=4.5.0,<5`
  hierarchies from seed cells or boundary vertices across ordered resolutions.
- Hierarchy outputs include deterministic `parent_child_map`,
  `child_parent_map`, `same_level_neighbors`, level summaries, validation
  diagnostics, and finite child-to-parent aggregation.
- Validation rejects invalid H3 cells, unordered resolutions, orphan children,
  wrong-resolution children, and parent/child mismatches.

```python
from geo_infer_space.nested import NestedH3Grid

grid = NestedH3Grid("sf_nested")
hierarchy = grid.build_h3_hierarchy_from_cells(
    ["89283082803ffff"],
    resolutions=[7, 8, 9],
)
assert hierarchy["validation"]["is_valid"]
assert hierarchy["validation"]["orphan_count"] == 0
```

Nested validation command:

```bash
uv run pytest GEO-INFER-SPACE/tests/unit/test_nested_h3_contract.py -q
uv run python GEO-INFER-TEST/validate_h3_active_inference_contract.py
```
"""
    return ""


def module_agent_notes(path: Path, module: ModuleInfo | None) -> str:
    """Return implemented module-specific AGENTS notes for module roots."""
    if not module or path.parent != module.path:
        return ""
    if module.name == "GEO-INFER-TEST":
        return """
## Strict Testing Contracts

- Reuse `geo_infer_test.testing` fixtures and assertions for local boundaries,
  model contracts, and visualization artifacts.
- Missing dependencies, unavailable backends, warnings, skips, xfails, and
  empty selections are failures; do not hide them with warning filters or
  conditional pytest controls.
- Keep `validate_test_contracts.py`, `validate_model_contracts.py`, and
  `run_model_audit.py` synchronized with the documented commands and output
  schemas.
"""
    if module.name == "GEO-INFER-ACT":
        return """
## Current H3 Contracts

- Production ACT H3 runtime paths must use
  `geo_infer_act.utils.pymdp_adapter` and fail if `inferactively-pymdp` is not
  exactly `1.0.3`.
- Keep flat H3 method signatures and dictionary return shapes backward-compatible.
- Keep trace diagnostics JSON-safe and backed by typed result classes:
  `H3CellDiagnostics`, `H3EdgeDiagnostics`, `H3LevelDiagnostics`, and
  `SpatialInferenceTrace`.
- Use nested methods only for opt-in nested H3 behavior:
  `enable_nested_h3_spatial`, `update_nested_h3_beliefs`,
  `infer_over_nested_h3_grid`, `trace_over_nested_h3_grid`, `step_nested`,
  `trace_nested_step`, and `simulate_nested_h3_lattice`.
- Nested inference must reject invalid cells, observations outside the enabled
  hierarchy, mixed unexpected resolutions, non-finite observations, and empty
  belief vectors.
- Runner nested mode must keep outputs under the configured output directory and
  list generated hierarchy, diagnostics, and visualization files in the manifest.
- Runner flat and nested H3 modes must emit pymdp posterior, negative-EFE,
  free-energy, entropy, and backend-version diagnostics through manifest-linked
  sidecars.
- Runner flat and nested H3 modes must emit spatial trace JSON/CSV outputs plus
  belief-flux, policy-surface, policy-transition, spatial-autocorrelation,
  entropy/free-energy phase, and research-report HTML visualizations through
  the manifest sidecar pipeline.
- Research-profile and gallery runs must remain deterministic, real-H3, and
  non-degenerate: policy probabilities, entropy, local coherence, and belief
  flux should show finite variation above the validator thresholds.
- Use `uv run` for ACT/H3 commands. A system Python installation with a legacy
  `inferactively-pymdp` distribution is outside the supported contract.

## Failure Triage

- If nested belief tests fail, inspect `geo_infer_act.core.generative_model`
  before changing agents or runners.
- If artifact validation fails, inspect `geo_infer_act.runners.scenarios` and
  `geo_infer_act.runners.io` together.
- Re-run `uv run python GEO-INFER-TEST/run_unified_tests.py --h3-migration`
  after changing any H3 or nested spatial inference path.
"""
    if module.name == "GEO-INFER-SPACE":
        return """
## Current Nested H3 Contracts

- `NestedH3Grid` owns H3 parent/child closure, validation, same-resolution
  neighbor maps, and child-to-parent aggregation.
- Build hierarchies with ordered real `h3>=4.5.0,<5` resolutions and
  deterministic cell ordering; do not pass synthetic cell IDs to nested H3
  paths.
- Validate orphan counts, parent/child membership, resolution matches, and
  finite aggregate values before handing hierarchies to ACT.

## Failure Triage

- If hierarchy validation fails, inspect
  `geo_infer_space.nested.core.nested_grid.NestedH3Grid` first.
- If ACT nested contracts fail after SPACE edits, run the SPACE nested unit test
  and then `uv run python GEO-INFER-TEST/validate_h3_active_inference_contract.py`.
"""
    return ""


def render_root_readme(
    modules: dict[str, ModuleInfo], readme_count: int, agents_count: int
) -> str:
    source_files = sum(module.source_files for module in modules.values())
    test_files = sum(module.test_files for module in modules.values())
    module_rows = "\n".join(
        f"| `{module.name}` | `{module.package}` | {module.source_files} | {module.test_files} |"
        for module in modules.values()
    )
    return f"""# GEO-INFER Framework

GEO-INFER is a 44-module geospatial inference monorepo for spatial analysis, active inference, domain modeling, agent workflows, and repository validation.

## Current Repository Facts

| Metric | Value |
| --- | ---: |
| Modules | {len(modules)} |
| Python source files | {source_files} |
| Python test files | {test_files} |
| Tracked README.md files | {readme_count} |
| Tracked AGENTS.md files | {agents_count} |

## Quick Start

```bash
uv sync --all-packages --all-extras
python -m compileall GEO-INFER-*/src GEO-INFER-*/examples
uv run python GEO-INFER-TEST/validate_repo_contracts.py --strict-source-language --skip-import-smoke
uv run python GEO-INFER-TEST/run_unified_tests.py --category unit
```

## Module Index

| Module | Package | Source files | Test files |
| --- | --- | ---: | ---: |
{module_rows}

## Modular Hygiene

- Root `pyproject.toml`, `uv.lock`, and `.python-version` are the canonical uv environment surfaces.
- Sync the full workspace with `uv sync --all-packages --all-extras` before repo-wide validation.
- Each module owns importable behavior under `src/` and keeps at least four pytest files under `tests/`.
- Planned work belongs in root `TODO.md` or a tracked issue, not source or test task markers.
- Importable libraries use `logging.getLogger(__name__)`; process-wide logging configuration belongs in CLI entrypoints.

## Validation

- Repository contracts: `uv run python GEO-INFER-TEST/validate_repo_contracts.py --strict-source-language`
- Syntax gate: `python -m compileall GEO-INFER-*/src GEO-INFER-*/examples`
- Skill contracts: `uv run python GEO-INFER-TEST/validate_skills.py --check-xrefs`
- Unit tests: `uv run python GEO-INFER-TEST/run_unified_tests.py --category unit`
- Integration tests: `uv run python GEO-INFER-TEST/run_unified_tests.py --category integration`
- Performance tests: `uv run python GEO-INFER-TEST/run_unified_tests.py --category performance`
- H3 contracts: `uv run python GEO-INFER-TEST/run_unified_tests.py --h3-migration`
- Test contract: `uv run python GEO-INFER-TEST/validate_test_contracts.py --strict`
- Model contract: `uv run python GEO-INFER-TEST/validate_model_contracts.py --strict --seed 42`
- Reproducible model audit: `uv run python GEO-INFER-TEST/run_model_audit.py --seed 42 --reproducible`

## Zero-warning test policy

The shared pytest policy treats warnings as errors, requires strict markers/configuration, assigns exactly one primary marker to every test, and rejects skips, xfails, xpasses, collection errors, missing dependencies, missing fixtures, and empty selections. Every module has a test inventory at `GEO-INFER-*/tests/README.md`; the inventory records purpose, fixtures, dependencies, artifacts, and triage commands.

## Documentation Policy

README.md and AGENTS.md files describe current, discoverable repository state. Do not add aspirational APIs to these files unless the implementation, export path, and validation command exist in this checkout.
"""


def render_root_agents(modules: dict[str, ModuleInfo]) -> str:
    module_names = ", ".join(f"`{name}`" for name in modules)
    return f"""# GEO-INFER Agent Instructions

Use this file as the repository-level operating contract for automated agents working in GEO-INFER.

## Repository Scope

- Root path: `{REPO_ROOT}`
- Modules: {module_names}
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
uv run python GEO-INFER-TEST/validate_skills.py --check-xrefs
uv run python GEO-INFER-TEST/run_unified_tests.py --category unit
uv run python GEO-INFER-TEST/run_unified_tests.py --category integration
uv run python GEO-INFER-TEST/run_unified_tests.py --category performance
uv run python GEO-INFER-TEST/run_unified_tests.py --h3-migration
uv run python GEO-INFER-TEST/validate_test_contracts.py --strict
uv run python GEO-INFER-TEST/validate_model_contracts.py --strict --seed 42
uv run python GEO-INFER-TEST/run_model_audit.py --seed 42 --reproducible
```

## Modular Hygiene Contract

- Use root `pyproject.toml`, `uv.lock`, and `.python-version` as the shared uv environment contract.
- Sync the shared workspace with `uv sync --all-packages --all-extras`.
- Keep module behavior in the owning `GEO-INFER-*` package under `src/`; keep scripts and examples as orchestration surfaces.
- Keep every module's local test inventory above the minimum release gate of four pytest files.
- Put planned work in root `TODO.md` or a tracked issue; do not leave task markers in module source or tests.
- Use module loggers in libraries and configure handlers only from CLI entrypoints.

## Documentation Contract

Agent-facing documentation must be operational: current paths, commands, package names, public exports, test surfaces, and failure triage. Do not advertise planned APIs in AGENTS.md; use issues, roadmaps, or implementation status files for future work.
"""


def render_readme(path: Path, module: ModuleInfo | None) -> str:
    if path.parent == REPO_ROOT:
        modules = discover_modules()
        readmes, agents = tracked_doc_files()
        return render_root_readme(modules, len(readmes), len(agents))

    rel = path.parent.relative_to(REPO_ROOT)
    dirs, py_files, other_files = direct_contents(path.parent)
    symbols = public_symbols(path.parent)
    title = rel.as_posix()
    content_lines = (
        "\n".join(f"- `{item}`" for item in dirs + py_files + other_files)
        or "- No direct tracked child entries."
    )
    symbol_lines = (
        "\n".join(f"- {symbol}" for symbol in symbols)
        or "- No public Python symbols are defined directly in this directory."
    )
    module_lines = ""
    if module:
        deps = (
            "\n".join(f"- `{dep}`" for dep in module.dependencies)
            or "- Dependencies are declared in `pyproject.toml` or inherited from the workspace."
        )
        install = f"uv pip install -e ./{module.name}"
        module_lines = f"""
## Module Metadata

- Module: `{module.name}`
- Package: `{module.package}`
- Version: `{module.version}`
- Install: `{install}`
- Tests: `{test_command(path, module)}`

## Dependencies

{deps}
"""

    test_inventory = ""
    if module and path.parent.name == "tests":
        test_inventory = f"""
## Strict Test Inventory

- Purpose: validate the `{module.name}` module's current behavior through unit,
  integration, system, and performance test surfaces.
- Primary marker: tests receive exactly one primary marker from their canonical
  directory; additive domain markers remain allowed.
- Required fixtures: local `tests/conftest.py` fixtures and shared
  `geo_infer_test.testing` fixtures for deterministic RNG, filesystem, HTTP,
  SQLite, service, model, and artifact boundaries.
- Dependencies: required test/runtime dependencies are installed by
  `uv sync --all-packages --all-extras`; missing backends are failures.
- Expected artifacts: JUnit XML under `.geo-infer-test-results/`; model and
  visualization outputs require finite statistics, sidecars, hashes, and a
  manifest.
- Failure triage: `env -u VIRTUAL_ENV uv run pytest -c pyproject.toml -q
  {module.name}/tests`, followed by
  `uv run python GEO-INFER-TEST/validate_test_contracts.py --strict`.
"""

    return f"""# {title}

{purpose_for(path, module)}

## Contents

{content_lines}

## Public Interface

{symbol_lines}
{module_lines}
{test_inventory}
## Validation

```bash
{validation_commands(path, module)}
```

{module_readme_notes(path, module)}
## Documentation Notes

This README describes current repository state only. Keep examples and claims tied to importable code, tracked files, or validation commands.
"""


def render_agents(path: Path, module: ModuleInfo | None) -> str:
    if path.parent == REPO_ROOT:
        return render_root_agents(discover_modules())

    rel = path.parent.relative_to(REPO_ROOT)
    dirs, py_files, other_files = direct_contents(path.parent)
    content_lines = (
        "\n".join(f"- `{item}`" for item in dirs + py_files + other_files)
        or "- No direct tracked child entries."
    )
    module_name = module.name if module else "GEO-INFER"
    package = module.package if module else "workspace"
    return f"""# Agent Instructions: {rel.as_posix()}

## Scope

- Owning module: `{module_name}`
- Python package: `{package}`
- Directory role: {purpose_for(path, module)}

## Capabilities

- Maintains the tracked files and subdirectories listed below for this workspace.
- Validates behavior with the command in the Validation section.
- Integrates through `{package}` and the owning module's public contracts.

## Working Rules

- Keep changes scoped to this directory unless an import, test, or documented command requires a coordinated edit.
- Prefer existing module patterns and public exports over new orchestration layers.
- Do not add planned, fake, mock, stub, or placeholder behavior to user-facing docs.
- If external services are involved, keep deterministic local validation available.

## Local Contents

{content_lines}

## Validation

```bash
{validation_commands(path, module)}
```

{module_agent_notes(path, module)}
## Integration Notes

- Update this AGENTS.md and the sibling README.md when commands, exports, dependencies, or generated outputs change.
- Keep cross-module references anchored to real package imports and tracked files.
"""


def expected_doc_files() -> list[tuple[Path, str]]:
    """Return tracked documentation files and their generated contents."""
    modules = discover_modules()
    readmes, agents = tracked_doc_files()
    expected: list[tuple[Path, str]] = []

    for readme in readmes:
        expected.append((readme, render_readme(readme, module_for(readme, modules))))
    for agents_file in agents:
        expected.append(
            (agents_file, render_agents(agents_file, module_for(agents_file, modules)))
        )

    return expected


def check_docs_current() -> list[Path]:
    """Return generated documentation files whose tracked content is stale."""
    stale: list[Path] = []
    for path, expected in expected_doc_files():
        current = path.read_text(encoding="utf-8")
        if current != expected:
            stale.append(path)
    return stale


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="Fail if generated README.md or AGENTS.md files are stale.",
    )
    args = parser.parse_args()

    expected = expected_doc_files()
    if args.check:
        stale = [
            path
            for path, expected_text in expected
            if path.read_text(encoding="utf-8") != expected_text
        ]
        if stale:
            print(
                "Generated documentation is stale. First mismatches: "
                + ", ".join(str(path.relative_to(REPO_ROOT)) for path in stale[:20]),
                file=sys.stderr,
            )
            return 1
        print(f"All {len(expected)} generated README.md/AGENTS.md files are current.")
        return 0

    for path, content in expected:
        path.write_text(content, encoding="utf-8")

    readme_count = sum(1 for path, _ in expected if path.name == "README.md")
    agents_count = sum(1 for path, _ in expected if path.name == "AGENTS.md")
    print(
        f"Rewrote {readme_count} README.md files and "
        f"{agents_count} AGENTS.md files."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

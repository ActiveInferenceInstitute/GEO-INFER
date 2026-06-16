#!/usr/bin/env python3
"""Rewrite tracked README.md and AGENTS.md files from repository facts.

The generated files are intentionally compact and operational. They avoid
roadmap language and only describe the current filesystem, package metadata,
test entry points, and public symbols discoverable from Python source files.
"""

from __future__ import annotations

import ast
import subprocess
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
- H3 contracts: `uv run python GEO-INFER-TEST/run_unified_tests.py --h3-migration`

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
uv run python GEO-INFER-TEST/run_unified_tests.py --h3-migration
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

    return f"""# {title}

{purpose_for(path, module)}

## Contents

{content_lines}

## Public Interface

{symbol_lines}
{module_lines}
## Validation

```bash
{test_command(path, module)}
```

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
{test_command(path, module)}
```

## Integration Notes

- Update this AGENTS.md and the sibling README.md when commands, exports, dependencies, or generated outputs change.
- Keep cross-module references anchored to real package imports and tracked files.
"""


def main() -> int:
    modules = discover_modules()
    readmes, agents = tracked_doc_files()

    for readme in readmes:
        readme.write_text(
            render_readme(readme, module_for(readme, modules)), encoding="utf-8"
        )
    for agents_file in agents:
        agents_file.write_text(
            render_agents(agents_file, module_for(agents_file, modules)),
            encoding="utf-8",
        )

    print(f"Rewrote {len(readmes)} README.md files and {len(agents)} AGENTS.md files.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

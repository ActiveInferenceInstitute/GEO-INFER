#!/usr/bin/env python3
"""Validate the repository-wide strict test contract."""

from __future__ import annotations

import argparse
import ast
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
PRIMARY = {"unit", "integration", "system", "performance"}
BUILTIN_MARKERS = {"parametrize", "asyncio", "benchmark", "timeout", "usefixtures"}
FORBIDDEN_TEXT = (
    "pytest.skip",
    "pytest.mark.skip",
    "skipif",
    "importorskip",
    "skipTest",
    "unittest.skip",
    "pytest.xfail",
    "expectedFailure",
)


def test_files() -> list[Path]:
    """Return all repository test files in stable order."""
    return sorted(ROOT.glob("GEO-INFER-*/tests/**/*.py"))


def configured_markers() -> set[str]:
    """Read marker names declared by the shared and module pyprojects."""
    markers = PRIMARY | BUILTIN_MARKERS
    for config in [ROOT / "pyproject.toml", *ROOT.glob("GEO-INFER-*/pyproject.toml")]:
        text = config.read_text(encoding="utf-8")
        markers.update(re.findall(r'^\s*"([A-Za-z_][\w-]*):', text, re.MULTILINE))
    return markers


def marker_names(tree: ast.AST) -> set[str]:
    """Find pytest marker names used by a test module."""
    names: set[str] = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.Attribute) or node.attr == "mark":
            continue
        parent = node.value
        if isinstance(parent, ast.Attribute) and parent.attr == "mark":
            root = parent.value
            if isinstance(root, ast.Name) and root.id == "pytest":
                names.add(node.attr)
    return names


def forbidden_controls(tree: ast.AST, source: str) -> list[str]:
    """Return source-level skip/xfail controls, including decorator aliases."""
    findings: list[str] = []
    for line_number, line in enumerate(source.splitlines(), 1):
        if any(token in line for token in FORBIDDEN_TEXT):
            findings.append(f"line {line_number}: forbidden test control")
    return findings


def missing_docstrings(tree: ast.Module, path: Path) -> list[str]:
    """Return tests lacking a function, class, or module behavior description."""
    missing: list[str] = []
    module_doc = bool(ast.get_docstring(tree))
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        if not node.name.startswith("test_"):
            continue
        if ast.get_docstring(node) or module_doc:
            continue
        parent_doc = False
        for candidate in ast.walk(tree):
            if isinstance(candidate, ast.ClassDef) and any(
                child is node for child in candidate.body
            ):
                parent_doc = bool(ast.get_docstring(candidate))
                break
        if not parent_doc:
            missing.append(f"{path}:{node.lineno}:{node.name}")
    return missing


def validate(strict: bool) -> list[str]:
    """Return contract violations; strict mode includes documentation checks."""
    errors: list[str] = []
    known = configured_markers()
    for module in sorted(ROOT.glob("GEO-INFER-*")):
        tests = module / "tests"
        if not tests.is_dir():
            errors.append(f"{module.name}: missing tests directory")
            continue
        inventory = tests / "README.md"
        if not inventory.exists():
            errors.append(f"{module.name}: missing tests/README.md inventory")

    for path in test_files():
        if path.name in {"conftest.py", "__init__.py"}:
            continue
        source = path.read_text(encoding="utf-8")
        try:
            tree = ast.parse(source, filename=str(path))
        except SyntaxError as exc:
            errors.append(f"{path}:{exc.lineno}: syntax error: {exc.msg}")
            continue
        errors.extend(
            f"{path}: {finding}" for finding in forbidden_controls(tree, source)
        )
        unknown = marker_names(tree) - known
        errors.extend(f"{path}: unknown marker {name!r}" for name in sorted(unknown))
        if strict:
            errors.extend(missing_docstrings(tree, path))
    return errors


def main() -> int:
    """Run the validator and print actionable findings."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()
    errors = validate(args.strict)
    if errors:
        print("\n".join(errors), file=sys.stderr)
        print(f"test contract failed: {len(errors)} violation(s)", file=sys.stderr)
        return 1
    print(
        "test contract passed: every inventory, marker, control, and docstring check is clean"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

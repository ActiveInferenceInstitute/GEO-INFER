"""Unit tests for repository contract validator helpers."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
CONTRACTS_PATH = REPO_ROOT / "GEO-INFER-TEST" / "validate_repo_contracts.py"


def load_contracts_module():
    spec = importlib.util.spec_from_file_location(
        "geo_infer_validate_repo_contracts", CONTRACTS_PATH
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def write_root_uv_files(root: Path) -> None:
    (root / "pyproject.toml").write_text(
        "\n".join(
            [
                "[project]",
                'requires-python = ">=3.11"',
                "",
                "[tool.uv.workspace]",
                'members = ["GEO-INFER-*"]',
                "",
            ]
        )
    )
    (root / ".python-version").write_text("3.12.11\n")
    (root / "uv.lock").write_text("")


def write_canonical_uv_docs(root: Path, contracts) -> None:
    for relative_path in contracts.CANONICAL_UV_DOC_FILES:
        doc_path = root / relative_path
        doc_path.parent.mkdir(parents=True, exist_ok=True)
        doc_path.write_text(
            f"Setup command: `{contracts.CANONICAL_UV_SYNC_COMMAND}`\n"
        )


def test_uv_environment_contract_accepts_root_workspace(tmp_path, monkeypatch):
    contracts = load_contracts_module()
    monkeypatch.setattr(contracts, "REPO_ROOT", tmp_path)
    write_root_uv_files(tmp_path)
    report = contracts.ContractReport()

    contracts.validate_uv_environment(report)

    assert report.errors == []


def test_uv_environment_contract_rejects_missing_lock(tmp_path, monkeypatch):
    contracts = load_contracts_module()
    monkeypatch.setattr(contracts, "REPO_ROOT", tmp_path)
    write_root_uv_files(tmp_path)
    (tmp_path / "uv.lock").unlink()
    report = contracts.ContractReport()

    contracts.validate_uv_environment(report)

    assert any("uv.lock" in error for error in report.errors)


def test_uv_setup_documentation_requires_workspace_sync_command(tmp_path, monkeypatch):
    contracts = load_contracts_module()
    monkeypatch.setattr(contracts, "REPO_ROOT", tmp_path)
    write_canonical_uv_docs(tmp_path, contracts)
    (tmp_path / "README.md").write_text("Setup command: `uv sync --all-extras`\n")
    report = contracts.ContractReport()

    contracts.validate_uv_setup_documentation(report)

    assert any("README.md" in error for error in report.errors)


def test_uv_setup_documentation_accepts_canonical_sync_command(tmp_path, monkeypatch):
    contracts = load_contracts_module()
    monkeypatch.setattr(contracts, "REPO_ROOT", tmp_path)
    write_canonical_uv_docs(tmp_path, contracts)
    report = contracts.ContractReport()

    contracts.validate_uv_setup_documentation(report)

    assert report.errors == []


def test_test_inventory_contract_requires_minimum_files(tmp_path):
    contracts = load_contracts_module()
    module_dir = tmp_path / "GEO-INFER-SAMPLE"
    tests_dir = module_dir / "tests"
    tests_dir.mkdir(parents=True)
    for index in range(3):
        (tests_dir / f"test_case_{index}.py").write_text("def test_ok():\n    pass\n")
    report = contracts.ContractReport()

    contracts.validate_test_inventory([module_dir], report)

    assert any("expected at least" in error for error in report.errors)


def test_module_task_marker_contract_scans_source_and_tests(tmp_path, monkeypatch):
    contracts = load_contracts_module()
    monkeypatch.setattr(contracts, "REPO_ROOT", tmp_path)
    src_dir = tmp_path / "GEO-INFER-SAMPLE" / "src" / "geo_infer_sample"
    tests_dir = tmp_path / "GEO-INFER-SAMPLE" / "tests"
    src_dir.mkdir(parents=True)
    tests_dir.mkdir(parents=True)
    marker = "TO" + "DO"
    (src_dir / "module.py").write_text(f"# {marker}: route work through tracker\n")
    (tests_dir / "test_module.py").write_text(
        f"def test_marker():\n    value = '{marker}'\n    assert value\n"
    )
    report = contracts.ContractReport()

    contracts.validate_module_task_markers(report)

    errors = "\n".join(report.errors)
    assert "module.py" in errors
    assert "test_module.py" in errors


def test_logging_contract_rejects_library_basic_config(tmp_path, monkeypatch):
    contracts = load_contracts_module()
    monkeypatch.setattr(contracts, "REPO_ROOT", tmp_path)
    src_dir = tmp_path / "GEO-INFER-SAMPLE" / "src" / "geo_infer_sample"
    src_dir.mkdir(parents=True)
    (src_dir / "library.py").write_text(
        "import logging\nlogging.basicConfig(level=logging.INFO)\n"
    )
    (src_dir / "cli.py").write_text(
        "import logging\n"
        "if __name__ == '__main__':\n"
        "    logging.basicConfig(level=logging.INFO)\n"
    )
    report = contracts.ContractReport()

    contracts.validate_logging_configuration(report)

    errors = "\n".join(report.errors)
    assert "library.py" in errors
    assert "cli.py" not in errors

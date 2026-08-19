"""Unit tests for repository contract validator helpers."""

from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
CONTRACTS_PATH = REPO_ROOT / "GEO-INFER-TEST" / "validate_repo_contracts.py"
REWRITER_PATH = REPO_ROOT / "GEO-INFER-TEST" / "rewrite_readme_agents.py"


def load_contracts_module():
    spec = importlib.util.spec_from_file_location(
        "geo_infer_validate_repo_contracts", CONTRACTS_PATH
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def load_rewriter_module():
    spec = importlib.util.spec_from_file_location(
        "geo_infer_rewrite_readme_agents_for_test", REWRITER_PATH
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_signpost_inventory_includes_new_files_and_excludes_deletions(
    tmp_path, monkeypatch
):
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
    tracked = tmp_path / "tracked.py"
    tracked.write_text("tracked = True\n")
    subprocess.run(["git", "add", "tracked.py"], cwd=tmp_path, check=True)
    tracked.unlink()

    added = tmp_path / "added.py"
    added.write_text("added = True\n")
    (tmp_path / ".gitignore").write_text("ignored.py\n")
    (tmp_path / "ignored.py").write_text("ignored = True\n")

    rewriter = load_rewriter_module()
    monkeypatch.setattr(rewriter, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(rewriter, "_TRACKED_FILES", None)

    inventory = rewriter.tracked_files()
    assert added in inventory
    assert tracked not in inventory
    assert tmp_path / "ignored.py" not in inventory


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
        doc_path.write_text(f"Setup command: `{contracts.CANONICAL_UV_SYNC_COMMAND}`\n")


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


def test_python_source_syntax_contract_rejects_invalid_module_source(
    tmp_path, monkeypatch
):
    contracts = load_contracts_module()
    monkeypatch.setattr(contracts, "REPO_ROOT", tmp_path)
    src_dir = tmp_path / "GEO-INFER-SAMPLE" / "src" / "geo_infer_sample"
    examples_dir = tmp_path / "GEO-INFER-SAMPLE" / "examples"
    src_dir.mkdir(parents=True)
    examples_dir.mkdir(parents=True)
    (src_dir / "valid.py").write_text("VALUE = 1\n")
    (examples_dir / "broken.py").write_text("def broken(:\n    pass\n")
    report = contracts.ContractReport()

    contracts.validate_python_source_syntax(report)

    errors = "\n".join(report.errors)
    assert "GEO-INFER-SAMPLE/examples/broken.py" in errors
    assert "invalid syntax" in errors


def test_concrete_pass_contract_rejects_non_abstract_source_pass(tmp_path, monkeypatch):
    contracts = load_contracts_module()
    monkeypatch.setattr(contracts, "REPO_ROOT", tmp_path)
    src_dir = tmp_path / "GEO-INFER-SAMPLE" / "src" / "geo_infer_sample"
    src_dir.mkdir(parents=True)
    (src_dir / "module.py").write_text("def real_behavior():\n    pass\n")
    report = contracts.ContractReport()

    contracts.validate_no_concrete_pass_bodies(report)

    errors = "\n".join(report.errors)
    assert "module.py:2" in errors
    assert "Concrete pass bodies" in errors


def test_concrete_pass_contract_allows_abstract_methods_and_except_handlers(
    tmp_path, monkeypatch
):
    contracts = load_contracts_module()
    monkeypatch.setattr(contracts, "REPO_ROOT", tmp_path)
    src_dir = tmp_path / "GEO-INFER-SAMPLE" / "src" / "geo_infer_sample"
    src_dir.mkdir(parents=True)
    (src_dir / "module.py").write_text(
        "from abc import abstractmethod\n\n"
        "class Base:\n"
        "    @abstractmethod\n"
        "    def run(self):\n"
        "        pass\n\n"
        "def cleanup(value):\n"
        "    try:\n"
        "        return int(value)\n"
        "    except ValueError:\n"
        "        pass\n"
        "    return None\n"
    )
    report = contracts.ContractReport()

    contracts.validate_no_concrete_pass_bodies(report)

    assert report.errors == []


def test_python_tool_targets_reject_black_targets_below_python_311(
    tmp_path, monkeypatch
):
    contracts = load_contracts_module()
    monkeypatch.setattr(contracts, "REPO_ROOT", tmp_path)
    (tmp_path / "pyproject.toml").write_text(
        "[tool.black]\ntarget-version = ['py310', 'py311']\n"
    )
    report = contracts.ContractReport()

    contracts.validate_python_tool_targets(report)

    assert any("py310" in error for error in report.errors)


def test_h3_dependency_metadata_rejects_old_h3_v4_floor(tmp_path, monkeypatch):
    contracts = load_contracts_module()
    monkeypatch.setattr(contracts, "REPO_ROOT", tmp_path)
    module_dir = tmp_path / "GEO-INFER-SAMPLE"
    module_dir.mkdir()
    (module_dir / "pyproject.toml").write_text(
        "[project]\ndependencies = ['h3>=4.0.0']\n"
    )
    report = contracts.ContractReport()

    contracts.validate_h3_dependency_metadata(report)

    assert any("h3>=4.5.0,<5" in error for error in report.errors)


def test_generated_doc_freshness_rejects_stale_rendered_docs(tmp_path, monkeypatch):
    contracts = load_contracts_module()
    monkeypatch.setattr(contracts, "REPO_ROOT", tmp_path)
    readme = tmp_path / "README.md"
    readme.write_text("stale\n")

    class FakeRewriter:
        @staticmethod
        def expected_doc_files():
            return [(readme, "fresh\n")]

    report = contracts.ContractReport()

    contracts.validate_generated_doc_freshness(report, rewriter=FakeRewriter)

    assert any(
        "README.md/AGENTS.md files are stale" in error for error in report.errors
    )


def test_generated_artifact_contract_checks_root_test_output(tmp_path, monkeypatch):
    contracts = load_contracts_module()
    monkeypatch.setattr(contracts, "REPO_ROOT", tmp_path)

    class FakeCompleted:
        stdout = "?? test_output/\n"

    def fake_run(*args, **kwargs):
        return FakeCompleted()

    monkeypatch.setattr(contracts.subprocess, "run", fake_run)
    report = contracts.ContractReport()

    contracts.validate_generated_artifacts(report)

    assert any("test_output" in error for error in report.errors)


def test_pymdp_runtime_import_contract_rejects_legacy_runtime_paths(
    tmp_path, monkeypatch
):
    contracts = load_contracts_module()
    monkeypatch.setattr(contracts, "REPO_ROOT", tmp_path)
    act_src = tmp_path / "GEO-INFER-ACT" / "src" / "geo_infer_act"
    tests_dir = tmp_path / "GEO-INFER-ACT" / "tests"
    act_src.mkdir(parents=True)
    tests_dir.mkdir(parents=True)
    (act_src / "runtime.py").write_text(
        "from pymdp.control import construct_policies\n"
    )
    (tests_dir / "test_legacy_note.py").write_text("LEGACY = 'pymdp.control'\n")
    report = contracts.ContractReport()

    contracts.validate_pymdp_runtime_imports(report)

    errors = "\n".join(report.errors)
    assert "runtime.py" in errors
    assert "test_legacy_note.py" not in errors

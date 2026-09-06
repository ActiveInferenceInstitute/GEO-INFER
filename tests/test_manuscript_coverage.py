"""Tests that the generated surfaces cover the module set and the evidence set."""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path
from types import ModuleType

import pytest


class TestModuleTable:
    """Every measured module must reach the manuscript with a described surface."""

    def test_every_module_has_exactly_one_row(
        self, generator: ModuleType, repo_inventory
    ) -> None:
        table = generator._module_table(repo_inventory)
        rows = table.splitlines()[2:]
        assert len(rows) == repo_inventory.module_count
        named = re.findall(r"\| `(GEO-INFER-[A-Z0-9]+)` \|", table)
        assert sorted(named) == sorted(
            module.name for module in repo_inventory.modules
        )

    def test_rows_carry_the_measured_counts(
        self, generator: ModuleType, repo_inventory
    ) -> None:
        table = generator._module_table(repo_inventory)
        for module in repo_inventory.modules:
            expected = (
                f"| `{module.name}` | `{module.package}` | "
                f"{module.source_files} | {module.test_files} |"
            )
            assert expected in table

    def test_an_unthemed_module_fails_the_build(
        self, generator: ModuleType, repo_inventory
    ) -> None:
        import dataclasses

        extra = dataclasses.replace(
            repo_inventory.modules[0],
            name="GEO-INFER-NOTATHEME",
            package="geo_infer_notatheme",
        )
        broken = dataclasses.replace(
            repo_inventory, modules=(*repo_inventory.modules, extra)
        )
        with pytest.raises(ValueError, match="no declared theme"):
            generator._module_table(broken)

    def test_a_theme_naming_an_absent_module_fails_the_build(
        self, generator: ModuleType, repo_inventory
    ) -> None:
        import dataclasses

        broken = dataclasses.replace(
            repo_inventory, modules=repo_inventory.modules[:-1]
        )
        with pytest.raises(ValueError, match="absent from the checkout"):
            generator._module_table(broken)

    def test_the_token_is_published(
        self, generator: ModuleType, repo_inventory
    ) -> None:
        variables = generator.build_variables(
            repo_inventory,
            (
                generator.FigureSpec(
                    label="fig:example",
                    filename="example.png",
                    caption="Example caption.",
                    generated_by="tests",
                    alt_text="Example alt text.",
                    sha256="0" * 64,
                ),
            ),
            (),
            full_validation=False,
        )
        assert variables["MODULE_TABLE"] == generator._module_table(repo_inventory)
        assert variables["MODULE_THEME_COUNT"] == str(len(generator.MODULE_THEMES))


class TestPublicationGate:
    """A publication build may not ship an empty evidence record."""

    def test_publication_requires_verification_to_be_requested(
        self, generator: ModuleType, git_repo: Path
    ) -> None:
        with pytest.raises(RuntimeError, match="must execute its verification"):
            generator.generate(git_repo, verify=False, publication=True)

    def test_publication_names_the_defined_group_count(
        self, generator: ModuleType
    ) -> None:
        assert generator.defined_command_groups(full_validation=False) == tuple(
            name for name, _command in generator.VERIFICATION_COMMANDS
        )
        assert len(generator.defined_command_groups(full_validation=True)) == len(
            generator.VERIFICATION_COMMANDS
        ) + len(generator.FULL_VALIDATION_COMMANDS)


class TestRenderHydrationShim:
    """The template hydrates through ``scripts/z_generate_manuscript_variables.py``."""

    def test_the_shim_exists_at_the_path_the_template_looks_for(
        self, repo_root: Path
    ) -> None:
        # infrastructure/rendering/_manuscript_source.py resolves exactly this
        # path and silently returns 0 when it is absent.
        shim = repo_root / "scripts" / "z_generate_manuscript_variables.py"
        assert shim.is_file()

    def test_the_shim_regenerates_and_then_verifies(
        self, generator: ModuleType, repo_root: Path
    ) -> None:
        # This test runs the real shim against the real checkout, so it writes
        # the shipped output/ tree as a side effect.  That is how the last
        # verifier destroyed the evidence bundle by accident: on a tree with
        # any uncommitted entry the shim used to republish an empty record and
        # still exit 0.  The before/after count below is the guard, and it is
        # the reason this test can be run without losing a measurement.
        record = generator._verification_record_path(repo_root)
        before = json.loads(record.read_text(encoding="utf-8"))["results"]
        completed = subprocess.run(
            [sys.executable, "scripts/z_generate_manuscript_variables.py"],
            cwd=repo_root,
            capture_output=True,
            text=True,
            check=False,
        )
        assert completed.returncode == 0, completed.stderr
        assert "hydrated" in completed.stdout
        variables = repo_root / "output" / "data" / "manuscript_variables.json"
        assert variables.is_file()
        after = json.loads(record.read_text(encoding="utf-8"))["results"]
        assert [entry["name"] for entry in after] == [
            entry["name"] for entry in before
        ], "the shim discarded executed-command evidence it did not re-measure"

    def test_a_stale_tree_is_reported_after_hydration(
        self, generator: ModuleType, repo_root: Path
    ) -> None:
        # The shim's post-condition is check_published_artifacts, which is the
        # comparison that never existed: source hash measured against published.
        assert generator.check_published_artifacts(repo_root) == ()

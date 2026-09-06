"""Tests that the generated surfaces cover the module set and the evidence set."""

from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
from pathlib import Path
from types import ModuleType
from typing import Iterator

import pytest


def _figure_specs(generator: ModuleType):
    """A minimal, valid figure-spec tuple for variable-building tests."""
    return (
        generator.FigureSpec(
            label="fig:example",
            filename="example.png",
            caption="Example caption.",
            generated_by="tests",
            alt_text="Example alt text.",
        ),
    )


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
            generator.VerificationRecord.unmeasured(),
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


class TestPublishedCountsPartitionTheDefinition:
    """The published denominator is the record's own, and the counts fill it.

    The abstract shipped "Of the 7 verification command groups this build
    defines, 9 passed, 2 failed, and 0 did not run" beside an eleven-row
    table.  Nothing tied the numerator to the denominator: the passes and
    failures were counted over the whole record while the defined and unrun
    counts were scoped to the tier the build happened to request.  Both
    halves are now read from the record, and the sum is checked.
    """

    @staticmethod
    def _results(generator: ModuleType, names, status: str = "passed"):
        return tuple(
            generator.VerificationResult(
                name=name,
                command="x",
                status=status,
                return_code=0 if status == "passed" else 1,
                duration_seconds=0.0,
                output_tail="",
            )
            for name in names
        )

    def test_a_full_record_publishes_the_full_denominator(
        self, generator: ModuleType, repo_inventory
    ) -> None:
        names = generator.defined_command_groups(full_validation=True)
        record = generator.VerificationRecord(
            results=self._results(generator, names),
            source_commit="abc1234",
            source_hash="0" * 16,
            full_validation_requested=True,
        )
        variables = generator.build_variables(
            repo_inventory, _figure_specs(generator), record
        )
        assert variables["VERIFICATION_DEFINED_COUNT"] == str(len(names))
        assert variables["VERIFICATION_PASS_COUNT"] == str(len(names))
        assert variables["VERIFICATION_UNRUN_COUNT"] == "0"
        assert variables["VERIFICATION_RECORD_TIER"] == "full-validation"

    def test_the_counts_always_partition_the_denominator(
        self, generator: ModuleType, repo_inventory
    ) -> None:
        for full_validation in (False, True):
            names = generator.defined_command_groups(
                full_validation=full_validation
            )
            record = generator.VerificationRecord(
                results=self._results(generator, names[:1], status="failed"),
                source_commit="abc1234",
                source_hash="0" * 16,
                full_validation_requested=full_validation,
            )
            variables = generator.build_variables(
                repo_inventory, _figure_specs(generator), record
            )
            total = sum(
                int(variables[f"VERIFICATION_{key}_COUNT"])
                for key in ("PASS", "FAIL", "UNRUN")
            )
            assert total == int(variables["VERIFICATION_DEFINED_COUNT"]) == len(
                names
            )

    def test_a_record_wider_than_its_tier_fails_the_build(
        self, generator: ModuleType, repo_inventory
    ) -> None:
        # The exact shipped state: eleven measured results carrying the
        # default tier's seven-group denominator.  It used to render.
        record = generator.VerificationRecord(
            results=self._results(
                generator, generator.defined_command_groups(full_validation=True)
            ),
            source_commit="abc1234",
            source_hash="0" * 16,
            full_validation_requested=False,
        )
        with pytest.raises(ValueError, match="must partition the defined"):
            generator.build_variables(
                repo_inventory, _figure_specs(generator), record
            )

    def test_a_group_no_tier_defines_fails_the_build(
        self, generator: ModuleType, repo_inventory
    ) -> None:
        record = generator.VerificationRecord(
            results=self._results(generator, ("retired-group",)),
            source_commit="abc1234",
            source_hash="0" * 16,
            full_validation_requested=False,
        )
        with pytest.raises(ValueError, match="must partition the defined"):
            generator.build_variables(
                repo_inventory, _figure_specs(generator), record
            )


class TestHydrationTierSelection:
    """The shim's tier flag requests commands; it never picks a denominator."""

    @staticmethod
    def _shim(repo_root: Path) -> ModuleType:
        import importlib.util

        path = repo_root / "scripts" / "z_generate_manuscript_variables.py"
        spec = importlib.util.spec_from_file_location("_shim_under_test", path)
        assert spec is not None and spec.loader is not None
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def test_the_tier_flag_requests_no_run_of_its_own(
        self, repo_root: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        # Asking for the wider tier must not ask the renderer to execute
        # eleven suites inside its 300-second bounded hydration timeout.
        shim = self._shim(repo_root)
        monkeypatch.setenv(shim.FULL_VALIDATION_ENV, "1")
        monkeypatch.delenv(shim.VERIFY_ENV, raising=False)
        monkeypatch.delenv(shim.PUBLICATION_ENV, raising=False)
        assert shim._full_validation_requested() is True
        assert shim._verify_requested() is False
        assert shim._publication_requested() is False

    def test_a_publication_build_still_implies_the_full_tier(
        self, repo_root: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        shim = self._shim(repo_root)
        monkeypatch.delenv(shim.FULL_VALIDATION_ENV, raising=False)
        monkeypatch.setenv(shim.PUBLICATION_ENV, "1")
        assert shim._full_validation_requested() is True
        assert shim._verify_requested() is True


def _variables(root: Path) -> dict:
    return json.loads(
        (root / "output" / "data" / "manuscript_variables.json").read_text(
            encoding="utf-8"
        )
    )


def _git(repo_root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(repo_root), *args],
        capture_output=True,
        text=True,
        check=False,
    )


def _mirror_working_tree(repo_root: Path, copy: Path) -> None:
    """Bring a worktree of ``HEAD`` up to the working tree's actual content.

    ``git worktree add HEAD`` materialises the last commit, which is not what
    a developer is running.  A test that exercised ``HEAD`` would report on
    code the author has not written yet and pass over the change under test.
    Applying the working tree's own additions, modifications, and deletions
    on top makes the copy equal to what an invocation in ``repo_root`` would
    see, minus the ignored trees the generator does not read.
    """
    deleted = _git(repo_root, "diff", "--name-only", "--diff-filter=D", "HEAD")
    for name in deleted.stdout.split():
        target = copy / name
        if target.is_file():
            target.unlink()
    changed = _git(repo_root, "diff", "--name-only", "--diff-filter=d", "HEAD")
    untracked = _git(repo_root, "ls-files", "--others", "--exclude-standard")
    for name in (*changed.stdout.split(), *untracked.stdout.split()):
        source = repo_root / name
        if not source.is_file():
            continue
        target = copy / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)


@pytest.fixture(scope="module")
def shim_checkout(
    repo_root: Path, tmp_path_factory: pytest.TempPathFactory
) -> Iterator[Path]:
    """A throwaway checkout carrying a copy of the published bundle.

    The shim writes ``output/``.  Running it against the real checkout made
    the test suite rewrite the shipped artifact tree — twice observed
    replacing the eleven-result bundle with a seven-result one, which the
    following assertion then certified as current.  A test may not be the
    thing that changes what the repository ships, so the shim runs here
    against a worktree mirroring the developer's tree, with ``output/``
    copied in because it is gitignored and a worktree does not carry it.
    """
    copy = tmp_path_factory.mktemp("shim") / "checkout"
    add = _git(repo_root, "worktree", "add", "--detach", str(copy), "HEAD")
    if add.returncode != 0:  # pragma: no cover - environment without git
        pytest.skip(f"git worktree add failed: {add.stderr.strip()}")
    try:
        _mirror_working_tree(repo_root, copy)
        shutil.copytree(repo_root / "output", copy / "output")
        yield copy
    finally:
        subprocess.run(
            ["git", "-C", str(repo_root), "worktree", "remove", "--force",
             str(copy)],
            capture_output=True,
            check=False,
        )


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
        self, generator: ModuleType, shim_checkout: Path
    ) -> None:
        # On a tree with any uncommitted entry the shim used to republish an
        # empty record and still exit 0.  The before/after comparison below is
        # the guard.  It compares the published counts as well as the result
        # names, because a name-only guard cannot see a tier change: the run
        # that flipped the shipped bundle from eleven groups to seven kept
        # every name it re-measured and passed.
        record = generator._verification_record_path(shim_checkout)
        before = json.loads(record.read_text(encoding="utf-8"))["results"]
        before_variables = _variables(shim_checkout)
        completed = subprocess.run(
            [sys.executable, "scripts/z_generate_manuscript_variables.py"],
            cwd=shim_checkout,
            capture_output=True,
            text=True,
            check=False,
        )
        assert completed.returncode == 0, completed.stderr
        assert "hydrated" in completed.stdout
        after = json.loads(record.read_text(encoding="utf-8"))["results"]
        assert [entry["name"] for entry in after] == [
            entry["name"] for entry in before
        ], "the shim discarded executed-command evidence it did not re-measure"
        after_variables = _variables(shim_checkout)
        for key in (
            "VERIFICATION_DEFINED_COUNT",
            "VERIFICATION_PASS_COUNT",
            "VERIFICATION_FAIL_COUNT",
            "VERIFICATION_UNRUN_COUNT",
            "VERIFICATION_RECORD_TIER",
        ):
            assert after_variables[key] == before_variables[key], (
                f"the shim republished the record under a different {key}"
            )

    def test_a_stale_tree_is_reported_after_hydration(
        self, generator: ModuleType, shim_checkout: Path
    ) -> None:
        # The shim's post-condition is check_published_artifacts, which is the
        # comparison that never existed: source hash measured against
        # published, and published counts against the record they summarise.
        completed = subprocess.run(
            [sys.executable, "scripts/z_generate_manuscript_variables.py"],
            cwd=shim_checkout,
            capture_output=True,
            text=True,
            check=False,
        )
        assert completed.returncode == 0, completed.stderr
        assert generator.check_published_artifacts(shim_checkout) == ()

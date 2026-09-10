"""Provenance regression tests for the manuscript generator.

Every assertion here pins a published claim to a measurement.  The two
regressions that motivated the suite were both constants standing in for
measurements: a clean short SHA stamped onto a dirty checkout, and a literal
``1`` published as the count of verification groups that did not run.
"""

from __future__ import annotations

from pathlib import Path
from types import ModuleType

import pytest


class TestVerificationUnrunCount:
    """``VERIFICATION_UNRUN_COUNT`` must count defined-but-unrun groups."""

    def test_empty_record_reports_every_defined_group(
        self, generator: ModuleType
    ) -> None:
        _summary, passed, failed, unrun = generator._verification_summary(
            [], full_validation=False
        )
        assert (passed, failed) == (0, 0)
        assert unrun == len(generator.VERIFICATION_COMMANDS)
        # The regression: the empty branch used to return the literal 1.
        assert unrun != 1 or len(generator.VERIFICATION_COMMANDS) == 1

    def test_empty_record_includes_full_validation_groups(
        self, generator: ModuleType
    ) -> None:
        _summary, _passed, _failed, unrun = generator._verification_summary(
            [], full_validation=True
        )
        assert unrun == len(generator.VERIFICATION_COMMANDS) + len(
            generator.FULL_VALIDATION_COMMANDS
        )

    def test_complete_record_reports_no_unrun_group(
        self, generator: ModuleType
    ) -> None:
        results = [
            generator.VerificationResult(
                name=name,
                command=command,
                status="passed",
                return_code=0,
                duration_seconds=0.1,
                output_tail="",
            )
            for name, command in generator.VERIFICATION_COMMANDS
        ]
        summary, passed, failed, unrun = generator._verification_summary(
            results, full_validation=False
        )
        assert (passed, failed, unrun) == (len(results), 0, 0)
        assert summary == f"{len(results)} passed"

    def test_partial_record_reports_the_missing_groups(
        self, generator: ModuleType
    ) -> None:
        name, command = generator.VERIFICATION_COMMANDS[0]
        results = [
            generator.VerificationResult(
                name=name,
                command=command,
                status="passed",
                return_code=0,
                duration_seconds=0.1,
                output_tail="",
            )
        ]
        _summary, _passed, _failed, unrun = generator._verification_summary(
            results, full_validation=False
        )
        assert unrun == len(generator.VERIFICATION_COMMANDS) - 1

    def test_published_token_matches_the_summary(
        self, generator: ModuleType, repo_inventory, figure_specs
    ) -> None:
        variables = generator.build_variables(
            repo_inventory,
            figure_specs,
            generator.VerificationRecord.unmeasured(),
        )
        assert variables["VERIFICATION_UNRUN_COUNT"] == str(
            len(generator.VERIFICATION_COMMANDS)
        )
        assert variables["VERIFICATION_DEFINED_COUNT"] == str(
            len(generator.VERIFICATION_COMMANDS)
        )
        assert variables["VERIFICATION_STATUS"] == "not run"


class TestWorkingTreeProvenance:
    """A dirty checkout must never be stamped with a clean commit SHA."""

    def test_clean_tree_counts_zero(
        self, generator: ModuleType, git_repo: Path
    ) -> None:
        assert generator._dirty_file_count(git_repo) == 0

    def test_modified_and_untracked_entries_are_counted(
        self, generator: ModuleType, git_repo: Path
    ) -> None:
        (git_repo / "seed.txt").write_text("changed\n", encoding="utf-8")
        (git_repo / "extra.txt").write_text("new\n", encoding="utf-8")
        assert generator._dirty_file_count(git_repo) == 2

    def test_missing_git_reports_unavailable_not_clean(
        self, generator: ModuleType, tmp_path: Path
    ) -> None:
        not_a_repo = tmp_path / "plain"
        not_a_repo.mkdir()
        assert generator._dirty_file_count(not_a_repo) == -1

    @pytest.mark.parametrize(
        ("count", "expected"),
        [(0, ""), (1, "-dirty"), (92, "-dirty"), (-1, "-unverified")],
    )
    def test_commit_marker_describes_the_tree(
        self, generator: ModuleType, count: int, expected: str
    ) -> None:
        assert generator._dirty_marker(count) == expected

    def test_dirty_tree_marks_the_commit_and_publishes_the_count(
        self, generator: ModuleType, git_repo: Path
    ) -> None:
        (git_repo / "extra.txt").write_text("new\n", encoding="utf-8")
        inventory = generator.collect_inventory(git_repo)
        assert inventory.dirty_file_count == 1
        assert inventory.commit.endswith("-dirty")

    def test_generate_refuses_a_dirty_checkout(
        self, generator: ModuleType, git_repo: Path
    ) -> None:
        (git_repo / "extra.txt").write_text("new\n", encoding="utf-8")
        with pytest.raises(RuntimeError, match="unclean checkout"):
            generator.generate(git_repo)

    def test_the_real_checkout_publishes_its_own_dirty_count(
        self, generator: ModuleType, repo_inventory, figure_specs
    ) -> None:
        variables = generator.build_variables(
            repo_inventory,
            figure_specs,
            generator.VerificationRecord.unmeasured(),
        )
        published = variables["RESEARCH_TREE_DIRTY_FILE_COUNT"]
        if repo_inventory.dirty_file_count < 0:
            assert published == "unavailable"
        else:
            assert published == str(repo_inventory.dirty_file_count)
        assert inventory_commit_is_marked(repo_inventory)


def inventory_commit_is_marked(inventory) -> bool:
    """The commit stamp and the dirty count must agree."""
    if inventory.dirty_file_count > 0:
        return inventory.commit.endswith("-dirty")
    if inventory.dirty_file_count < 0:
        return inventory.commit.endswith("-unverified")
    return not inventory.commit.endswith(("-dirty", "-unverified"))

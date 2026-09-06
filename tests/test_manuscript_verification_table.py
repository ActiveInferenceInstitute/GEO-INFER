"""Regression tests for the published per-group verification table.

Before this table existed the manuscript described its verification record in
prose and left the per-command outcomes inside a JSON file no reader of the PDF
opens, and ``generate`` aborted on the first failing group — which made the
``N passed, M failed`` summary branch unreachable.  These tests pin both: every
defined group gets a row, and a failed group is published rather than fatal.
"""

from __future__ import annotations

from pathlib import Path
from types import ModuleType


def _result(generator: ModuleType, name: str, status: str, code: int):
    return generator.VerificationResult(
        name=name,
        command=f"run {name}",
        status=status,
        return_code=code,
        duration_seconds=1.5,
        output_tail="",
    )


class TestVerificationTable:
    """Every defined command group appears, run or not."""

    def test_empty_record_prints_every_defined_group_as_not_run(
        self, generator: ModuleType
    ) -> None:
        table = generator._verification_table([], full_validation=False)
        rows = [line for line in table.splitlines() if line.startswith("| `")]
        assert len(rows) == len(generator.VERIFICATION_COMMANDS)
        assert all("not run" in row for row in rows)
        for name, _command in generator.VERIFICATION_COMMANDS:
            assert f"| `{name}` |" in table

    def test_full_validation_adds_the_second_tier(
        self, generator: ModuleType
    ) -> None:
        table = generator._verification_table([], full_validation=True)
        rows = [line for line in table.splitlines() if line.startswith("| `")]
        assert len(rows) == len(generator.VERIFICATION_COMMANDS) + len(
            generator.FULL_VALIDATION_COMMANDS
        )

    def test_a_failed_group_publishes_its_return_code(
        self, generator: ModuleType
    ) -> None:
        name = generator.VERIFICATION_COMMANDS[0][0]
        table = generator._verification_table(
            [_result(generator, name, "failed", 1)], full_validation=False
        )
        row = next(line for line in table.splitlines() if line.startswith(f"| `{name}`"))
        assert "failed" in row
        assert "| 1 |" in row

    def test_table_reaches_the_manuscript_as_a_token(
        self, generator: ModuleType, repo_root
    ) -> None:
        source = Path(generator.__file__ or "").read_text(encoding="utf-8")
        assert '"VERIFICATION_TABLE": _verification_table(' in source
        authored = (
            repo_root / "manuscript" / "04_artifacts_and_evidence.md"
        ).read_text(encoding="utf-8")
        assert "{{VERIFICATION_TABLE}}" in authored


class TestFailureIsPublishedNotFatal:
    """A failed group must reach the summary, not abort the build."""

    def test_summary_reports_mixed_outcomes(self, generator: ModuleType) -> None:
        names = [name for name, _ in generator.VERIFICATION_COMMANDS]
        results = [
            _result(generator, names[0], "passed", 0),
            _result(generator, names[1], "failed", 1),
        ]
        summary, passed, failed, unrun = generator._verification_summary(
            results, full_validation=False
        )
        assert (passed, failed) == (1, 1)
        assert summary == "1 passed, 1 failed"
        assert unrun == len(names) - 2

    def test_generate_only_refuses_failures_in_publication_mode(
        self, generator: ModuleType
    ) -> None:
        source = Path(generator.__file__ or "").read_text(encoding="utf-8")
        assert "if publication and failed_groups:" in source
        assert "research verification failed: " not in source


class TestVerificationRecordReuse:
    """A stored record is reused only when it still describes the tree."""

    def _write(self, generator: ModuleType, root, payload) -> None:
        data = root / "output" / "data"
        data.mkdir(parents=True, exist_ok=True)
        (data / "research_verification.json").write_text(
            __import__("json").dumps(payload), encoding="utf-8"
        )

    def test_missing_record_is_not_reused(
        self, generator: ModuleType, tmp_path, repo_inventory
    ) -> None:
        assert (
            generator.load_matching_verification(
                tmp_path, repo_inventory, full_validation=False
            )
            is None
        )

    def test_matching_record_is_reused(
        self, generator: ModuleType, tmp_path, repo_inventory
    ) -> None:
        name = generator.VERIFICATION_COMMANDS[0][0]
        self._write(
            generator,
            tmp_path,
            {
                "schema_version": generator.RESEARCH_SCHEMA,
                "full_validation_requested": False,
                "source_commit": repo_inventory.commit,
                "source_hash": repo_inventory.source_hash,
                "results": [
                    {
                        "name": name,
                        "command": "run it",
                        "status": "passed",
                        "return_code": 0,
                        "duration_seconds": 1.0,
                        "output_tail": "",
                    }
                ],
            },
        )
        reused = generator.load_matching_verification(
            tmp_path, repo_inventory, full_validation=False
        )
        assert reused is not None
        assert [result.name for result in reused] == [name]

    def test_a_different_source_hash_is_not_reused(
        self, generator: ModuleType, tmp_path, repo_inventory
    ) -> None:
        self._write(
            generator,
            tmp_path,
            {
                "schema_version": generator.RESEARCH_SCHEMA,
                "full_validation_requested": False,
                "source_commit": repo_inventory.commit,
                "source_hash": "0" * 16,
                "results": [
                    {
                        "name": "compile",
                        "command": "run it",
                        "status": "passed",
                        "return_code": 0,
                        "duration_seconds": 1.0,
                        "output_tail": "",
                    }
                ],
            },
        )
        assert (
            generator.load_matching_verification(
                tmp_path, repo_inventory, full_validation=False
            )
            is None
        )

    def test_an_empty_record_is_not_reused(
        self, generator: ModuleType, tmp_path, repo_inventory
    ) -> None:
        self._write(
            generator,
            tmp_path,
            {
                "schema_version": generator.RESEARCH_SCHEMA,
                "full_validation_requested": False,
                "source_commit": repo_inventory.commit,
                "source_hash": repo_inventory.source_hash,
                "results": [],
            },
        )
        assert (
            generator.load_matching_verification(
                tmp_path, repo_inventory, full_validation=False
            )
            is None
        )

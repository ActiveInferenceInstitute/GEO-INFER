"""Regression tests for the published per-group verification table.

Before this table existed the manuscript described its verification record in
prose and left the per-command outcomes inside a JSON file no reader of the PDF
opens, and ``generate`` aborted on the first failing group — which made the
``N passed, M failed`` summary branch unreachable.  These tests pin both: every
defined group gets a row, and a failed group is published rather than fatal.
"""

from __future__ import annotations

import dataclasses
import json
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


class TestVerificationResolutionTier:
    """A build that measures nothing must not discard a record that stands.

    The reuse lookup used to sit inside ``if verify:``.  Every default render —
    the only render the supported pipeline performs — therefore replaced a
    measured record with an empty one and republished ``not run``.  These tests
    drive the decision seam itself rather than asserting on source text.
    """

    def _store(self, generator: ModuleType, root: Path, inventory, results) -> None:
        data = root / "output" / "data"
        data.mkdir(parents=True, exist_ok=True)
        record = generator.VerificationRecord(
            results=tuple(results),
            source_commit=inventory.commit,
            source_hash=inventory.source_hash,
            full_validation_requested=False,
        )
        (data / "research_verification.json").write_text(
            json.dumps(generator._verification_payload(record)), encoding="utf-8"
        )

    def _result(self, generator: ModuleType, name: str):
        return generator.VerificationResult(
            name=name,
            command="run it",
            status="passed",
            return_code=0,
            duration_seconds=1.0,
            output_tail="",
        )

    def test_a_non_verifying_build_republishes_a_record_that_still_stands(
        self, generator: ModuleType, tmp_path: Path, repo_inventory
    ) -> None:
        name = generator.VERIFICATION_COMMANDS[0][0]
        stored = (self._result(generator, name),)
        self._store(generator, tmp_path, repo_inventory, stored)
        resolved = generator.resolve_verification(
            tmp_path,
            repo_inventory,
            verify=False,
            full_validation=False,
            reuse_verification=True,
        )
        assert [result.name for result in resolved.results] == [name]
        assert resolved.measured_elsewhere is False
        status, passed, failed, unrun = generator._verification_summary(
            resolved.results, full_validation=False
        )
        assert (status, passed, failed) == ("1 passed", 1, 0)
        assert unrun == len(generator.VERIFICATION_COMMANDS) - 1

    def test_a_record_describing_another_tree_is_carried_not_deleted(
        self, generator: ModuleType, tmp_path: Path, repo_inventory
    ) -> None:
        # Discarding it was the defect.  The record is the only copy of a
        # measurement that costs minutes, and the build replacing it measured
        # nothing, so it is republished with its own provenance instead.
        other = dataclasses.replace(repo_inventory, source_hash="0" * 16)
        name = generator.VERIFICATION_COMMANDS[0][0]
        self._store(generator, tmp_path, other, (self._result(generator, name),))
        resolved = generator.resolve_verification(
            tmp_path,
            repo_inventory,
            verify=False,
            full_validation=False,
            reuse_verification=True,
        )
        assert [result.name for result in resolved.results] == [name]
        assert resolved.measured_elsewhere is True
        assert resolved.source_hash == "0" * 16

    def test_reuse_is_the_default_for_the_command_line(
        self, generator: ModuleType
    ) -> None:
        # ``--rerun-verification`` is the opt-out.  A default invocation that
        # opted out of reuse is what deleted the record in the first place.
        assert generator._parse_args([]).rerun_verification is False
        assert generator._parse_args(["--rerun-verification"]).rerun_verification

    def test_a_non_verifying_build_runs_no_command(
        self, generator: ModuleType, tmp_path: Path, repo_inventory, monkeypatch
    ) -> None:
        def _fail(*_args, **_kwargs):  # pragma: no cover - must not be reached
            raise AssertionError("a non-verifying build ran a verification command")

        monkeypatch.setattr(generator, "run_verification", _fail)
        resolved = generator.resolve_verification(
            tmp_path,
            repo_inventory,
            verify=False,
            full_validation=False,
            reuse_verification=True,
        )
        assert resolved.results == ()
        assert resolved.source_commit == repo_inventory.commit

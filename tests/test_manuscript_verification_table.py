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
import subprocess
from pathlib import Path
from types import ModuleType

import pytest


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

    def test_full_validation_adds_the_second_tier(self, generator: ModuleType) -> None:
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
        row = next(
            line for line in table.splitlines() if line.startswith(f"| `{name}`")
        )
        assert "failed" in row
        assert "| 1 |" in row

    def test_build_variables_publishes_a_table_naming_every_defined_group(
        self, generator: ModuleType, repo_inventory, figure_specs
    ) -> None:
        variables = generator.build_variables(
            repo_inventory,
            figure_specs,
            generator.VerificationRecord.unmeasured(),
        )
        table = variables["VERIFICATION_TABLE"]
        assert table.strip()
        for name, _command in generator.VERIFICATION_COMMANDS:
            assert f"| `{name}` |" in table

    def test_the_token_is_authored_into_the_manuscript(self, repo_root) -> None:
        authored = (
            repo_root / "manuscript" / "04_artifacts_and_evidence.md"
        ).read_text(encoding="utf-8")
        assert "{{VERIFICATION_TABLE}}" in authored

    def test_generate_refuses_a_failed_group_when_publishing(
        self, generator: ModuleType, generatable_checkout: Path, monkeypatch
    ) -> None:
        name = generator.VERIFICATION_COMMANDS[0][0]
        monkeypatch.setattr(
            generator,
            "run_verification",
            lambda _root, **_kwargs: (_result(generator, name, "failed", 1),),
        )
        with pytest.raises(RuntimeError, match="verification record contains"):
            generator.generate(generatable_checkout, verify=True, publication=True)

    def test_a_non_publication_build_publishes_the_failure(
        self, generator: ModuleType, generatable_checkout: Path, monkeypatch
    ) -> None:
        name = generator.VERIFICATION_COMMANDS[0][0]
        monkeypatch.setattr(
            generator,
            "run_verification",
            lambda _root, **_kwargs: (_result(generator, name, "failed", 1),),
        )
        manifest = generator.generate(generatable_checkout, verify=True)
        assert manifest["verification_failures"] == [name]
        variables = json.loads(
            (
                generatable_checkout / "output" / "data" / "manuscript_variables.json"
            ).read_text(encoding="utf-8")
        )
        assert variables["VERIFICATION_FAIL_COUNT"] == "1"
        row = next(
            line
            for line in variables["VERIFICATION_TABLE"].splitlines()
            if line.startswith(f"| `{name}`")
        )

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


class TestRunVerification:
    """``run_verification`` maps a real execution onto the record directly.

    Every other test fakes ``run_verification`` wholesale, so nothing pinned
    the mapping a real execution feeds it: exit code to status, combined
    output to the bounded tail the record stores, and the fact that a failing
    group does not stop the remaining groups from running.
    """

    @staticmethod
    def _fake_run(
        monkeypatch: pytest.MonkeyPatch,
        generator: ModuleType,
        outcomes: list[tuple[int, str, str]],
    ) -> None:
        """Drive ``subprocess.run`` from a queue of (code, stdout, stderr).

        The last outcome repeats when the queue empties, so a single entry
        fakes a uniform run and a pair fakes a divergence between the first
        group and everything after it.
        """
        pending = list(outcomes)

        def _run(_command, **_kwargs):
            code, stdout, stderr = pending.pop(0) if len(pending) > 1 else pending[0]
            return subprocess.CompletedProcess(
                _command, code, stdout=stdout, stderr=stderr
            )

        monkeypatch.setattr(generator.subprocess, "run", _run)

    def test_run_verification_maps_an_exit_code_to_a_bounded_failed_tail(
        self, generator: ModuleType, tmp_path: Path, monkeypatch
    ) -> None:
        self._fake_run(monkeypatch, generator, [(3, "x" * 2500, "")])
        results = generator.run_verification(tmp_path)
        assert len(results) == len(generator.VERIFICATION_COMMANDS)
        first = results[0]
        assert first.status == "failed"
        assert first.return_code == 3
        assert 0 < len(first.output_tail) <= 2000

    def test_run_verification_continues_after_a_failing_first_group(
        self, generator: ModuleType, tmp_path: Path, monkeypatch
    ) -> None:
        self._fake_run(
            monkeypatch, generator, [(1, "boom", "traceback"), (0, "ok", "")]
        )
        results = generator.run_verification(tmp_path)
        assert len(results) == len(generator.VERIFICATION_COMMANDS)
        assert results[0].status == "failed"
        assert results[0].return_code == 1
        assert "boom" in results[0].output_tail
        assert results[1].status == "passed"
        assert results[1].return_code == 0


class TestTierAxisOfReuse:
    """The reuse lookup is exact at the record's tier; a mismatch re-measures.

    The chosen rule, deliberately: a record is reused only when it was
    measured at the tier being requested.  A default-tier record never
    satisfies a full-validation request — its results cover the narrower
    tier, and accepting it would publish the wider tier's groups as evidence
    they never produced.  A full-validation record never satisfies a
    default-tier request — the caller that wants the narrower tier either
    re-measures or widens (which ``resolve_verification`` does).  A tier
    mismatch returns ``None``, and the caller runs the commands.
    """

    def _write(self, generator: ModuleType, root, payload) -> None:
        data = root / "output" / "data"
        data.mkdir(parents=True, exist_ok=True)
        (data / "research_verification.json").write_text(
            json.dumps(payload), encoding="utf-8"
        )

    @staticmethod
    def _entry(name: str) -> dict:
        return {
            "name": name,
            "command": "run it",
            "status": "passed",
            "return_code": 0,
            "duration_seconds": 1.0,
            "output_tail": "",
        }

    def test_a_full_tier_record_is_not_reused_for_a_default_request(
        self, generator: ModuleType, tmp_path: Path, repo_inventory
    ) -> None:
        name = generator.FULL_VALIDATION_COMMANDS[0][0]
        self._write(
            generator,
            tmp_path,
            {
                "schema_version": generator.RESEARCH_SCHEMA,
                "full_validation_requested": True,
                "source_commit": repo_inventory.commit,
                "source_hash": repo_inventory.source_hash,
                "results": [self._entry(name)],
            },
        )
        assert (
            generator.load_matching_verification(
                tmp_path, repo_inventory, full_validation=False
            )
            is None
        )

    def test_a_default_tier_record_is_not_reused_for_a_full_request(
        self, generator: ModuleType, tmp_path: Path, repo_inventory
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
                "results": [self._entry(name)],
            },
        )
        assert (
            generator.load_matching_verification(
                tmp_path, repo_inventory, full_validation=True
            )
            is None
        )

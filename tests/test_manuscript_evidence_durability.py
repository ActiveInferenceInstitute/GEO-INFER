"""A build that measures nothing must not be able to delete the measurement.

``output/data/research_verification.json`` is the manuscript's only record of
executed commands, and the commands behind it take minutes.  The supported
render path — ``stage_03_render.py --project GEO-INFER`` — hydrates through
``scripts/z_generate_manuscript_variables.py`` with no verification requested,
so every ordinary render calls ``generate(verify=False)`` against whatever the
record already holds.

Reuse keyed on commit *identity* was not enough to protect it.  The commit
stamp gains a ``-dirty`` suffix as soon as ``git status --porcelain`` prints a
single line, so one untracked file — or any commit made after the evidence was
measured — made the reuse lookup miss and an empty record win.  Measured
before this module existed: seven results in, ``touch`` one file, run the
shim, zero results out, exit 0.

These tests drive the real ``generate`` against a synthetic checkout, so they
pin the file on disk rather than the intent of a branch.  They never touch the
real ``output/`` tree, and they never execute a verification command.
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from types import ModuleType

import pytest

GIT_ENV = {
    "GIT_AUTHOR_NAME": "test",
    "GIT_AUTHOR_EMAIL": "test@example.invalid",
    "GIT_COMMITTER_NAME": "test",
    "GIT_COMMITTER_EMAIL": "test@example.invalid",
    "PATH": "/usr/bin:/bin:/usr/local/bin:/opt/homebrew/bin",
}
FOREIGN_COMMIT = "deadbee"
FOREIGN_HASH = "0" * 16


@pytest.fixture
def generatable_checkout(generator: ModuleType, tmp_path: Path) -> Path:
    """A committed checkout with the minimum shape ``generate`` accepts.

    The generator refuses a tree missing any themed module, so every declared
    module gets a one-file source package.  None of those counts are the
    subject here; the verification record is.
    """
    root = tmp_path / "checkout"
    root.mkdir()
    manuscript = root / "manuscript"
    manuscript.mkdir()
    (manuscript / "config.yaml").write_text(
        "paper:\n"
        '  version: "0.0.0"\n'
        '  date: "1970-01-01T00:00:00+00:00"\n'
        "publication:\n"
        '  year: "1970"\n'
        "metadata:\n"
        '  license: "unset"\n',
        encoding="utf-8",
    )
    (manuscript / "00_abstract.md").write_text(
        "# Abstract\n\nSource hash {{RESEARCH_SOURCE_HASH}}.\n", encoding="utf-8"
    )
    (manuscript / "references.bib").write_text("", encoding="utf-8")
    (root / "pyproject.toml").write_text(
        '[project]\nname = "example"\nversion = "1.2.3"\nlicense = "MIT"\n',
        encoding="utf-8",
    )
    # The real checkout ignores ``/output/``, so writing the evidence bundle
    # does not itself make the tree dirty.  Mirroring that is what lets these
    # tests distinguish "the record moved" from "the tree moved".
    (root / ".gitignore").write_text("/output/\n", encoding="utf-8")
    for _theme, names in generator.MODULE_THEMES:
        for name in names:
            package = name.removeprefix("GEO-INFER-").lower()
            source = root / name / "src" / f"geo_infer_{package}"
            source.mkdir(parents=True)
            (source / "__init__.py").write_text("VALUE = 1\n", encoding="utf-8")
    env = {**GIT_ENV, "HOME": str(tmp_path)}
    for args in (
        ["init", "-q", "-b", "main"],
        ["add", "-A"],
        ["commit", "-q", "-m", "seed"],
    ):
        subprocess.run(
            ["git", "-C", str(root), *args], check=True, env=env, capture_output=True
        )
    return root


def _measured(generator: ModuleType, name: str, tail: str):
    return generator.VerificationResult(
        name=name,
        command="run it",
        status="passed",
        return_code=0,
        duration_seconds=12.5,
        output_tail=tail,
    )


def _store(
    generator: ModuleType, root: Path, *, commit: str, source_hash: str
) -> dict[str, object]:
    """Write a populated record stamped with the tree it names."""
    record = generator.VerificationRecord(
        results=(
            _measured(generator, generator.VERIFICATION_COMMANDS[0][0], "measured"),
        ),
        source_commit=commit,
        source_hash=source_hash,
        full_validation_requested=False,
    )
    payload = generator._verification_payload(record)
    path = generator._verification_record_path(root)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")
    return payload


def _published(generator: ModuleType, root: Path) -> dict:
    return json.loads(
        generator._verification_record_path(root).read_text(encoding="utf-8")
    )


def _variables(root: Path) -> dict:
    return json.loads(
        (root / "output" / "data" / "manuscript_variables.json").read_text(
            encoding="utf-8"
        )
    )


class TestRecordSurvivesANonVerifyingBuild:
    """``generate(verify=False)`` may add provenance; it may not empty the file."""

    def test_a_record_from_another_tree_survives_on_disk(
        self, generator: ModuleType, generatable_checkout: Path
    ) -> None:
        stored = _store(
            generator,
            generatable_checkout,
            commit=FOREIGN_COMMIT,
            source_hash=FOREIGN_HASH,
        )
        manifest = generator.generate(generatable_checkout, verify=False)
        published = _published(generator, generatable_checkout)
        assert published["results"] == stored["results"]
        assert manifest["verification_measured_elsewhere"] is True
        # The record keeps its own stamps.  Restamping it with the commit of
        # the build that merely republished it would make carried evidence
        # indistinguishable from evidence measured here.
        assert published["source_commit"] == FOREIGN_COMMIT
        assert published["source_hash"] == FOREIGN_HASH

    def test_one_untracked_file_no_longer_deletes_the_record(
        self, generator: ModuleType, generatable_checkout: Path
    ) -> None:
        # The whole reproduction: a record that matches the clean tree exactly,
        # then a single untracked file, which appends "-dirty" to the commit
        # stamp and is what made the old reuse lookup miss.
        clean = generator.collect_inventory(generatable_checkout)
        assert not clean.commit.endswith("-dirty")
        stored = _store(
            generator,
            generatable_checkout,
            commit=clean.commit,
            source_hash=clean.source_hash,
        )
        (generatable_checkout / "untracked.txt").write_text("x\n", encoding="utf-8")
        # ``allow_dirty`` is what the render shim passes on every default
        # render, so this is the supported path, not a test-only concession.
        manifest = generator.generate(
            generatable_checkout, verify=False, allow_dirty=True
        )
        assert manifest["source_commit"] == f"{clean.commit}-dirty"
        assert manifest["verification_measured_elsewhere"] is True
        assert (
            _published(generator, generatable_checkout)["results"] == stored["results"]
        )

    def test_a_record_written_before_the_stamps_existed_survives(
        self, generator: ModuleType, generatable_checkout: Path
    ) -> None:
        # An unstamped record still holds executed commands.  Rejecting it as
        # unparseable would put it back in the class a non-verifying build may
        # delete, which is the defect this module exists to prevent.
        path = generator._verification_record_path(generatable_checkout)
        path.parent.mkdir(parents=True, exist_ok=True)
        legacy = {
            "schema_version": generator.RESEARCH_SCHEMA,
            "full_validation_requested": False,
            "results": [
                {
                    "name": generator.VERIFICATION_COMMANDS[0][0],
                    "command": "run it",
                    "status": "passed",
                    "return_code": 0,
                    "duration_seconds": 1.0,
                    "output_tail": "measured",
                }
            ],
        }
        path.write_text(json.dumps(legacy), encoding="utf-8")
        generator.generate(generatable_checkout, verify=False)
        published = _published(generator, generatable_checkout)
        assert published["results"] == legacy["results"]
        assert published["source_commit"] == generator.UNSTAMPED
        variables = _variables(generatable_checkout)
        assert variables["VERIFICATION_RECORD_PROVENANCE"].startswith(
            f"carried forward from commit `{generator.UNSTAMPED}`"
        )

    def test_declining_reuse_is_not_a_licence_to_delete(
        self, generator: ModuleType, generatable_checkout: Path
    ) -> None:
        # ``--rerun-verification`` opts out of the shortcut.  With nothing run
        # in its place there is no replacement to write, so the record stands.
        stored = _store(
            generator,
            generatable_checkout,
            commit=FOREIGN_COMMIT,
            source_hash=FOREIGN_HASH,
        )
        generator.generate(generatable_checkout, verify=False, reuse_verification=False)
        assert (
            _published(generator, generatable_checkout)["results"] == stored["results"]
        )

    def test_a_verifying_build_does_replace_the_record(
        self, generator: ModuleType, generatable_checkout: Path, monkeypatch
    ) -> None:
        # The protection is scoped to builds that measured nothing.  A build
        # that ran the commands publishes its own outcome, not the old one.
        _store(
            generator,
            generatable_checkout,
            commit=FOREIGN_COMMIT,
            source_hash=FOREIGN_HASH,
        )
        monkeypatch.setattr(
            generator,
            "run_verification",
            lambda _root, **_kwargs: (_measured(generator, "compile", "fresh"),),
        )
        manifest = generator.generate(generatable_checkout, verify=True)
        published = _published(generator, generatable_checkout)
        assert manifest["verification_measured_elsewhere"] is False
        assert published["source_commit"] == manifest["source_commit"]
        assert [entry["output_tail"] for entry in published["results"]] == ["fresh"]


class TestCarriedEvidenceIsPublishedAsCarried:
    """Keeping the record is only honest if the manuscript says whose it is."""

    def test_the_published_provenance_names_the_other_tree(
        self, generator: ModuleType, generatable_checkout: Path
    ) -> None:
        _store(
            generator,
            generatable_checkout,
            commit=FOREIGN_COMMIT,
            source_hash=FOREIGN_HASH,
        )
        generator.generate(generatable_checkout, verify=False)
        variables = _variables(generatable_checkout)
        assert variables["VERIFICATION_RECORD_COMMIT"] == FOREIGN_COMMIT
        assert variables["VERIFICATION_RECORD_SOURCE_HASH"] == FOREIGN_HASH
        provenance = variables["VERIFICATION_RECORD_PROVENANCE"]
        assert provenance.startswith(f"carried forward from commit `{FOREIGN_COMMIT}`")
        assert "not re-run against this" in provenance
        # The evidence is republished, so the summary reports it instead of
        # reporting "not run" over a record that exists.
        assert variables["VERIFICATION_PASS_COUNT"] == "1"

    def test_a_record_measured_here_is_published_as_measured_here(
        self, generator: ModuleType, generatable_checkout: Path, monkeypatch
    ) -> None:
        monkeypatch.setattr(
            generator,
            "run_verification",
            lambda _root, **_kwargs: (_measured(generator, "compile", "fresh"),),
        )
        manifest = generator.generate(generatable_checkout, verify=True)
        variables = _variables(generatable_checkout)
        assert variables["VERIFICATION_RECORD_COMMIT"] == manifest["source_commit"]
        assert variables["VERIFICATION_RECORD_PROVENANCE"].startswith(
            "measured on this build's own tree"
        )

    def test_an_empty_record_says_so_rather_than_naming_a_tree(
        self, generator: ModuleType, generatable_checkout: Path
    ) -> None:
        generator.generate(generatable_checkout, verify=False)
        variables = _variables(generatable_checkout)
        assert variables["VERIFICATION_RECORD_PROVENANCE"].startswith(
            "holding no executed command"
        )
        assert variables["VERIFICATION_UNRUN_COUNT"] == str(
            len(generator.VERIFICATION_COMMANDS)
        )

    def test_the_manuscript_publishes_the_provenance_token(
        self, generator: ModuleType, repo_root: Path
    ) -> None:
        # A generated sentence nothing prints is not a disclosure.
        section = (repo_root / "manuscript" / "04_artifacts_and_evidence.md").read_text(
            encoding="utf-8"
        )
        assert "{{VERIFICATION_RECORD_PROVENANCE}}" in section

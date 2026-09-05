"""Tests that the published source fingerprint fingerprints what ships.

``manuscript/config.yaml`` is both a generator-owned file and a hashed input.
Writing it after the digest was taken made ``RESEARCH_SOURCE_HASH``
irreproducible by the procedure its own glossary describes.
"""

from __future__ import annotations

import json
from pathlib import Path
from types import ModuleType

import pytest


@pytest.fixture
def manuscript_tree(git_repo: Path) -> Path:
    """A checkout with the minimum shape the fingerprint helpers need."""
    manuscript = git_repo / "manuscript"
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
    (git_repo / "pyproject.toml").write_text(
        '[project]\nname = "example"\nversion = "1.2.3"\nlicense = "MIT"\n',
        encoding="utf-8",
    )
    return git_repo


class TestSourceHashCoversConfig:
    def test_config_is_inside_the_hashed_input_set(
        self, generator: ModuleType, manuscript_tree: Path
    ) -> None:
        before = generator._source_hash(manuscript_tree)
        config = manuscript_tree / "manuscript" / "config.yaml"
        config.write_text(config.read_text(encoding="utf-8") + "# touched\n", "utf-8")
        assert generator._source_hash(manuscript_tree) != before

    def test_hash_taken_after_the_refresh_is_reproducible(
        self, generator: ModuleType, manuscript_tree: Path
    ) -> None:
        values = generator.config_metadata_values(manuscript_tree)
        assert generator.refresh_config_metadata(manuscript_tree, values)
        digest = generator._source_hash(manuscript_tree)
        # Re-running the whole ordering must land on the same fingerprint.
        assert generator.refresh_config_metadata(manuscript_tree, values) == ()
        assert generator._source_hash(manuscript_tree) == digest

    def test_hash_taken_before_the_refresh_is_not_reproducible(
        self, generator: ModuleType, manuscript_tree: Path
    ) -> None:
        # The defect, pinned: hashing first and writing second publishes a
        # fingerprint of a tree that no longer exists when the run ends.
        digest = generator._source_hash(manuscript_tree)
        generator.refresh_config_metadata(
            manuscript_tree, generator.config_metadata_values(manuscript_tree)
        )
        assert generator._source_hash(manuscript_tree) != digest

    def test_refresh_writes_measured_values(
        self, generator: ModuleType, manuscript_tree: Path
    ) -> None:
        generator.refresh_config_metadata(
            manuscript_tree, generator.config_metadata_values(manuscript_tree)
        )
        text = (manuscript_tree / "manuscript" / "config.yaml").read_text("utf-8")
        assert '  version: "1.2.3"  # generator-owned (PROJECT_VERSION)' in text
        assert '  license: "MIT"  # generator-owned (PROJECT_LICENSE)' in text

    def test_dry_run_reports_without_writing(
        self, generator: ModuleType, manuscript_tree: Path
    ) -> None:
        config = manuscript_tree / "manuscript" / "config.yaml"
        original = config.read_text(encoding="utf-8")
        stale = generator.refresh_config_metadata(
            manuscript_tree,
            generator.config_metadata_values(manuscript_tree),
            dry_run=True,
        )
        assert set(stale) == {
            "paper.version",
            "paper.date",
            "publication.year",
            "metadata.license",
        }
        assert config.read_text(encoding="utf-8") == original


class TestCheckMode:
    def test_missing_published_variables_fail_closed(
        self, generator: ModuleType, manuscript_tree: Path
    ) -> None:
        problems = generator.check_published_artifacts(manuscript_tree)
        assert any("no published variables" in problem for problem in problems)

    def test_stale_source_hash_is_detected(
        self, generator: ModuleType, manuscript_tree: Path
    ) -> None:
        generator.refresh_config_metadata(
            manuscript_tree, generator.config_metadata_values(manuscript_tree)
        )
        data = manuscript_tree / "output" / "data"
        data.mkdir(parents=True)
        (data / "manuscript_variables.json").write_text(
            json.dumps({"RESEARCH_SOURCE_HASH": "0000000000000000"}), encoding="utf-8"
        )
        problems = generator.check_published_artifacts(manuscript_tree)
        assert any("RESEARCH_SOURCE_HASH is stale" in p for p in problems)

    def test_a_matching_tree_reports_no_problems(
        self, generator: ModuleType, manuscript_tree: Path
    ) -> None:
        generator.refresh_config_metadata(
            manuscript_tree, generator.config_metadata_values(manuscript_tree)
        )
        data = manuscript_tree / "output" / "data"
        data.mkdir(parents=True)
        (data / "manuscript_variables.json").write_text(
            json.dumps(
                {"RESEARCH_SOURCE_HASH": generator._source_hash(manuscript_tree)}
            ),
            encoding="utf-8",
        )
        assert generator.check_published_artifacts(manuscript_tree) == ()

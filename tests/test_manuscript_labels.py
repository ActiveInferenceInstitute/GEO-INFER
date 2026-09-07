"""Tests that every published label describes what the generator measured."""

from __future__ import annotations

from pathlib import Path
from types import ModuleType


class TestValidatorCount:
    """``VALIDATOR_FILE_COUNT`` must count validators, not a directory."""

    def test_only_validate_entry_points_are_counted(
        self, repo_root: Path, repo_inventory
    ) -> None:
        expected = len(
            [
                path
                for path in (repo_root / "GEO-INFER-TEST").glob("validate_*.py")
                if path.is_file()
            ]
        )
        assert expected > 0
        assert repo_inventory.validator_files == expected

    def test_non_validators_are_excluded(self, repo_root: Path, repo_inventory) -> None:
        all_top_level = [
            path
            for path in (repo_root / "GEO-INFER-TEST").glob("*.py")
            if path.is_file()
        ]
        non_validators = {
            path.name for path in all_top_level if not path.name.startswith("validate_")
        }
        assert non_validators, "fixture assumption: the directory holds non-validators"
        assert repo_inventory.validator_files == len(all_top_level) - len(
            non_validators
        )
        assert repo_inventory.test_tooling_files == len(all_top_level)

    def test_both_counts_are_published_under_distinct_names(
        self, generator: ModuleType, repo_inventory
    ) -> None:
        variables = generator.build_variables(
            repo_inventory,
            _figure_specs(generator),
            generator.VerificationRecord.unmeasured(),
        )
        assert variables["VALIDATOR_FILE_COUNT"] == str(repo_inventory.validator_files)
        assert variables["TEST_TOOLING_FILE_COUNT"] == str(
            repo_inventory.test_tooling_files
        )
        assert variables["VALIDATOR_FILE_COUNT"] != variables["TEST_TOOLING_FILE_COUNT"]


class TestModuleCountLabel:
    """``MODULE_COUNT`` is a ``src/`` glob; nothing in this build imports."""

    def test_caption_does_not_claim_importability(
        self, generator: ModuleType, repo_inventory
    ) -> None:
        caption = generator._caption_module_inventory(repo_inventory)
        assert "importable" not in caption.lower()
        assert "src/-bearing" in caption

    def test_module_count_equals_the_src_bearing_directory_count(
        self, repo_root: Path, repo_inventory
    ) -> None:
        expected = len(
            [
                path
                for path in repo_root.glob("GEO-INFER-*")
                if path.is_dir() and (path / "src").is_dir()
            ]
        )
        assert repo_inventory.module_count == expected


def _figure_specs(generator: ModuleType):
    return (
        generator.FigureSpec(
            label="fig:example",
            filename="example.png",
            caption="Example caption.",
            generated_by="tests",
            alt_text="Example alt text.",
        ),
    )

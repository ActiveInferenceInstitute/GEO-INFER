"""Bibliography gate tests.

``bibliography.fail_on_missing`` and ``bibliography.fail_on_unused`` are
documented config keys that no renderer code reads.  The generator honours
them, so these tests pin that the gate is real rather than declared.
"""

from __future__ import annotations

from pathlib import Path
from types import ModuleType

import pytest


@pytest.fixture
def bib_tree(tmp_path: Path) -> Path:
    root = tmp_path / "checkout"
    manuscript = root / "manuscript"
    manuscript.mkdir(parents=True)
    (manuscript / "references.bib").write_text(
        "@article{cited_entry,\n  title = {Cited},\n}\n\n"
        "@book{orphan_entry,\n  title = {Orphan},\n}\n",
        encoding="utf-8",
    )
    (manuscript / "config.yaml").write_text(
        "bibliography:\n"
        '  references_path: "manuscript/references.bib"\n'
        "  fail_on_missing: true\n"
        "  fail_on_unused: false\n",
        encoding="utf-8",
    )
    return root


def _body(root: Path, text: str) -> list[Path]:
    body = root / "body.md"
    body.write_text(text, encoding="utf-8")
    return [body]


class TestBibliographyAudit:
    def test_an_orphan_entry_is_reported(
        self, generator: ModuleType, bib_tree: Path
    ) -> None:
        uncited, undefined = generator.audit_bibliography(
            bib_tree, _body(bib_tree, "As shown [@cited_entry], the result holds.\n")
        )
        assert uncited == ("orphan_entry",)
        assert undefined == ()

    def test_a_citation_with_no_entry_is_reported(
        self, generator: ModuleType, bib_tree: Path
    ) -> None:
        _uncited, undefined = generator.audit_bibliography(
            bib_tree,
            _body(bib_tree, "See [@cited_entry] and [@orphan_entry] and [@ghost].\n"),
        )
        assert undefined == ("ghost",)

    def test_crossreferences_are_not_bibliography_keys(
        self, generator: ModuleType, bib_tree: Path
    ) -> None:
        _uncited, undefined = generator.audit_bibliography(
            bib_tree,
            _body(
                bib_tree,
                "See [@fig:module_inventory], [@tbl:evidence] and [@sec:methods]; "
                "[@cited_entry] and [@orphan_entry] cover the rest.\n",
            ),
        )
        assert undefined == ()

    def test_an_email_address_is_not_a_citation(
        self, generator: ModuleType, bib_tree: Path
    ) -> None:
        _uncited, undefined = generator.audit_bibliography(
            bib_tree,
            _body(
                bib_tree,
                "Contact daniel@activeinference.institute. "
                "[@cited_entry] [@orphan_entry]\n",
            ),
        )
        assert undefined == ()

    def test_policy_is_read_from_config(
        self, generator: ModuleType, bib_tree: Path
    ) -> None:
        assert generator.bibliography_policy(bib_tree) == {
            "fail_on_missing": True,
            "fail_on_unused": False,
        }
        config = bib_tree / "manuscript" / "config.yaml"
        config.write_text(
            config.read_text(encoding="utf-8").replace(
                "fail_on_unused: false", "fail_on_unused: true"
            ),
            encoding="utf-8",
        )
        assert generator.bibliography_policy(bib_tree)["fail_on_unused"] is True


class TestRealBibliography:
    def test_no_citation_is_missing_an_entry(
        self, generator: ModuleType, repo_root: Path
    ) -> None:
        resolved = sorted((repo_root / "output" / "manuscript").glob("*.md"))
        assert resolved, "run scripts/z_generate_manuscript_variables.py first"
        _uncited, undefined = generator.audit_bibliography(repo_root, resolved)
        assert undefined == ()

    def test_the_orphan_is_visible_rather_than_silent(
        self, generator: ModuleType, repo_root: Path
    ) -> None:
        # GI-M3: gelman_bda_2014 sits in references.bib and is cited nowhere.
        # The gate makes that visible on every run; flipping fail_on_unused to
        # true once it is cited makes it fatal.
        resolved = sorted((repo_root / "output" / "manuscript").glob("*.md"))
        uncited, _undefined = generator.audit_bibliography(repo_root, resolved)
        policy = generator.bibliography_policy(repo_root)
        assert policy["fail_on_missing"] is True
        if uncited:
            assert policy["fail_on_unused"] is False, (
                "fail_on_unused is set, so an uncited entry must fail the build "
                f"rather than reach this assertion: {uncited}"
            )

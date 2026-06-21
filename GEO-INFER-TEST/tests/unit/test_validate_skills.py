"""Unit tests for SKILL.md semantic validation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
SKILLS_PATH = REPO_ROOT / "GEO-INFER-TEST" / "validate_skills.py"


def load_skills_module():
    spec = importlib.util.spec_from_file_location(
        "geo_infer_validate_skills", SKILLS_PATH
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_skill_claim_language_rejects_unscoped_planned_claim():
    skills = load_skills_module()
    content = "\n".join(
        [
            "## Guidelines",
            "- Missing dashboard workflow planned for v0.4.0",
        ]
    )

    errors = skills.validate_skill_claim_language(content, "[TEST]")

    assert errors
    assert "planned" in errors[0]


def test_skill_claim_language_allows_intentional_placeholder_contexts():
    skills = load_skills_module()
    content = "\n".join(
        [
            "- HTML form inputs use standard `placeholder` attributes.",
            "- SQL uses parameterized queries (`:param` placeholders).",
            "- Students fill in the `pass` block in the generated template.",
        ]
    )

    errors = skills.validate_skill_claim_language(content, "[TEST]")

    assert errors == []


def test_skill_claim_language_ignores_code_blocks():
    skills = load_skills_module()
    content = "\n".join(
        [
            "```python",
            "def exercise():",
            "    pass",
            "```",
        ]
    )

    errors = skills.validate_skill_claim_language(content, "[TEST]")

    assert errors == []

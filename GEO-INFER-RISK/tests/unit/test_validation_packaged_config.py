"""Packaged config resolution for risk validation utilities."""

import json

from geo_infer_risk.utils.validation import ConfigurationValidator
from geo_infer_test.testing import assert_packaged_config_loads


class TestPackagedSchemaResolution:
    """ConfigurationValidator must resolve schema.json from the package tree."""

    def test_default_resolution_works_from_empty_cwd(
        self, tmp_path, monkeypatch
    ) -> None:
        """Default schema resolution must not depend on cwd (no parent climbing)."""
        monkeypatch.delenv("GEO_INFER_RISK_SCHEMA_PATH", raising=False)
        monkeypatch.chdir(tmp_path)

        validator = ConfigurationValidator()

        assert validator.schema is not None
        assert validator.schema.get("title") == "GEO-INFER-RISK Configuration Schema"

    def test_default_schema_resolves_under_package_tree(self, monkeypatch) -> None:
        """The packaged schema resolves under the geo_infer_risk package tree."""
        monkeypatch.delenv("GEO_INFER_RISK_SCHEMA_PATH", raising=False)

        parsed = assert_packaged_config_loads(
            "geo_infer_risk",
            "config/schema.json",
            format="json",
            required_sections=("properties",),
            required_keys={"": ("$schema", "title", "type")},
        )
        assert parsed["title"] == "GEO-INFER-RISK Configuration Schema"

    def test_env_var_override_is_honored(self, tmp_path, monkeypatch) -> None:
        """GEO_INFER_RISK_SCHEMA_PATH must take precedence when explicitly set."""
        override_schema = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "title": "Override Schema",
            "type": "object",
        }
        override_path = tmp_path / "override_schema.json"
        override_path.write_text(json.dumps(override_schema))

        monkeypatch.setenv("GEO_INFER_RISK_SCHEMA_PATH", str(override_path))

        validator = ConfigurationValidator()

        assert validator.schema == override_schema
        assert validator.schema_path == str(override_path)
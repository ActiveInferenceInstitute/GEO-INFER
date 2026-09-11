"""CLI handler tests with real tmp_path files (GS-224).

Exercises the documented geo-infer-sec command surface end to end through
its argparse handlers: data loading/saving helpers, the anonymize /
encrypt / decrypt round-trips, compliance checking, auditing, and risk
report generation. Exit-code and failure-handling behavior lives in
test_cli_exit_codes.py (GS-225); these tests cover the success paths.
"""

import argparse
import json
from pathlib import Path

import geopandas as gpd
import pandas as pd
import pytest
from shapely.geometry import Point

from geo_infer_sec.cli import (
    command_anonymize,
    command_audit,
    command_check_compliance,
    command_decrypt,
    command_encrypt,
    command_risk_assessment,
    load_geospatial_data,
    save_geospatial_data,
    setup_parser,
)


@pytest.fixture
def points_geojson(tmp_path: Path) -> str:
    """A small EPSG:4326 point dataset on disk."""
    gdf = gpd.GeoDataFrame(
        {"id": [1, 2, 3, 4, 5], "email": [f"user{i}@example.com" for i in range(5)]},
        geometry=[Point(-122.33 + i * 0.01, 47.61 + i * 0.01) for i in range(5)],
        crs="EPSG:4326",
    )
    path = tmp_path / "points.geojson"
    gdf.to_file(path, driver="GeoJSON")
    return str(path)


class TestParser:
    """setup_parser surface and defaults."""

    def test_anonymize_defaults(self):
        args = setup_parser().parse_args(["anonymize", "in.geojson", "out.geojson"])
        assert args.command == "anonymize"
        assert args.method == "perturbation"
        assert args.epsilon == 100.0
        assert args.k == 5
        assert args.h3_resolution == 9

    def test_encrypt_and_decrypt_flags(self):
        parser = setup_parser()
        encrypt_args = parser.parse_args(
            ["encrypt", "in.csv", "out.csv", "--key-file", "k.bin", "--columns", "a,b"]
        )
        assert encrypt_args.command == "encrypt"
        assert encrypt_args.key_file == "k.bin"
        assert encrypt_args.encrypt_geometry is False
        decrypt_args = parser.parse_args(
            ["decrypt", "in.csv", "out.csv", "--key-file", "k.bin"]
        )
        assert decrypt_args.command == "decrypt"

    def test_audit_and_risk_flags(self):
        parser = setup_parser()
        audit_args = parser.parse_args(
            ["audit", "in.geojson", "--check-pii", "--output-file", "r.json"]
        )
        assert audit_args.check_pii is True
        assert audit_args.check_bounds is False
        risk_args = parser.parse_args(["risk-assessment", "--format", "text"])
        assert risk_args.format == "text"
        assert risk_args.name == "Geospatial Security Risk Assessment"

    def test_unknown_command_exits(self):
        with pytest.raises(SystemExit):
            setup_parser().parse_args(["not-a-command"])


class TestGeoDataIO:
    """load_geospatial_data / save_geospatial_data format handling."""

    def test_csv_with_lat_lon_becomes_geodataframe(self, tmp_path):
        path = tmp_path / "points.csv"
        pd.DataFrame(
            {
                "latitude": [47.61, 47.62],
                "longitude": [-122.33, -122.34],
                "value": [1, 2],
            }
        ).to_csv(path, index=False)

        gdf = load_geospatial_data(str(path))

        assert isinstance(gdf, gpd.GeoDataFrame)
        assert gdf.crs.to_epsg() == 4326
        assert len(gdf) == 2

    def test_unsupported_input_extension_raises(self, tmp_path):
        path = tmp_path / "data.txt"
        path.write_text("nope\n")
        with pytest.raises(ValueError, match="Unsupported file format"):
            load_geospatial_data(str(path))

    def test_unsupported_output_extension_raises(self, tmp_path):
        gdf = gpd.GeoDataFrame({"a": [1]}, geometry=[Point(0, 0)], crs="EPSG:4326")
        with pytest.raises(ValueError, match="Unsupported output format"):
            save_geospatial_data(gdf, str(tmp_path / "out.parquet"))

    def test_geojson_roundtrip(self, tmp_path):
        gdf = gpd.GeoDataFrame(
            {"a": [1, 2]}, geometry=[Point(1, 2), Point(3, 4)], crs="EPSG:4326"
        )
        path = tmp_path / "round.geojson"
        save_geospatial_data(gdf, str(path))
        loaded = load_geospatial_data(str(path))
        assert list(loaded["a"]) == [1, 2]
        assert list(loaded.geometry.x) == [1, 3]


class TestAnonymizeCommand:
    def test_perturbation_writes_perturbed_output(self, points_geojson, tmp_path):
        output = str(tmp_path / "anonymized.geojson")
        args = argparse.Namespace(
            input_file=points_geojson,
            output_file=output,
            method="perturbation",
            epsilon=1000.0,
            k=5,
            h3_resolution=9,
            admin_boundaries=None,
            attribute_cols=None,
        )
        assert command_anonymize(args) is True

        original = load_geospatial_data(points_geojson)
        anonymized = load_geospatial_data(output)
        assert len(anonymized) == len(original) == 5
        assert list(anonymized.columns) == list(original.columns)
        # Each point moved by at most epsilon meters (111,000 m per degree).
        deltas = (
            (anonymized.geometry.x - original.geometry.x) ** 2
            + (anonymized.geometry.y - original.geometry.y) ** 2
        ) ** 0.5
        max_degrees = 1000.0 / 111000.0
        assert (deltas <= max_degrees + 1e-9).all()

    def test_geographic_masking_requires_attribute_cols(self, points_geojson, tmp_path):
        args = argparse.Namespace(
            input_file=points_geojson,
            output_file=str(tmp_path / "out.geojson"),
            method="geographic-masking",
            epsilon=100.0,
            k=5,
            h3_resolution=9,
            admin_boundaries=None,
            attribute_cols=None,
        )
        assert command_anonymize(args) is False

    def test_unknown_method_rejected(self, points_geojson, tmp_path):
        args = argparse.Namespace(
            input_file=points_geojson,
            output_file=str(tmp_path / "out.geojson"),
            method="wave-a-wave",
            epsilon=100.0,
            k=5,
            h3_resolution=9,
            admin_boundaries=None,
            attribute_cols=None,
        )
        assert command_anonymize(args) is False


class TestEncryptDecryptCommand:
    def test_key_file_roundtrip_restores_values(self, tmp_path):
        input_csv = tmp_path / "data.csv"
        pd.DataFrame(
            {
                "latitude": [47.61, 47.62],
                "longitude": [-122.33, -122.34],
                "secret": ["hunter2", "s3cr3t"],
            }
        ).to_csv(input_csv, index=False)
        key_file = tmp_path / "key.bin"
        encrypted_csv = tmp_path / "encrypted.csv"
        decrypted_csv = tmp_path / "decrypted.csv"

        encrypt_args = argparse.Namespace(
            input_file=str(input_csv),
            output_file=str(encrypted_csv),
            password=None,
            key_file=str(key_file),
            columns="secret",
            encrypt_geometry=False,
        )
        assert command_encrypt(encrypt_args) is True
        assert key_file.exists()

        # The stored values are ciphertext, not plaintext.
        stored = pd.read_csv(encrypted_csv)
        assert list(stored["secret"]) != ["hunter2", "s3cr3t"]

        decrypt_args = argparse.Namespace(
            input_file=str(encrypted_csv),
            output_file=str(decrypted_csv),
            password=None,
            key_file=str(key_file),
            columns="secret",
        )
        assert command_decrypt(decrypt_args) is True

        decrypted = pd.read_csv(decrypted_csv)
        assert list(decrypted["secret"]) == ["hunter2", "s3cr3t"]
        # Coordinates stayed untouched through the explicit-column flow.
        assert list(decrypted["latitude"]) == [47.61, 47.62]

    def test_decrypt_without_key_or_password_fails(self, tmp_path):
        args = argparse.Namespace(
            input_file=str(tmp_path / "missing.csv"),
            output_file=str(tmp_path / "out.csv"),
            password=None,
            key_file=None,
            columns=None,
        )
        assert command_decrypt(args) is False

    def test_encrypt_unreadable_input_fails(self, tmp_path):
        args = argparse.Namespace(
            input_file=str(tmp_path / "missing.geojson"),
            output_file=str(tmp_path / "out.csv"),
            password=None,
            key_file=None,
            columns=None,
            encrypt_geometry=False,
        )
        assert command_encrypt(args) is False


class TestAuditCommand:
    def test_audit_detects_pii_columns(self, points_geojson, tmp_path):
        output = str(tmp_path / "audit.json")
        args = argparse.Namespace(
            input_file=points_geojson,
            output_file=output,
            check_pii=True,
            check_bounds=True,
            detect_outliers=False,
        )
        assert command_audit(args) is True

        report = json.loads(Path(output).read_text())
        assert report["record_count"] == 5
        assert "email" in report["columns"]
        issue_types = [issue["type"] for issue in report["issues"]]
        assert "pii_columns" in issue_types
        pii_issue = next(i for i in report["issues"] if i["type"] == "pii_columns")
        assert "email" in pii_issue["details"]
        # In-bounds WGS84 data must not raise the invalid-bounds flag.
        assert "invalid_bounds" not in issue_types

    def test_audit_clean_file_has_no_issues(self, tmp_path):
        path = tmp_path / "clean.geojson"
        gpd.GeoDataFrame(
            {"value": [1, 2, 3]},
            geometry=[Point(1, 2), Point(3, 4), Point(5, 6)],
            crs="EPSG:4326",
        ).to_file(path, driver="GeoJSON")
        args = argparse.Namespace(
            input_file=str(path),
            output_file=None,
            check_pii=True,
            check_bounds=True,
            detect_outliers=False,
        )
        assert command_audit(args) is True

    def test_audit_missing_input_fails(self, tmp_path):
        args = argparse.Namespace(
            input_file=str(tmp_path / "missing.geojson"),
            output_file=None,
            check_pii=True,
            check_bounds=False,
            detect_outliers=False,
        )
        assert command_audit(args) is False


class TestComplianceCommand:
    def test_gdpr_report_written_to_file(self, tmp_path):
        path = tmp_path / "pings.csv"
        # Three PII-named columns trip the data-minimization rule.
        pd.DataFrame(
            {
                "latitude": [47.61, 47.62, 47.63],
                "longitude": [-122.33, -122.34, -122.35],
                "name": ["a", "b", "c"],
                "email": ["a@x.com", "b@x.com", "c@x.com"],
                "phone": ["555", "556", "557"],
            }
        ).to_csv(path, index=False)
        report_path = tmp_path / "report.json"

        args = argparse.Namespace(
            input_file=str(path),
            output_file=str(report_path),
            regimes="gdpr",
            format="json",
        )
        assert command_check_compliance(args) is True

        report = json.loads(report_path.read_text())
        assert report["total_rules"] > 0
        assert report["total_violations"] >= 1
        assert report["violations_by_regime"].get("gdpr", 0) >= 1

    def test_tabular_input_without_coordinates_fails(self, tmp_path):
        path = tmp_path / "plain.csv"
        pd.DataFrame({"a": [1]}).to_csv(path, index=False)
        args = argparse.Namespace(
            input_file=str(path),
            output_file=None,
            regimes="gdpr",
            format="json",
        )
        assert command_check_compliance(args) is False


class TestRiskAssessmentCommand:
    @pytest.mark.parametrize("report_format", ["text", "html"])
    def test_report_written_for_each_supported_format(self, tmp_path, report_format):
        output = tmp_path / f"risk.{report_format}"
        args = argparse.Namespace(
            name="GS-224 Assessment",
            format=report_format,
            output_file=str(output),
        )
        assert command_risk_assessment(args) is True

        content = output.read_text()
        assert "GS-224 Assessment" in content
        assert "Total Risk Score" in content
        assert "Number of Risks" in content

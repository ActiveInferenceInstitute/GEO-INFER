"""Tests for deterministic visualization receipt helper.

SPACE's ``visualization_receipt`` module forms the shared deterministic contract
for visualization output manifests.
"""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

import pytest

from geo_infer_space.core.visualization_receipt import write_visualization_receipt


def test_write_receipt_minimal() -> None:
    """Produces a valid manifest with minimum required fields."""
    with tempfile.TemporaryDirectory() as tmp:
        artifact = Path(tmp) / "map.html"
        artifact.write_text("<html><title>Test</title></html>", encoding="utf-8")

        manifest_path = write_visualization_receipt(
            artifact_path=artifact,
            input_payload={"location": "test_bbox"},
            schema_version="test/v1",
        )

        assert manifest_path.exists()
        assert manifest_path.suffix == ".json"
        assert "manifest" in manifest_path.name

        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        assert manifest["schema_version"] == "test/v1"
        assert "generated_at" in manifest
        assert manifest["input_sha256"] is not None
        assert len(manifest["input_sha256"]) == 64
        assert manifest["h3_version"] is not None
        assert len(manifest["artifacts"]) == 1
        assert manifest["artifacts"][0]["path"] == "map.html"
        assert manifest["artifacts"][0]["bytes"] >= 30


def test_receipt_artifact_bytes() -> None:
    """Artifact entry includes correct byte count."""
    with tempfile.TemporaryDirectory() as tmp:
        artifact = Path(tmp) / "output.html"
        artifact.write_text("x" * 1234, encoding="utf-8")

        manifest_path = write_visualization_receipt(
            artifact_path=artifact,
            input_payload={"n": 42},
            schema_version="test/v1",
        )
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        assert manifest["artifacts"][0]["bytes"] == 1234


def test_receipt_accessibility_html() -> None:
    """HTML artifacts get nonempty_html and has_title checks."""
    with tempfile.TemporaryDirectory() as tmp:
        artifact = Path(tmp) / "dashboard.html"
        artifact.write_text(
            "<h1>GEO-INFER Place-Based Analysis</h1>", encoding="utf-8"
        )

        manifest_path = write_visualization_receipt(
            artifact_path=artifact,
            input_payload={},
            schema_version="test/v1",
            title_marker="GEO-INFER Place-Based Analysis",
        )
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        acc = manifest["accessibility"]
        assert acc.get("nonempty_html") is True
        assert acc.get("has_title") is True


def test_receipt_json_artifact() -> None:
    """JSON artifacts get valid_json accessibility check."""
    with tempfile.TemporaryDirectory() as tmp:
        artifact = Path(tmp) / "results.json"
        artifact.write_text('{"key": "value"}', encoding="utf-8")

        manifest_path = write_visualization_receipt(
            artifact_path=artifact,
            input_payload={"key": "value"},
            schema_version="test/v1",
        )
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        acc = manifest["accessibility"]
        assert acc.get("nonempty") is True
        assert acc.get("valid_json") is True


def test_receipt_markdown_artifact() -> None:
    """Markdown artifacts get has_heading accessibility check."""
    with tempfile.TemporaryDirectory() as tmp:
        artifact = Path(tmp) / "report.md"
        artifact.write_text("# Analysis Report\n\nResults here.", encoding="utf-8")

        manifest_path = write_visualization_receipt(
            artifact_path=artifact,
            input_payload={"report": True},
            schema_version="test/v1",
            title_marker="Analysis Report",
        )
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        acc = manifest["accessibility"]
        assert acc.get("nonempty") is True
        assert acc.get("has_heading") is True


def test_receipt_extra_fields() -> None:
    """Extra top-level fields are merged into the manifest."""
    with tempfile.TemporaryDirectory() as tmp:
        artifact = Path(tmp) / "viz.html"
        artifact.write_text("<html></html>", encoding="utf-8")

        manifest_path = write_visualization_receipt(
            artifact_path=artifact,
            input_payload={},
            schema_version="test/v1",
            extra={"location": "Del Norte County, CA", "run_id": "abc123"},
        )
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        assert manifest["location"] == "Del Norte County, CA"
        assert manifest["run_id"] == "abc123"


def test_receipt_input_digest_stability() -> None:
    """Same input payload produces same digest."""
    with tempfile.TemporaryDirectory() as tmp:
        a = Path(tmp) / "a.html"
        b = Path(tmp) / "b.html"
        a.write_text("content", encoding="utf-8")
        b.write_text("content", encoding="utf-8")

        m1 = write_visualization_receipt(
            artifact_path=a, input_payload={"x": 1, "y": "z"}, schema_version="v1"
        )
        m2 = write_visualization_receipt(
            artifact_path=b, input_payload={"y": "z", "x": 1}, schema_version="v1"
        )
        d1 = json.loads(m1.read_text(encoding="utf-8"))
        d2 = json.loads(m2.read_text(encoding="utf-8"))
        assert d1["input_sha256"] == d2["input_sha256"]


def test_receipt_missing_artifact_raises() -> None:
    """Missing artifact file raises FileNotFoundError."""
    with tempfile.TemporaryDirectory() as tmp:
        missing = Path(tmp) / "nonexistent.html"
        with pytest.raises(FileNotFoundError):
            write_visualization_receipt(
                artifact_path=missing,
                input_payload={},
                schema_version="test/v1",
            )
"""Smoke tests for the GEO-INFER-BIO REST API (FastAPI TestClient)."""

from __future__ import annotations

import base64

import matplotlib

matplotlib.use("Agg")  # plots are rendered inside the TestClient worker thread

import pytest
from fastapi.testclient import TestClient

from geo_infer_bio import __version__
from geo_infer_bio.api.rest_api import app


@pytest.fixture()
def client() -> TestClient:
    return TestClient(app)


def _sequence_payload(sequence: str = "ATCGATCGAAACCCGGG") -> dict:
    return {
        "id": "seq-1",
        "sequence": sequence,
        "spatial_data": {"latitude": 37.7, "longitude": -122.4},
    }


class TestRestApi:
    """FastAPI TestClient smoke tests for the REST surface."""

    def test_root_reports_package_version(self, client: TestClient) -> None:
        response = client.get("/")
        assert response.status_code == 200
        body = response.json()
        assert body["name"] == "GEO-INFER-BIO API"
        assert body["version"] == __version__

    def test_health(self, client: TestClient) -> None:
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "healthy"}

    def test_analyze_sequence(self, client: TestClient) -> None:
        # "ATCGATCGAAACCCGGG" -> 10 GC of 17 bases
        response = client.post(
            "/analyze/sequence",
            json=_sequence_payload("ATCGATCGAAACCCGGG"),
        )
        assert response.status_code == 200
        body = response.json()
        assert body["sequence_id"] == "seq-1"
        assert body["gc_content"] == pytest.approx(10 / 17 * 100)
        assert body["spatial_data"]["latitude"] == 37.7

    def test_analyze_sequence_rejects_invalid_sequence(self, client: TestClient) -> None:
        response = client.post("/analyze/sequence", json=_sequence_payload("XYZ123"))
        assert response.status_code == 400
        assert "Invalid sequence" in response.json()["detail"]

    def test_analyze_file(self, client: TestClient, tmp_path) -> None:
        fasta = ">seq-1\nATCGATCGAAACCCGGG\n>bad-seq\nXYZ123\n"
        response = client.post(
            "/analyze/file",
            files={"file": ("sample.fasta", fasta.encode(), "text/plain")},
        )
        assert response.status_code == 200
        results = response.json()
        # The invalid record is skipped by validation
        assert [r["sequence_id"] for r in results] == ["seq-1"]
        assert results[0]["gc_content"] == pytest.approx(10 / 17 * 100)

    def test_analyze_file_with_spatial_csv(self, client: TestClient) -> None:
        fasta = ">seq-1\nATCGATCGAAACCCGGG\n"
        spatial = "latitude,longitude\n37.7,-122.4\n"
        response = client.post(
            "/analyze/file",
            files=[
                ("file", ("sample.fasta", fasta.encode(), "text/plain")),
                ("spatial_data", ("spatial.csv", spatial.encode(), "text/csv")),
            ],
        )
        assert response.status_code == 200
        results = response.json()
        assert results[0]["gc_content"] == pytest.approx(10 / 17 * 100)
        assert results[0]["spatial_data"] == {
            "latitude": 37.7,
            "longitude": -122.4,
        }

    def test_visualize_spatial_returns_base64_png(self, client: TestClient) -> None:
        payload = [
            {
                "sequence_id": "seq-1",
                "gc_content": 50.0,
                "motif_count": 1,
                "coding_regions": 0,
                "spatial_data": {"latitude": 37.7, "longitude": -122.4},
            },
            {
                "sequence_id": "seq-2",
                "gc_content": 30.0,
                "motif_count": 0,
                "coding_regions": 0,
                "spatial_data": {"latitude": 38.0, "longitude": -122.0},
            },
        ]
        response = client.post("/visualize/spatial", json=payload)
        assert response.status_code == 200
        plots = response.json()
        assert set(plots) == {"gc_content", "motif_density", "coding_potential"}
        for name, encoded in plots.items():
            raw = base64.b64decode(encoded, validate=True)
            assert raw[:8] == b"\x89PNG\r\n\x1a\n", f"{name} is not a PNG"

    def test_visualize_spatial_requires_spatial_data(self, client: TestClient) -> None:
        payload = [
            {
                "sequence_id": "seq-1",
                "gc_content": 50.0,
                "motif_count": 1,
                "coding_regions": 0,
                "spatial_data": None,
            }
        ]
        response = client.post("/visualize/spatial", json=payload)
        assert response.status_code == 400
        assert "spatial_data" in response.json()["detail"]

    def test_visualize_spatial_requires_results(self, client: TestClient) -> None:
        response = client.post("/visualize/spatial", json=[])
        assert response.status_code == 400

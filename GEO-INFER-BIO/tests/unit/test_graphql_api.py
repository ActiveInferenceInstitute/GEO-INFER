"""Smoke tests for the GEO-INFER-BIO GraphQL API (FastAPI TestClient)."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from geo_infer_bio.api.graphql_api import app


@pytest.fixture()
def client() -> TestClient:
    return TestClient(app)


def _query(client: TestClient, query: str, variables: dict | None = None) -> dict:
    response = client.post("/graphql", json={"query": query, "variables": variables})
    assert response.status_code == 200
    return response.json()


class TestGraphqlApi:
    """FastAPI TestClient smoke tests for the GraphQL surface."""

    def test_health_check(self, client: TestClient) -> None:
        body = _query(client, "query { healthCheck }")
        assert body["data"]["healthCheck"] == "healthy"

    def test_analyze_sequence(self, client: TestClient) -> None:
        body = _query(
            client,
            """
            query($input: SequenceDataInput!) {
                analyzeSequence(sequenceData: $input) {
                    sequenceId
                    gcContent
                    motifCount
                    codingRegions
                }
            }
            """,
            {
                "input": {
                    "id": "seq-1",
                    "sequence": "ATCGATCGAAACCCGGG",
                    "spatialData": {"latitude": 37.7, "longitude": -122.4},
                }
            },
        )
        assert "errors" not in body, body.get("errors")
        result = body["data"]["analyzeSequence"]
        assert result["sequenceId"] == "seq-1"
        assert result["gcContent"] == pytest.approx(10 / 17 * 100)

    def test_analyze_sequence_rejects_invalid_sequence(self, client: TestClient) -> None:
        body = _query(
            client,
            """
            query($input: SequenceDataInput!) {
                analyzeSequence(sequenceData: $input) {
                    sequenceId
                }
            }
            """,
            {"input": {"id": "seq-1", "sequence": "XYZ123"}},
        )
        assert body["errors"], "invalid sequence must produce a GraphQL error"

    def test_analyze_file(self, client: TestClient, tmp_path) -> None:
        fasta_path = tmp_path / "sample.fasta"
        fasta_path.write_text(">seq-1\nATCGATCGAAACCCGGG\n", encoding="utf-8")
        body = _query(
            client,
            """
            query($path: String!) {
                analyzeFile(filePath: $path) {
                    sequenceId
                    gcContent
                }
            }
            """,
            {"path": str(fasta_path)},
        )
        assert "errors" not in body, body.get("errors")
        results = body["data"]["analyzeFile"]
        assert [r["sequenceId"] for r in results] == ["seq-1"]

    def test_health_check_via_playground_page(self, client: TestClient) -> None:
        response = client.get("/graphql")
        assert response.status_code == 200

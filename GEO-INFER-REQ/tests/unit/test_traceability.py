"""Tests for requirement traceability: trace matrix, coverage, impact analysis."""

import pytest
from geo_infer_req.core.traceability import (
    TraceabilityManager,
    TraceLink,
    ArtifactType,
)


@pytest.fixture
def manager():
    m = TraceabilityManager()
    m.register_requirement("R001", dependencies=[])
    m.register_requirement("R002", dependencies=["R001"])
    m.register_requirement("R003", dependencies=["R001", "R002"])
    m.register_requirement("R004")  # No deps, no links

    m.add_trace_links([
        TraceLink("R001", "auth.py", ArtifactType.SOURCE_CODE, verified=True),
        TraceLink("R001", "test_auth.py", ArtifactType.TEST_CASE, verified=True),
        TraceLink("R002", "api.py", ArtifactType.SOURCE_CODE),
        TraceLink("R002", "test_api.py", ArtifactType.TEST_CASE, verified=True),
        TraceLink("R003", "perf_test.py", ArtifactType.TEST_CASE),
    ])
    return m


class TestTraceabilityManager:
    def test_trace_matrix(self, manager):
        matrix = manager.build_trace_matrix()
        assert "R001" in matrix
        assert matrix["R001"].forward_coverage == 1.0
        assert matrix["R001"].verification_status == "fully_verified"

    def test_untraced_requirement(self, manager):
        matrix = manager.build_trace_matrix()
        assert "R004" in matrix
        assert matrix["R004"].forward_coverage == 0.0
        assert matrix["R004"].verification_status == "untraced"

    def test_partially_verified(self, manager):
        matrix = manager.build_trace_matrix()
        # R002 has one verified and one unverified link
        assert matrix["R002"].verification_status == "partially_verified"

    def test_coverage_analysis(self, manager):
        report = manager.analyze_coverage()
        assert report.total_requirements == 4
        assert report.traced_requirements == 3
        assert "R004" in report.untraced_requirements
        assert report.coverage_ratio == 0.75
        assert "source_code" in report.coverage_by_type

    def test_impact_analysis_direct(self, manager):
        impact = manager.analyze_impact("R001")
        assert "auth.py" in impact.directly_affected_artifacts
        assert "test_auth.py" in impact.directly_affected_artifacts
        # R002 and R003 depend on R001
        assert "R002" in impact.indirectly_affected_requirements
        assert "R003" in impact.indirectly_affected_requirements

    def test_impact_analysis_leaf(self, manager):
        impact = manager.analyze_impact("R003")
        assert len(impact.indirectly_affected_requirements) == 0
        assert len(impact.directly_affected_artifacts) == 1

    def test_impact_not_found(self, manager):
        with pytest.raises(KeyError, match="not registered"):
            manager.analyze_impact("R999")

    def test_unverified_links(self, manager):
        unverified = manager.get_unverified_links()
        assert len(unverified) == 2

    def test_verify_link(self, manager):
        assert manager.verify_link("R002", "api.py")
        unverified = manager.get_unverified_links()
        assert len(unverified) == 1

    def test_verify_nonexistent_link(self, manager):
        assert not manager.verify_link("R001", "nonexistent.py")

    def test_artifact_type_counts(self, manager):
        report = manager.analyze_coverage()
        assert report.artifact_counts["source_code"] == 2
        assert report.artifact_counts["test_case"] == 3

    def test_bidirectional_vs_unidirectional(self, manager):
        report = manager.analyze_coverage()
        assert report.bidirectional_links + report.unidirectional_links == 5


class TestVerifyLink:
    """verify_link marks existing links verified and reports misses."""

    def test_verify_existing_link(self, manager):
        before = len(manager.get_unverified_links())
        assert manager.verify_link("R002", "api.py") is True
        after = manager.get_unverified_links()
        assert len(after) == before - 1
        assert all(
            not (link.req_id == "R002" and link.artifact_id == "api.py")
            for link in after
        )

    def test_verify_missing_link_returns_false(self, manager):
        assert manager.verify_link("R001", "no_such_artifact.py") is False

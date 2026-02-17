"""Tests for GEO-INFER-REQ module initialization and imports."""

import pytest


class TestReqImports:
    def test_import_module(self):
        import geo_infer_req
        assert geo_infer_req.__version__ == "0.1.0"

    def test_import_requirements(self):
        from geo_infer_req import RequirementsAnalyzer, Requirement, RequirementType, PriorityLevel
        assert RequirementsAnalyzer is not None
        analyzer = RequirementsAnalyzer()
        assert analyzer is not None

    def test_import_traceability(self):
        from geo_infer_req import TraceabilityManager, TraceLink, ArtifactType
        assert TraceabilityManager is not None
        assert TraceLink is not None

    def test_import_validation(self):
        from geo_infer_req import RequirementValidator, RequirementSpec, ValidationSeverity
        assert RequirementValidator is not None
        assert RequirementSpec is not None

    def test_core_imports(self):
        from geo_infer_req.core import RequirementsAnalyzer, TraceabilityManager, RequirementValidator
        assert RequirementsAnalyzer is not None
        assert TraceabilityManager is not None
        assert RequirementValidator is not None

"""Tests for GEO-INFER-CIV module initialization and imports."""

import pytest


class TestCivImports:
    def test_import_module(self):
        import geo_infer_civ
        assert geo_infer_civ.__version__ == "0.1.0"

    def test_import_participation(self):
        from geo_infer_civ import ParticipationAnalyzer, ParticipationMethod, ParticipantRecord
        assert ParticipationAnalyzer is not None
        analyzer = ParticipationAnalyzer()
        assert analyzer is not None

    def test_import_engagement(self):
        from geo_infer_civ import AttendanceTracker, PublicCommentAnalyzer, VoterTurnoutModel
        assert AttendanceTracker is not None
        assert PublicCommentAnalyzer is not None
        assert VoterTurnoutModel is not None

    def test_import_policy(self):
        from geo_infer_civ import CostBenefitAnalyzer, StakeholderImpactAnalyzer, EquityAnalyzer
        assert CostBenefitAnalyzer is not None
        assert StakeholderImpactAnalyzer is not None
        assert EquityAnalyzer is not None

    def test_import_enums(self):
        from geo_infer_civ import ParticipationMethod, MeetingType, CommentCategory, ImpactLevel, PolicyDomain
        assert len(ParticipationMethod) > 0
        assert len(MeetingType) > 0
        assert len(CommentCategory) > 0
        assert len(ImpactLevel) > 0
        assert len(PolicyDomain) > 0

    def test_core_module_imports(self):
        from geo_infer_civ.core import ParticipationAnalyzer, AttendanceTracker, CostBenefitAnalyzer
        assert ParticipationAnalyzer is not None
        assert AttendanceTracker is not None
        assert CostBenefitAnalyzer is not None

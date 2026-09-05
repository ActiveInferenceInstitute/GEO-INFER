"""
Unit tests for ProgressTracker.

Tests progress tracking, competency reports, gap identification,
and at-risk learner detection.
"""

import json
import pytest
from datetime import datetime
from geo_infer_edu.core.progress import (
    ProgressTracker,
    LearnerProgress,
    LearnerActivity,
    CompetencyRecord,
    CompetencyLevel
)


class TestProgressTracker:
    """Test suite for ProgressTracker class."""
    
    @pytest.fixture
    def tracker(self):
        """Create a ProgressTracker instance for testing."""
        return ProgressTracker(
            competency_framework="geospatial_bok",
            analytics_level="detailed",
            privacy_compliance="ferpa"
        )
    
    @pytest.fixture
    def sample_activities(self):
        """Sample activity log for testing."""
        return [
            {
                "id": "act_1",
                "type": "exercise",
                "topic": "spatial_analysis",
                "start_time": datetime.now(),
                "status": "completed",
                "score": 0.85,
                "duration_minutes": 30,
                "attempts": 1
            },
            {
                "id": "act_2",
                "type": "reading",
                "topic": "geovisualization",
                "start_time": datetime.now(),
                "status": "completed",
                "duration_minutes": 20
            }
        ]
    
    @pytest.fixture
    def sample_assessments(self):
        """Sample assessment results for testing."""
        return [
            {
                "id": "assess_1",
                "competency": "spatial_analysis",
                "score": 0.8
            },
            {
                "id": "assess_2",
                "competency": "data_management",
                "score": 0.6
            }
        ]
    
    def test_init_default(self):
        """Test default initialization."""
        tracker = ProgressTracker()
        assert tracker.competency_framework == "geospatial_bok"
        assert tracker.analytics_level == "detailed"
    
    def test_track_progress(self, tracker, sample_activities):
        """Test basic progress tracking."""
        progress = tracker.track_progress(
            learner_id="learner_001",
            activity_log=sample_activities
        )
        
        assert isinstance(progress, LearnerProgress)
        assert progress.learner_id == "learner_001"
        assert len(progress.activities) == 2
        assert progress.total_time_hours > 0
    
    def test_track_progress_with_assessments(self, tracker, sample_activities, sample_assessments):
        """Test progress tracking with assessments."""
        progress = tracker.track_progress(
            learner_id="learner_002",
            activity_log=sample_activities,
            assessments=sample_assessments
        )
        
        assert len(progress.competencies) == 2
        assert "spatial_analysis" in progress.competencies
        assert "data_management" in progress.competencies
    
    def test_competency_level_assignment(self, tracker, sample_activities):
        """Test that competency levels are assigned correctly based on score."""
        assessments = [
            {"id": "a1", "competency": "high_score", "score": 0.95},
            {"id": "a2", "competency": "medium_score", "score": 0.65},
            {"id": "a3", "competency": "low_score", "score": 0.3}
        ]
        
        progress = tracker.track_progress(
            learner_id="learner_003",
            activity_log=sample_activities,
            assessments=assessments
        )
        
        assert progress.competencies["high_score"].level == CompetencyLevel.EXEMPLARY
        assert progress.competencies["medium_score"].level == CompetencyLevel.DEVELOPING
        assert progress.competencies["low_score"].level == CompetencyLevel.NOT_STARTED
    
    def test_completion_rate_calculation(self, tracker):
        """Test completion rate calculation."""
        activities = [
            {"id": "1", "type": "exercise", "topic": "a", "start_time": datetime.now(), 
             "status": "completed", "duration_minutes": 10},
            {"id": "2", "type": "exercise", "topic": "b", "start_time": datetime.now(), 
             "status": "completed", "duration_minutes": 10},
            {"id": "3", "type": "exercise", "topic": "c", "start_time": datetime.now(), 
             "status": "in_progress", "duration_minutes": 5}
        ]
        
        progress = tracker.track_progress("learner_004", activities)
        
        assert progress.completion_rate == pytest.approx(2/3, rel=0.01)
    
    def test_generate_competency_report(self, tracker, sample_activities, sample_assessments):
        """Test competency report generation."""
        tracker.track_progress("learner_005", sample_activities, sample_assessments)
        
        report = tracker.generate_competency_report(
            learner_id="learner_005",
            competencies=["spatial_analysis", "data_management", "geovisualization"],
            visualization="radar_chart"
        )
        
        assert report["learner_id"] == "learner_005"
        assert "competencies" in report
        assert "summary" in report
        assert len(report["competencies"]) == 3
        assert "visualization_data" in report
    
    def test_competency_report_summary(self, tracker, sample_activities, sample_assessments):
        """Test competency report summary statistics."""
        tracker.track_progress("learner_006", sample_activities, sample_assessments)
        
        report = tracker.generate_competency_report(
            learner_id="learner_006",
            competencies=["spatial_analysis", "data_management"]
        )
        
        summary = report["summary"]
        assert "total_competencies" in summary
        assert "proficient_or_above" in summary
        assert "developing" in summary
        assert "not_started" in summary
        assert summary["total_competencies"] == 2
    
    def test_competency_report_learner_not_found(self, tracker):
        """Test report generation for non-existent learner."""
        report = tracker.generate_competency_report(
            learner_id="nonexistent",
            competencies=["spatial_analysis"]
        )
        
        assert "error" in report
    
    def test_identify_gaps(self, tracker, sample_activities, sample_assessments):
        """Test knowledge gap identification."""
        progress = tracker.track_progress("learner_007", sample_activities, sample_assessments)
        
        required = ["spatial_analysis", "data_management", "geovisualization", "programming"]
        
        gaps = tracker.identify_gaps(
            learner_progress=progress,
            required_competencies=required,
            recommendations=True
        )
        
        assert "gaps" in gaps
        assert "gap_summary" in gaps
        assert "recommendations" in gaps
        # Should have gaps for competencies not proficient in
        assert len(gaps["gaps"]) > 0
    
    def test_gap_severity_levels(self, tracker, sample_activities):
        """Test gap severity classification."""
        # No assessments - all should be critical
        progress = tracker.track_progress("learner_008", sample_activities)
        
        gaps = tracker.identify_gaps(
            learner_progress=progress,
            required_competencies=["unknown_competency"],
            recommendations=True
        )
        
        assert len(gaps["gaps"]) == 1
        assert gaps["gaps"][0]["gap_severity"] == "critical"
    
    def test_generate_analytics(self, tracker, sample_activities, sample_assessments):
        """Test cohort analytics generation."""
        # Create some learner data
        for i in range(5):
            tracker.track_progress(f"learner_{i}", sample_activities, sample_assessments)
        
        cohort = [f"learner_{i}" for i in range(5)]
        
        analytics = tracker.generate_analytics(
            cohort=cohort,
            metrics=["completion_rate", "assessment_scores", "time_on_task", "engagement"],
            aggregation="weekly",
            visualization="dashboard"
        )
        
        assert analytics["cohort_size"] == 5
        assert "metrics" in analytics
        assert "completion_rate" in analytics["metrics"]
        assert "assessment_scores" in analytics["metrics"]
    
    def test_identify_at_risk(self, tracker):
        """Test at-risk learner identification."""
        # Create learners with different risk profiles
        # Learner with low engagement
        tracker.track_progress("at_risk_1", [
            {"id": "1", "type": "exercise", "topic": "a", "start_time": datetime.now(),
             "status": "completed", "duration_minutes": 5}
        ])
        
        # Learner with good engagement
        tracker.track_progress("good_learner", [
            {"id": f"{i}", "type": "exercise", "topic": "t", "start_time": datetime.now(),
             "status": "completed", "duration_minutes": 20, "score": 0.9}
            for i in range(10)
        ])
        
        at_risk = tracker.identify_at_risk(
            cohort=["at_risk_1", "good_learner"],
            risk_indicators=["low_engagement", "declining_scores", "missed_deadlines"],
            intervention_recommendations=True
        )
        
        # Should identify at least the low engagement learner
        at_risk_ids = [r["learner_id"] for r in at_risk]
        assert "at_risk_1" in at_risk_ids
    
    def test_at_risk_interventions(self, tracker):
        """Test that at-risk identification includes interventions."""
        tracker.track_progress("risk_learner", [
            {"id": "1", "type": "exercise", "topic": "a", "start_time": datetime.now(),
             "status": "abandoned", "duration_minutes": 5},
            {"id": "2", "type": "exercise", "topic": "b", "start_time": datetime.now(),
             "status": "abandoned", "duration_minutes": 5},
            {"id": "3", "type": "exercise", "topic": "c", "start_time": datetime.now(),
             "status": "abandoned", "duration_minutes": 5}
        ])
        
        at_risk = tracker.identify_at_risk(
            cohort=["risk_learner"],
            risk_indicators=["missed_deadlines"],
            intervention_recommendations=True
        )
        
        if at_risk:
            assert "interventions" in at_risk[0]
            assert len(at_risk[0]["interventions"]) > 0


class TestLearnerProgress:
    """Test suite for LearnerProgress dataclass."""
    
    def test_create_progress(self):
        """Test creating learner progress."""
        progress = LearnerProgress(learner_id="test_learner")
        
        assert progress.learner_id == "test_learner"
        assert progress.activities == []
        assert progress.competencies == {}
        assert progress.total_time_hours == 0
    
    def test_progress_with_activities(self):
        """Test progress with activities."""
        activity = LearnerActivity(
            activity_id="act_1",
            activity_type="exercise",
            topic="test",
            start_time=datetime.now(),
            time_spent_minutes=30
        )
        
        progress = LearnerProgress(
            learner_id="test",
            activities=[activity]
        )
        
        assert len(progress.activities) == 1


class TestCompetencyRecord:
    """Test suite for CompetencyRecord dataclass."""
    
    def test_create_record(self):
        """Test creating competency record."""
        record = CompetencyRecord(
            competency_id="spatial_analysis",
            competency_name="Spatial Analysis",
            level=CompetencyLevel.PROFICIENT
        )
        
        assert record.competency_id == "spatial_analysis"
        assert record.level == CompetencyLevel.PROFICIENT
        assert record.evidence == []
        assert record.confidence == 0.0
    
    def test_competency_levels(self):
        """Test all competency levels."""
        levels = [
            CompetencyLevel.NOT_STARTED,
            CompetencyLevel.EMERGING,
            CompetencyLevel.DEVELOPING,
            CompetencyLevel.PROFICIENT,
            CompetencyLevel.EXEMPLARY
        ]
        
        for level in levels:
            record = CompetencyRecord(
                competency_id="test",
                competency_name="Test",
                level=level
            )
            assert record.level == level


class TestPrivacyCompliance:
    """privacy_compliance must be enforced in progress exports."""

    @pytest.fixture
    def tracked(self):
        tracker = ProgressTracker(privacy_compliance="ferpa")
        tracker.track_progress(
            learner_id="student_42",
            activity_log=[{"type": "exercise", "topic": "spatial_thinking", "score": 0.9}],
        )
        return tracker

    def test_invalid_policy_rejected(self):
        from geo_infer_edu.core.progress import ProgressTracker

        with pytest.raises(ValueError, match="privacy_compliance"):
            ProgressTracker(privacy_compliance="hipaa")

    def test_ferpa_suppresses_identifier(self, tracked):
        export = json.loads(tracked.export_progress("student_42"))
        assert export["learner_id"] != "student_42"
        assert export["learner_id"].startswith("learner_")
        assert export["identifier_handling"] == "identifier_suppressed_ferpa"

    def test_gdpr_adds_retention_metadata(self):
        from geo_infer_edu.core.progress import ProgressTracker

        tracker = ProgressTracker(privacy_compliance="gdpr")
        tracker.track_progress(learner_id="student_7", activity_log=[])
        export = json.loads(tracker.export_progress("student_7"))
        assert export["learner_id"] == "student_7"
        assert export["data_retention"]["regulation"] == "gdpr"
        assert export["data_retention"]["erasure_available"] is True

    def test_none_includes_identifier(self):
        from geo_infer_edu.core.progress import ProgressTracker

        tracker = ProgressTracker(privacy_compliance="none")
        tracker.track_progress(learner_id="student_9", activity_log=[])
        export = json.loads(tracker.export_progress("student_9"))
        assert export["learner_id"] == "student_9"

    def test_export_unknown_learner_raises(self, tracked):
        with pytest.raises(ValueError, match="Learner not found"):
            tracked.export_progress("nobody")


class TestCompetencyOrdering:
    """Competency levels are ordered; later low scores must not downgrade records."""

    def test_low_score_assessment_does_not_downgrade(self):
        tracker = ProgressTracker()
        tracker.track_progress(
            learner_id="student_1",
            activity_log=[],
            assessments=[
                {"competency": "spatial_analysis", "score": 0.7, "id": "a1"},
                {"competency": "spatial_analysis", "score": 0.2, "id": "a2"},
            ],
        )
        record = tracker._learner_data["student_1"].competencies["spatial_analysis"]
        assert record.level is CompetencyLevel.DEVELOPING

    def test_higher_score_assessment_upgrades(self):
        tracker = ProgressTracker()
        tracker.track_progress(
            learner_id="student_2",
            activity_log=[],
            assessments=[
                {"competency": "spatial_analysis", "score": 0.5, "id": "a1"},
                {"competency": "spatial_analysis", "score": 0.92, "id": "a2"},
            ],
        )
        record = tracker._learner_data["student_2"].competencies["spatial_analysis"]
        assert record.level is CompetencyLevel.EXEMPLARY

    def test_export_serializes_competency_levels(self):
        """export_progress must return valid JSON even with competency records."""
        tracker = ProgressTracker(privacy_compliance="none")
        tracker.track_progress(
            learner_id="student_3",
            activity_log=[],
            assessments=[{"competency": "spatial_analysis", "score": 0.91}],
        )
        export = json.loads(tracker.export_progress("student_3"))
        assert export["competencies"]["spatial_analysis"]["level"] == "exemplary"

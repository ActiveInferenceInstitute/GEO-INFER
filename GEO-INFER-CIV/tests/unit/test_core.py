"""
Unit tests for GEO-INFER-CIV core functionality.
"""

import pytest

from geo_infer_civ import __version__


class TestCivicModule:
    """Test basic module functionality."""

    def test_module_import(self) -> None:
        """Test that the module can be imported."""
        import geo_infer_civ

        assert geo_infer_civ is not None

    def test_module_version(self) -> None:
        """Test that module has a version."""
        assert __version__ is not None
        assert isinstance(__version__, str)

    def test_module_structure(self) -> None:
        """Exported analyzers construct and honor their contracts."""
        import geo_infer_civ
        from geo_infer_civ.core.civic_engagement import MeetingRecord, MeetingType
        from geo_infer_civ.core.participation import (
            ParticipantRecord,
            ParticipationMethod,
        )

        analyzer = geo_infer_civ.ParticipationAnalyzer()
        analyzer.add_record(
            ParticipantRecord(
                participant_id="p-1",
                method=ParticipationMethod.SURVEY,
                timestamp=1.0,
                sentiment_score=0.5,
            )
        )
        summary = analyzer.get_participation_summary()
        assert summary["total_records"] == 1
        assert summary["method_counts"] == {"survey": 1}
        assert summary["average_sentiment"] == 0.5

        tracker = geo_infer_civ.AttendanceTracker()
        tracker.add_meeting(
            MeetingRecord(
                meeting_id="m-1",
                meeting_type=MeetingType.CITY_COUNCIL,
                date=1.0,
                registered_attendees=10,
                actual_attendees=8,
            )
        )
        trend = tracker.compute_attendance_trend(MeetingType.CITY_COUNCIL)
        assert trend.attendance_rate == pytest.approx(0.8)

        assert geo_infer_civ.CostBenefitAnalyzer() is not None
        with pytest.raises(ValueError):
            geo_infer_civ.CostBenefitAnalyzer(discount_rate=1.5)

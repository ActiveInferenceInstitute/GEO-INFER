"""Tests for civic engagement metrics: attendance, comments, voter turnout."""

import pytest
from geo_infer_civ.core.civic_engagement import (
    AttendanceTracker,
    PublicCommentAnalyzer,
    VoterTurnoutModel,
    MeetingRecord,
    MeetingType,
    PublicComment,
    CommentCategory,
)


@pytest.fixture
def tracker():
    return AttendanceTracker()


@pytest.fixture
def comment_analyzer():
    return PublicCommentAnalyzer()


@pytest.fixture
def turnout_model():
    return VoterTurnoutModel()


@pytest.fixture
def sample_meetings():
    meetings = []
    types = [MeetingType.CITY_COUNCIL, MeetingType.TOWN_HALL, MeetingType.PUBLIC_HEARING]
    for i in range(12):
        meetings.append(MeetingRecord(
            meeting_id=f"m_{i}",
            meeting_type=types[i % 3],
            date=1000.0 + i * 30,
            registered_attendees=100 + i * 5,
            actual_attendees=50 + i * 3,
            public_comments_count=5 + i,
        ))
    return meetings


@pytest.fixture
def sample_comments():
    comments = []
    categories = list(CommentCategory)
    for i in range(30):
        comments.append(PublicComment(
            comment_id=f"c_{i}",
            meeting_id=f"m_{i % 12}",
            category=categories[i % len(categories)],
            word_count=50 + i * 10,
            timestamp=1000.0 + i * 10,
            submitter_id=f"s_{i % 15}",
            topic="zoning" if i % 3 == 0 else "budget",
            sentiment_score=-0.5 + (i % 10) * 0.15,
        ))
    return comments


class TestAttendanceTracker:
    def test_empty_raises_error(self, tracker):
        with pytest.raises(ValueError, match="No meeting"):
            tracker.compute_attendance_trend()

    def test_trend_computation(self, tracker, sample_meetings):
        tracker.add_meetings(sample_meetings)
        trend = tracker.compute_attendance_trend()
        assert trend.meeting_count == 12
        assert trend.average_attendance > 0
        assert trend.attendance_rate > 0
        assert trend.trend_direction in ("increasing", "decreasing", "stable")
        assert trend.peak_meeting_type in [t.value for t in MeetingType]

    def test_trend_by_type(self, tracker, sample_meetings):
        tracker.add_meetings(sample_meetings)
        trend = tracker.compute_attendance_trend(meeting_type=MeetingType.CITY_COUNCIL)
        assert trend.meeting_count == 4  # 12 meetings / 3 types

    def test_meeting_effectiveness(self, tracker, sample_meetings):
        tracker.add_meetings(sample_meetings)
        eff = tracker.get_meeting_effectiveness("m_0")
        assert "effectiveness_score" in eff
        assert 0.0 <= eff["effectiveness_score"] <= 1.0
        assert eff["attendance_rate"] > 0.0

    def test_meeting_not_found(self, tracker):
        with pytest.raises(ValueError, match="not found"):
            tracker.get_meeting_effectiveness("nonexistent")

    def test_add_single_meeting(self, tracker):
        tracker.add_meeting(MeetingRecord(
            meeting_id="solo",
            meeting_type=MeetingType.WORKSHOP,
            date=1000.0,
            registered_attendees=50,
            actual_attendees=30,
        ))
        trend = tracker.compute_attendance_trend()
        assert trend.meeting_count == 1
        assert trend.average_attendance == 30.0


class TestPublicCommentAnalyzer:
    def test_empty_analysis(self, comment_analyzer):
        result = comment_analyzer.analyze()
        assert result.total_comments == 0
        assert result.engagement_depth_score == 0.0

    def test_analysis_with_data(self, comment_analyzer, sample_comments):
        comment_analyzer.add_comments(sample_comments)
        result = comment_analyzer.analyze()
        assert result.total_comments == 30
        assert result.unique_submitters == 15
        assert result.average_word_count > 0
        assert len(result.category_distribution) > 1
        assert result.engagement_depth_score > 0.0

    def test_analysis_filtered_by_meeting(self, comment_analyzer, sample_comments):
        comment_analyzer.add_comments(sample_comments)
        result = comment_analyzer.analyze(meeting_id="m_0")
        assert result.total_comments > 0
        assert result.total_comments < 30

    def test_topics_counted(self, comment_analyzer, sample_comments):
        comment_analyzer.add_comments(sample_comments)
        result = comment_analyzer.analyze()
        assert "zoning" in result.topics
        assert "budget" in result.topics

    def test_category_proportions_sum_to_one(self, comment_analyzer, sample_comments):
        comment_analyzer.add_comments(sample_comments)
        result = comment_analyzer.analyze()
        total = sum(result.category_distribution.values())
        assert abs(total - 1.0) < 0.01


class TestVoterTurnoutModel:
    def test_empty_average_raises(self, turnout_model):
        with pytest.raises(ValueError, match="No election"):
            turnout_model.compute_average_turnout()

    def test_average_turnout(self, turnout_model):
        turnout_model.add_election("e1", 1000, 600, "general", 1000.0)
        turnout_model.add_election("e2", 1000, 400, "general", 2000.0)
        avg = turnout_model.compute_average_turnout()
        assert avg == 0.5

    def test_average_by_type(self, turnout_model):
        turnout_model.add_election("e1", 1000, 600, "general", 1000.0)
        turnout_model.add_election("e2", 1000, 200, "primary", 2000.0)
        assert turnout_model.compute_average_turnout("general") == 0.6
        assert turnout_model.compute_average_turnout("primary") == 0.2

    def test_predict_turnout(self, turnout_model):
        for i in range(10):
            turnout_model.add_election(
                f"e_{i}", 1000, 400 + i * 20, "general", 1000.0 + i * 365,
                is_contested=True, media_coverage_score=0.5,
            )
        prediction = turnout_model.predict_turnout(
            eligible_voters=2000,
            election_type="general",
            is_contested=True,
            media_coverage_score=0.7,
        )
        assert 0.0 <= prediction["predicted_turnout_rate"] <= 1.0
        assert prediction["predicted_voters"] > 0
        assert prediction["confidence"] > 0

    def test_predict_uncontested_lower(self, turnout_model):
        for i in range(5):
            turnout_model.add_election(f"c_{i}", 1000, 600, "general", 1000.0 + i, is_contested=True)
        for i in range(5):
            turnout_model.add_election(f"u_{i}", 1000, 300, "general", 2000.0 + i, is_contested=False)

        contested = turnout_model.predict_turnout(1000, "general", is_contested=True)
        uncontested = turnout_model.predict_turnout(1000, "general", is_contested=False)
        assert uncontested["predicted_turnout_rate"] < contested["predicted_turnout_rate"]

    def test_turnout_summary(self, turnout_model):
        turnout_model.add_election("e1", 1000, 600, "general", 1000.0)
        turnout_model.add_election("e2", 500, 100, "primary", 2000.0)
        summary = turnout_model.get_turnout_summary()
        assert summary["total_elections"] == 2
        assert "general" in summary["by_type"]
        assert "primary" in summary["by_type"]

    def test_predict_no_data_raises(self, turnout_model):
        with pytest.raises(ValueError, match="No historical"):
            turnout_model.predict_turnout(1000, "general")

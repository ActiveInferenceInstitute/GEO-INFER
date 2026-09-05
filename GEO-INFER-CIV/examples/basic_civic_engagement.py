"""Basic civic engagement example using GEO-INFER-CIV.

Demonstrates the three pillars of the module against the real public API:
meeting attendance tracking, participation analysis, and cost-benefit
appraisal of a policy proposal. Runs entirely offline on synthetic data.
"""

from geo_infer_civ import (
    AttendanceTracker,
    CostBenefitAnalyzer,
    CostBenefitItem,
    MeetingRecord,
    MeetingType,
    ParticipantRecord,
    ParticipationAnalyzer,
    ParticipationMethod,
    PublicComment,
    PublicCommentAnalyzer,
    CommentCategory,
)


def attendance_example() -> None:
    """Track meeting attendance and report the trend."""
    tracker = AttendanceTracker()
    tracker.add_meetings(
        [
            MeetingRecord("mtg_001", MeetingType.CITY_COUNCIL, 1704067200.0, 200, 145, 23),
            MeetingRecord("mtg_002", MeetingType.CITY_COUNCIL, 1706745600.0, 200, 162, 31),
            MeetingRecord("mtg_003", MeetingType.TOWN_HALL, 1705881600.0, 300, 187, 56),
            MeetingRecord("mtg_004", MeetingType.BUDGET_HEARING, 1708041600.0, 120, 78, 28),
        ]
    )
    trend = tracker.compute_attendance_trend()
    print("--- Attendance ---")
    print(f"Average attendance: {trend.average_attendance}")
    print(f"Attendance rate: {trend.attendance_rate:.1%}")
    print(f"Trend direction: {trend.trend_direction}")


def participation_example() -> None:
    """Score engagement and representation for a participation program."""
    analyzer = ParticipationAnalyzer()
    analyzer.add_records(
        [
            ParticipantRecord("p01", ParticipationMethod.TOWN_HALL, 1705276800.0, "north"),
            ParticipantRecord("p02", ParticipationMethod.SURVEY, 1705363200.0, "north"),
            ParticipantRecord("p03", ParticipationMethod.PUBLIC_COMMENT, 1705449600.0, "south"),
            ParticipantRecord("p04", ParticipationMethod.ONLINE_FORUM, 1705536000.0, "east"),
            ParticipantRecord("p05", ParticipationMethod.WORKSHOP, 1705622400.0, "south"),
            ParticipantRecord("p06", ParticipationMethod.MAP_ANNOTATION, 1705708800.0, "north"),
        ]
    )
    score = analyzer.compute_engagement_score(target_population=5000)
    index = analyzer.compute_participation_index(target_population=50, baseline_rate=0.10)
    report = analyzer.analyze_representation({"north": 0.5, "south": 0.3, "east": 0.2})
    print("\n--- Participation ---")
    print(f"Overall engagement score: {score.overall_score:.3f}")
    print(f"Participation index (vs 10% baseline): {index:.2f}")
    print(f"Underrepresented groups: {report.underrepresented_groups}")
    print(f"Overrepresented groups: {report.overrepresented_groups}")


def comments_example() -> None:
    """Analyze categorized public comments for engagement depth."""
    analyzer = PublicCommentAnalyzer()
    analyzer.add_comments(
        [
            PublicComment("c01", "mtg_005", CommentCategory.SUPPORT, 150, 1705276900.0, "p001", "zoning"),
            PublicComment("c02", "mtg_005", CommentCategory.OPPOSITION, 280, 1705277000.0, "p002", "zoning"),
            PublicComment("c03", "mtg_005", CommentCategory.QUESTION, 45, 1705277100.0, "p003", "zoning"),
            PublicComment("c04", "mtg_005", CommentCategory.CONCERN, 120, 1705277300.0, "p004", "transit"),
            PublicComment("c05", "mtg_005", CommentCategory.SUGGESTION, 200, 1705277200.0, "p005", "transit"),
        ]
    )
    analysis = analyzer.analyze(meeting_id="mtg_005")
    print("\n--- Public Comments ---")
    print(f"Total comments: {analysis.total_comments}")
    print(f"Category distribution: {analysis.category_distribution}")
    print(f"Engagement depth score: {analysis.engagement_depth_score:.3f}")


def cost_benefit_example() -> None:
    """Appraise a flood-mitigation proposal."""
    cba = CostBenefitAnalyzer(discount_rate=0.05)
    cba.add_items(
        [
            CostBenefitItem("construction", 250_000.0, is_benefit=False),
            CostBenefitItem("flood avoidance", 900_000.0, is_benefit=True, time_horizon_years=10),
        ]
    )
    result = cba.analyze()
    print("\n--- Cost-Benefit ---")
    print(f"NPV: ${result.net_present_value:,.0f}")
    print(f"Benefit-cost ratio: {result.benefit_cost_ratio:.2f}")
    print(f"IRR: {result.internal_rate_of_return:.3f}")
    print(f"Payback period: {result.payback_period_years:.1f} years")


def main() -> None:
    """Run the basic civic engagement example."""
    print("=" * 60)
    print("GEO-INFER-CIV: Basic Civic Engagement Example")
    print("=" * 60)
    attendance_example()
    participation_example()
    comments_example()
    cost_benefit_example()
    print("\nExample complete.")


if __name__ == "__main__":
    main()

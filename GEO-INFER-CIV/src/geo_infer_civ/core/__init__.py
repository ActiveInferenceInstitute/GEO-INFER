"""Core civic engagement functionality."""

try:
    from .participation import (
        ParticipationAnalyzer,
        ParticipationMethod,
        ParticipantRecord,
        EngagementScore,
        RepresentationReport,
    )
except ImportError:
    ParticipationAnalyzer = None

try:
    from .civic_engagement import (
        AttendanceTracker,
        PublicCommentAnalyzer,
        VoterTurnoutModel,
        MeetingRecord,
        MeetingType,
        PublicComment,
        CommentCategory,
        AttendanceTrend,
        CommentAnalysis,
    )
except ImportError:
    AttendanceTracker = None

try:
    from .policy_analysis import (
        CostBenefitAnalyzer,
        StakeholderImpactAnalyzer,
        EquityAnalyzer,
        CostBenefitItem,
        StakeholderImpact,
        ImpactLevel,
        PolicyDomain,
        CostBenefitResult,
        EquityScore,
    )
except ImportError:
    CostBenefitAnalyzer = None

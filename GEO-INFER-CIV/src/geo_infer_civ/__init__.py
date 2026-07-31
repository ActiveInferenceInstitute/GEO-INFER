"""
GEO-INFER-CIV: Civic Engagement and Participatory Mapping

This module provides tools for community engagement, participatory mapping,
citizen science, and collaborative geospatial decision-making.
"""

__version__ = "0.1.0"
__author__ = "GEO-INFER Development Team"

try:
    from .core.participation import (
        ParticipationAnalyzer,
        ParticipationMethod,
        ParticipantRecord,
        EngagementScore,
        RepresentationReport,
    )
except ImportError:
    ParticipationAnalyzer = None

try:
    from .core.civic_engagement import (
        AttendanceTracker,
        PublicCommentAnalyzer,
        VoterTurnoutModel,
        MeetingRecord,
        MeetingType,
        PublicComment,
        CommentCategory,
    )
except ImportError:
    AttendanceTracker = None

try:
    from .core.policy_analysis import (
        CostBenefitAnalyzer,
        StakeholderImpactAnalyzer,
        EquityAnalyzer,
        CostBenefitItem,
        StakeholderImpact,
        ImpactLevel,
        PolicyDomain,
    )
except ImportError:
    CostBenefitAnalyzer = None

__all__ = [
    "ParticipationAnalyzer",
    "ParticipationMethod",
    "ParticipantRecord",
    "EngagementScore",
    "RepresentationReport",
    "AttendanceTracker",
    "PublicCommentAnalyzer",
    "VoterTurnoutModel",
    "MeetingRecord",
    "MeetingType",
    "PublicComment",
    "CommentCategory",
    "CostBenefitAnalyzer",
    "StakeholderImpactAnalyzer",
    "EquityAnalyzer",
    "CostBenefitItem",
    "StakeholderImpact",
    "ImpactLevel",
    "PolicyDomain",
]

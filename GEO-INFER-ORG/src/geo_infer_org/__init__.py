"""
GEO-INFER-ORG: Organizational Modeling

This module provides tools for organizational structure modeling,
governance, team coordination, and collaboration network analysis.
"""

__version__ = "0.1.0"
__author__ = "GEO-INFER Development Team"

try:
    from .core.organization import (
        OrganizationModel,
        OrgUnit,
        Role,
        Resource,
        OrgStructureType,
        RoleLevel,
        OrgMetrics,
    )
except ImportError:
    OrganizationModel = None

try:
    from .core.governance import (
        VotingEngine,
        ConsensusModel,
        VotingMethod,
        DecisionStatus,
        Vote,
        Proposal,
        VotingResult,
    )
except ImportError:
    VotingEngine = None

try:
    from .core.collaboration import (
        CollaborationNetwork,
        TeamFormation,
        CollaborationEdge,
        CollaborationType,
        TeamMember,
        NetworkMetrics,
        TeamFormationResult,
    )
except ImportError:
    CollaborationNetwork = None

__all__ = [
    "OrganizationModel",
    "OrgUnit",
    "Role",
    "Resource",
    "OrgStructureType",
    "RoleLevel",
    "OrgMetrics",
    "VotingEngine",
    "ConsensusModel",
    "VotingMethod",
    "DecisionStatus",
    "Vote",
    "Proposal",
    "VotingResult",
]

"""Core organizational modeling functionality."""

try:
    from .organization import (
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
    from .governance import (
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
    from .collaboration import (
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

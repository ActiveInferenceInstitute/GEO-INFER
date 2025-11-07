"""Integration modules for GEO-INFER-METAGOV with other GEO-INFER modules."""

from geo_infer_metagov.integrations.spatial import SpatialGovernanceIntegration
from geo_infer_metagov.integrations.organizational import OrganizationalGovernanceIntegration
from geo_infer_metagov.integrations.security import SecurityGovernanceIntegration
from geo_infer_metagov.integrations.normative import NormativeGovernanceIntegration

__all__ = [
    "SpatialGovernanceIntegration",
    "OrganizationalGovernanceIntegration",
    "SecurityGovernanceIntegration",
    "NormativeGovernanceIntegration",
]




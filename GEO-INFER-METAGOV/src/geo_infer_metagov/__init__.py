"""
GEO-INFER-METAGOV: Meta-Governance and Organizational Governance Methods

This module implements comprehensive meta-governance, organizational governance,
and multi-level governance coordination frameworks for autonomous geospatial systems.
"""

__version__ = "4.0.0"
__author__ = "GEO-INFER Development Team"
__license__ = "CC BY-ND-SA 4.0"

from geo_infer_metagov.core.multi_level import MultiLevelGovernanceFramework
from geo_infer_metagov.core.institutional import InstitutionalDesigner
from geo_infer_metagov.core.stakeholder import StakeholderGovernanceCoordinator
from geo_infer_metagov.core.polycentric import PolycentricGovernanceSystem
from geo_infer_metagov.core.adaptation import AdaptiveGovernanceSystem
from geo_infer_metagov.core.accountability import AccountabilityFramework

__all__ = [
    "MultiLevelGovernanceFramework",
    "InstitutionalDesigner",
    "StakeholderGovernanceCoordinator",
    "PolycentricGovernanceSystem",
    "AdaptiveGovernanceSystem",
    "AccountabilityFramework",
]

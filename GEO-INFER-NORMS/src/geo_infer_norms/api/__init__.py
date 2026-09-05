"""
API module for GEO-INFER-NORMS geospatial normative and legal analysis.

This module provides API endpoints and interfaces for interacting with
the normative and legal analysis functionality.
"""

from geo_infer_norms.api.compliance_api import ComplianceAPI as ComplianceAPI
from geo_infer_norms.api.legal_api import LegalAPI as LegalAPI
from geo_infer_norms.api.zoning_api import ZoningAPI as ZoningAPI
from geo_infer_norms.api.policy_api import PolicyAPI as PolicyAPI
from geo_infer_norms.api.normative_api import NormativeAPI as NormativeAPI
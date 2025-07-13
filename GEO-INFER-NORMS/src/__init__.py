"""
GEO-INFER-NORMS: Social-technical compliance modeling with deterministic and probabilistic aspects.

This module provides tools and frameworks for understanding, modeling, and analyzing social norms,
regulatory frameworks, and compliance requirements in spatial contexts.
"""

__version__ = "0.1.0"
__author__ = "GEO-INFER Team"
__email__ = "blanket@activeinference.institute"

# Import core submodules with error handling
try:
    from .core import (
        legal_frameworks,
        zoning_analysis,
        compliance_tracking,
        policy_impact,
        normative_inference
    )
except ImportError as e:
    import logging
    logging.warning(f"NORMS core submodules not available: {e}")

try:
    from .models import (
        legal_entity,
        regulation,
        compliance_status,
        zoning,
        policy
    )
except ImportError as e:
    import logging
    logging.warning(f"NORMS models submodules not available: {e}") 
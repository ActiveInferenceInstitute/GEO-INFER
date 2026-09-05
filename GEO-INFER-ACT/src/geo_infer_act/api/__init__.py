"""
API interfaces for GEO-INFER-ACT module.

This module provides standardized interfaces for interacting with
the active inference components and integration with other modules.
"""

from geo_infer_act.api.interface import ActiveInferenceInterface as ActiveInferenceInterface
from geo_infer_act.api.client import Client as Client
from geo_infer_act.api.endpoints import create_endpoints as create_endpoints
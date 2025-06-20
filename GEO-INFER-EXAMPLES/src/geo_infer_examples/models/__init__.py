#!/usr/bin/env python3
"""
GEO-INFER Examples Models Package

Comprehensive data models and structures for cross-module integrations.
"""

from .integration_models import (
    # Enums
    ModuleType,
    DataFormat,
    IntegrationPattern,
    
    # Core Models
    ModuleSpec,
    ModuleConnection,
    WorkflowStep,
    WorkflowDefinition,
    ExecutionContext,
    
    # Data Models
    SpatialTemporalData,
    AnalysisResult,
    IntegrationResult,
    
    # Domain-Specific Models
    HealthSurveillanceData,
    AgriculturalData,
    UrbanPlanningData,
    ClimateData,
    
    # Utilities
    IntegrationPatterns,
    DataFormatConverter,
    load_workflow_from_file,
    save_workflow_to_file,
    GEO_INFER_MODULES
)

__all__ = [
    # Enums
    'ModuleType',
    'DataFormat', 
    'IntegrationPattern',
    
    # Core Models
    'ModuleSpec',
    'ModuleConnection',
    'WorkflowStep',
    'WorkflowDefinition',
    'ExecutionContext',
    
    # Data Models
    'SpatialTemporalData',
    'AnalysisResult',
    'IntegrationResult',
    
    # Domain-Specific Models
    'HealthSurveillanceData',
    'AgriculturalData',
    'UrbanPlanningData',
    'ClimateData',
    
    # Utilities
    'IntegrationPatterns',
    'DataFormatConverter',
    'load_workflow_from_file',
    'save_workflow_to_file',
    'GEO_INFER_MODULES'
]

__version__ = "1.0.0"
__author__ = "GEO-INFER Team"
__email__ = "info@geo-infer.org" 
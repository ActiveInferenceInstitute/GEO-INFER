"""
GEO-INFER-REQ: Requirements and Dependencies

This module provides tools for requirements analysis, dependency resolution,
traceability tracking, and requirement validation.
"""

__version__ = "0.1.0"
__author__ = "GEO-INFER Development Team"

try:
    from .core.requirements import (
        RequirementsAnalyzer,
        Requirement,
        RequirementType,
        RequirementStatus,
        PriorityLevel,
        DependencyGraph,
        CompletenessReport,
    )
except ImportError:
    RequirementsAnalyzer = None

try:
    from .core.traceability import (
        TraceabilityManager,
        TraceLink,
        ArtifactType,
        TraceMatrixEntry,
        CoverageReport,
        ImpactReport,
    )
except ImportError:
    TraceabilityManager = None

try:
    from .core.validation import (
        RequirementValidator,
        RequirementSpec,
        ValidationIssue,
        ValidationSeverity,
        ConflictType,
        ConflictDetectionResult,
        ConsistencyReport,
        FeasibilityAssessment,
    )
except ImportError:
    RequirementValidator = None

__all__ = [
    "RequirementsAnalyzer",
    "Requirement",
    "RequirementType",
    "RequirementStatus",
    "PriorityLevel",
    "DependencyGraph",
    "CompletenessReport",
    "TraceabilityManager",
    "TraceLink",
    "ArtifactType",
    "TraceMatrixEntry",
    "CoverageReport",
    "ImpactReport",
    "RequirementValidator",
]

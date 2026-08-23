"""Core requirements management functionality."""

from .requirements import (
    RequirementsAnalyzer,
    Requirement,
    RequirementType,
    RequirementStatus,
    PriorityLevel,
    DependencyGraph,
    CompletenessReport,
)
from .traceability import (
    TraceabilityManager,
    TraceLink,
    ArtifactType,
    TraceMatrixEntry,
    CoverageReport,
    ImpactReport,
)
from .validation import (
    RequirementValidator,
    RequirementSpec,
    ValidationIssue,
    ValidationSeverity,
    ConflictType,
    ConflictDetectionResult,
    ConsistencyReport,
    FeasibilityAssessment,
)

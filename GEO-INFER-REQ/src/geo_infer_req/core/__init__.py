"""Core requirements management functionality."""

from .requirements import (
    RequirementsAnalyzer as RequirementsAnalyzer,
    Requirement as Requirement,
    RequirementType as RequirementType,
    RequirementStatus as RequirementStatus,
    PriorityLevel as PriorityLevel,
    DependencyGraph as DependencyGraph,
    CompletenessReport as CompletenessReport,
)
from .traceability import (
    TraceabilityManager as TraceabilityManager,
    TraceLink as TraceLink,
    ArtifactType as ArtifactType,
    TraceMatrixEntry as TraceMatrixEntry,
    CoverageReport as CoverageReport,
    ImpactReport as ImpactReport,
)
from .validation import (
    RequirementValidator as RequirementValidator,
    RequirementSpec as RequirementSpec,
    ValidationIssue as ValidationIssue,
    ValidationSeverity as ValidationSeverity,
    ConflictType as ConflictType,
    ConflictDetectionResult as ConflictDetectionResult,
    ConsistencyReport as ConsistencyReport,
    FeasibilityAssessment as FeasibilityAssessment,
)

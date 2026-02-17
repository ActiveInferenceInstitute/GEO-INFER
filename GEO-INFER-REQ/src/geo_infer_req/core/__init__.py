"""Core requirements management functionality."""

try:
    from .requirements import (
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
    from .traceability import (
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
except ImportError:
    RequirementValidator = None

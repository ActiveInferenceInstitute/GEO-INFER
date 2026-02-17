"""
Requirement validation for GEO-INFER-REQ.

Provides consistency checking, conflict detection,
and feasibility scoring for requirement specifications.
"""

import re
from typing import Dict, List, Optional, Tuple, Set, Any
from dataclasses import dataclass, field
from enum import Enum


class ConflictType(Enum):
    """Types of requirement conflicts."""
    CONTRADICTORY = "contradictory"
    OVERLAPPING = "overlapping"
    RESOURCE_CONFLICT = "resource_conflict"
    PRIORITY_CONFLICT = "priority_conflict"
    TEMPORAL_CONFLICT = "temporal_conflict"


class ValidationSeverity(Enum):
    """Severity levels for validation issues."""
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


@dataclass
class ValidationIssue:
    """A single validation issue found during checking."""
    issue_id: str
    severity: ValidationSeverity
    req_ids: List[str]
    description: str
    suggestion: Optional[str] = None


@dataclass
class ConflictDetectionResult:
    """Result of conflict detection analysis."""
    total_conflicts: int
    conflicts: List[ValidationIssue]
    conflict_pairs: List[Tuple[str, str]]
    severity_distribution: Dict[str, int]


@dataclass
class ConsistencyReport:
    """Report on requirement specification consistency."""
    is_consistent: bool
    total_issues: int
    errors: List[ValidationIssue]
    warnings: List[ValidationIssue]
    info_items: List[ValidationIssue]
    consistency_score: float


@dataclass
class FeasibilityAssessment:
    """Feasibility assessment for a set of requirements."""
    overall_feasibility: float
    per_requirement_scores: Dict[str, float]
    risk_factors: List[str]
    bottleneck_requirements: List[str]
    resource_utilization: float


@dataclass
class RequirementSpec:
    """Simplified requirement spec for validation purposes."""
    req_id: str
    title: str
    description: str
    priority: int  # 1-4
    effort_estimate: float  # person-days
    dependencies: List[str] = field(default_factory=list)
    constraints: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    resources_required: List[str] = field(default_factory=list)


class RequirementValidator:
    """
    Validates requirement specifications for consistency,
    completeness, and feasibility.

    Detects conflicts between requirements, checks logical
    consistency, and scores implementation feasibility.
    """

    def __init__(self) -> None:
        self._specs: Dict[str, RequirementSpec] = {}
        self._resource_capacity: Dict[str, float] = {}

    def add_spec(self, spec: RequirementSpec) -> None:
        """
        Add a requirement specification for validation.

        Args:
            spec: The requirement specification.
        """
        self._specs[spec.req_id] = spec

    def add_specs(self, specs: List[RequirementSpec]) -> None:
        """
        Add multiple requirement specifications.

        Args:
            specs: List of requirement specifications.
        """
        for spec in specs:
            self.add_spec(spec)

    def set_resource_capacity(self, resources: Dict[str, float]) -> None:
        """
        Set available resource capacities for feasibility analysis.

        Args:
            resources: Mapping of resource name to available capacity (person-days).
        """
        self._resource_capacity = dict(resources)

    def check_consistency(self) -> ConsistencyReport:
        """
        Check the overall consistency of all requirement specs.

        Validates:
        - No circular dependencies
        - All referenced dependencies exist
        - No duplicate titles
        - Descriptions meet minimum length
        - Priority values are valid

        Returns:
            ConsistencyReport with all found issues.
        """
        errors: List[ValidationIssue] = []
        warnings: List[ValidationIssue] = []
        info_items: List[ValidationIssue] = []
        issue_counter = 0

        all_ids = set(self._specs.keys())

        # Check for dangling dependencies
        for rid, spec in self._specs.items():
            for dep in spec.dependencies:
                if dep not in all_ids:
                    issue_counter += 1
                    errors.append(ValidationIssue(
                        issue_id=f"E{issue_counter:04d}",
                        severity=ValidationSeverity.ERROR,
                        req_ids=[rid],
                        description=f"Dependency '{dep}' referenced by {rid} does not exist",
                        suggestion=f"Add requirement '{dep}' or remove the dependency",
                    ))

        # Check for circular dependencies
        cycles = self._detect_dependency_cycles()
        for cycle in cycles:
            issue_counter += 1
            errors.append(ValidationIssue(
                issue_id=f"E{issue_counter:04d}",
                severity=ValidationSeverity.ERROR,
                req_ids=cycle,
                description=f"Circular dependency detected: {' -> '.join(cycle)}",
                suggestion="Break the circular dependency by removing one link",
            ))

        # Check for duplicate titles
        titles: Dict[str, List[str]] = {}
        for rid, spec in self._specs.items():
            normalized = spec.title.strip().lower()
            if normalized not in titles:
                titles[normalized] = []
            titles[normalized].append(rid)

        for title, rids in titles.items():
            if len(rids) > 1:
                issue_counter += 1
                warnings.append(ValidationIssue(
                    issue_id=f"W{issue_counter:04d}",
                    severity=ValidationSeverity.WARNING,
                    req_ids=rids,
                    description=f"Duplicate title found: '{title}' in requirements {rids}",
                    suggestion="Consider merging or differentiating these requirements",
                ))

        # Check description quality
        for rid, spec in self._specs.items():
            if len(spec.description.strip()) < 10:
                issue_counter += 1
                warnings.append(ValidationIssue(
                    issue_id=f"W{issue_counter:04d}",
                    severity=ValidationSeverity.WARNING,
                    req_ids=[rid],
                    description=f"Requirement {rid} has a very short description",
                    suggestion="Provide a more detailed description (at least 10 characters)",
                ))

        total = len(errors) + len(warnings) + len(info_items)
        is_consistent = len(errors) == 0
        max_possible_issues = len(self._specs) * 3
        consistency_score = max(0.0, 1.0 - total / max_possible_issues) if max_possible_issues > 0 else 1.0

        return ConsistencyReport(
            is_consistent=is_consistent,
            total_issues=total,
            errors=errors,
            warnings=warnings,
            info_items=info_items,
            consistency_score=round(consistency_score, 4),
        )

    def detect_conflicts(self) -> ConflictDetectionResult:
        """
        Detect conflicts between requirements.

        Checks for:
        - Contradictory constraints
        - Resource conflicts
        - Priority conflicts (same priority, conflicting goals)
        - Overlapping specifications

        Returns:
            ConflictDetectionResult with found conflicts.
        """
        conflicts: List[ValidationIssue] = []
        conflict_pairs: List[Tuple[str, str]] = []
        issue_counter = 0

        specs_list = list(self._specs.values())

        for i in range(len(specs_list)):
            for j in range(i + 1, len(specs_list)):
                s1 = specs_list[i]
                s2 = specs_list[j]

                # Check for overlapping constraints
                shared_constraints = set(s1.constraints) & set(s2.constraints)
                if shared_constraints:
                    issue_counter += 1
                    conflicts.append(ValidationIssue(
                        issue_id=f"C{issue_counter:04d}",
                        severity=ValidationSeverity.WARNING,
                        req_ids=[s1.req_id, s2.req_id],
                        description=f"Overlapping constraints between {s1.req_id} and {s2.req_id}: {shared_constraints}",
                    ))
                    conflict_pairs.append((s1.req_id, s2.req_id))

                # Check for resource conflicts
                shared_resources = set(s1.resources_required) & set(s2.resources_required)
                if shared_resources:
                    for resource in shared_resources:
                        capacity = self._resource_capacity.get(resource, float("inf"))
                        if s1.effort_estimate + s2.effort_estimate > capacity:
                            issue_counter += 1
                            conflicts.append(ValidationIssue(
                                issue_id=f"C{issue_counter:04d}",
                                severity=ValidationSeverity.ERROR,
                                req_ids=[s1.req_id, s2.req_id],
                                description=(
                                    f"Resource conflict: {resource} needed by both "
                                    f"{s1.req_id} ({s1.effort_estimate}d) and "
                                    f"{s2.req_id} ({s2.effort_estimate}d), "
                                    f"capacity={capacity}d"
                                ),
                            ))
                            if (s1.req_id, s2.req_id) not in conflict_pairs:
                                conflict_pairs.append((s1.req_id, s2.req_id))

                # Check for tag overlap suggesting duplication
                shared_tags = set(s1.tags) & set(s2.tags)
                if len(shared_tags) >= 3:
                    issue_counter += 1
                    conflicts.append(ValidationIssue(
                        issue_id=f"C{issue_counter:04d}",
                        severity=ValidationSeverity.INFO,
                        req_ids=[s1.req_id, s2.req_id],
                        description=f"High tag overlap between {s1.req_id} and {s2.req_id}: {shared_tags}",
                        suggestion="Check if these requirements are duplicates",
                    ))

        severity_dist: Dict[str, int] = {"error": 0, "warning": 0, "info": 0}
        for c in conflicts:
            severity_dist[c.severity.value] += 1

        return ConflictDetectionResult(
            total_conflicts=len(conflicts),
            conflicts=conflicts,
            conflict_pairs=conflict_pairs,
            severity_distribution=severity_dist,
        )

    def assess_feasibility(
        self,
        available_effort: float = 100.0,
        risk_tolerance: float = 0.3,
    ) -> FeasibilityAssessment:
        """
        Assess the feasibility of implementing all requirements.

        Considers effort estimates, resource availability, dependency
        complexity, and priority distribution.

        Args:
            available_effort: Total available effort in person-days.
            risk_tolerance: Acceptable risk level (0-1, lower = more conservative).

        Returns:
            FeasibilityAssessment with feasibility scores.

        Raises:
            ValueError: If no specs have been added.
        """
        if not self._specs:
            raise ValueError("No requirement specs to assess")

        total_effort = sum(s.effort_estimate for s in self._specs.values())
        resource_utilization = total_effort / available_effort if available_effort > 0 else float("inf")

        # Per-requirement feasibility scores
        per_req_scores: Dict[str, float] = {}
        risk_factors: List[str] = []
        bottlenecks: List[str] = []

        for rid, spec in self._specs.items():
            # Base feasibility: effort relative to available
            if available_effort > 0:
                effort_ratio = spec.effort_estimate / available_effort
                effort_score = max(0.0, 1.0 - effort_ratio)
            else:
                effort_score = 0.0

            # Dependency complexity penalty
            dep_count = len(spec.dependencies)
            dep_penalty = min(dep_count * 0.1, 0.5)

            # Priority bonus (higher priority = more likely to be feasible in cuts)
            priority_bonus = spec.priority * 0.05

            score = max(0.0, min(1.0, effort_score - dep_penalty + priority_bonus))
            per_req_scores[rid] = round(score, 4)

            # Flag bottlenecks
            if dep_count >= 3:
                bottlenecks.append(rid)
            if effort_ratio > risk_tolerance:
                risk_factors.append(f"{rid}: effort ({spec.effort_estimate}d) exceeds risk threshold")

        if resource_utilization > 1.0:
            risk_factors.append(
                f"Total effort ({total_effort:.1f}d) exceeds available ({available_effort:.1f}d)"
            )

        # Overall feasibility
        if per_req_scores:
            avg_score = sum(per_req_scores.values()) / len(per_req_scores)
            utilization_penalty = max(0.0, resource_utilization - 1.0) * 0.5
            overall = max(0.0, min(1.0, avg_score - utilization_penalty))
        else:
            overall = 0.0

        return FeasibilityAssessment(
            overall_feasibility=round(overall, 4),
            per_requirement_scores=per_req_scores,
            risk_factors=risk_factors,
            bottleneck_requirements=bottlenecks,
            resource_utilization=round(min(resource_utilization, 10.0), 4),
        )

    def _detect_dependency_cycles(self) -> List[List[str]]:
        """Detect circular dependencies in requirement specs."""
        WHITE, GRAY, BLACK = 0, 1, 2
        color: Dict[str, int] = {rid: WHITE for rid in self._specs}
        cycles: List[List[str]] = []
        path: List[str] = []

        def dfs(node: str) -> None:
            color[node] = GRAY
            path.append(node)

            spec = self._specs.get(node)
            if spec:
                for dep in spec.dependencies:
                    if dep not in color:
                        continue
                    if color[dep] == GRAY:
                        # Found cycle
                        cycle_start = path.index(dep)
                        cycles.append(path[cycle_start:] + [dep])
                    elif color[dep] == WHITE:
                        dfs(dep)

            path.pop()
            color[node] = BLACK

        for rid in self._specs:
            if color[rid] == WHITE:
                dfs(rid)

        return cycles

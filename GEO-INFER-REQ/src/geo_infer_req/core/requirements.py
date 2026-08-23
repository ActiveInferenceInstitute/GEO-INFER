"""
Requirements analysis for GEO-INFER-REQ.

Provides dependency graph construction, requirement priority scoring,
and completeness checking for software and system requirements.
"""

import re
from typing import Dict, List, Optional, Tuple, Set, Any
from dataclasses import dataclass, field
from enum import Enum


class RequirementType(Enum):
    """Classification of requirement types."""
    FUNCTIONAL = "functional"
    NON_FUNCTIONAL = "non_functional"
    INTERFACE = "interface"
    CONSTRAINT = "constraint"
    DATA = "data"
    PERFORMANCE = "performance"
    SECURITY = "security"


class RequirementStatus(Enum):
    """Status of a requirement in its lifecycle."""
    DRAFT = "draft"
    REVIEWED = "reviewed"
    APPROVED = "approved"
    IMPLEMENTED = "implemented"
    VERIFIED = "verified"
    DEPRECATED = "deprecated"


class PriorityLevel(Enum):
    """Priority classification for requirements."""
    CRITICAL = 4
    HIGH = 3
    MEDIUM = 2
    LOW = 1


@dataclass
class Requirement:
    """Represents a single requirement."""
    req_id: str
    title: str
    description: str
    req_type: RequirementType
    priority: PriorityLevel = PriorityLevel.MEDIUM
    status: RequirementStatus = RequirementStatus.DRAFT
    dependencies: List[str] = field(default_factory=list)
    stakeholders: List[str] = field(default_factory=list)
    acceptance_criteria: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    effort_estimate: Optional[float] = None


@dataclass
class DependencyGraph:
    """Representation of requirement dependency relationships."""
    nodes: List[str]
    edges: List[Tuple[str, str]]
    topological_order: List[str]
    cycles: List[List[str]]
    critical_path: List[str]
    depth: int


@dataclass
class CompletenessReport:
    """Report on requirements completeness."""
    total_requirements: int
    completeness_score: float
    missing_descriptions: List[str]
    missing_acceptance_criteria: List[str]
    missing_priorities: List[str]
    orphaned_requirements: List[str]
    coverage_by_type: Dict[str, float]


class RequirementsAnalyzer:
    """
    Analyzes software and system requirements.

    Constructs dependency graphs, scores priorities, and checks
    completeness of requirement specifications.
    """

    def __init__(self) -> None:
        self._requirements: Dict[str, Requirement] = {}

    def add_requirement(self, req: Requirement) -> None:
        """
        Add a requirement to the analyzer.

        Args:
            req: The requirement to add.

        Raises:
            ValueError: If req_id already exists.
        """
        if req.req_id in self._requirements:
            raise ValueError(f"Requirement {req.req_id} already exists")
        self._requirements[req.req_id] = req

    def add_requirements(self, requirements: List[Requirement]) -> None:
        """
        Add multiple requirements.

        Args:
            requirements: List of requirements to add.
        """
        for req in requirements:
            self.add_requirement(req)

    def get_requirement(self, req_id: str) -> Requirement:
        """
        Retrieve a requirement by ID.

        Args:
            req_id: The requirement identifier.

        Returns:
            The requirement object.

        Raises:
            KeyError: If not found.
        """
        if req_id not in self._requirements:
            raise KeyError(f"Requirement {req_id} not found")
        return self._requirements[req_id]

    def build_dependency_graph(self) -> DependencyGraph:
        """
        Construct the dependency graph from all requirements.

        Performs topological sorting, detects cycles, and computes
        the critical path (longest dependency chain).

        Returns:
            DependencyGraph with structural analysis.
        """
        nodes = list(self._requirements.keys())
        edges: List[Tuple[str, str]] = []
        adjacency: Dict[str, List[str]] = {n: [] for n in nodes}
        in_degree: Dict[str, int] = {n: 0 for n in nodes}

        for req_id, req in self._requirements.items():
            for dep_id in req.dependencies:
                if dep_id in self._requirements:
                    edges.append((dep_id, req_id))
                    adjacency[dep_id].append(req_id)
                    in_degree[req_id] = in_degree.get(req_id, 0) + 1

        # Kahn's algorithm for topological sort
        topo_order = []
        queue = [n for n in nodes if in_degree[n] == 0]
        while queue:
            current = queue.pop(0)
            topo_order.append(current)
            for neighbor in adjacency[current]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)

        # Detect cycles (nodes not in topological order)
        cycles = self._detect_cycles(adjacency, nodes)

        # Critical path (longest path in DAG)
        critical_path, depth = self._compute_critical_path(adjacency, topo_order)

        return DependencyGraph(
            nodes=nodes,
            edges=edges,
            topological_order=topo_order,
            cycles=cycles,
            critical_path=critical_path,
            depth=depth,
        )

    def compute_priority_scores(
        self,
        weights: Optional[Dict[str, float]] = None,
    ) -> Dict[str, float]:
        """
        Compute weighted priority scores for all requirements.

        Factors in:
        - Base priority level
        - Number of dependents (things that depend on this req)
        - Stakeholder count
        - Effort estimate (inverse: lower effort = higher score)

        Args:
            weights: Optional weights for scoring factors.
                Keys: "priority", "dependents", "stakeholders", "effort"

        Returns:
            Mapping of req_id to composite priority score.
        """
        w = weights or {
            "priority": 0.40,
            "dependents": 0.30,
            "stakeholders": 0.15,
            "effort": 0.15,
        }

        # Count dependents for each requirement
        dependent_counts: Dict[str, int] = {rid: 0 for rid in self._requirements}
        for req in self._requirements.values():
            for dep in req.dependencies:
                if dep in dependent_counts:
                    dependent_counts[dep] += 1

        max_dependents = max(dependent_counts.values()) if dependent_counts else 1
        max_stakeholders = max(
            (len(r.stakeholders) for r in self._requirements.values()), default=1
        )
        max_effort = max(
            (r.effort_estimate for r in self._requirements.values() if r.effort_estimate),
            default=1.0,
        )

        scores: Dict[str, float] = {}
        for rid, req in self._requirements.items():
            # Normalize priority to [0, 1]
            priority_norm = req.priority.value / PriorityLevel.CRITICAL.value

            # Normalize dependents
            dep_norm = dependent_counts[rid] / max_dependents if max_dependents > 0 else 0.0

            # Normalize stakeholder count
            stake_norm = len(req.stakeholders) / max_stakeholders if max_stakeholders > 0 else 0.0

            # Effort: inverse normalized (low effort = higher priority)
            if req.effort_estimate and max_effort > 0:
                effort_norm = 1.0 - (req.effort_estimate / max_effort)
            else:
                effort_norm = 0.5  # Default if no estimate

            score = (
                w["priority"] * priority_norm
                + w["dependents"] * dep_norm
                + w["stakeholders"] * stake_norm
                + w["effort"] * effort_norm
            )
            scores[rid] = round(score, 4)

        return scores

    def check_completeness(self) -> CompletenessReport:
        """
        Check the completeness of the requirements specification.

        Evaluates whether requirements have descriptions, acceptance
        criteria, priorities, and proper dependency links.

        Returns:
            CompletenessReport with detailed findings.
        """
        missing_desc: List[str] = []
        missing_criteria: List[str] = []
        missing_priorities: List[str] = []
        orphaned: List[str] = []

        all_ids = set(self._requirements.keys())
        referenced_ids: Set[str] = set()
        for req in self._requirements.values():
            referenced_ids.update(req.dependencies)

        for rid, req in self._requirements.items():
            if not req.description or len(req.description.strip()) < 10:
                missing_desc.append(rid)
            if not req.acceptance_criteria:
                missing_criteria.append(rid)
            # Check for dangling dependencies
            for dep in req.dependencies:
                if dep not in all_ids:
                    orphaned.append(f"{rid} -> {dep}")

        # Coverage by type
        type_counts: Dict[str, int] = {}
        type_complete: Dict[str, int] = {}
        for req in self._requirements.values():
            t = req.req_type.value
            type_counts[t] = type_counts.get(t, 0) + 1
            is_complete = (
                len(req.description.strip()) >= 10
                and len(req.acceptance_criteria) > 0
            )
            if is_complete:
                type_complete[t] = type_complete.get(t, 0) + 1

        coverage_by_type = {}
        for t, count in type_counts.items():
            coverage_by_type[t] = round(type_complete.get(t, 0) / count, 4) if count > 0 else 0.0

        # Overall completeness
        total = len(self._requirements)
        if total > 0:
            complete_count = sum(
                1 for req in self._requirements.values()
                if len(req.description.strip()) >= 10
                and len(req.acceptance_criteria) > 0
            )
            completeness = complete_count / total
        else:
            completeness = 0.0

        return CompletenessReport(
            total_requirements=total,
            completeness_score=round(completeness, 4),
            missing_descriptions=missing_desc,
            missing_acceptance_criteria=missing_criteria,
            missing_priorities=missing_priorities,
            orphaned_requirements=orphaned,
            coverage_by_type=coverage_by_type,
        )

    def get_requirements_by_type(self, req_type: RequirementType) -> List[Requirement]:
        """
        Filter requirements by type.

        Args:
            req_type: The type to filter by.

        Returns:
            List of matching requirements.
        """
        return [r for r in self._requirements.values() if r.req_type == req_type]

    def get_requirements_by_status(self, status: RequirementStatus) -> List[Requirement]:
        """
        Filter requirements by status.

        Args:
            status: The status to filter by.

        Returns:
            List of matching requirements.
        """
        return [r for r in self._requirements.values() if r.status == status]

    def _detect_cycles(
        self, adjacency: Dict[str, List[str]], nodes: List[str]
    ) -> List[List[str]]:
        """Detect cycles using DFS-based cycle detection."""
        WHITE, GRAY, BLACK = 0, 1, 2
        color: Dict[str, int] = {n: WHITE for n in nodes}
        parent: Dict[str, Optional[str]] = {n: None for n in nodes}
        cycles: List[List[str]] = []

        def dfs(node: str) -> None:
            color[node] = GRAY
            for neighbor in adjacency.get(node, []):
                if neighbor not in color:
                    continue
                if color[neighbor] == GRAY:
                    # Found a cycle, reconstruct it
                    cycle = [neighbor, node]
                    curr: Optional[str] = node
                    while curr and parent.get(curr) and parent[curr] != neighbor:
                        curr = parent[curr]
                        if curr:
                            cycle.append(curr)
                    cycles.append(cycle)
                elif color[neighbor] == WHITE:
                    parent[neighbor] = node
                    dfs(neighbor)
            color[node] = BLACK

        for node in nodes:
            if color[node] == WHITE:
                dfs(node)

        return cycles

    def _compute_critical_path(
        self, adjacency: Dict[str, List[str]], topo_order: List[str]
    ) -> Tuple[List[str], int]:
        """Compute the longest path (critical path) in the DAG."""
        if not topo_order:
            return [], 0

        dist: Dict[str, int] = {n: 0 for n in topo_order}
        predecessor: Dict[str, Optional[str]] = {n: None for n in topo_order}

        for node in topo_order:
            for neighbor in adjacency.get(node, []):
                if neighbor in dist and dist[node] + 1 > dist[neighbor]:
                    dist[neighbor] = dist[node] + 1
                    predecessor[neighbor] = node

        # Find end of critical path
        if not dist:
            return [], 0

        end_node = max(dist, key=lambda k: dist[k])
        max_depth = dist[end_node]

        # Reconstruct path
        path = []
        current: Optional[str] = end_node
        while current is not None:
            path.append(current)
            current = predecessor[current]
        path.reverse()

        return path, max_depth

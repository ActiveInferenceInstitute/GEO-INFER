"""Unit tests for the nested analytics modules.

Covers flow_analysis, pattern_detection, hierarchy_metrics and
performance_metrics with deterministic synthetic data.
"""




# Nine well-separated res-9 cells (no two adjacent). The last index carries
# the outlier value used by the pattern-detection tests.
SPREAD_INDICES = [
    "8928341aec3ffff",
    "89194ad14d7ffff",
    "892f5a36663ffff",
    "89be0e35cb3ffff",
    "8928308280fffff",
    "8928308280bffff",
    "89283082807ffff",
    "89283082803ffff",
    "8928308280effff",
]


def _make_cells(values_by_index):
    """Build NestedCell instances carrying the given state value."""
    raise NotImplementedError


def _make_grid(values_by_index, system_id="sys"):
    """Build a NestedH3Grid with one system holding the given cell values."""
    raise NotImplementedError


class TestFlowAnalysis:
    pass


class TestPatternDetection:
    pass


class TestHierarchyMetrics:
    pass


class TestPerformanceMetrics:
    pass

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, Any


@dataclass
class TestOutcome:
    """Test outcome with detailed information.

    Renamed from ``TestResult``: the canonical ``TestResult`` in
    ``core.test_runner`` is the runner's execution record; this dataclass is
    the outcome shape used by model-level reporting.
    """

    test_name: str
    passed: bool
    duration_seconds: float
    message: str
    details: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    category: str = "general"


@dataclass
class ValidationRule:
    """Data validation rule."""

    name: str
    field: str
    rule_type: str  # range, format, custom
    parameters: Dict[str, Any]
    severity: str = "error"  # error, warning, info
    description: str = ""

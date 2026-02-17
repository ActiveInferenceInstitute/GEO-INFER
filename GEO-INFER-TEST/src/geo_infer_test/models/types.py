from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional

@dataclass
class TestResult:
    """Test result with detailed information."""
    test_name: str
    passed: bool
    duration_seconds: float
    message: str
    details: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
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

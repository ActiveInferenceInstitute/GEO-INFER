"""
Validation implementations for GEO-INFER-DATA.

This module provides comprehensive validation implementations including
data quality rules, validation engines, and quality assessment utilities.

Classes:
    ValidationEngine: Core validation processing engine
    QualityRules: Predefined quality validation rules
    CustomValidator: Custom validation rule implementation
    ValidationReporter: Validation reporting and analytics

Examples:
    >>> from geo_infer_data.validation import ValidationEngine, QualityRules
    >>>
    >>> # Initialize validation engine
    >>> engine = ValidationEngine(rules='comprehensive')
    >>>
    >>> # Apply quality rules
    >>> rules = QualityRules()
    >>> quality_score = rules.assess_completeness(data)
    >>>
    >>> # Generate validation report
    >>> reporter = ValidationReporter()
    >>> report = reporter.generate_comprehensive_report(data, metadata)
"""

from .engine import ValidationEngine
from .rules import QualityRules
from .custom import CustomValidator
from .reporter import ValidationReporter

__all__ = [
    "ValidationEngine",
    "QualityRules",
    "CustomValidator",
    "ValidationReporter",
]

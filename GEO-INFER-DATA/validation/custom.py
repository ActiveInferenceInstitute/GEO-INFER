"""
Custom validation for GEO-INFER-DATA.

This module provides custom validation rule implementation and
custom quality assessment capabilities for specialized requirements.
"""

import logging
from typing import Dict, List, Optional, Union, Any, Callable

from ..models.schemas import QualityCheck, QualityStatus, DatasetMetadata


logger = logging.getLogger(__name__)


class CustomValidator:
    """
    Custom validation rule implementation.

    This class provides capabilities for implementing custom validation
    rules and quality assessment logic for specialized requirements.

    Args:
        custom_rules: Dictionary of custom validation functions

    Examples:
        >>> validator = CustomValidator({
        ...     'business_rule_check': lambda data, metadata: check_business_rules(data),
        ...     'domain_specific_validation': lambda data, metadata: validate_domain_constraints(data)
        ... })
        >>>
        >>> result = await validator.validate_custom(data, metadata)
    """

    def __init__(self, custom_rules: Optional[Dict[str, Callable]] = None):
        self.custom_rules = custom_rules or {}

        logger.info(f"Initialized CustomValidator with {len(self.custom_rules)} custom rules")

    async def validate_custom(
        self,
        data: Any,
        metadata: Optional[DatasetMetadata] = None,
        rule_names: Optional[List[str]] = None
    ) -> Dict[str, QualityCheck]:
        """
        Validate data using custom rules.

        Args:
            data: Data to validate
            metadata: Dataset metadata
            rule_names: Specific rules to apply

        Returns:
            Validation results by rule name
        """
        logger.info(f"Applying {len(rule_names) if rule_names else len(self.custom_rules)} custom validation rules")

        results = {}
        rules_to_apply = rule_names or list(self.custom_rules.keys())

        for rule_name in rules_to_apply:
            if rule_name in self.custom_rules:
                try:
                    result = await self.custom_rules[rule_name](data, metadata)
                    results[rule_name] = result
                except Exception as e:
                    logger.error(f"Custom validation rule {rule_name} failed: {e}")
                    results[rule_name] = QualityCheck(
                        score=0.0,
                        status=QualityStatus.FAIL,
                        issues=[{'type': 'custom_rule_error', 'message': str(e)}]
                    )

        return results

    def add_rule(self, name: str, validation_function: Callable):
        """
        Add custom validation rule.

        Args:
            name: Rule name
            validation_function: Validation function
        """
        self.custom_rules[name] = validation_function
        logger.info(f"Added custom validation rule: {name}")

    def remove_rule(self, name: str):
        """
        Remove custom validation rule.

        Args:
            name: Rule name to remove
        """
        if name in self.custom_rules:
            del self.custom_rules[name]
            logger.info(f"Removed custom validation rule: {name}")

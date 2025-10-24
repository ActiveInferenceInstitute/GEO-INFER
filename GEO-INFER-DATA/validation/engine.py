"""
Validation engine for GEO-INFER-DATA.

This module provides the core validation engine that orchestrates
various validation rules and quality assessments for geospatial data.
"""

import logging
from typing import Dict, List, Optional, Union, Any, Callable
from datetime import datetime
from dataclasses import dataclass
import asyncio

import geopandas as gpd
import pandas as pd
import numpy as np

from ..models.schemas import (
    QualityCheck, QualityStatus, DataQualityReport,
    DatasetMetadata, ValidationRule
)


logger = logging.getLogger(__name__)


@dataclass
class ValidationRule:
    """Validation rule definition."""
    name: str
    description: str
    function: Callable
    weight: float = 1.0
    severity: str = 'medium'
    enabled: bool = True
    parameters: Dict[str, Any] = None

    def __post_init__(self):
        if self.parameters is None:
            self.parameters = {}


class ValidationEngine:
    """
    Core validation engine for geospatial data.

    This class orchestrates various validation rules and provides
    comprehensive quality assessment for geospatial datasets.

    Args:
        rules_config: Validation rules configuration
        quality_threshold: Overall quality threshold
        parallel_validation: Whether to run validations in parallel

    Examples:
        >>> engine = ValidationEngine(
        ...     rules_config='comprehensive',
        ...     quality_threshold=0.8,
        ...     parallel_validation=True
        ... )
        >>>
        >>> # Validate dataset
        >>> report = await engine.validate_dataset(data, metadata)
        >>>
        >>> # Get validation rules
        >>> rules = engine.get_available_rules()
        >>> print(f"Available rules: {len(rules)}")
    """

    def __init__(
        self,
        rules_config: str = 'standard',
        quality_threshold: float = 0.8,
        parallel_validation: bool = True
    ):
        self.rules_config = rules_config
        self.quality_threshold = quality_threshold
        self.parallel_validation = parallel_validation

        self.validation_rules = {}
        self.validation_history = []

        self._initialize_rules()

        logger.info(f"Initialized ValidationEngine with {rules_config} rules")

    def _initialize_rules(self):
        """Initialize validation rules."""
        # Import rule functions
        from .rules import get_validation_rules

        self.validation_rules = get_validation_rules(self.rules_config)

        logger.info(f"Loaded {len(self.validation_rules)} validation rules")

    async def validate_dataset(
        self,
        data: Union[pd.DataFrame, gpd.GeoDataFrame],
        metadata: Optional[DatasetMetadata] = None,
        custom_rules: Optional[List[ValidationRule]] = None
    ) -> DataQualityReport:
        """
        Validate dataset with comprehensive quality assessment.

        Args:
            data: Data to validate
            metadata: Dataset metadata
            custom_rules: Additional custom validation rules

        Returns:
            Comprehensive quality report
        """
        logger.info(f"Starting comprehensive validation for dataset: {metadata.title if metadata else 'unknown'}")

        # Combine default and custom rules
        all_rules = self.validation_rules.copy()
        if custom_rules:
            for rule in custom_rules:
                all_rules[rule.name] = rule

        # Execute validation rules
        if self.parallel_validation:
            validation_results = await self._validate_parallel(data, metadata, all_rules)
        else:
            validation_results = await self._validate_sequential(data, metadata, all_rules)

        # Calculate overall score
        overall_score = self._calculate_overall_score(validation_results)

        # Generate recommendations
        recommendations = self._generate_recommendations(validation_results, overall_score)

        # Create quality report
        dataset_id = metadata.title if metadata else "unknown_dataset"
        quality_report = DataQualityReport(
            dataset_id=dataset_id,
            overall_score=overall_score,
            checks=validation_results,
            recommendations=recommendations,
            assessment_method=list(all_rules.keys()),
            validation_rules=list(all_rules.keys())
        )

        # Store in history
        self.validation_history.append(quality_report)

        logger.info(f"Validation completed with overall score: {overall_score:.2f}")
        return quality_report

    async def _validate_parallel(
        self,
        data: Union[pd.DataFrame, gpd.GeoDataFrame],
        metadata: Optional[DatasetMetadata],
        rules: Dict[str, ValidationRule]
    ) -> Dict[str, QualityCheck]:
        """Execute validation rules in parallel."""
        logger.debug("Executing validation rules in parallel")

        # Create validation tasks
        validation_tasks = []
        for rule_name, rule in rules.items():
            if rule.enabled:
                task = self._execute_validation_rule(data, metadata, rule)
                validation_tasks.append((rule_name, task))

        # Execute tasks concurrently
        results = {}
        for rule_name, task in validation_tasks:
            try:
                result = await task
                results[rule_name] = result
            except Exception as e:
                logger.error(f"Validation rule {rule_name} failed: {e}")
                results[rule_name] = QualityCheck(
                    score=0.0,
                    status=QualityStatus.FAIL,
                    issues=[{'type': 'validation_error', 'message': str(e)}]
                )

        return results

    async def _validate_sequential(
        self,
        data: Union[pd.DataFrame, gpd.GeoDataFrame],
        metadata: Optional[DatasetMetadata],
        rules: Dict[str, ValidationRule]
    ) -> Dict[str, QualityCheck]:
        """Execute validation rules sequentially."""
        logger.debug("Executing validation rules sequentially")

        results = {}

        for rule_name, rule in rules.items():
            if rule.enabled:
                try:
                    result = await self._execute_validation_rule(data, metadata, rule)
                    results[rule_name] = result
                except Exception as e:
                    logger.error(f"Validation rule {rule_name} failed: {e}")
                    results[rule_name] = QualityCheck(
                        score=0.0,
                        status=QualityStatus.FAIL,
                        issues=[{'type': 'validation_error', 'message': str(e)}]
                    )

        return results

    async def _execute_validation_rule(
        self,
        data: Union[pd.DataFrame, gpd.GeoDataFrame],
        metadata: Optional[DatasetMetadata],
        rule: ValidationRule
    ) -> QualityCheck:
        """Execute a single validation rule."""
        try:
            # Execute validation function
            result = await rule.function(data, metadata, rule.parameters)

            # Ensure result is QualityCheck
            if not isinstance(result, QualityCheck):
                result = QualityCheck(
                    score=float(result) if isinstance(result, (int, float)) else 1.0,
                    status=QualityStatus.PASS,
                    issues=[]
                )

            logger.debug(f"Validation rule {rule.name} completed: {result.score:.2f}")
            return result

        except Exception as e:
            logger.error(f"Validation rule {rule.name} execution failed: {e}")
            return QualityCheck(
                score=0.0,
                status=QualityStatus.FAIL,
                issues=[{'type': 'rule_execution_error', 'message': str(e)}]
            )

    def _calculate_overall_score(self, validation_results: Dict[str, QualityCheck]) -> float:
        """Calculate overall quality score."""
        if not validation_results:
            return 0.0

        # Weight scores by rule weight
        weighted_scores = []
        total_weight = 0

        for rule_name, result in validation_results.items():
            rule = self.validation_rules.get(rule_name)
            weight = rule.weight if rule else 1.0

            weighted_scores.append(result.score * weight)
            total_weight += weight

        if total_weight == 0:
            return 0.0

        # Calculate weighted average
        overall_score = sum(weighted_scores) / total_weight

        # Apply penalty for failed rules
        failed_rules = [r for r in validation_results.values() if r.status == QualityStatus.FAIL]
        if failed_rules:
            penalty = len(failed_rules) / len(validation_results) * 0.2  # 20% penalty
            overall_score = max(0.0, overall_score - penalty)

        return min(1.0, overall_score)

    def _generate_recommendations(
        self,
        validation_results: Dict[str, QualityCheck],
        overall_score: float
    ) -> List[str]:
        """Generate improvement recommendations."""
        recommendations = []

        # Overall recommendations
        if overall_score < self.quality_threshold:
            recommendations.append("Overall data quality is below acceptable threshold")

        # Rule-specific recommendations
        for rule_name, result in validation_results.items():
            if result.status == QualityStatus.FAIL:
                recommendations.append(f"Fix {rule_name} validation failures")
            elif result.status == QualityStatus.WARNING:
                recommendations.append(f"Review {rule_name} warnings")

            # Check for specific issues
            for issue in result.issues:
                if issue.get('severity') == 'high':
                    recommendations.append(f"Address high-priority issue in {rule_name}: {issue['message']}")
                elif issue.get('severity') == 'critical':
                    recommendations.append(f"URGENT: Fix critical issue in {rule_name}: {issue['message']}")

        return recommendations

    def add_custom_rule(self, rule: ValidationRule):
        """
        Add custom validation rule.

        Args:
            rule: Custom validation rule
        """
        self.validation_rules[rule.name] = rule
        logger.info(f"Added custom validation rule: {rule.name}")

    def remove_rule(self, rule_name: str):
        """
        Remove validation rule.

        Args:
            rule_name: Name of rule to remove
        """
        if rule_name in self.validation_rules:
            del self.validation_rules[rule_name]
            logger.info(f"Removed validation rule: {rule_name}")

    def get_available_rules(self) -> List[str]:
        """Get list of available validation rules."""
        return list(self.validation_rules.keys())

    def get_validation_history(self, dataset_id: Optional[str] = None) -> List[DataQualityReport]:
        """
        Get validation history.

        Args:
            dataset_id: Optional dataset filter

        Returns:
            List of validation reports
        """
        if dataset_id:
            return [r for r in self.validation_history if r.dataset_id == dataset_id]
        else:
            return self.validation_history.copy()

    def get_quality_trends(self, days: int = 30) -> Dict[str, Any]:
        """
        Get quality trends over time.

        Args:
            days: Number of days to analyze

        Returns:
            Quality trend analysis
        """
        cutoff_date = datetime.now() - timedelta(days=days)
        recent_reports = [r for r in self.validation_history if r.generated_at >= cutoff_date]

        if not recent_reports:
            return {'message': 'No recent validation reports available'}

        scores = [r.overall_score for r in recent_reports]

        return {
            'average_score': sum(scores) / len(scores),
            'reports_count': len(recent_reports),
            'score_trend': 'improving' if scores[-1] > scores[0] else 'declining',
            'best_score': max(scores),
            'worst_score': min(scores),
            'period_days': days
        }


class BatchValidationEngine:
    """
    Batch validation engine for multiple datasets.

    This class provides batch validation capabilities for processing
    multiple datasets efficiently with progress tracking and reporting.
    """

    def __init__(self, validation_engine: ValidationEngine):
        self.validation_engine = validation_engine
        self.batch_history = []

        logger.info("Initialized BatchValidationEngine")

    async def validate_batch(
        self,
        datasets: List[Dict[str, Any]],
        progress_callback: Optional[Callable] = None
    ) -> List[DataQualityReport]:
        """
        Validate multiple datasets in batch.

        Args:
            datasets: List of dataset configurations
            progress_callback: Optional progress callback function

        Returns:
            List of validation reports
        """
        logger.info(f"Starting batch validation for {len(datasets)} datasets")

        validation_reports = []
        start_time = datetime.now()

        for i, dataset_config in enumerate(datasets):
            try:
                # Extract data and metadata
                data = dataset_config.get('data')
                metadata = dataset_config.get('metadata')

                if data is None:
                    logger.warning(f"No data provided for dataset {i}")
                    continue

                # Validate dataset
                report = await self.validation_engine.validate_dataset(data, metadata)

                validation_reports.append(report)

                # Call progress callback
                if progress_callback:
                    progress = (i + 1) / len(datasets)
                    await progress_callback(i + 1, len(datasets), report)

                logger.info(f"Validated dataset {i + 1}/{len(datasets)}: {report.overall_score:.2f}")

            except Exception as e:
                logger.error(f"Batch validation failed for dataset {i}: {e}")

                # Create error report
                error_report = DataQualityReport(
                    dataset_id=f"dataset_{i}",
                    overall_score=0.0,
                    checks={'error': QualityCheck(
                        score=0.0,
                        status=QualityStatus.FAIL,
                        issues=[{'type': 'validation_error', 'message': str(e)}]
                    )},
                    recommendations=[f"Fix validation error: {str(e)}"]
                )

                validation_reports.append(error_report)

        end_time = datetime.now()
        duration = end_time - start_time

        # Create batch summary
        batch_summary = {
            'total_datasets': len(datasets),
            'successful_validations': len([r for r in validation_reports if r.overall_score > 0]),
            'failed_validations': len([r for r in validation_reports if r.overall_score == 0]),
            'average_score': sum(r.overall_score for r in validation_reports) / len(validation_reports),
            'duration_seconds': duration.total_seconds(),
            'validation_reports': validation_reports,
            'timestamp': end_time
        }

        self.batch_history.append(batch_summary)

        logger.info(f"Batch validation completed in {duration}: {batch_summary['average_score']:.2f} average score")
        return validation_reports

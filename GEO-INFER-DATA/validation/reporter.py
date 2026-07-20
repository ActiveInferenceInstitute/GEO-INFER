"""
Validation reporting for GEO-INFER-DATA.

This module provides comprehensive validation reporting and analytics
including trend analysis, quality metrics, and improvement tracking.
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta

from ..models.schemas import DataQualityReport, DatasetMetadata, QualityStatus


logger = logging.getLogger(__name__)


class ValidationReporter:
    """
    Validation reporting and analytics.

    This class provides comprehensive validation reporting including trend
    analysis, quality metrics visualization, and improvement recommendations.

    Args:
        report_format: Output format for reports
        include_trends: Whether to include trend analysis
        retention_days: Number of days to retain reports

    Examples:
        >>> reporter = ValidationReporter(
        ...     report_format='json',
        ...     include_trends=True,
        ...     retention_days=90
        ... )
        >>>
        >>> report = await reporter.generate_comprehensive_report(data, metadata)
        >>> trends = reporter.analyze_quality_trends(datasets, days=30)
    """

    def __init__(
        self,
        report_format: str = "json",
        include_trends: bool = True,
        retention_days: int = 90,
    ):
        self.report_format = report_format
        self.include_trends = include_trends
        self.retention_days = retention_days

        self.reports = []

        logger.info(f"Initialized ValidationReporter with format={report_format}")

    async def generate_comprehensive_report(
        self, data: Any, metadata: Optional[DatasetMetadata] = None
    ) -> Dict[str, Any]:
        """
        Generate comprehensive validation report.

        Args:
            data: Data to analyze
            metadata: Dataset metadata

        Returns:
            Comprehensive validation report
        """
        logger.info("Generating comprehensive validation report")

        from geo_infer_data.core.validation import GeospatialValidator, ValidationConfig

        validator = GeospatialValidator(ValidationConfig())
        quality_report = await validator.validate_data(data, metadata)
        self.reports.append(quality_report)
        report = quality_report.model_dump(mode="json")
        report["report_format"] = self.report_format
        return report

    def analyze_quality_trends(
        self, datasets: List[str], days: int = 30
    ) -> Dict[str, Any]:
        """
        Analyze quality trends across datasets.

        Args:
            datasets: List of dataset identifiers
            days: Number of days to analyze

        Returns:
            Quality trend analysis
        """
        if days < 0:
            raise ValueError("days must not be negative")
        logger.info(
            f"Analyzing quality trends for {len(datasets)} datasets over {days} days"
        )
        cutoff = datetime.utcnow() - timedelta(days=days)
        selected = [
            report
            for report in self.reports
            if report.dataset_id in datasets
            and report.generated_at.replace(tzinfo=None) >= cutoff
        ]
        scores = [report.overall_score for report in selected]
        distribution = {
            "excellent": sum(score >= 0.9 for score in scores),
            "good": sum(0.8 <= score < 0.9 for score in scores),
            "fair": sum(0.5 <= score < 0.8 for score in scores),
            "poor": sum(score < 0.5 for score in scores),
        }
        best = max(selected, key=lambda report: report.overall_score, default=None)
        return {
            "period_days": days,
            "datasets_analyzed": len({report.dataset_id for report in selected}),
            "reports_analyzed": len(selected),
            "overall_trend": self._trend(scores),
            "average_score": sum(scores) / len(scores) if scores else None,
            "best_performing": best.dataset_id if best else None,
            "needs_attention": [
                report.dataset_id for report in selected if report.overall_score < 0.8
            ],
            "quality_distribution": distribution,
        }

    def generate_improvement_plan(
        self, reports: List[DataQualityReport]
    ) -> Dict[str, Any]:
        """
        Generate improvement plan based on validation reports.

        Args:
            reports: List of quality reports

        Returns:
            Improvement plan and recommendations
        """
        logger.info(f"Generating improvement plan for {len(reports)} reports")
        if not reports:
            return {
                "priority_actions": [],
                "estimated_improvement": None,
                "reports_analyzed": 0,
                "success_metrics": [],
            }

        actions = []
        for report in reports:
            actions.extend(report.recommendations)
            for check_name, check in report.checks.items():
                if check.status != QualityStatus.PASS:
                    actions.append(f"Resolve {check_name} quality issues")
        unique_actions = list(dict.fromkeys(actions))
        average_score = sum(report.overall_score for report in reports) / len(reports)
        return {
            "priority_actions": unique_actions,
            "estimated_improvement": max(0.0, 1.0 - average_score),
            "reports_analyzed": len(reports),
            "average_score": average_score,
            "success_metrics": ["Overall quality score reaches 0.8 or higher"],
        }

    @staticmethod
    def _trend(scores: List[float]) -> Optional[str]:
        """Classify score direction from chronological report scores."""
        if len(scores) < 2:
            return None
        if scores[-1] > scores[0]:
            return "improving"
        if scores[-1] < scores[0]:
            return "declining"
        return "stable"

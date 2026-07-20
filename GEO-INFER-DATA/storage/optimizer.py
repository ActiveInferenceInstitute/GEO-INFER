"""
Storage optimization utilities for GEO-INFER-DATA.

This module provides storage performance optimization including
access pattern analysis, index optimization, and cost management.
"""

import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Any


logger = logging.getLogger(__name__)


class StorageOptimizer:
    """
    Storage performance optimization utilities.

    This class provides comprehensive storage optimization including
    access pattern analysis, index optimization, and cost management.

    Args:
        optimization_config: Optimization configuration

    Examples:
        >>> optimizer = StorageOptimizer({
        ...     'target_performance': 'high',
        ...     'cost_optimization': True,
        ...     'auto_optimization': True
        ... })
        >>>
        >>> optimizations = await optimizer.analyze_and_optimize(datasets)
    """

    def __init__(self, optimization_config: Optional[Dict[str, Any]] = None):
        self.optimization_config = optimization_config or {}

        logger.info("Initialized StorageOptimizer")

    async def analyze_and_optimize(self, datasets: List[str]) -> Dict[str, Any]:
        """
        Analyze datasets and generate optimization recommendations.

        Args:
            datasets: List of dataset identifiers

        Returns:
            Optimization recommendations
        """
        logger.info(f"Analyzing {len(datasets)} datasets for optimization")

        if not datasets:
            return {
                "datasets_analyzed": 0,
                "recommendations": [],
                "estimated_savings": None,
                "performance_improvement": None,
                "analysis_timestamp": datetime.now(timezone.utc).isoformat(),
            }

        paths = [Path(dataset) for dataset in datasets]
        existing = [path for path in paths if path.is_file()]
        total_bytes = sum(path.stat().st_size for path in existing)
        recommendations = []
        if total_bytes >= self.optimization_config.get(
            "compression_threshold_bytes", 100_000_000
        ):
            recommendations.append("Compress large datasets before archival")
        if any(
            path.suffix.lower() in {".csv", ".json", ".geojson"} for path in existing
        ):
            recommendations.append(
                "Convert repeated analytical inputs to a columnar format"
            )
        if self.optimization_config.get("spatial_index_required"):
            recommendations.append("Create spatial indexes for geospatial queries")

        optimizations = {
            "datasets_analyzed": len(datasets),
            "existing_files": len(existing),
            "total_bytes": total_bytes,
            "recommendations": recommendations,
            "estimated_savings": self.optimization_config.get("estimated_savings"),
            "performance_improvement": self.optimization_config.get(
                "performance_improvement"
            ),
            "analysis_timestamp": datetime.now(timezone.utc).isoformat(),
        }

        return optimizations

    def calculate_storage_costs(self, datasets: List[str]) -> Dict[str, float]:
        """
        Calculate storage costs for datasets.

        Args:
            datasets: List of dataset identifiers

        Returns:
            Cost analysis by dataset
        """
        costs = {}
        rate = self.optimization_config.get("cost_per_gb_month")
        if rate is None:
            raise ValueError("cost_per_gb_month is required to calculate storage costs")
        for dataset in datasets:
            path = Path(dataset)
            if not path.is_file():
                raise FileNotFoundError(path)
            costs[dataset] = path.stat().st_size / (1024**3) * float(rate)

        return costs

    def recommend_indexing_strategy(
        self, dataset: str, access_patterns: Dict[str, Any]
    ) -> str:
        """
        Recommend indexing strategy for dataset.

        Args:
            dataset: Dataset identifier
            access_patterns: Access pattern analysis

        Returns:
            Recommended indexing strategy
        """
        if not dataset:
            raise ValueError("dataset must not be empty")
        if access_patterns.get("spatial_queries"):
            return "spatial_index"
        if access_patterns.get("temporal_queries"):
            return "temporal_index"
        if access_patterns.get("key_lookups"):
            return "key_index"
        return "no_additional_index"

    def optimize_partitioning(
        self, dataset: str, data_characteristics: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Optimize data partitioning for dataset.

        Args:
            dataset: Dataset identifier
            data_characteristics: Data characteristics analysis

        Returns:
            Partitioning optimization recommendations
        """
        if not dataset:
            raise ValueError("dataset must not be empty")
        if not data_characteristics:
            raise ValueError("data_characteristics are required")
        if data_characteristics.get("temporal_column"):
            strategy = "time_based"
        elif data_characteristics.get("spatial_column"):
            strategy = "spatial_based"
        else:
            strategy = "size_based"
        return {
            "partition_strategy": strategy,
            "partition_size": data_characteristics.get("recommended_partition_size"),
            "partition_column": data_characteristics.get("temporal_column")
            or data_characteristics.get("spatial_column"),
        }

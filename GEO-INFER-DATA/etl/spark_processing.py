"""
Apache Spark processing for GEO-INFER-DATA ETL pipelines.

This module provides comprehensive Apache Spark integration for large-scale
geospatial data processing and distributed ETL operations.
"""

import logging
import asyncio
import time
from pathlib import Path
from typing import Dict, List, Optional, Any


logger = logging.getLogger(__name__)


class SparkETLProcessor:
    """
    Apache Spark-based ETL processor for large-scale geospatial data.

    This class provides Apache Spark integration for distributed processing
    of large geospatial datasets with automatic optimization and monitoring.

    Args:
        spark_config: Spark configuration dictionary
        master: Spark master URL
        app_name: Application name for Spark

    Examples:
        >>> processor = SparkETLProcessor(
        ...     spark_config={'spark.sql.adaptive.enabled': True},
        ...     master='local[*]',
        ...     app_name='geo_infer_etl'
        ... )
        >>>
        >>> result = await processor.process_large_dataset(
        ...     input_path='s3://data/large_dataset/',
        ...     transformations=['clean', 'aggregate', 'spatial_join'],
        ...     output_path='s3://processed/optimized_data/'
        ... )
    """

    def __init__(
        self,
        spark_config: Optional[Dict[str, Any]] = None,
        master: str = "local[*]",
        app_name: str = "geo_infer_data_etl",
    ):
        self.spark_config = spark_config or {}
        self.master = master
        self.app_name = app_name

        self.spark_session = None

        self._initialize_spark()

        logger.info(f"Initialized SparkETLProcessor with master={master}")

    def _initialize_spark(self):
        """Initialize Spark session."""
        try:
            from pyspark.sql import SparkSession
        except ImportError as exc:
            raise RuntimeError(
                "SparkETLProcessor requires pyspark; install the Spark extra before use"
            ) from exc

        builder = SparkSession.builder.master(self.master).appName(self.app_name)
        for key, value in self.spark_config.items():
            builder = builder.config(key, value)
        self.spark_session = builder.getOrCreate()
        logger.info(f"Initialized Spark session: {self.app_name}")

    async def process_large_dataset(
        self, input_path: str, transformations: List[str], output_path: str, **kwargs
    ) -> Dict[str, Any]:
        """
        Process large dataset using Apache Spark.

        Args:
            input_path: Input data path (HDFS, S3, local)
            transformations: List of transformations to apply
            output_path: Output data path
            **kwargs: Additional processing parameters

        Returns:
            Processing results and metrics
        """
        if not transformations:
            raise ValueError("transformations must contain at least one operation")
        started = time.perf_counter()

        def process() -> Dict[str, Any]:
            suffix = Path(input_path).suffix.lower()
            reader = self.spark_session.read
            if suffix == ".csv":
                frame = (
                    reader.option("header", True)
                    .option("inferSchema", True)
                    .csv(input_path)
                )
            elif suffix in {".json", ".geojson"}:
                frame = reader.json(input_path)
            elif suffix == ".parquet":
                frame = reader.parquet(input_path)
            else:
                raise ValueError(
                    f"Unsupported Spark input format: {suffix or input_path}"
                )

            for transformation in transformations:
                if transformation == "clean":
                    frame = frame.dropna()
                elif transformation == "deduplicate":
                    frame = frame.dropDuplicates()
                elif transformation == "aggregate":
                    group_by = kwargs.get("group_by")
                    aggregations = kwargs.get("aggregations")
                    if not group_by or not aggregations:
                        raise ValueError("aggregate requires group_by and aggregations")
                    frame = frame.groupBy(*group_by).agg(*aggregations)
                elif transformation == "spatial_join":
                    raise RuntimeError(
                        "spatial_join requires an explicit Spark geospatial extension"
                    )
                else:
                    raise ValueError(
                        f"Unsupported Spark transformation: {transformation}"
                    )

            frame.write.mode(kwargs.get("write_mode", "overwrite")).parquet(output_path)
            return {"records_processed": frame.count(), "columns": frame.columns}

        metrics = await asyncio.to_thread(process)
        result = {
            "input_path": input_path,
            "output_path": output_path,
            "transformations_applied": transformations,
            **metrics,
            "processing_time": time.perf_counter() - started,
            "optimization_applied": bool(self.spark_config),
            "status": "completed",
        }

        logger.info(
            f"Dataset processing completed: {result['records_processed']} records"
        )
        return result

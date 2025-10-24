"""
ETL pipeline implementations for GEO-INFER-DATA.

This module provides comprehensive ETL pipeline implementations including
Apache Airflow DAGs, Apache Spark jobs, and custom pipeline orchestrators.

Classes:
    AirflowDAGGenerator: Generate Airflow DAGs for ETL workflows
    SparkETLProcessor: Apache Spark-based ETL processing
    CustomETLOrchestrator: Custom ETL pipeline orchestration
    DataQualityETL: Data quality-focused ETL pipelines

Examples:
    >>> from geo_infer_data.etl import AirflowDAGGenerator, SparkETLProcessor
    >>>
    >>> # Generate Airflow DAG
    >>> dag_generator = AirflowDAGGenerator(config='pipeline_config.yaml')
    >>> dag_code = dag_generator.generate_dag('environmental_monitoring')
    >>>
    >>> # Process with Spark
    >>> spark_processor = SparkETLProcessor(spark_config='spark_config.yaml')
    >>> result = spark_processor.process_large_dataset(input_path, transformations)
"""

from .airflow_dags import AirflowDAGGenerator
from .spark_processing import SparkETLProcessor
from .custom_orchestrator import CustomETLOrchestrator
from .quality_pipelines import DataQualityETL

__all__ = [
    "AirflowDAGGenerator",
    "SparkETLProcessor",
    "CustomETLOrchestrator",
    "DataQualityETL",
]

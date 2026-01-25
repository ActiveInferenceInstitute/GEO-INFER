#!/usr/bin/env python3
"""
Enhanced Logging System for Cascadia Agricultural Analysis Framework

This module provides comprehensive, configurable logging that clearly distinguishes
between real data, synthetic data, and fallback data sources. It includes detailed
information about data size, sources, processing steps, and visualization capabilities.

Based on Python logging best practices from:
- https://docs.python.org/3/library/logging.html
- https://medium.com/@tzhaonj/writing-proper-logs-in-python-for-data-scientists-f1bed1158440
"""

import logging
import logging.config
import json
import sys
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime
import pandas as pd
import geopandas as gpd

class EnhancedLoggingConfig:
    """
    Enhanced logging configuration for Cascadia framework.
    
    Provides clear distinction between:
    - Real data sources (with detailed metadata)
    - Synthetic/test data (clearly marked)
    - Fallback data (when real data unavailable)
    - Processing steps and performance metrics
    - Visualization capabilities and interactions
    """
    
    @staticmethod
    def setup_logging(
        log_level: str = "INFO",
        log_file: Optional[Path] = None,
        console_output: bool = True,
        include_timestamps: bool = True,
        include_module_names: bool = True,
        include_line_numbers: bool = False
    ) -> logging.Logger:
        """
        Set up comprehensive logging configuration.
        
        Args:
            log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            log_file: Optional file path for log output
            console_output: Whether to output to console
            include_timestamps: Include timestamps in log messages
            include_module_names: Include module names in log messages
            include_line_numbers: Include line numbers in log messages
        """
        # Create formatter
        format_parts = []
        if include_timestamps:
            format_parts.append('%(asctime)s')
        format_parts.append('%(levelname)s')
        if include_module_names:
            format_parts.append('%(name)s')
        if include_line_numbers:
            format_parts.append('%(filename)s:%(lineno)d')
        format_parts.append('%(message)s')
        
        formatter = logging.Formatter(' - '.join(format_parts))
        
        # Create handlers
        handlers = []
        
        if console_output:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setFormatter(formatter)
            handlers.append(console_handler)
        
        if log_file:
            file_handler = logging.FileHandler(log_file)
            file_handler.setFormatter(formatter)
            handlers.append(file_handler)
        
        # Configure root logger
        logging.basicConfig(
            level=getattr(logging, log_level.upper()),
            handlers=handlers,
            format='%(asctime)s - %(levelname)s - %(name)s - %(message)s'
        )
        
        logger = logging.getLogger('cascadia')
        logger.info(f"Enhanced logging initialized with level: {log_level}")
        return logger

class DataSourceLogger:
    """
    Specialized logger for data source operations.
    
    Provides detailed logging for:
    - Real data acquisition (with source URLs, file sizes, row counts)
    - Synthetic data generation (with parameters and coverage)
    - Fallback data usage (with reasons and limitations)
    - Data validation and quality metrics
    """
    
    def __init__(self, module_name: str):
        self.logger = logging.getLogger(f'cascadia.data.{module_name}')
        self.module_name = module_name
    
    def log_real_data_acquisition(
        self, 
        source_url: str, 
        file_path: Path, 
        data_type: str,
        row_count: int,
        file_size_mb: float,
        geometry_types: List[str],
        crs: str,
        bbox: Optional[tuple] = None,
        attributes: Optional[List[str]] = None
    ):
        """Log comprehensive information about real data acquisition."""
        self.logger.info(f"📊 REAL DATA ACQUIRED - Module: {self.module_name}")
        self.logger.info(f"   Source URL: {source_url}")
        self.logger.info(f"   File Path: {file_path}")
        self.logger.info(f"   Data Type: {data_type}")
        self.logger.info(f"   Row Count: {row_count:,}")
        self.logger.info(f"   File Size: {file_size_mb:.2f} MB")
        self.logger.info(f"   Geometry Types: {geometry_types}")
        self.logger.info(f"   CRS: {crs}")
        
        if bbox:
            self.logger.info(f"   Bounding Box: {bbox}")
        if attributes:
            self.logger.info(f"   Attributes: {attributes}")
    
    def log_synthetic_data_generation(
        self,
        reason: str,
        parameters: Dict[str, Any],
        row_count: int,
        coverage_area_km2: float,
        geometry_types: List[str]
    ):
        """Log synthetic data generation with clear marking."""
        self.logger.warning(f"🧪 SYNTHETIC DATA GENERATED - Module: {self.module_name}")
        self.logger.warning(f"   Reason: {reason}")
        self.logger.warning(f"   Parameters: {parameters}")
        self.logger.warning(f"   Row Count: {row_count:,}")
        self.logger.warning(f"   Coverage Area: {coverage_area_km2:.2f} km²")
        self.logger.warning(f"   Geometry Types: {geometry_types}")
    
    def log_fallback_data_usage(
        self,
        original_source: str,
        fallback_reason: str,
        fallback_type: str,
        limitations: List[str]
    ):
        """Log fallback data usage with clear limitations."""
        self.logger.error(f"⚠️  FALLBACK DATA USED - Module: {self.module_name}")
        self.logger.error(f"   Original Source: {original_source}")
        self.logger.error(f"   Fallback Reason: {fallback_reason}")
        self.logger.error(f"   Fallback Type: {fallback_type}")
        self.logger.error(f"   Limitations: {limitations}")
    
    def log_data_validation(
        self,
        validation_results: Dict[str, Any],
        quality_score: float,
        issues: List[str]
    ):
        """Log data validation results."""
        self.logger.info(f"🔍 DATA VALIDATION - Module: {self.module_name}")
        self.logger.info(f"   Quality Score: {quality_score:.2f}")
        self.logger.info(f"   Validation Results: {validation_results}")
        
        if issues:
            self.logger.warning(f"   Issues Found: {issues}")
    
    def log_h3_processing(
        self,
        input_features: int,
        output_hexagons: int,
        coverage_percentage: float,
        processing_time: float
    ):
        """Log H3 processing results."""
        self.logger.info(f"🔷 H3 PROCESSING - Module: {self.module_name}")
        self.logger.info(f"   Input Features: {input_features:,}")
        self.logger.info(f"   Output Hexagons: {output_hexagons:,}")
        self.logger.info(f"   Coverage: {coverage_percentage:.1f}%")
        self.logger.info(f"   Processing Time: {processing_time:.2f}s")

class ProcessingLogger:
    """
    Specialized logger for data processing operations.
    """
    
    def __init__(self, module_name: str):
        self.logger = logging.getLogger(f'cascadia.processing.{module_name}')
        self.module_name = module_name
    
    def log_processing_start(self, operation: str, parameters: Dict[str, Any]):
        """Log the start of a processing operation."""
        self.logger.info(f"🚀 PROCESSING START - {operation}")
        self.logger.info(f"   Module: {self.module_name}")
        self.logger.info(f"   Parameters: {parameters}")
    
    def log_processing_step(self, step: str, details: Dict[str, Any]):
        """Log a processing step."""
        self.logger.info(f"   Step: {step}")
        for key, value in details.items():
            self.logger.info(f"     {key}: {value}")
    
    def log_processing_complete(self, operation: str, results: Dict[str, Any], duration: float):
        """Log the completion of a processing operation."""
        self.logger.info(f"✅ PROCESSING COMPLETE - {operation}")
        self.logger.info(f"   Duration: {duration:.2f}s")
        for key, value in results.items():
            self.logger.info(f"   {key}: {value}")

class VisualizationLogger:
    """
    Specialized logger for visualization operations.
    """
    
    def __init__(self, module_name: str):
        self.logger = logging.getLogger(f'cascadia.visualization.{module_name}')
        self.module_name = module_name
    
    def log_visualization_creation(
        self,
        viz_type: str,
        data_sources: List[str],
        hexagon_count: int,
        layers: List[str],
        interactive_features: List[str]
    ):
        """Log visualization creation."""
        self.logger.info(f"🎨 VISUALIZATION CREATED - {viz_type}")
        self.logger.info(f"   Module: {self.module_name}")
        self.logger.info(f"   Data Sources: {data_sources}")
        self.logger.info(f"   Hexagon Count: {hexagon_count:,}")
        self.logger.info(f"   Layers: {layers}")
        self.logger.info(f"   Interactive Features: {interactive_features}")
    
    def log_interactive_feature(self, feature: str, status: str):
        """Log interactive feature status."""
        self.logger.info(f"   Interactive Feature: {feature} - {status}")

class PerformanceLogger:
    """
    Specialized logger for performance metrics.
    """
    
    def __init__(self):
        self.logger = logging.getLogger('cascadia.performance')
    
    def log_performance_metrics(
        self,
        operation: str,
        duration: float,
        memory_usage_mb: float,
        cpu_usage_percent: float,
        data_size_mb: float
    ):
        """Log performance metrics."""
        self.logger.info(f"⚡ PERFORMANCE - {operation}")
        self.logger.info(f"   Duration: {duration:.2f}s")
        self.logger.info(f"   Memory Usage: {memory_usage_mb:.2f} MB")
        self.logger.info(f"   CPU Usage: {cpu_usage_percent:.1f}%")
        self.logger.info(f"   Data Size: {data_size_mb:.2f} MB")

def create_enhanced_logger(module_name: str) -> tuple:
    """
    Create enhanced loggers for a module.
    
    Returns:
        Tuple of (data_logger, processing_logger, viz_logger)
    """
    data_logger = DataSourceLogger(module_name)
    processing_logger = ProcessingLogger(module_name)
    viz_logger = VisualizationLogger(module_name)
    
    return data_logger, processing_logger, viz_logger

def log_dataframe_summary(logger: logging.Logger, df: pd.DataFrame, name: str):
    """Log a comprehensive summary of a DataFrame."""
    logger.info(f"📋 DATAFRAME SUMMARY - {name}")
    logger.info(f"   Shape: {df.shape}")
    logger.info(f"   Memory Usage: {df.memory_usage(deep=True).sum() / 1024 / 1024:.2f} MB")
    logger.info(f"   Columns: {list(df.columns)}")
    logger.info(f"   Data Types: {dict(df.dtypes)}")
    
    if not df.empty:
        logger.info(f"   Null Values: {df.isnull().sum().to_dict()}")
        logger.info(f"   Unique Values (first 5 cols): {df.nunique().head().to_dict()}")

def log_geodataframe_summary(logger: logging.Logger, gdf: gpd.GeoDataFrame, name: str):
    """Log a comprehensive summary of a GeoDataFrame."""
    logger.info(f"🗺️  GEODATAFRAME SUMMARY - {name}")
    logger.info(f"   Shape: {gdf.shape}")
    logger.info(f"   CRS: {gdf.crs}")
    logger.info(f"   Geometry Type: {gdf.geometry.geom_type.unique()}")
    logger.info(f"   Bounds: {gdf.total_bounds}")
    
    if not gdf.empty:
        area_km2 = gdf.geometry.area.sum() * 111 * 111  # Rough conversion
        logger.info(f"   Total Area: {area_km2:.2f} km²")
    
    log_dataframe_summary(logger, gdf, name)

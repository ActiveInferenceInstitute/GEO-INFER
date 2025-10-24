"""
Data compression utilities for GEO-INFER-DATA.

This module provides data compression capabilities for efficient storage
and transmission of geospatial data.
"""

import logging
from typing import Dict, List, Optional, Union, Any
import gzip
import lzma
import bz2
import pickle

import geopandas as gpd
import pandas as pd
import numpy as np

from ..models.schemas import DataFormat


logger = logging.getLogger(__name__)


class DataCompressor:
    """
    Data compression for efficient storage.

    This class provides compression utilities for geospatial data
    including various compression algorithms and format-specific
    optimizations.

    Examples:
        >>> compressor = DataCompressor()
        >>>
        >>> # Compress geospatial data
        >>> compressed_data = compressor.compress_data(geodataframe)
        >>>
        >>> # Decompress data
        >>> decompressed_data = compressor.decompress_data(compressed_data)
        >>>
        >>> # Get compression statistics
        >>> stats = compressor.get_compression_stats()
        >>> print(f"Compression ratio: {stats['ratio']:.2f}x")
    """

    def __init__(self, algorithm: str = 'gzip', level: int = 6):
        self.algorithm = algorithm
        self.level = level
        self.compression_stats = {
            'total_compressed': 0,
            'total_original': 0,
            'compression_count': 0
        }

        logger.info(f"Initialized DataCompressor with {algorithm} algorithm")

    def is_enabled(self) -> bool:
        """Check if compression is enabled."""
        return self.algorithm != 'none'

    def compress_data(self, data: Any, format: Optional[DataFormat] = None) -> bytes:
        """
        Compress geospatial data.

        Args:
            data: Data to compress
            format: Data format hint

        Returns:
            Compressed data as bytes
        """
        logger.debug(f"Compressing data with {self.algorithm} algorithm")

        # Serialize data first
        serialized_data = self._serialize_data(data, format)

        # Compress based on algorithm
        if self.algorithm == 'gzip':
            compressed_data = gzip.compress(serialized_data, compresslevel=self.level)
        elif self.algorithm == 'lzma':
            compressed_data = lzma.compress(serialized_data, preset=self.level)
        elif self.algorithm == 'bz2':
            compressed_data = bz2.compress(serialized_data, compresslevel=self.level)
        elif self.algorithm == 'none':
            compressed_data = serialized_data
        else:
            raise ValueError(f"Unknown compression algorithm: {self.algorithm}")

        # Update statistics
        self.compression_stats['total_compressed'] += len(compressed_data)
        self.compression_stats['total_original'] += len(serialized_data)
        self.compression_stats['compression_count'] += 1

        logger.debug(f"Compressed data: {len(serialized_data)} -> {len(compressed_data)} bytes")
        return compressed_data

    def decompress_data(self, compressed_data: bytes, format: Optional[DataFormat] = None) -> Any:
        """
        Decompress geospatial data.

        Args:
            compressed_data: Compressed data bytes
            format: Data format hint

        Returns:
            Decompressed data
        """
        logger.debug(f"Decompressing data with {self.algorithm} algorithm")

        # Decompress based on algorithm
        if self.algorithm == 'gzip':
            decompressed_data = gzip.decompress(compressed_data)
        elif self.algorithm == 'lzma':
            decompressed_data = lzma.decompress(compressed_data)
        elif self.algorithm == 'bz2':
            decompressed_data = bz2.decompress(compressed_data)
        elif self.algorithm == 'none':
            decompressed_data = compressed_data
        else:
            raise ValueError(f"Unknown compression algorithm: {self.algorithm}")

        # Deserialize data
        data = self._deserialize_data(decompressed_data, format)

        logger.debug(f"Decompressed data: {len(compressed_data)} -> {len(decompressed_data)} bytes")
        return data

    def _serialize_data(self, data: Any, format: Optional[DataFormat] = None) -> bytes:
        """Serialize data to bytes."""
        if isinstance(data, (pd.DataFrame, gpd.GeoDataFrame)):
            if format == DataFormat.PARQUET or (format is None and len(data) > 1000):
                # Use Parquet for large datasets
                return data.to_parquet()
            else:
                # Use pickle for smaller datasets or complex objects
                return pickle.dumps(data)
        elif isinstance(data, np.ndarray):
            return pickle.dumps(data)
        elif isinstance(data, dict):
            return pickle.dumps(data)
        else:
            return pickle.dumps(data)

    def _deserialize_data(self, data: bytes, format: Optional[DataFormat] = None) -> Any:
        """Deserialize data from bytes."""
        try:
            # Try to deserialize as DataFrame first
            if format == DataFormat.PARQUET or b'PAR1' in data[:4]:
                return pd.read_parquet(data)
            else:
                return pickle.loads(data)
        except Exception:
            # Fallback to pickle
            return pickle.loads(data)

    def get_compression_stats(self) -> Dict[str, Any]:
        """Get compression statistics."""
        total_compressed = self.compression_stats['total_compressed']
        total_original = self.compression_stats['total_original']

        if total_original > 0:
            compression_ratio = total_original / total_compressed
        else:
            compression_ratio = 1.0

        return {
            'algorithm': self.algorithm,
            'level': self.level,
            'total_compressed_bytes': total_compressed,
            'total_original_bytes': total_original,
            'compression_ratio': compression_ratio,
            'compression_count': self.compression_stats['compression_count']
        }

    def optimize_for_storage(self, data: Any) -> Dict[str, Any]:
        """
        Optimize data for storage with compression recommendations.

        Args:
            data: Data to analyze

        Returns:
            Optimization recommendations
        """
        recommendations = {
            'recommended_compression': self.algorithm,
            'estimated_savings': 0.0,
            'format_recommendation': DataFormat.CSV
        }

        if isinstance(data, (pd.DataFrame, gpd.GeoDataFrame)):
            # Analyze data characteristics
            data_size = data.memory_usage(deep=True).sum()

            if len(data) > 10000:
                recommendations['format_recommendation'] = DataFormat.PARQUET
                recommendations['estimated_savings'] = 0.7  # 70% compression
            elif isinstance(data, gpd.GeoDataFrame):
                recommendations['format_recommendation'] = DataFormat.GEOPACKAGE
                recommendations['estimated_savings'] = 0.5  # 50% compression
            else:
                recommendations['format_recommendation'] = DataFormat.CSV
                recommendations['estimated_savings'] = 0.3  # 30% compression

        return recommendations

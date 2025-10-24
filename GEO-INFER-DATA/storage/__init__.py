"""
Storage implementations for GEO-INFER-DATA.

This module provides comprehensive storage implementations including
database schemas, indexing strategies, and storage optimization utilities.

Classes:
    PostgreSQLStorage: PostgreSQL/PostGIS storage implementation
    MinIOStorage: MinIO/S3 object storage implementation
    RedisStorage: Redis caching and storage implementation
    FileSystemStorage: Local file system storage implementation
    StorageOptimizer: Storage performance optimization utilities

Examples:
    >>> from geo_infer_data.storage import PostgreSQLStorage, StorageOptimizer
    >>>
    >>> # PostgreSQL storage
    >>> pg_storage = PostgreSQLStorage(connection_string='postgresql://...')
    >>> await pg_storage.create_table(table_schema, 'sensor_data')
    >>>
    >>> # Storage optimization
    >>> optimizer = StorageOptimizer()
    >>> optimizations = optimizer.analyze_and_optimize(datasets)
"""

from .postgresql import PostgreSQLStorage
from .minio_storage import MinIOStorage
from .redis_storage import RedisStorage
from .filesystem import FileSystemStorage
from .optimizer import StorageOptimizer

__all__ = [
    "PostgreSQLStorage",
    "MinIOStorage",
    "RedisStorage",
    "FileSystemStorage",
    "StorageOptimizer",
]

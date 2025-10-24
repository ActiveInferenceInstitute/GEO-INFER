"""
Data connectors for GEO-INFER-DATA.

This module provides comprehensive data connectors for various geospatial
data sources including databases, APIs, files, and streaming services.

Classes:
    DatabaseConnector: Connect to relational and NoSQL databases
    APIConnector: Connect to REST and GraphQL APIs
    FileConnector: Read from various file formats
    StreamConnector: Connect to streaming data sources
    CloudConnector: Connect to cloud storage services

Examples:
    >>> from geo_infer_data.connectors import DatabaseConnector, APIConnector
    >>>
    >>> # Connect to PostgreSQL database
    >>> db_connector = DatabaseConnector(
    ...     connection_type='postgresql',
    ...     connection_string='postgresql://user:pass@localhost/db'
    ... )
    >>>
    >>> # Connect to REST API
    >>> api_connector = APIConnector(
    ...     base_url='https://api.example.com',
    ...     authentication={'api_key': 'your_key'}
    ... )
"""

from .database import DatabaseConnector
from .api import APIConnector
from .file import FileConnector
from .stream import StreamConnector
from .cloud import CloudConnector

__all__ = [
    "DatabaseConnector",
    "APIConnector",
    "FileConnector",
    "StreamConnector",
    "CloudConnector",
]

"""
API implementations for GEO-INFER-DATA.

This module contains REST API and other interface implementations
for accessing and managing geospatial data.

Classes:
    DataAPI: REST API server for data access
    DataService: Core data service functionality

Examples:
    >>> from geo_infer_data.api import DataAPI
    >>>
    >>> # Start data API server
    >>> api = DataAPI(config='config/local.yaml')
    >>> api.start()
    >>>
    >>> # Access data service
    >>> service = DataService()
    >>> datasets = service.list_datasets()
"""
from .rest_api import DataAPI
from .service import DataService

__all__ = [
    "DataAPI",
    "DataService",
]

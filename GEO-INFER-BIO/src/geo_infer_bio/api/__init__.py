"""
GEO-INFER-BIO api package.

HTTP interfaces for the bioinformatics module:
- rest_api: FastAPI application exposing sequence/spatial analysis endpoints
- graphql_api: FastAPI application mounting a GraphQL router
"""

from .graphql_api import app as graphql_app
from .rest_api import app as rest_app

__all__ = [
    "graphql_app",
    "rest_app",
]

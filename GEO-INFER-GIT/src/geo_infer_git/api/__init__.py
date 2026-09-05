#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
REST API subpackage for GEO-INFER-GIT.

Exposes the FastAPI application and server helpers implemented in
:mod:`geo_infer_git.api.rest_api`.
"""

from .rest_api import (
    app,
    initialize_api,
    run_api,
)

__all__ = ["app", "initialize_api", "run_api"]
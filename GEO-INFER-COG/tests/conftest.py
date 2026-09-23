"""
Pytest configuration for GEO-INFER-COG tests.
"""

# GS19-56: flask/flask_cors are optional (api-extra) dependencies; without
# them the REST-API suite is skipped at collection instead of erroring.
try:
    import flask  # noqa: F401
    import flask_cors  # noqa: F401
except ImportError:  # pragma: no cover - only reached on bare installs
    collect_ignore_glob = ["test_rest_api.py"]
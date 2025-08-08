#!/bin/bash
set -e

# Run tests with uv-managed environment
# - Ensures Python from .python-version is used
# - Installs test requirements declared in pyproject (tool/uv extras) if any

# Sync dependencies (uses pyproject.toml)
uv sync

# Run tests with coverage in the project environment
uv run pytest --cov=src --cov-report=term-missing
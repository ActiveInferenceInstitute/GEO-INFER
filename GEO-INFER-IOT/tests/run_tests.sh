#!/bin/bash
set -e

# Run tests with uv-managed environment

uv sync
uv run pytest --cov=src --cov-report=term-missing
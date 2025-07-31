#!/bin/bash
set -e

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install test requirements
pip install -r requirements-test.txt

# Run tests with coverage
pytest --cov=src --cov-report=term-missing

# Deactivate virtual environment
deactivate
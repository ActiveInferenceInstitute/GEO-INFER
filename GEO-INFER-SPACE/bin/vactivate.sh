#!/bin/bash
# Activate the virtual environment for GEO-INFER-SPACE

# Get the project directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

# Source the environment variables
source "$SCRIPT_DIR/environment.sh"

# Activate the virtual environment
source "$PROJECT_DIR/venv/bin/activate"

echo "Virtual environment activated"
echo "Python: $(which python)"
echo "Python version: $(python --version)" 
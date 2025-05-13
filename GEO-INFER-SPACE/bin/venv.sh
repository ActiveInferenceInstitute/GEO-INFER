#!/bin/bash
# Create a virtual environment for GEO-INFER-SPACE

# Get the project directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

# Create a virtual environment
python3 -m venv "$PROJECT_DIR/venv"

echo "Virtual environment created at $PROJECT_DIR/venv"
echo "Activate it with: source $PROJECT_DIR/bin/vactivate.sh" 
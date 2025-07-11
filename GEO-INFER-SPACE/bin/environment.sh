#!/bin/bash
# Environment setup for GEO-INFER-SPACE

# Set project directory
export PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# Add project source to PYTHONPATH
export PYTHONPATH="$PROJECT_DIR/src:$PYTHONPATH"

# Set output directory for cloned repositories
export OSC_REPOS_DIR="$PROJECT_DIR/repo"

# Set log level
export LOG_LEVEL="INFO"

echo "Environment variables set for GEO-INFER-SPACE"
echo "Project directory: $PROJECT_DIR" 
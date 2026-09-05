#!/bin/bash
# Markdown to PDF Converter Wrapper Script
# Part of the GEO-INFER Framework

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Run the Python script with python3
python3 "$SCRIPT_DIR/markdown_to_pdf.py" "$@" 
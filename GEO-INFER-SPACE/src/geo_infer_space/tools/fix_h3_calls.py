#!/usr/bin/env python3
"""
Fix h3 function calls in visualization module
"""

import re

def fix_h3_calls_in_file(filepath):
    """Fix h3 function calls in a file."""
    with open(filepath, 'r') as f:
        content = f.read()
    
    # Replace function calls with h3_lib calls
    replacements = [
        (r'\bis_valid_cell\b', 'h3_lib.is_valid_cell'),
        (r'\bcell_to_boundary\b', 'h3_lib.cell_to_boundary'),
        (r'\bget_resolution\b', 'h3_lib.get_resolution'),
        (r'\bcell_area\b', 'h3_lib.cell_area'),
        (r'\bcell_to_latlng\b', 'h3_lib.cell_to_latlng'),
        (r'\blatlng_to_cell\b', 'h3_lib.latlng_to_cell'),
    ]
    
    for pattern, replacement in replacements:
        content = re.sub(pattern, replacement, content)
    
    with open(filepath, 'w') as f:
        f.write(content)

def main():
    """Fix h3 calls in modules."""
    files = ["src/h3/visualization.py", "src/h3/animation.py", "src/h3/interactive.py"]
    for filepath in files:
        print(f"Fixing h3 calls in {filepath}")
        fix_h3_calls_in_file(filepath)

if __name__ == "__main__":
    main() 
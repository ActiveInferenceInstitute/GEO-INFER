#!/usr/bin/env python3
"""
Fix double h3_lib references
"""

import re

def fix_double_h3_lib(filepath):
    """Fix double h3_lib references in a file."""
    with open(filepath, 'r') as f:
        content = f.read()
    
    # Replace double h3_lib references
    content = re.sub(r'h3_lib\.h3_lib\.', 'h3_lib.', content)
    
    with open(filepath, 'w') as f:
        f.write(content)

def main():
    """Fix double h3_lib references in modules."""
    files = ["src/h3/visualization.py", "src/h3/animation.py", "src/h3/interactive.py"]
    for filepath in files:
        print(f"Fixing double h3_lib references in {filepath}")
        fix_double_h3_lib(filepath)

if __name__ == "__main__":
    main() 
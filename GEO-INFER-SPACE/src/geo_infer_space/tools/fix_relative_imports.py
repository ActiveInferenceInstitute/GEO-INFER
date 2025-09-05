#!/usr/bin/env python3
"""
Fix relative imports in H3 modules
"""

import os
import re

def fix_relative_imports_in_file(filepath):
    """Fix relative imports in a file."""
    with open(filepath, 'r') as f:
        content = f.read()
    
    # Replace relative imports with absolute imports
    content = re.sub(r'from \.(\w+) import', r'from \1 import', content)
    
    with open(filepath, 'w') as f:
        f.write(content)

def main():
    """Fix relative imports in all h3 module files."""
    h3_dir = "src/h3"
    
    for filename in os.listdir(h3_dir):
        if filename.endswith('.py') and filename != '__init__.py':
            filepath = os.path.join(h3_dir, filename)
            print(f"Fixing relative imports in {filename}")
            fix_relative_imports_in_file(filepath)

if __name__ == "__main__":
    main() 
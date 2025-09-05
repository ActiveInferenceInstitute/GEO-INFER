#!/usr/bin/env python3
"""
Fix import statements in H3 examples
"""

import os
import re

def fix_imports_in_file(filepath):
    """Fix import statements in a file."""
    with open(filepath, 'r') as f:
        content = f.read()
    
    # Replace h3.module with module
    content = re.sub(r'from h3\.(\w+) import', r'from \1 import', content)
    
    with open(filepath, 'w') as f:
        f.write(content)

def main():
    """Fix imports in all example files."""
    examples_dir = "src/h3/examples"
    
    for filename in os.listdir(examples_dir):
        if filename.endswith('.py'):
            filepath = os.path.join(examples_dir, filename)
            print(f"Fixing imports in {filename}")
            fix_imports_in_file(filepath)

if __name__ == "__main__":
    main() 
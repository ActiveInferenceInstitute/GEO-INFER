#!/usr/bin/env python3
"""
Validate that all user-facing code and documentation uses uv instead of pip.

This script checks for remaining 'pip install' references in:
- README files
- Documentation files
- Python source code (excluding auto-generated files)
- Error messages
- Setup scripts
"""

import re
import sys
from pathlib import Path
from typing import List, Tuple

PROJECT_ROOT = Path(__file__).parent.parent.parent

# Patterns to search for
PIP_PATTERNS = [
    r'pip install',
    r'python -m pip install',
    r'python3 -m pip install',
    r'sys\.executable.*pip',
    r'\[sys\.executable.*-m.*pip',
]

# Files/directories to exclude
EXCLUDE_PATTERNS = [
    r'\.egg-info',
    r'__pycache__',
    r'\.pyc$',
    r'\.pyo$',
    r'\.pytest_cache',
    r'\.test-results',
    r'\.benchmarks',
    r'\.coverage',
    r'\.git',
    r'\.venv',
    r'venv/',
    r'node_modules',
    r'\.log$',
    r'\.md\.log$',
    r'uv\.lock$',  # Lock file may contain pip references
]

# File types to check
CHECK_EXTENSIONS = ['.md', '.py', '.txt', '.yaml', '.yml', '.rst']

# Files that are allowed to have pip references (auto-generated or special cases)
ALLOWED_FILES = [
    'PKG-INFO',  # Auto-generated
    'SOURCES.txt',  # Auto-generated
    'uv.lock',  # Lock file
    'validate_uv_migration.py',  # This script itself (contains patterns to search for)
]


def should_check_file(file_path: Path) -> bool:
    """Determine if a file should be checked."""
    # Check if file is in excluded directory
    for pattern in EXCLUDE_PATTERNS:
        if re.search(pattern, str(file_path)):
            return False
    
    # Check if file is in allowed list
    if file_path.name in ALLOWED_FILES:
        return False
    
    # Check file extension
    if file_path.suffix not in CHECK_EXTENSIONS:
        return False
    
    return True


def find_pip_references(file_path: Path) -> List[Tuple[int, str]]:
    """Find all pip install references in a file."""
    issues = []
    
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            for line_num, line in enumerate(f, 1):
                for pattern in PIP_PATTERNS:
                    if re.search(pattern, line, re.IGNORECASE):
                        # Check if it's already using uv
                        if 'uv pip install' in line or 'uv run' in line:
                            continue
                        issues.append((line_num, line.strip()))
                        break
    except Exception as e:
        # Skip files that can't be read
        pass
    
    return issues


def scan_directory(directory: Path) -> dict:
    """Scan a directory for pip install references."""
    results = {}
    
    for file_path in directory.rglob('*'):
        if not file_path.is_file():
            continue
        
        if not should_check_file(file_path):
            continue
        
        issues = find_pip_references(file_path)
        if issues:
            results[file_path] = issues
    
    return results


def main():
    """Main validation function."""
    print("=" * 70)
    print("Validating UV Migration - Checking for pip install references")
    print("=" * 70)
    print()
    
    # Scan key directories
    directories_to_scan = [
        PROJECT_ROOT / 'GEO-INFER-INTRA' / 'docs',
        PROJECT_ROOT / 'GEO-INFER-INTRA' / 'scripts',
    ]
    
    # Also scan all module README files
    all_results = {}
    
    # Check main README
    main_readme = PROJECT_ROOT / 'README.md'
    if main_readme.exists():
        issues = find_pip_references(main_readme)
        if issues:
            all_results[main_readme] = issues
    
    # Check all module READMEs
    for item in PROJECT_ROOT.iterdir():
        if item.is_dir() and item.name.startswith('GEO-INFER-'):
            readme = item / 'README.md'
            if readme.exists():
                issues = find_pip_references(readme)
                if issues:
                    all_results[readme] = issues
            
            # Check examples directories
            examples_dir = item / 'examples'
            if examples_dir.exists():
                for file_path in examples_dir.rglob('*.py'):
                    if should_check_file(file_path):
                        issues = find_pip_references(file_path)
                        if issues:
                            all_results[file_path] = issues
            
            # Check src directories for error messages
            src_dir = item / 'src'
            if src_dir.exists():
                for file_path in src_dir.rglob('*.py'):
                    if should_check_file(file_path):
                        issues = find_pip_references(file_path)
                        if issues:
                            all_results[file_path] = issues
    
    # Scan additional directories
    for directory in directories_to_scan:
        if directory.exists():
            results = scan_directory(directory)
            all_results.update(results)
    
    # Report results
    if not all_results:
        print("✅ No pip install references found in user-facing code/docs!")
        print("   All files are using uv for package management.")
        return 0
    
    print(f"❌ Found {len(all_results)} files with pip install references:\n")
    
    for file_path, issues in sorted(all_results.items()):
        rel_path = file_path.relative_to(PROJECT_ROOT)
        print(f"📄 {rel_path}")
        for line_num, line in issues[:5]:  # Show first 5 issues per file
            print(f"   Line {line_num}: {line[:80]}")
        if len(issues) > 5:
            print(f"   ... and {len(issues) - 5} more issues")
        print()
    
    print("=" * 70)
    print(f"Summary: {len(all_results)} files need updates")
    print("=" * 70)
    print("\nRecommendation: Update all references to use 'uv pip install'")
    
    return 1


if __name__ == "__main__":
    sys.exit(main())


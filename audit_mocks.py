#!/usr/bin/env python3
"""
Audit mock usage in test files across GEO-INFER repository.

Categorizes each file's mock usage as:
- UNUSED: imports mock but never uses it  
- EXTERNAL: mocks external services (redis, requests, kubernetes, etc.)
- INTERNAL: mocks internal code that has real implementations
"""
import os
import re
import sys

EXTERNAL_PATTERNS = [
    'redis', 'Redis', 'requests', 'kubernetes', 'git.Repo',
    'subprocess.', 'builtins.open', 'prometheus', 'structlog',
    'start_http_server', 'os.environ'
]


def audit_file(filepath):
    """Audit a single test file for mock usage."""
    with open(filepath, 'r') as f:
        content = f.read()
    
    # Check for mock import
    has_mock_import = bool(re.search(
        r'from unittest\.mock import|from unittest import mock|import unittest\.mock',
        content
    ))
    
    if not has_mock_import:
        return None  # Not relevant
    
    # Count mock usages
    mock_calls = len(re.findall(r'Mock\(\)|MagicMock\(\)|@patch|patch\(|patch\.object', content))
    
    if mock_calls == 0:
        return 'UNUSED'
    
    # Check if mocks are for external services
    external_count = 0
    internal_count = 0
    
    for line in content.split('\n'):
        if 'patch(' in line or '@patch' in line:
            is_external = any(pat in line for pat in EXTERNAL_PATTERNS)
            if is_external:
                external_count += 1
            else:
                internal_count += 1
        elif 'Mock()' in line or 'MagicMock()' in line:
            # Check context
            internal_count += 1
    
    if internal_count == 0 and external_count > 0:
        return f'EXTERNAL ({external_count} patches)'
    elif internal_count > 0 and external_count == 0:
        return f'INTERNAL ({internal_count} mocks)'
    else:
        return f'MIXED (ext={external_count}, int={internal_count})'


def main():
    repo_root = sys.argv[1] if len(sys.argv) > 1 else '.'
    
    results = {'UNUSED': [], 'EXTERNAL': [], 'INTERNAL': [], 'MIXED': []}
    
    for dirpath, _, filenames in os.walk(repo_root):
        if '.git' in dirpath:
            continue
        for filename in filenames:
            if not filename.startswith('test_') and filename != 'conftest.py':
                continue
            if not filename.endswith('.py'):
                continue
            filepath = os.path.join(dirpath, filename)
            result = audit_file(filepath)
            if result is None:
                continue
            
            category = result.split('(')[0].strip() if '(' in result else result
            results.setdefault(category, []).append((filepath, result))
    
    for category, files in sorted(results.items()):
        print(f"\n=== {category} ({len(files)} files) ===")
        for filepath, detail in files:
            print(f"  {filepath}: {detail}")


if __name__ == '__main__':
    main()

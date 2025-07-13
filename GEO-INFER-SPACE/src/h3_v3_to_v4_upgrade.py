#!/usr/bin/env python3
"""
H3 v3 to v4 Upgrade Scanner

This script recursively scans the GEO-INFER-SPACE repository for Python files using legacy H3 3.x method names,
and logs all findings (file, line, and code context) to a report file. This helps surface all places needing
manual v3→v4 migration for the H3 library.

Usage:
    python h3_v3_to_v4_upgrade.py [--repo-root <path>] [--output <logfile>]

Example:
    python h3_v3_to_v4_upgrade.py --repo-root ../ --output h3_upgrade_report.txt
"""
import os
import re
import argparse
from pathlib import Path

# List of H3 3.x method names to search for (as regex patterns)
H3_V3_METHODS = [
    r'geo_to_h3\s*\(',
    r'h3_to_geo\s*\(',
    r'h3_to_geo_boundary\s*\(',
    r'k_ring\s*\(',
    r'hex_ring\s*\(',
    r'h3_distance\s*\(',
    r'h3_line\s*\(',
    r'h3_to_parent\s*\(',
    r'h3_to_children\s*\(',
    r'compact\s*\(',
    r'uncompact\s*\(',
    r'polyfill\s*\(',
    r'h3SetToMultiPolygon\s*\(',
    r'h3SetToLinkedGeo\s*\(',
    r'h3IndexesAreNeighbors\s*\(',
    r'h3IsValid\s*\(',
    r'h3_cell_area\s*\(',
    r'h3_cell_to_boundary\s*\(',
    r'h3_cell_to_latlng\s*\(',
    r'h3_cell_to_string\s*\(',
    r'cell_area\s*\(',
    r'cell_to_boundary\s*\(',
    r'cell_to_latlng\s*\(',
    r'cell_to_string\s*\(',
]

# Compile regex patterns
H3_PATTERNS = [re.compile(pattern) for pattern in H3_V3_METHODS]


def scan_file(file_path: Path) -> list:
    """Scan a single file for H3 v3 method usages."""
    results = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        for i, line in enumerate(lines):
            for pattern in H3_PATTERNS:
                if pattern.search(line):
                    # Capture a few lines of context
                    context = ''.join(lines[max(0, i-1):min(len(lines), i+2)])
                    results.append({
                        'file': str(file_path),
                        'line_num': i+1,
                        'line': line.strip(),
                        'context': context.strip()
                    })
    except Exception as e:
        results.append({'file': str(file_path), 'error': str(e)})
    return results


def scan_repo(repo_root: Path) -> list:
    """Recursively scan all .py files in the repo for H3 v3 method usages."""
    findings = []
    for root, _, files in os.walk(repo_root):
        for fname in files:
            if fname.endswith('.py'):
                fpath = Path(root) / fname
                findings.extend(scan_file(fpath))
    return findings


def main():
    parser = argparse.ArgumentParser(description="Scan for H3 v3 method usages needing v4 migration.")
    parser.add_argument('--repo-root', type=str, default=str(Path(__file__).parent.parent),
                        help='Root directory of the repo to scan (default: parent of this script)')
    parser.add_argument('--output', type=str, default='h3_upgrade_report.txt',
                        help='Output log file for findings')
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve()
    output_path = Path(args.output).resolve()

    print(f"Scanning repo: {repo_root}")
    findings = scan_repo(repo_root)

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(f"H3 v3 to v4 Upgrade Report\nRepo: {repo_root}\n\n")
        for result in findings:
            if 'error' in result:
                f.write(f"[ERROR] {result['file']}: {result['error']}\n")
            else:
                f.write(f"File: {result['file']}\nLine: {result['line_num']}\nCode: {result['line']}\nContext:\n{result['context']}\n{'-'*40}\n")
    print(f"Scan complete. {len(findings)} findings written to {output_path}")

if __name__ == "__main__":
    main() 
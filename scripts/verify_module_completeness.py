#!/usr/bin/env python3
"""
Module Completeness Verification Script

Systematically checks all GEO-INFER modules for:
- requirements.txt
- setup.py/pyproject.toml
- README.md with YAML front matter
- src/ directory structure
- examples/ directory with files
- tests/ directory with test files
- API Reference in README
- Integration examples
"""

import os
import re
import yaml
from pathlib import Path
from typing import Dict, List, Tuple
from collections import defaultdict


class ModuleCompletenessChecker:
    """Check completeness of GEO-INFER modules."""
    
    def __init__(self, root_dir: str = "."):
        self.root_dir = Path(root_dir)
        self.results = defaultdict(dict)
        self.modules = []
        
    def find_modules(self) -> List[str]:
        """Find all GEO-INFER modules."""
        modules = []
        for item in self.root_dir.iterdir():
            if item.is_dir() and item.name.startswith("GEO-INFER-"):
                modules.append(item.name)
        return sorted(modules)
    
    def check_file_exists(self, module_path: Path, filename: str) -> bool:
        """Check if a file exists."""
        return (module_path / filename).exists()
    
    def check_yaml_front_matter(self, readme_path: Path) -> Tuple[bool, dict]:
        """Check if README has YAML front matter."""
        if not readme_path.exists():
            return False, {}
        
        try:
            with open(readme_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for YAML front matter (--- delimited)
            yaml_match = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
            if yaml_match:
                try:
                    yaml_content = yaml.safe_load(yaml_match.group(1))
                    return True, yaml_content or {}
                except yaml.YAMLError:
                    return False, {}
            return False, {}
        except Exception:
            return False, {}
    
    def check_api_reference(self, readme_path: Path) -> bool:
        """Check if README contains API Reference section."""
        if not readme_path.exists():
            return False
        
        try:
            with open(readme_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for API Reference section (case insensitive, handles emojis)
            api_patterns = [
                r'#+\s+.*API\s+Reference',
                r'#+\s+API\s+Reference',
                r'##\s+API',
                r'#+\s+API',
            ]
            
            for pattern in api_patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    # Check if it has code examples
                    if '```python' in content or '```' in content:
                        return True
            return False
        except Exception:
            return False
    
    def check_directory_structure(self, module_path: Path, dirname: str) -> Tuple[bool, int]:
        """Check if directory exists and count files."""
        dir_path = module_path / dirname
        if not dir_path.exists() or not dir_path.is_dir():
            return False, 0
        
        # Count files recursively for src, tests, and examples
        if dirname == 'src':
            files = list(dir_path.rglob('*.py'))
        elif dirname == 'tests':
            # Count test files recursively
            files = list(dir_path.rglob('test_*.py')) + list(dir_path.rglob('*_test.py'))
        else:
            # For examples, count all files recursively
            files = list(dir_path.rglob('*'))
        
        files = [f for f in files if f.is_file()]
        return True, len(files)
    
    def verify_module(self, module_name: str) -> Dict:
        """Verify completeness of a single module."""
        module_path = self.root_dir / module_name
        result = {
            'module': module_name,
            'requirements_txt': False,
            'setup_py': False,
            'pyproject_toml': False,
            'readme_md': False,
            'yaml_front_matter': False,
            'api_reference': False,
            'src_dir': False,
            'src_files': 0,
            'examples_dir': False,
            'examples_files': 0,
            'tests_dir': False,
            'test_files': 0,
            'integration_examples': False,
        }
        
        # Check requirements.txt
        result['requirements_txt'] = self.check_file_exists(module_path, 'requirements.txt')
        
        # Check setup.py
        result['setup_py'] = self.check_file_exists(module_path, 'setup.py')
        
        # Check pyproject.toml
        result['pyproject_toml'] = self.check_file_exists(module_path, 'pyproject.toml')
        
        # Check README.md
        readme_path = module_path / 'README.md'
        result['readme_md'] = readme_path.exists()
        
        # Check YAML front matter
        if result['readme_md']:
            has_yaml, yaml_data = self.check_yaml_front_matter(readme_path)
            result['yaml_front_matter'] = has_yaml
            result['yaml_data'] = yaml_data
        
        # Check API Reference
        if result['readme_md']:
            result['api_reference'] = self.check_api_reference(readme_path)
        
        # Check src/ directory
        has_src, src_count = self.check_directory_structure(module_path, 'src')
        result['src_dir'] = has_src
        result['src_files'] = src_count
        
        # Check examples/ directory
        has_examples, examples_count = self.check_directory_structure(module_path, 'examples')
        result['examples_dir'] = has_examples
        result['examples_files'] = examples_count
        
        # Check tests/ directory
        has_tests, tests_count = self.check_directory_structure(module_path, 'tests')
        result['tests_dir'] = has_tests
        result['test_files'] = tests_count
        
        # Check for integration examples in README
        if result['readme_md']:
            try:
                with open(readme_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                result['integration_examples'] = 'integration' in content.lower() or 'cross-module' in content.lower()
            except Exception:
                pass
        
        return result
    
    def verify_all_modules(self) -> Dict:
        """Verify all modules."""
        modules = self.find_modules()
        self.modules = modules
        
        for module in modules:
            self.results[module] = self.verify_module(module)
        
        return dict(self.results)
    
    def generate_report(self) -> str:
        """Generate a comprehensive report."""
        if not self.results:
            self.verify_all_modules()
        
        report = []
        report.append("=" * 80)
        report.append("GEO-INFER Module Completeness Report")
        report.append("=" * 80)
        report.append("")
        
        # Summary statistics
        total_modules = len(self.results)
        stats = {
            'requirements_txt': sum(1 for r in self.results.values() if r['requirements_txt']),
            'setup_py': sum(1 for r in self.results.values() if r['setup_py']),
            'pyproject_toml': sum(1 for r in self.results.values() if r['pyproject_toml']),
            'readme_md': sum(1 for r in self.results.values() if r['readme_md']),
            'yaml_front_matter': sum(1 for r in self.results.values() if r['yaml_front_matter']),
            'api_reference': sum(1 for r in self.results.values() if r['api_reference']),
            'src_dir': sum(1 for r in self.results.values() if r['src_dir']),
            'examples_dir': sum(1 for r in self.results.values() if r['examples_dir']),
            'tests_dir': sum(1 for r in self.results.values() if r['tests_dir']),
        }
        
        report.append("Summary Statistics:")
        report.append(f"  Total Modules: {total_modules}")
        report.append(f"  requirements.txt: {stats['requirements_txt']}/{total_modules} ({stats['requirements_txt']*100//total_modules}%)")
        report.append(f"  setup.py: {stats['setup_py']}/{total_modules} ({stats['setup_py']*100//total_modules}%)")
        report.append(f"  pyproject.toml: {stats['pyproject_toml']}/{total_modules} ({stats['pyproject_toml']*100//total_modules}%)")
        report.append(f"  README.md: {stats['readme_md']}/{total_modules} ({stats['readme_md']*100//total_modules}%)")
        report.append(f"  YAML Front Matter: {stats['yaml_front_matter']}/{total_modules} ({stats['yaml_front_matter']*100//total_modules}%)")
        report.append(f"  API Reference: {stats['api_reference']}/{total_modules} ({stats['api_reference']*100//total_modules}%)")
        report.append(f"  src/ directory: {stats['src_dir']}/{total_modules} ({stats['src_dir']*100//total_modules}%)")
        report.append(f"  examples/ directory: {stats['examples_dir']}/{total_modules} ({stats['examples_dir']*100//total_modules}%)")
        report.append(f"  tests/ directory: {stats['tests_dir']}/{total_modules} ({stats['tests_dir']*100//total_modules}%)")
        report.append("")
        
        # Detailed module report
        report.append("Detailed Module Status:")
        report.append("-" * 80)
        
        for module, result in sorted(self.results.items()):
            report.append(f"\n{module}:")
            report.append(f"  requirements.txt: {'✓' if result['requirements_txt'] else '✗'}")
            report.append(f"  setup.py: {'✓' if result['setup_py'] else '✗'}")
            report.append(f"  pyproject.toml: {'✓' if result['pyproject_toml'] else '✗'}")
            report.append(f"  README.md: {'✓' if result['readme_md'] else '✗'}")
            report.append(f"  YAML Front Matter: {'✓' if result['yaml_front_matter'] else '✗'}")
            report.append(f"  API Reference: {'✓' if result['api_reference'] else '✗'}")
            report.append(f"  src/ directory: {'✓' if result['src_dir'] else '✗'} ({result['src_files']} files)")
            report.append(f"  examples/ directory: {'✓' if result['examples_dir'] else '✗'} ({result['examples_files']} files)")
            report.append(f"  tests/ directory: {'✓' if result['tests_dir'] else '✗'} ({result['test_files']} files)")
        
        # Missing items
        report.append("\n" + "=" * 80)
        report.append("Missing Items:")
        report.append("=" * 80)
        
        missing_requirements = [m for m, r in self.results.items() if not r['requirements_txt']]
        if missing_requirements:
            report.append(f"\nMissing requirements.txt ({len(missing_requirements)}):")
            for m in missing_requirements:
                report.append(f"  - {m}")
        
        missing_setup = [m for m, r in self.results.items() if not r['setup_py'] and not r['pyproject_toml']]
        if missing_setup:
            report.append(f"\nMissing setup.py/pyproject.toml ({len(missing_setup)}):")
            for m in missing_setup:
                report.append(f"  - {m}")
        
        missing_api_ref = [m for m, r in self.results.items() if r['readme_md'] and not r['api_reference']]
        if missing_api_ref:
            report.append(f"\nMissing API Reference in README ({len(missing_api_ref)}):")
            for m in missing_api_ref:
                report.append(f"  - {m}")
        
        missing_tests = [m for m, r in self.results.items() if not r['tests_dir'] or r['test_files'] == 0]
        if missing_tests:
            report.append(f"\nMissing or empty tests/ directory ({len(missing_tests)}):")
            for m in missing_tests:
                report.append(f"  - {m}")
        
        missing_examples = [m for m, r in self.results.items() if not r['examples_dir'] or r['examples_files'] == 0]
        if missing_examples:
            report.append(f"\nMissing or empty examples/ directory ({len(missing_examples)}):")
            for m in missing_examples:
                report.append(f"  - {m}")
        
        return "\n".join(report)


def main():
    """Main entry point."""
    checker = ModuleCompletenessChecker()
    checker.verify_all_modules()
    report = checker.generate_report()
    print(report)
    
    # Save report to file
    report_path = Path("module_completeness_report.txt")
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)
    print(f"\nReport saved to: {report_path}")


if __name__ == "__main__":
    main()


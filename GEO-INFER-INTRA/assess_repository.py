#!/usr/bin/env python3
"""
Comprehensive GEO-INFER Repository Assessment Tool

This script performs a systematic assessment of all GEO-INFER modules across
six critical dimensions:
1. Documentation completeness
2. Structural coherence
3. Testing infrastructure
4. Integration patterns
5. Modularity
6. Harmonization
"""

import os
import sys
import json
import yaml
from pathlib import Path
from typing import Dict, List, Set, Optional, Tuple
from datetime import datetime
from collections import defaultdict

# Project root
PROJECT_ROOT = Path(__file__).parent.parent
MODULE_PREFIX = "GEO-INFER-"

# Required YAML front matter fields
REQUIRED_YAML_FIELDS = [
    "title",
    "description",
    "purpose",
    "module_type",
    "status",
    "last_updated",
]

# Standard directory structure
STANDARD_DIRS = {
    "src": "Source code",
    "tests": "Test suite",
    "docs": "Documentation",
    "examples": "Examples",
    "config": "Configuration",
}

# Required sections in README
REQUIRED_SECTIONS = [
    "Overview",
    "Core Features",
    "API Reference",
    "Integration",
]


class RepositoryAssessment:
    """Comprehensive repository assessment tool."""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.modules: Dict[str, Path] = {}
        self.assessment_results: Dict[str, Dict] = {}
        self.find_all_modules()
    
    def find_all_modules(self):
        """Discover all GEO-INFER modules."""
        for item in self.project_root.iterdir():
            if item.is_dir() and item.name.startswith(MODULE_PREFIX):
                module_name = item.name[len(MODULE_PREFIX):]
                self.modules[module_name] = item
    
    def assess_yaml_front_matter(self, readme_path: Path) -> Dict:
        """Check YAML front matter in README."""
        if not readme_path.exists():
            return {"exists": False, "has_yaml": False, "fields": {}}
        
        content = readme_path.read_text()
        has_yaml = content.startswith("---\n")
        
        fields = {}
        if has_yaml:
            try:
                # Extract YAML front matter
                parts = content.split("---\n", 2)
                if len(parts) >= 3:
                    yaml_content = parts[1]
                    fields = yaml.safe_load(yaml_content) or {}
            except Exception as e:
                return {"exists": True, "has_yaml": True, "error": str(e), "fields": {}}
        
        # Check required fields
        missing_fields = [f for f in REQUIRED_YAML_FIELDS if f not in fields]
        
        return {
            "exists": True,
            "has_yaml": has_yaml,
            "fields": fields,
            "missing_fields": missing_fields,
            "compliance": len(missing_fields) == 0
        }
    
    def assess_required_sections(self, readme_path: Path) -> Dict:
        """Check for required sections in README."""
        if not readme_path.exists():
            return {"exists": False, "sections_found": []}
        
        content = readme_path.read_text().lower()
        sections_found = []
        for section in REQUIRED_SECTIONS:
            # Check for section headers (various formats)
            patterns = [
                f"## {section}",
                f"### {section}",
                f"# {section}",
                f"**{section}**",
            ]
            if any(pattern.lower() in content for pattern in patterns):
                sections_found.append(section)
        
        missing_sections = [s for s in REQUIRED_SECTIONS if s not in sections_found]
        
        return {
            "exists": True,
            "sections_found": sections_found,
            "missing_sections": missing_sections,
            "compliance": len(missing_sections) == 0
        }
    
    def assess_structure(self, module_path: Path) -> Dict:
        """Assess module directory structure."""
        structure = {}
        
        # Check standard directories
        for dir_name, description in STANDARD_DIRS.items():
            dir_path = module_path / dir_name
            structure[dir_name] = {
                "exists": dir_path.exists() and dir_path.is_dir(),
                "description": description
            }
        
        # Check for setup files
        setup_py = module_path / "setup.py"
        pyproject_toml = module_path / "pyproject.toml"
        
        structure["setup_files"] = {
            "setup.py": setup_py.exists(),
            "pyproject.toml": pyproject_toml.exists(),
            "has_setup": setup_py.exists() or pyproject_toml.exists()
        }
        
        # Check requirements.txt
        requirements_txt = module_path / "requirements.txt"
        structure["requirements"] = {
            "exists": requirements_txt.exists(),
            "path": str(requirements_txt) if requirements_txt.exists() else None
        }
        
        # Check src structure
        src_path = module_path / "src"
        if src_path.exists():
            structure["src_structure"] = {
                "exists": True,
                "has_package": len(list(src_path.glob("*/__init__.py"))) > 0
            }
        else:
            structure["src_structure"] = {"exists": False}
        
        return structure
    
    def assess_tests(self, module_path: Path) -> Dict:
        """Assess test infrastructure."""
        tests_path = module_path / "tests"
        
        if not tests_path.exists():
            return {"exists": False, "has_tests": False}
        
        # Find test files
        test_files = list(tests_path.rglob("test_*.py"))
        test_dirs = {
            "unit": (tests_path / "unit").exists(),
            "integration": (tests_path / "integration").exists(),
            "performance": (tests_path / "performance").exists(),
        }
        
        # Check pytest.ini
        pytest_ini = module_path / "pytest.ini"
        pytest_ini_tests = tests_path / "pytest.ini"
        
        return {
            "exists": True,
            "has_tests": len(test_files) > 0,
            "test_file_count": len(test_files),
            "test_directories": test_dirs,
            "pytest_ini": pytest_ini.exists() or pytest_ini_tests.exists(),
            "test_files": [str(f.relative_to(module_path)) for f in test_files[:10]]  # Limit to 10
        }
    
    def assess_module(self, module_name: str, module_path: Path) -> Dict:
        """Comprehensive assessment of a single module."""
        readme_path = module_path / "README.md"
        
        assessment = {
            "module_name": module_name,
            "module_path": str(module_path.relative_to(self.project_root)),
            "documentation": {
                "readme": self.assess_yaml_front_matter(readme_path),
                "sections": self.assess_required_sections(readme_path),
            },
            "structure": self.assess_structure(module_path),
            "tests": self.assess_tests(module_path),
        }
        
        # Calculate compliance scores
        doc_compliance = (
            assessment["documentation"]["readme"]["compliance"] and
            assessment["documentation"]["sections"]["compliance"]
        )
        
        structure_compliance = (
            assessment["structure"]["setup_files"]["has_setup"] and
            assessment["structure"]["requirements"]["exists"]
        )
        
        assessment["compliance_scores"] = {
            "documentation": doc_compliance,
            "structure": structure_compliance,
            "tests": assessment["tests"]["has_tests"],
        }
        
        return assessment
    
    def assess_all_modules(self) -> Dict:
        """Assess all modules and generate comprehensive report."""
        print(f"🔍 Assessing {len(self.modules)} modules...")
        
        for module_name, module_path in sorted(self.modules.items()):
            print(f"  ✓ {module_name}")
            self.assessment_results[module_name] = self.assess_module(module_name, module_path)
        
        return self.generate_report()
    
    def generate_report(self) -> Dict:
        """Generate comprehensive assessment report."""
        total_modules = len(self.assessment_results)
        
        # Calculate statistics
        stats = {
            "total_modules": total_modules,
            "documentation": {
                "yaml_front_matter": sum(1 for m in self.assessment_results.values() 
                                        if m["documentation"]["readme"]["compliance"]),
                "required_sections": sum(1 for m in self.assessment_results.values()
                                       if m["documentation"]["sections"]["compliance"]),
                "fully_compliant": sum(1 for m in self.assessment_results.values()
                                     if m["compliance_scores"]["documentation"]),
            },
            "structure": {
                "has_setup": sum(1 for m in self.assessment_results.values()
                               if m["structure"]["setup_files"]["has_setup"]),
                "has_requirements": sum(1 for m in self.assessment_results.values()
                                      if m["structure"]["requirements"]["exists"]),
                "fully_compliant": sum(1 for m in self.assessment_results.values()
                                     if m["compliance_scores"]["structure"]),
            },
            "tests": {
                "has_tests": sum(1 for m in self.assessment_results.values()
                              if m["tests"]["has_tests"]),
                "test_file_count": sum(m["tests"]["test_file_count"] 
                                     for m in self.assessment_results.values()
                                     if m["tests"]["exists"]),
            },
        }
        
        # Find modules needing attention
        issues = {
            "missing_yaml_front_matter": [
                name for name, result in self.assessment_results.items()
                if not result["documentation"]["readme"]["compliance"]
            ],
            "missing_setup": [
                name for name, result in self.assessment_results.items()
                if not result["structure"]["setup_files"]["has_setup"]
            ],
            "missing_requirements": [
                name for name, result in self.assessment_results.items()
                if not result["structure"]["requirements"]["exists"]
            ],
            "missing_tests": [
                name for name, result in self.assessment_results.items()
                if not result["tests"]["has_tests"]
            ],
        }
        
        return {
            "assessment_date": datetime.now().isoformat(),
            "statistics": stats,
            "issues": issues,
            "module_details": self.assessment_results,
        }
    
    def save_report(self, report: Dict, output_path: Path):
        """Save assessment report to file."""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Save JSON
        json_path = output_path.with_suffix(".json")
        with open(json_path, "w") as f:
            json.dump(report, f, indent=2)
        
        # Save Markdown report
        md_path = output_path.with_suffix(".md")
        self.generate_markdown_report(report, md_path)
        
        print(f"\n📊 Report saved:")
        print(f"  - JSON: {json_path}")
        print(f"  - Markdown: {md_path}")
    
    def generate_markdown_report(self, report: Dict, output_path: Path):
        """Generate human-readable Markdown report."""
        lines = [
            "# GEO-INFER Repository Assessment Report",
            "",
            f"**Assessment Date**: {report['assessment_date']}",
            "",
            "## Executive Summary",
            "",
            f"**Total Modules Assessed**: {report['statistics']['total_modules']}",
            "",
            "### Documentation Compliance",
            f"- Modules with YAML front matter: {report['statistics']['documentation']['yaml_front_matter']}/{report['statistics']['total_modules']}",
            f"- Modules with required sections: {report['statistics']['documentation']['required_sections']}/{report['statistics']['total_modules']}",
            f"- Fully documentation compliant: {report['statistics']['documentation']['fully_compliant']}/{report['statistics']['total_modules']}",
            "",
            "### Structure Compliance",
            f"- Modules with setup.py/pyproject.toml: {report['statistics']['structure']['has_setup']}/{report['statistics']['total_modules']}",
            f"- Modules with requirements.txt: {report['statistics']['structure']['has_requirements']}/{report['statistics']['total_modules']}",
            f"- Fully structure compliant: {report['statistics']['structure']['fully_compliant']}/{report['statistics']['total_modules']}",
            "",
            "### Testing",
            f"- Modules with tests: {report['statistics']['tests']['has_tests']}/{report['statistics']['total_modules']}",
            f"- Total test files: {report['statistics']['tests']['test_file_count']}",
            "",
            "## Issues Requiring Attention",
            "",
        ]
        
        # Add issues
        for issue_type, modules in report['issues'].items():
            if modules:
                issue_name = issue_type.replace("_", " ").title()
                lines.append(f"### {issue_name}")
                for module in modules:
                    lines.append(f"- {module}")
                lines.append("")
        
        # Add per-module details
        lines.extend([
            "## Module Details",
            "",
            "| Module | YAML | Sections | Setup | Requirements | Tests |",
            "|---------|------|----------|-------|--------------|-------|",
        ])
        
        for module_name, details in sorted(report['module_details'].items()):
            doc = details['documentation']
            struct = details['structure']
            tests = details['tests']
            
            yaml_status = "✅" if doc['readme']['compliance'] else "❌"
            sections_status = "✅" if doc['sections']['compliance'] else "❌"
            setup_status = "✅" if struct['setup_files']['has_setup'] else "❌"
            req_status = "✅" if struct['requirements']['exists'] else "❌"
            test_status = "✅" if tests['has_tests'] else "❌"
            
            lines.append(
                f"| {module_name} | {yaml_status} | {sections_status} | "
                f"{setup_status} | {req_status} | {test_status} |"
            )
        
        output_path.write_text("\n".join(lines))


def main():
    """Main assessment execution."""
    print("=" * 70)
    print("GEO-INFER Repository Comprehensive Assessment")
    print("=" * 70)
    
    assessor = RepositoryAssessment(PROJECT_ROOT)
    report = assessor.assess_all_modules()
    
    # Save report
    output_path = PROJECT_ROOT / "GEO-INFER-INTRA" / "assessment_results" / "comprehensive_assessment"
    assessor.save_report(report, output_path)
    
    # Print summary
    print("\n" + "=" * 70)
    print("ASSESSMENT SUMMARY")
    print("=" * 70)
    print(f"\nTotal Modules: {report['statistics']['total_modules']}")
    print(f"\nDocumentation Compliance: {report['statistics']['documentation']['fully_compliant']}/{report['statistics']['total_modules']}")
    print(f"Structure Compliance: {report['statistics']['structure']['fully_compliant']}/{report['statistics']['total_modules']}")
    print(f"Modules with Tests: {report['statistics']['tests']['has_tests']}/{report['statistics']['total_modules']}")
    
    print("\n" + "=" * 70)
    print("Issues Found:")
    print("=" * 70)
    for issue_type, modules in report['issues'].items():
        if modules:
            print(f"\n{issue_type.replace('_', ' ').title()}: {len(modules)} modules")
            for module in modules[:5]:  # Show first 5
                print(f"  - {module}")
            if len(modules) > 5:
                print(f"  ... and {len(modules) - 5} more")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())


#!/usr/bin/env python3
"""
Comprehensive GEO-INFER Repository Review Script

This script performs a comprehensive review of all GEO-INFER modules across
multiple dimensions: structure, dependencies, code quality, testing, documentation, and security.
"""

import os
import json
import re
from pathlib import Path
from typing import Dict, List, Set, Optional, Any
from collections import defaultdict
import ast
import yaml

# Module categories from README
MODULE_CATEGORIES = {
    "Core Analytical": ["MATH", "ACT", "BAYES", "AI", "COG", "AGENT", "SPM"],
    "Spatial-Temporal": ["SPACE", "TIME", "IOT"],
    "Infrastructure": ["DATA", "API", "SEC", "OPS", "METAGOV"],
    "Domain Applications": ["AG", "HEALTH", "ECON", "RISK", "LOG", "BIO", "CLIMATE", "ENERGY", "WATER", "FOREST", "MARINE"],
    "Community": ["CIV", "APP", "ART", "PLACE", "PEP", "ORG", "COMMS", "NORMS", "REQ"],
    "Operations": ["INTRA", "GIT", "TEST", "EXAMPLES", "SIM", "ANT"]
}

# Module status from README
MODULE_STATUS = {
    "Beta": ["MATH", "ACT", "BAYES", "AGENT", "AG", "HEALTH", "LOG", "BIO", "API", "APP", "ART", "PLACE", "IOT", "SPACE"],
    "Alpha": ["AI", "COG", "SPM", "TIME", "DATA", "SEC", "OPS", "ECON", "RISK", "CIV", "SIM", "ANT"],
    "Planning": ["METAGOV", "CLIMATE", "ENERGY", "WATER", "FOREST", "MARINE"]
}

class ModuleReviewer:
    """Comprehensive module reviewer."""
    
    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.findings: Dict[str, Any] = defaultdict(dict)
        self.modules: List[str] = []
        
    def discover_modules(self) -> List[str]:
        """Discover all GEO-INFER modules."""
        modules = []
        for item in self.repo_root.iterdir():
            if item.is_dir() and item.name.startswith("GEO-INFER-"):
                module_name = item.name.replace("GEO-INFER-", "")
                modules.append(module_name)
        return sorted(modules)
    
    def analyze_structure(self, module_name: str) -> Dict[str, Any]:
        """Analyze module directory structure."""
        module_path = self.repo_root / f"GEO-INFER-{module_name}"
        if not module_path.exists():
            return {"error": "Module directory not found"}
        
        structure = {
            "has_src": (module_path / "src").exists(),
            "has_tests": (module_path / "tests").exists(),
            "has_docs": (module_path / "docs").exists(),
            "has_examples": (module_path / "examples").exists(),
            "has_config": (module_path / "config").exists(),
            "has_readme": (module_path / "README.md").exists(),
            "has_setup_py": (module_path / "setup.py").exists(),
            "has_pyproject_toml": (module_path / "pyproject.toml").exists(),
            "has_requirements_txt": (module_path / "requirements.txt").exists(),
        }
        
        # Check src structure
        if structure["has_src"]:
            src_path = module_path / "src"
            structure["src_structure"] = {}
            for item in src_path.iterdir():
                if item.is_dir():
                    structure["src_structure"][item.name] = True
        
        # Count files
        structure["test_file_count"] = len(list((module_path / "tests").glob("**/*.py"))) if structure["has_tests"] else 0
        structure["src_file_count"] = len(list((module_path / "src").glob("**/*.py"))) if structure["has_src"] else 0
        
        return structure
    
    def analyze_dependencies(self, module_name: str) -> Dict[str, Any]:
        """Analyze module dependencies."""
        module_path = self.repo_root / f"GEO-INFER-{module_name}"
        deps = {
            "requirements_txt": [],
            "setup_py": [],
            "pyproject_toml": [],
            "actual_imports": set(),
            "missing_deps": [],
            "inconsistencies": []
        }
        
        # Read requirements.txt
        req_file = module_path / "requirements.txt"
        if req_file.exists():
            with open(req_file) as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        # Extract package name
                        pkg = re.split(r'[>=<!=]', line)[0].strip()
                        deps["requirements_txt"].append(pkg)
        
        # Read setup.py dependencies
        setup_file = module_path / "setup.py"
        if setup_file.exists():
            try:
                with open(setup_file) as f:
                    content = f.read()
                    # Simple regex extraction (not perfect but works for most cases)
                    install_requires = re.findall(r"install_requires\s*=\s*\[(.*?)\]", content, re.DOTALL)
                    if install_requires:
                        for req in re.findall(r"['\"]([^'\"]+)['\"]", install_requires[0]):
                            pkg = re.split(r'[>=<!=]', req)[0].strip()
                            deps["setup_py"].append(pkg)
            except Exception as e:
                deps["setup_py_error"] = str(e)
        
        # Read pyproject.toml
        pyproject_file = module_path / "pyproject.toml"
        if pyproject_file.exists():
            try:
                with open(pyproject_file) as f:
                    content = f.read()
                    # Extract dependencies from pyproject.toml
                    deps_section = re.findall(r"dependencies\s*=\s*\[(.*?)\]", content, re.DOTALL)
                    if deps_section:
                        for req in re.findall(r"['\"]([^'\"]+)['\"]", deps_section[0]):
                            pkg = re.split(r'[>=<!=]', req)[0].strip()
                            deps["pyproject_toml"].append(pkg)
            except Exception as e:
                deps["pyproject_toml_error"] = str(e)
        
        # Extract actual imports from source code
        src_path = module_path / "src"
        if src_path.exists():
            for py_file in src_path.rglob("*.py"):
                try:
                    with open(py_file) as f:
                        tree = ast.parse(f.read(), filename=str(py_file))
                        for node in ast.walk(tree):
                            if isinstance(node, ast.Import):
                                for alias in node.names:
                                    deps["actual_imports"].add(alias.name.split('.')[0])
                            elif isinstance(node, ast.ImportFrom):
                                if node.module:
                                    deps["actual_imports"].add(node.module.split('.')[0])
                except Exception:
                    pass
        
        deps["actual_imports"] = sorted(list(deps["actual_imports"]))
        
        # Find missing dependencies (imports not in requirements)
        declared_deps = set(deps["requirements_txt"] + deps["setup_py"] + deps["pyproject_toml"])
        # Filter out internal geo_infer modules
        external_imports = {imp for imp in deps["actual_imports"] 
                           if not imp.startswith("geo_infer") and imp not in ["__future__", "typing", "collections", "dataclasses", "abc", "enum"]}
        deps["missing_deps"] = sorted(list(external_imports - declared_deps))
        
        return deps
    
    def analyze_documentation(self, module_name: str) -> Dict[str, Any]:
        """Analyze module documentation."""
        module_path = self.repo_root / f"GEO-INFER-{module_name}"
        docs = {
            "has_readme": False,
            "has_yaml_frontmatter": False,
            "required_sections": {},
            "api_docs": False,
            "examples_count": 0
        }
        
        readme_file = module_path / "README.md"
        if readme_file.exists():
            docs["has_readme"] = True
            with open(readme_file) as f:
                content = f.read()
                
                # Check for YAML front matter
                if content.startswith("---"):
                    docs["has_yaml_frontmatter"] = True
                
                # Check for required sections
                required = ["Overview", "Core Features", "API Reference", "Integration"]
                for section in required:
                    # Look for section headers
                    pattern = rf"#+\s*{section}|##+\s*{section}"
                    docs["required_sections"][section] = bool(re.search(pattern, content, re.IGNORECASE))
        
        # Count examples
        examples_path = module_path / "examples"
        if examples_path.exists():
            docs["examples_count"] = len(list(examples_path.glob("*.py")))
        
        return docs
    
    def analyze_testing(self, module_name: str) -> Dict[str, Any]:
        """Analyze module testing."""
        module_path = self.repo_root / f"GEO-INFER-{module_name}"
        testing = {
            "has_tests": False,
            "test_file_count": 0,
            "has_unit_tests": False,
            "has_integration_tests": False,
            "has_performance_tests": False
        }
        
        tests_path = module_path / "tests"
        if tests_path.exists():
            testing["has_tests"] = True
            testing["test_file_count"] = len(list(tests_path.rglob("*.py")))
            
            # Check for test organization
            if (tests_path / "unit").exists():
                testing["has_unit_tests"] = True
            if (tests_path / "integration").exists():
                testing["has_integration_tests"] = True
            if (tests_path / "performance").exists():
                testing["has_performance_tests"] = True
        
        return testing
    
    def analyze_code_quality(self, module_name: str) -> Dict[str, Any]:
        """Analyze code quality indicators."""
        module_path = self.repo_root / f"GEO-INFER-{module_name}"
        quality = {
            "todo_count": 0,
            "fixme_count": 0,
            "has_type_hints": False,
            "has_docstrings": False,
            "file_count": 0
        }
        
        src_path = module_path / "src"
        if src_path.exists():
            for py_file in src_path.rglob("*.py"):
                quality["file_count"] += 1
                try:
                    with open(py_file) as f:
                        content = f.read()
                        quality["todo_count"] += len(re.findall(r"TODO|todo", content))
                        quality["fixme_count"] += len(re.findall(r"FIXME|fixme", content))
                        
                        # Check for type hints
                        if "->" in content or ":" in content:
                            quality["has_type_hints"] = True
                        
                        # Check for docstrings
                        if '"""' in content or "'''" in content:
                            quality["has_docstrings"] = True
                except Exception:
                    pass
        
        return quality
    
    def review_module(self, module_name: str) -> Dict[str, Any]:
        """Perform comprehensive review of a single module."""
        print(f"Reviewing module: {module_name}")
        
        review = {
            "module": module_name,
            "structure": self.analyze_structure(module_name),
            "dependencies": self.analyze_dependencies(module_name),
            "documentation": self.analyze_documentation(module_name),
            "testing": self.analyze_testing(module_name),
            "code_quality": self.analyze_code_quality(module_name)
        }
        
        return review
    
    def review_all(self) -> Dict[str, Any]:
        """Review all modules."""
        self.modules = self.discover_modules()
        print(f"Found {len(self.modules)} modules")
        
        all_reviews = {}
        for module in self.modules:
            try:
                all_reviews[module] = self.review_module(module)
            except Exception as e:
                print(f"Error reviewing {module}: {e}")
                all_reviews[module] = {"error": str(e)}
        
        return {
            "modules": self.modules,
            "module_count": len(self.modules),
            "reviews": all_reviews
        }
    
    def generate_summary(self, reviews: Dict[str, Any]) -> Dict[str, Any]:
        """Generate summary statistics."""
        summary = {
            "total_modules": len(reviews.get("reviews", {})),
            "structure": {
                "has_requirements_txt": 0,
                "has_setup_py": 0,
                "has_pyproject_toml": 0,
                "has_tests": 0,
                "has_docs": 0,
                "has_examples": 0
            },
            "documentation": {
                "has_yaml_frontmatter": 0,
                "has_all_sections": 0
            },
            "testing": {
                "modules_with_tests": 0,
                "total_test_files": 0
            },
            "dependencies": {
                "modules_missing_deps": 0,
                "total_missing_deps": 0
            }
        }
        
        for module, review in reviews.get("reviews", {}).items():
            if "error" in review:
                continue
                
            struct = review.get("structure", {})
            if struct.get("has_requirements_txt"):
                summary["structure"]["has_requirements_txt"] += 1
            if struct.get("has_setup_py"):
                summary["structure"]["has_setup_py"] += 1
            if struct.get("has_pyproject_toml"):
                summary["structure"]["has_pyproject_toml"] += 1
            if struct.get("has_tests"):
                summary["structure"]["has_tests"] += 1
                summary["testing"]["modules_with_tests"] += 1
            if struct.get("has_docs"):
                summary["structure"]["has_docs"] += 1
            if struct.get("has_examples"):
                summary["structure"]["has_examples"] += 1
            
            docs = review.get("documentation", {})
            if docs.get("has_yaml_frontmatter"):
                summary["documentation"]["has_yaml_frontmatter"] += 1
            if all(docs.get("required_sections", {}).values()):
                summary["documentation"]["has_all_sections"] += 1
            
            testing = review.get("testing", {})
            summary["testing"]["total_test_files"] += testing.get("test_file_count", 0)
            
            deps = review.get("dependencies", {})
            if deps.get("missing_deps"):
                summary["dependencies"]["modules_missing_deps"] += 1
                summary["dependencies"]["total_missing_deps"] += len(deps["missing_deps"])
        
        return summary


def main():
    """Main execution."""
    repo_root = Path(__file__).parent.parent
    reviewer = ModuleReviewer(repo_root)
    
    print("Starting comprehensive repository review...")
    reviews = reviewer.review_all()
    summary = reviewer.generate_summary(reviews)
    
    # Save results
    output_dir = repo_root / "GEO-INFER-INTRA" / "assessment_results"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Save full review
    with open(output_dir / "comprehensive_review_2025.json", "w") as f:
        json.dump(reviews, f, indent=2)
    
    # Save summary
    with open(output_dir / "comprehensive_review_summary_2025.json", "w") as f:
        json.dump(summary, f, indent=2)
    
    print(f"\nReview complete!")
    print(f"Total modules reviewed: {summary['total_modules']}")
    print(f"Modules with requirements.txt: {summary['structure']['has_requirements_txt']}")
    print(f"Modules with tests: {summary['testing']['modules_with_tests']}")
    print(f"Modules with YAML frontmatter: {summary['documentation']['has_yaml_frontmatter']}")


if __name__ == "__main__":
    main()


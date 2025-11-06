#!/usr/bin/env python3
"""
GEO-INFER UV Migration Script

This script migrates all GEO-INFER modules to use pyproject.toml for uv-based
package management. It extracts dependencies from setup.py, requirements.txt,
and README.md files and generates standardized pyproject.toml files.
"""

import os
import sys
import re
import ast
import yaml
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple
from collections import defaultdict

# Project root
PROJECT_ROOT = Path(__file__).parent.parent.parent
MODULE_PREFIX = "GEO-INFER-"
TEMPLATE_PATH = PROJECT_ROOT / "GEO-INFER-INTRA" / "templates" / "pyproject.toml.template"


class SetupPyParser:
    """Parse setup.py files to extract metadata and dependencies."""
    
    @staticmethod
    def parse_setup_py(setup_path: Path) -> Dict:
        """Extract metadata from setup.py file."""
        result = {
            "name": None,
            "version": None,
            "description": None,
            "author": None,
            "author_email": None,
            "url": None,
            "install_requires": [],
            "extras_require": {},
            "entry_points": {},
            "python_requires": ">=3.9",
            "classifiers": [],
            "keywords": [],
        }
        
        if not setup_path.exists():
            return result
        
        content = setup_path.read_text()
        
        # Parse using AST
        try:
            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "setup":
                    for keyword in node.keywords:
                        key = keyword.arg
                        if key == "name":
                            result["name"] = ast.literal_eval(keyword.value)
                        elif key == "version":
                            result["version"] = ast.literal_eval(keyword.value)
                        elif key == "description":
                            result["description"] = ast.literal_eval(keyword.value)
                        elif key == "author":
                            result["author"] = ast.literal_eval(keyword.value)
                        elif key == "author_email":
                            result["author_email"] = ast.literal_eval(keyword.value)
                        elif key == "url":
                            result["url"] = ast.literal_eval(keyword.value)
                        elif key == "install_requires":
                            result["install_requires"] = ast.literal_eval(keyword.value)
                        elif key == "extras_require":
                            result["extras_require"] = ast.literal_eval(keyword.value)
                        elif key == "entry_points":
                            result["entry_points"] = ast.literal_eval(keyword.value)
                        elif key == "python_requires":
                            result["python_requires"] = ast.literal_eval(keyword.value)
                        elif key == "classifiers":
                            result["classifiers"] = ast.literal_eval(keyword.value)
                        elif key == "keywords":
                            result["keywords"] = ast.literal_eval(keyword.value)
        except Exception as e:
            print(f"Warning: Could not fully parse {setup_path}: {e}")
            # Fallback to regex parsing
            result.update(SetupPyParser._regex_parse(content))
        
        return result
    
    @staticmethod
    def _regex_parse(content: str) -> Dict:
        """Fallback regex parsing for setup.py."""
        result = {}
        
        # Extract install_requires
        install_match = re.search(r'install_requires\s*=\s*\[(.*?)\]', content, re.DOTALL)
        if install_match:
            deps = re.findall(r'["\']([^"\']+)["\']', install_match.group(1))
            result["install_requires"] = deps
        
        # Extract name
        name_match = re.search(r'name\s*=\s*["\']([^"\']+)["\']', content)
        if name_match:
            result["name"] = name_match.group(1)
        
        # Extract version
        version_match = re.search(r'version\s*=\s*["\']([^"\']+)["\']', content)
        if version_match:
            result["version"] = version_match.group(1)
        
        # Extract description
        desc_match = re.search(r'description\s*=\s*["\']([^"\']+)["\']', content)
        if desc_match:
            result["description"] = desc_match.group(1)
        
        return result


class RequirementsParser:
    """Parse requirements.txt files."""
    
    @staticmethod
    def parse_requirements(requirements_path: Path) -> List[str]:
        """Parse requirements.txt file."""
        if not requirements_path.exists():
            return []
        
        dependencies = []
        for line in requirements_path.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#"):
                # Remove comments
                if "#" in line:
                    line = line.split("#")[0].strip()
                dependencies.append(line)
        
        return dependencies


class ReadmeParser:
    """Parse README.md files to extract metadata."""
    
    @staticmethod
    def parse_readme(readme_path: Path) -> Dict:
        """Extract YAML front matter from README.md."""
        if not readme_path.exists():
            return {}
        
        content = readme_path.read_text()
        if not content.startswith("---\n"):
            return {}
        
        try:
            parts = content.split("---\n", 2)
            if len(parts) >= 3:
                yaml_content = parts[1]
                return yaml.safe_load(yaml_content) or {}
        except Exception as e:
            print(f"Warning: Could not parse README YAML front matter: {e}")
        
        return {}


class PyProjectGenerator:
    """Generate pyproject.toml files from templates and metadata."""
    
    def __init__(self, template_path: Path):
        self.template_path = template_path
        self.template = template_path.read_text() if template_path.exists() else self._default_template()
    
    def _default_template(self) -> str:
        """Default template if file doesn't exist."""
        return TEMPLATE_PATH.read_text() if TEMPLATE_PATH.exists() else ""
    
    def generate(
        self,
        module_name: str,
        metadata: Dict,
        dependencies: List[str],
        optional_deps: Dict[str, List[str]] = None,
        entry_points: Dict = None,
    ) -> str:
        """Generate pyproject.toml content."""
        module_name_lower = module_name.lower()
        
        # Prepare dependencies list
        deps_text = ",\n    ".join([f'"{dep}"' for dep in dependencies]) if dependencies else ""
        
        # Prepare optional dependencies
        optional_deps_text = ""
        if optional_deps:
            for extra_name, extra_deps in optional_deps.items():
                if extra_name not in ["dev", "docs"]:  # Already in template
                    deps_list = ",\n    ".join([f'"{dep}"' for dep in extra_deps])
                    optional_deps_text += f'{extra_name} = [\n    {deps_list}\n]\n'
        
        # Prepare entry points for [project.scripts] section
        entry_points_text = ""
        if entry_points:
            # Handle case where entry_points is already a dict with console_scripts
            if isinstance(entry_points, dict) and "console_scripts" in entry_points:
                console_scripts = entry_points["console_scripts"]
                # Handle both dict and list formats
                if isinstance(console_scripts, dict):
                    for script_name, script_path in console_scripts.items():
                        entry_points_text += f'{script_name} = "{script_path}"\n'
                elif isinstance(console_scripts, list):
                    # Parse list format: ['name=path:func', ...]
                    for script in console_scripts:
                        if "=" in script:
                            parts = script.split("=", 1)
                            entry_points_text += f'{parts[0].strip()} = "{parts[1].strip()}"\n'
            # Handle case where entry_points is a list directly
            elif isinstance(entry_points, list):
                for script in entry_points:
                    if "=" in script:
                        parts = script.split("=", 1)
                        entry_points_text += f'{parts[0].strip()} = "{parts[1].strip()}"\n'
        
        # If no entry points, ensure we have an empty line to avoid syntax errors
        if not entry_points_text:
            entry_points_text = "\n"
        
        # Extract description
        description = metadata.get("description") or metadata.get("purpose") or f"GEO-INFER {module_name} module"
        
        # Extract keywords
        keywords = metadata.get("tags", [])
        keywords_str = ", ".join(keywords) if keywords else "spatial analysis"
        
        # Replace template placeholders
        content = self.template
        content = content.replace("{MODULE_NAME}", module_name.lower())
        content = content.replace("{MODULE_NAME_LOWER}", module_name.lower())
        content = content.replace("{DESCRIPTION}", description)
        content = content.replace("{KEYWORDS}", keywords_str)
        content = content.replace("{DEPENDENCIES}", deps_text)
        content = content.replace("{OPTIONAL_DEPS}", optional_deps_text)
        content = content.replace("{ENTRY_POINTS}", entry_points_text)
        
        return content


class UVMigrator:
    """Main migration orchestrator."""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.modules: Dict[str, Path] = {}
        self.find_modules()
        self.setup_parser = SetupPyParser()
        self.req_parser = RequirementsParser()
        self.readme_parser = ReadmeParser()
        self.generator = PyProjectGenerator(TEMPLATE_PATH)
    
    def find_modules(self):
        """Discover all GEO-INFER modules."""
        for item in self.project_root.iterdir():
            if item.is_dir() and item.name.startswith(MODULE_PREFIX):
                module_name = item.name[len(MODULE_PREFIX):]
                self.modules[module_name] = item
    
    def migrate_module(self, module_name: str, dry_run: bool = False) -> bool:
        """Migrate a single module to pyproject.toml."""
        module_path = self.modules[module_name]
        print(f"\n{'[DRY RUN] ' if dry_run else ''}Migrating {module_name}...")
        
        # Collect metadata from various sources
        setup_path = module_path / "setup.py"
        pyproject_path = module_path / "pyproject.toml"
        requirements_path = module_path / "requirements.txt"
        readme_path = module_path / "README.md"
        
        # Parse existing files
        setup_data = self.setup_parser.parse_setup_py(setup_path) if setup_path.exists() else {}
        requirements_data = self.req_parser.parse_requirements(requirements_path)
        readme_data = self.readme_parser.parse_readme(readme_path)
        
        # Check if pyproject.toml already exists and has dependencies
        existing_pyproject = {}
        if pyproject_path.exists():
            try:
                import tomli
                existing_pyproject = tomli.loads(pyproject_path.read_text())
            except:
                try:
                    import tomllib
                    existing_pyproject = tomllib.loads(pyproject_path.read_bytes())
                except:
                    pass
        
        # Merge dependencies (setup.py takes precedence, then requirements.txt, then existing pyproject.toml)
        all_dependencies = []
        
        # Check if setup.py references requirements.txt
        if setup_path.exists():
            setup_content = setup_path.read_text()
            if "requirements.txt" in setup_content or "requirements" in setup_content.lower():
                # If setup.py reads from requirements.txt, use that
                if requirements_data:
                    all_dependencies.extend(requirements_data)
                elif setup_data.get("install_requires"):
                    all_dependencies.extend(setup_data["install_requires"])
            elif setup_data.get("install_requires"):
                all_dependencies.extend(setup_data["install_requires"])
        
        # Fallback to requirements.txt if no setup.py dependencies
        if not all_dependencies and requirements_data:
            all_dependencies.extend(requirements_data)
        
        # Fallback to existing pyproject.toml dependencies
        if not all_dependencies and existing_pyproject:
            project_deps = existing_pyproject.get("project", {}).get("dependencies", [])
            if project_deps:
                all_dependencies.extend(project_deps)
        
        # Remove duplicates while preserving order and keeping highest version
        dep_dict = {}
        for dep in all_dependencies:
            # Normalize dependency name
            dep_clean = dep.strip().replace('"', '').replace("'", "")
            dep_name = re.split(r'[>=<!=,\s]', dep_clean)[0].strip()
            if dep_name:
                # Keep the most specific version constraint
                if dep_name not in dep_dict:
                    dep_dict[dep_name] = dep_clean
                else:
                    # If both have versions, prefer the more specific one
                    current = dep_dict[dep_name]
                    if "," in dep_clean or "<" in dep_clean:
                        # More specific constraint
                        dep_dict[dep_name] = dep_clean
                    elif "," not in current and "<" not in current:
                        # Current is simple, new might be more specific
                        dep_dict[dep_name] = dep_clean
        
        unique_deps = [dep_dict[name] for name in sorted(dep_dict.keys())]
        
        # Merge metadata (readme takes precedence for description)
        metadata = {
            "name": setup_data.get("name") or f"geo-infer-{module_name.lower()}",
            "version": setup_data.get("version") or "0.1.0",
            "description": readme_data.get("description") or setup_data.get("description") or f"GEO-INFER {module_name} module",
            "author": setup_data.get("author") or "GEO-INFER Development Team",
            "author_email": setup_data.get("author_email") or "geo-infer@activeinference.institute",
            "url": setup_data.get("url") or "https://github.com/geo-infer/geo-infer",
        }
        metadata.update(readme_data)
        
        # Get optional dependencies
        optional_deps = setup_data.get("extras_require", {})
        
        # Get entry points - handle both dict and list formats
        entry_points_raw = setup_data.get("entry_points", {})
        entry_points = {}
        if isinstance(entry_points_raw, dict):
            entry_points = entry_points_raw
        elif isinstance(entry_points_raw, list):
            # Convert list format to dict
            entry_points = {"console_scripts": entry_points_raw}
        
        # Generate pyproject.toml
        pyproject_content = self.generator.generate(
            module_name=module_name,
            metadata=metadata,
            dependencies=unique_deps,
            optional_deps=optional_deps,
            entry_points=entry_points,
        )
        
        if not dry_run:
            # Write pyproject.toml
            pyproject_path.write_text(pyproject_content)
            print(f"  ✅ Created {pyproject_path}")
        else:
            print(f"  📝 Would create {pyproject_path}")
            print(f"  📦 Dependencies: {len(unique_deps)}")
        
        return True
    
    def migrate_all(self, dry_run: bool = False):
        """Migrate all modules."""
        print(f"\n{'=' * 70}")
        print(f"{'DRY RUN: ' if dry_run else ''}Migrating {len(self.modules)} modules to pyproject.toml")
        print(f"{'=' * 70}")
        
        results = {}
        for module_name in sorted(self.modules.keys()):
            try:
                success = self.migrate_module(module_name, dry_run=dry_run)
                results[module_name] = success
            except Exception as e:
                print(f"  ❌ Error migrating {module_name}: {e}")
                results[module_name] = False
        
        print(f"\n{'=' * 70}")
        print(f"Migration {'simulation' if dry_run else 'completed'}")
        print(f"Success: {sum(results.values())}/{len(results)}")
        print(f"{'=' * 70}")
        
        return results


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Migrate GEO-INFER modules to pyproject.toml")
    parser.add_argument("--dry-run", action="store_true", help="Simulate migration without writing files")
    parser.add_argument("--module", help="Migrate specific module only")
    
    args = parser.parse_args()
    
    migrator = UVMigrator(PROJECT_ROOT)
    
    if args.module:
        if args.module not in migrator.modules:
            print(f"Error: Module {args.module} not found")
            return 1
        migrator.migrate_module(args.module, dry_run=args.dry_run)
    else:
        migrator.migrate_all(dry_run=args.dry_run)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())


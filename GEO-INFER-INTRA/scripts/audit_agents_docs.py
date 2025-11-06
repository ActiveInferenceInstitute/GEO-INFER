#!/usr/bin/env python3
"""
Comprehensive audit script for AGENTS.md files.
Verifies all import paths, class names, and code examples against actual implementations.
"""

import re
import ast
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional
from collections import defaultdict

PROJECT_ROOT = Path(__file__).parent.parent.parent

# AGENTS.md files to audit
AGENTS_FILES = [
    PROJECT_ROOT / "AGENTS.md",
    PROJECT_ROOT / "GEO-INFER-AGENT" / "AGENTS.md",
    PROJECT_ROOT / "GEO-INFER-ACT" / "AGENTS.md",
    PROJECT_ROOT / "GEO-INFER-ANT" / "AGENTS.md",
]


class ImportExtractor:
    """Extract import statements from code blocks."""
    
    @staticmethod
    def extract_imports(content: str) -> List[Tuple[str, str, int]]:
        """
        Extract import statements from markdown code blocks.
        Returns list of (module_path, class_name, line_number)
        """
        imports = []
        lines = content.split('\n')
        in_code_block = False
        code_block_lang = None
        
        for i, line in enumerate(lines, 1):
            # Check for code block start/end
            if line.strip().startswith('```'):
                if in_code_block:
                    in_code_block = False
                    code_block_lang = None
                else:
                    in_code_block = True
                    # Extract language if specified
                    lang_match = re.match(r'```(\w+)', line)
                    code_block_lang = lang_match.group(1) if lang_match else None
                continue
            
            if in_code_block and code_block_lang == 'python':
                # Extract import statements
                import_match = re.match(r'from\s+([^\s]+)\s+import\s+([^\s]+)', line)
                if import_match:
                    module_path = import_match.group(1)
                    class_name = import_match.group(2)
                    imports.append((module_path, class_name, i))
        
        return imports


class ModuleChecker:
    """Check if modules and classes exist in source code."""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.module_cache: Dict[str, bool] = {}
        self.class_cache: Dict[Tuple[str, str], bool] = {}
    
    def module_exists(self, module_path: str) -> bool:
        """Check if a module exists."""
        if module_path in self.module_cache:
            return self.module_cache[module_path]
        
        # Convert module path to file path
        parts = module_path.split('.')
        
        # Check for geo_infer_* modules
        if parts[0].startswith('geo_infer_'):
            module_name = parts[0]
            # Look for src/geo_infer_*/ structure
            src_path = self.project_root / f"GEO-INFER-{module_name.replace('geo_infer_', '').upper()}" / "src" / module_name
            
            if src_path.exists() and src_path.is_dir():
                # Check if submodules exist
                if len(parts) > 1:
                    submodule_path = src_path / '/'.join(parts[1:])
                    exists = (submodule_path.with_suffix('.py').exists() or 
                             (submodule_path.is_dir() and (submodule_path / '__init__.py').exists()))
                else:
                    exists = (src_path / '__init__.py').exists()
                
                self.module_cache[module_path] = exists
                return exists
        
        self.module_cache[module_path] = False
        return False
    
    def class_exists(self, module_path: str, class_name: str) -> bool:
        """Check if a class exists in a module."""
        cache_key = (module_path, class_name)
        if cache_key in self.class_cache:
            return self.class_cache[cache_key]
        
        # Convert module path to file path
        parts = module_path.split('.')
        
        if parts[0].startswith('geo_infer_'):
            module_name = parts[0]
            module_dir = self.project_root / f"GEO-INFER-{module_name.replace('geo_infer_', '').upper()}" / "src" / module_name
            
            if len(parts) > 1:
                file_path = module_dir / '/'.join(parts[1:-1]) / f"{parts[-1]}.py"
            else:
                file_path = module_dir / '__init__.py'
            
            if file_path.exists():
                try:
                    content = file_path.read_text()
                    # Check if class exists
                    tree = ast.parse(content)
                    for node in ast.walk(tree):
                        if isinstance(node, ast.ClassDef) and node.name == class_name:
                            self.class_cache[cache_key] = True
                            return True
                except:
                    pass
        
        self.class_cache[cache_key] = False
        return False


def audit_agents_file(file_path: Path, checker: ModuleChecker) -> Dict:
    """Audit a single AGENTS.md file."""
    if not file_path.exists():
        return {"error": f"File not found: {file_path}"}
    
    content = file_path.read_text()
    extractor = ImportExtractor()
    imports = extractor.extract_imports(content)
    
    issues = {
        "file": str(file_path),
        "total_imports": len(imports),
        "missing_modules": [],
        "missing_classes": [],
        "verified": [],
    }
    
    for module_path, class_name, line_num in imports:
        module_exists = checker.module_exists(module_path)
        
        if not module_exists:
            issues["missing_modules"].append({
                "module": module_path,
                "class": class_name,
                "line": line_num
            })
        else:
            class_exists = checker.class_exists(module_path, class_name)
            if not class_exists:
                issues["missing_classes"].append({
                    "module": module_path,
                    "class": class_name,
                    "line": line_num
                })
            else:
                issues["verified"].append({
                    "module": module_path,
                    "class": class_name,
                    "line": line_num
                })
    
    return issues


def main():
    """Run comprehensive audit."""
    print("=" * 70)
    print("AGENTS.md Comprehensive Audit")
    print("=" * 70)
    
    checker = ModuleChecker(PROJECT_ROOT)
    all_issues = []
    
    for agents_file in AGENTS_FILES:
        print(f"\nAuditing: {agents_file.name}")
        print("-" * 70)
        
        issues = audit_agents_file(agents_file, checker)
        all_issues.append(issues)
        
        print(f"Total imports found: {issues['total_imports']}")
        print(f"Verified: {len(issues['verified'])}")
        print(f"Missing modules: {len(issues['missing_modules'])}")
        print(f"Missing classes: {len(issues['missing_classes'])}")
        
        if issues['missing_modules']:
            print("\nMissing Modules:")
            for item in issues['missing_modules'][:10]:  # Show first 10
                print(f"  Line {item['line']}: {item['module']}.{item['class']}")
        
        if issues['missing_classes']:
            print("\nMissing Classes:")
            for item in issues['missing_classes'][:10]:  # Show first 10
                print(f"  Line {item['line']}: {item['module']}.{item['class']}")
    
    # Generate report
    report_path = PROJECT_ROOT / "GEO-INFER-INTRA" / "assessment_results" / "AGENTS_DOC_AUDIT.md"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(report_path, 'w') as f:
        f.write("# AGENTS.md Documentation Audit Report\n\n")
        f.write("**Generated**: November 5, 2025\n\n")
        f.write("## Summary\n\n")
        
        total_imports = sum(i['total_imports'] for i in all_issues)
        total_missing_modules = sum(len(i['missing_modules']) for i in all_issues)
        total_missing_classes = sum(len(i['missing_classes']) for i in all_issues)
        total_verified = sum(len(i['verified']) for i in all_issues)
        
        f.write(f"- **Total Imports**: {total_imports}\n")
        f.write(f"- **Verified**: {total_verified}\n")
        f.write(f"- **Missing Modules**: {total_missing_modules}\n")
        f.write(f"- **Missing Classes**: {total_missing_classes}\n\n")
        
        f.write("## Detailed Findings\n\n")
        for issues in all_issues:
            f.write(f"### {Path(issues['file']).name}\n\n")
            f.write(f"- Total imports: {issues['total_imports']}\n")
            f.write(f"- Verified: {len(issues['verified'])}\n")
            f.write(f"- Missing modules: {len(issues['missing_modules'])}\n")
            f.write(f"- Missing classes: {len(issues['missing_classes'])}\n\n")
            
            if issues['missing_modules']:
                f.write("#### Missing Modules\n\n")
                for item in issues['missing_modules']:
                    f.write(f"- Line {item['line']}: `{item['module']}.{item['class']}`\n")
                f.write("\n")
            
            if issues['missing_classes']:
                f.write("#### Missing Classes\n\n")
                for item in issues['missing_classes']:
                    f.write(f"- Line {item['line']}: `{item['module']}.{item['class']}` (module exists)\n")
                f.write("\n")
    
    print(f"\n✅ Audit report written to: {report_path}")
    
    return all_issues


if __name__ == "__main__":
    main()


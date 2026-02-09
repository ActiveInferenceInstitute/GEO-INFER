import ast
import os
import sys
from pathlib import Path

def is_suspicious_body(node):
    """Check if function body looks like a placeholder."""
    if not node.body:
        return "Empty Body", True
    
    # Check for simple pass/...
    if len(node.body) == 1:
        stmt = node.body[0]
        if isinstance(stmt, ast.Pass):
            return "Pass Only", True
        if isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Constant) and stmt.value.value is Ellipsis:
            return "Ellipsis Only", True
        if isinstance(stmt, ast.Raise) and isinstance(stmt.exc, ast.Call):
            if hasattr(stmt.exc.func, 'id') and stmt.exc.func.id == 'NotImplementedError':
                return "NotImplementedError", True
    
    # Check for docstring only or docstring + pass
    if len(node.body) <= 2:
        has_docstring = isinstance(node.body[0], ast.Expr) and isinstance(node.body[0].value, ast.Constant) and isinstance(node.body[0].value.value, str)
        if has_docstring:
            if len(node.body) == 1:
                return "Docstring Only", True
            if isinstance(node.body[1], ast.Pass):
                return "Docstring + Pass", True

    return None, False

def check_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        tree = ast.parse(content)
    except Exception as e:
        return [f"ERROR parsing {filepath}: {str(e)}"]

    issues = []
    
    for node in ast.walk(tree):
        # Check Functions
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            # Skip abstract methods
            is_abstract = False
            for decorator in node.decorator_list:
                if isinstance(decorator, ast.Name) and decorator.id == 'abstractmethod':
                    is_abstract = True
                elif isinstance(decorator, ast.Attribute) and decorator.attr == 'abstractmethod':
                    is_abstract = True
            
            if is_abstract:
                continue

            reason, is_suspicious = is_suspicious_body(node)
            if is_suspicious:
                # Allow __init__ to be empty if strictly necessary (though dubious for 'real' code request)
                # But user said "no placeholders", so we flag everything for review.
                issues.append(f"[FUNCTION] {node.name} (line {node.lineno}): {reason}")
            
            if "mock" in node.name.lower() or "fake" in node.name.lower() or "dummy" in node.name.lower():
                issues.append(f"[NAMING] Function {node.name} (line {node.lineno}) contains suspicious term")

        # Check Classes
        if isinstance(node, ast.ClassDef):
            if "mock" in node.name.lower() or "fake" in node.name.lower() or "dummy" in node.name.lower():
                 issues.append(f"[NAMING] Class {node.name} (line {node.lineno}) contains suspicious term")

        # Check Comments (TODOs) logic is harder with AST as comments are stripped,
        # but we can scan raw lines for strictly TODO/FIXME comments
    
    # Scan raw lines for TODOs
    lines = content.splitlines()
    for i, line in enumerate(lines):
        if "TODO" in line or "FIXME" in line or "XXX" in line:
            issues.append(f"[COMMENT] Line {i+1}: Found TODO/FIXME")
        if "raise NotImplementedError" in line:
             # Double check in case AST missed it or it's inside a logic block
             pass 

    return issues

def main():
    root_dir = Path("/Users/4d/Documents/GitHub/GEO-INFER")
    modules = sorted([d for d in root_dir.iterdir() if d.is_dir() and d.name.startswith("GEO-INFER-")])
    
    print(f"Scanning {len(modules)} modules...")
    
    total_issues = 0
    modules_with_issues = 0

    for module in modules:
        module_issues = []
        for py_file in module.rglob("*.py"):
            # Skip tests for now as they often use mocks legitimately? 
            # User said "never use mock or fake methods", implies usually production code, 
            # but let's check everything including tests if they are just placeholders.
            # Actually, "never use mock" might apply to tests too if they want integration tests.
            # But let's verify production code primarily first.
            if "tests" in py_file.parts:
                continue
                
            file_issues = check_file(py_file)
            if file_issues:
                module_issues.append((py_file.relative_to(root_dir), file_issues))
        
        if module_issues:
            modules_with_issues += 1
            print(f"\n📦 {module.name}")
            for fpath, fissues in module_issues:
                print(f"  📄 {fpath}")
                for issue in fissues:
                    print(f"    - {issue}")
                    total_issues += 1

    print(f"\n{'='*40}")
    print(f"Scan Complete.")
    print(f"Modules with issues: {modules_with_issues}/{len(modules)}")
    print(f"Total suspicious items: {total_issues}")

if __name__ == "__main__":
    main()

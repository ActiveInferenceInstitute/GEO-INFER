#!/usr/bin/env python3
"""
Organize test files into unit/integration/performance directories.
"""

from pathlib import Path
import shutil

def organize_tests(module: str, repo_root: Path):
    """Organize test files into subdirectories."""
    tests_dir = repo_root / f"GEO-INFER-{module}" / "tests"
    if not tests_dir.exists():
        return False
    
    # Check if already organized
    if (tests_dir / "unit").exists() or (tests_dir / "integration").exists():
        return True
    
    # Create subdirectories
    unit_dir = tests_dir / "unit"
    integration_dir = tests_dir / "integration"
    unit_dir.mkdir(exist_ok=True)
    integration_dir.mkdir(exist_ok=True)
    
    # Create __init__.py files
    (unit_dir / "__init__.py").touch()
    (integration_dir / "__init__.py").touch()
    
    # Move test files
    moved = 0
    for test_file in tests_dir.glob("test_*.py"):
        if test_file.name.startswith("test_"):
            # Simple heuristic: integration tests often have "integration" in name
            if "integration" in test_file.name.lower():
                shutil.move(str(test_file), str(integration_dir / test_file.name))
            else:
                shutil.move(str(test_file), str(unit_dir / test_file.name))
            moved += 1
    
    if moved > 0:
        print(f"  ✅ {module}: Organized {moved} test files")
        return True
    
    return False

def main():
    """Main execution."""
    repo_root = Path(__file__).parent.parent
    
    modules_needing_organization = [
        "ACT", "API", "BIO", "ECON", "MATH", "NORMS", "PEP", "PLACE", "SPACE"
    ]
    
    print("Organizing test files...")
    for module in modules_needing_organization:
        organize_tests(module, repo_root)
    
    print("✅ Test organization completed!")

if __name__ == "__main__":
    main()


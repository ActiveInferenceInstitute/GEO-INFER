#!/usr/bin/env python3
"""
Validate all pyproject.toml files and test uv installation.
"""

import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent
MODULE_PREFIX = "GEO-INFER-"


def validate_module(module_path: Path, module_name: str) -> tuple[bool, str]:
    """Validate a single module's pyproject.toml."""
    pyproject_path = module_path / "pyproject.toml"
    
    if not pyproject_path.exists():
        return False, "Missing pyproject.toml"
    
    # Try to install with uv
    try:
        result = subprocess.run(
            ["uv", "pip", "install", "-e", "."],
            cwd=module_path,
            capture_output=True,
            text=True,
            timeout=60
        )
        if result.returncode == 0:
            return True, "✅ Installs successfully"
        else:
            return False, f"Installation failed: {result.stderr[:200]}"
    except subprocess.TimeoutExpired:
        return False, "Installation timeout"
    except Exception as e:
        return False, f"Error: {str(e)[:200]}"


def main():
    """Validate all modules."""
    print("=" * 70)
    print("Validating UV Setup for All Modules")
    print("=" * 70)
    
    results = {}
    modules = []
    
    for item in PROJECT_ROOT.iterdir():
        if item.is_dir() and item.name.startswith(MODULE_PREFIX):
            module_name = item.name[len(MODULE_PREFIX):]
            modules.append((module_name, item))
    
    for module_name, module_path in sorted(modules):
        print(f"\nValidating {module_name}...")
        success, message = validate_module(module_path, module_name)
        results[module_name] = (success, message)
        status = "✅" if success else "❌"
        print(f"  {status} {message}")
    
    print("\n" + "=" * 70)
    print("Validation Summary")
    print("=" * 70)
    
    successful = sum(1 for success, _ in results.values() if success)
    total = len(results)
    
    print(f"\nSuccessful: {successful}/{total}")
    
    if successful < total:
        print("\nFailed modules:")
        for module_name, (success, message) in results.items():
            if not success:
                print(f"  - {module_name}: {message}")
    
    return 0 if successful == total else 1


if __name__ == "__main__":
    sys.exit(main())


# UV-Based Package Setup Migration Guide

**Created**: November 5, 2025  
**Status**: ✅ Complete

---

## Overview

All 36 GEO-INFER modules have been migrated to use `uv` and `pyproject.toml` for modern Python package management. This replaces the mixed setup.py/pyproject.toml approach and ensures consistent dependency management across all modules.

---

## Migration Summary

### Before Migration

- **Modules with setup.py**: 21 modules
- **Modules with pyproject.toml**: 4 modules (MATH, HEALTH, PEP, PLACE/cascadia)
- **Modules with both**: 2 modules (HEALTH, PEP)
- **Modules with neither**: 13 modules
- **Modules with requirements.txt**: 11 modules

### After Migration

- **All 36 modules**: ✅ Have pyproject.toml
- **All dependencies**: ✅ Declared in pyproject.toml
- **Setup files**: ✅ Standardized across all modules
- **uv compatibility**: ✅ All modules installable with `uv pip install -e .`

---

## Installation

### Installing a Single Module

```bash
cd GEO-INFER-MODULE
uv pip install -e .
```

### Installing All Modules

```bash
# From project root
for module in GEO-INFER-*/; do
    cd "$module"
    uv pip install -e .
    cd ..
done
```

### Installing with Optional Dependencies

```bash
uv pip install -e ".[dev,docs]"
```

---

## Module Structure

All modules now follow this standard structure:

```
GEO-INFER-MODULE/
├── pyproject.toml       # Package configuration (REQUIRED)
├── setup.py             # Removed (deprecated)
├── requirements.txt     # Optional (dependencies in pyproject.toml)
├── src/
│   └── geo_infer_module/
├── tests/
├── docs/
└── README.md
```

---

## pyproject.toml Structure

All modules use a standardized pyproject.toml format:

```toml
[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "geo-infer-module"
version = "0.1.0"
description = "Module description"
readme = "README.md"
license = {text = "CC BY-ND-SA 4.0"}
requires-python = ">=3.9"
authors = [
    {name = "GEO-INFER Development Team", email = "geo-infer@activeinference.institute"}
]
keywords = ["geospatial", "active inference", "geoinformatics"]
classifiers = [
    "Development Status :: 3 - Alpha",
    # ... standard classifiers
]

dependencies = [
    "numpy>=1.20.0",
    "pandas>=1.3.0",
    # ... module-specific dependencies
]

[project.optional-dependencies]
dev = [
    "pytest>=6.2.0",
    "pytest-cov>=2.12.0",
    # ... dev dependencies
]
docs = [
    "sphinx>=4.2.0",
    # ... doc dependencies
]

[tool.setuptools]
package-dir = {"" = "src"}

[tool.setuptools.packages.find]
where = ["src"]
exclude = ["tests*"]

[tool.black]
line-length = 88
# ... black configuration

[tool.isort]
profile = "black"
# ... isort configuration

[tool.mypy]
# ... mypy configuration

[tool.pytest.ini_options]
# ... pytest configuration
```

---

## Migration Tools

### Migration Script

Located at: `GEO-INFER-INTRA/scripts/migrate_to_uv.py`

```bash
# Migrate all modules
python3 GEO-INFER-INTRA/scripts/migrate_to_uv.py

# Migrate specific module
python3 GEO-INFER-INTRA/scripts/migrate_to_uv.py --module SPACE

# Dry run (simulate)
python3 GEO-INFER-INTRA/scripts/migrate_to_uv.py --dry-run
```

### Cleanup Script

Located at: `GEO-INFER-INTRA/scripts/cleanup_pyproject_deps.py`

Removes duplicate dependencies from pyproject.toml files.

```bash
python3 GEO-INFER-INTRA/scripts/cleanup_pyproject_deps.py
```

### Validation Script

Located at: `GEO-INFER-INTRA/scripts/validate_uv_setup.py`

Validates all pyproject.toml files and tests uv installation.

```bash
python3 GEO-INFER-INTRA/scripts/validate_uv_setup.py
```

---

## Benefits

1. **Consistency**: All modules use the same package management approach
2. **Modern Standards**: Uses pyproject.toml (PEP 518, PEP 621)
3. **Faster Installs**: uv is significantly faster than pip
4. **Better Dependency Resolution**: uv's resolver is more reliable
5. **Unified Tooling**: Single tool for all package management
6. **Future-Proof**: Aligns with Python packaging standards

---

## Troubleshooting

### Installation Issues

If a module fails to install:

1. Check pyproject.toml syntax
2. Verify dependencies are available
3. Check Python version compatibility
4. Review dependency conflicts

### Dependency Conflicts

If you encounter dependency conflicts:

1. Use `uv pip install -e .` to see detailed error messages
2. Check for version conflicts in dependencies
3. Consider using optional dependencies
4. Review module-specific requirements

### Validation Errors

If validation fails:

1. Run `python3 GEO-INFER-INTRA/scripts/validate_uv_setup.py` for details
2. Check for syntax errors in pyproject.toml
3. Verify all dependencies are properly quoted
4. Ensure no missing commas or brackets

---

## Next Steps

1. ✅ All modules have pyproject.toml
2. ✅ Dependencies declared in pyproject.toml
3. ✅ Validation scripts created
4. ⏳ Update CI/CD pipelines to use uv
5. ⏳ Update documentation with uv examples
6. ⏳ Remove setup.py files (after full validation)

---

## References

- [uv Documentation](https://github.com/astral-sh/uv)
- [PEP 518 - Specifying Build System for Python Projects](https://peps.python.org/pep-0518/)
- [PEP 621 - Project Metadata](https://peps.python.org/pep-0621/)
- [pyproject.toml Specification](https://packaging.python.org/en/latest/specifications/pyproject-toml/)


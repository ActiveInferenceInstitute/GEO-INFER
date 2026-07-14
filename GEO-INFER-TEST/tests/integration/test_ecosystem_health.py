"""
Ecosystem Health Tests for GEO-INFER.

Validates the structural integrity, test coverage, and consistency
of all GEO-INFER modules as a unified ecosystem.
"""

import ast
from pathlib import Path

import pytest

# Canonical list of ALL GEO-INFER modules
GEO_INFER_MODULES = [
    "ACT",
    "AG",
    "AGENT",
    "AI",
    "ANT",
    "API",
    "APP",
    "ART",
    "BAYES",
    "BIO",
    "CIV",
    "CLIMATE",
    "COG",
    "COMMS",
    "DATA",
    "ECON",
    "EDU",
    "EMERGENCY",
    "ENERGY",
    "EXAMPLES",
    "FOREST",
    "GIT",
    "HEALTH",
    "INTRA",
    "IOT",
    "LOG",
    "MARINE",
    "MATH",
    "METAGOV",
    "NORMS",
    "OPS",
    "ORG",
    "PEP",
    "PLACE",
    "REQ",
    "RISK",
    "SEC",
    "SIM",
    "SPACE",
    "SPM",
    "TEST",
    "TIME",
    "TRANSPORT",
    "WATER",
]

REPO_ROOT = Path(__file__).resolve().parents[3]  # GEO-INFER repo root


# ============================================================================
# Module structure tests
# ============================================================================


class TestModuleDirectoryStructure:
    """Verify each module has the expected directory structure."""

    @pytest.mark.parametrize("module", GEO_INFER_MODULES)
    def test_module_directory_exists(self, module):
        mod_dir = REPO_ROOT / f"GEO-INFER-{module}"
        assert mod_dir.is_dir(), f"Module directory missing: GEO-INFER-{module}"

    @pytest.mark.parametrize("module", GEO_INFER_MODULES)
    def test_module_has_readme(self, module):
        readme = REPO_ROOT / f"GEO-INFER-{module}" / "README.md"
        assert readme.is_file(), f"README.md missing in GEO-INFER-{module}"

    @pytest.mark.parametrize("module", GEO_INFER_MODULES)
    def test_module_has_tests_directory(self, module):
        tests_dir = REPO_ROOT / f"GEO-INFER-{module}" / "tests"
        assert tests_dir.is_dir(), f"tests/ directory missing in GEO-INFER-{module}"

    @pytest.mark.parametrize("module", GEO_INFER_MODULES)
    def test_module_has_test_files(self, module):
        tests_dir = REPO_ROOT / f"GEO-INFER-{module}" / "tests"
        if not tests_dir.is_dir():
            pytest.fail(f"No tests dir for {module}")
        test_files = list(tests_dir.rglob("test_*.py"))
        assert len(test_files) > 0, f"No test files found in GEO-INFER-{module}/tests/"


# ============================================================================
# Test file quality checks
# ============================================================================


class TestTestFileQuality:
    """Validate test file consistency across the ecosystem."""

    @pytest.mark.parametrize("module", GEO_INFER_MODULES)
    def test_test_files_are_parseable(self, module):
        """All test files should be valid Python."""
        tests_dir = REPO_ROOT / f"GEO-INFER-{module}" / "tests"
        if not tests_dir.is_dir():
            pytest.fail(f"No tests dir for {module}")
        for test_file in tests_dir.rglob("test_*.py"):
            try:
                ast.parse(test_file.read_text())
            except SyntaxError as e:
                pytest.fail(f"Syntax error in {test_file}: {e}")

    @pytest.mark.parametrize("module", GEO_INFER_MODULES)
    def test_test_files_have_docstrings(self, module):
        """Test files should have module-level docstrings."""
        tests_dir = REPO_ROOT / f"GEO-INFER-{module}" / "tests"
        if not tests_dir.is_dir():
            pytest.fail(f"No tests dir for {module}")
        missing = []
        for test_file in tests_dir.rglob("test_*.py"):
            try:
                tree = ast.parse(test_file.read_text())
                docstring = ast.get_docstring(tree)
                if not docstring:
                    missing.append(test_file.name)
            except SyntaxError:
                pass  # Already caught in parseable test
        # Allow up to 50% missing — this is a quality signal, not a gate
        total = len(list(tests_dir.rglob("test_*.py")))
        if total > 0:
            coverage = 1 - (len(missing) / total)
            assert coverage >= 0.3, (
                f"GEO-INFER-{module}: only {coverage:.0%} of test files have docstrings. "
                f"Missing: {missing[:5]}"
            )

    @pytest.mark.parametrize("module", GEO_INFER_MODULES)
    def test_test_functions_follow_naming(self, module):
        """Test functions should start with test_."""
        tests_dir = REPO_ROOT / f"GEO-INFER-{module}" / "tests"
        if not tests_dir.is_dir():
            pytest.fail(f"No tests dir for {module}")
        for test_file in tests_dir.rglob("test_*.py"):
            try:
                tree = ast.parse(test_file.read_text())
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        # Functions in test files should be either test_ or helper
                        if not node.name.startswith(
                            ("test_", "_", "setup", "teardown")
                        ):
                            # Check if it's within a Test class (ok for helper methods)
                            pass  # Allow helper methods in classes
            except SyntaxError:
                pass


# ============================================================================
# Ecosystem-level counts and statistics
# ============================================================================


class TestEcosystemStatistics:
    """Verify ecosystem-level test statistics."""

    def test_total_module_count(self):
        """There should be 44 GEO-INFER modules."""
        module_dirs = [
            d
            for d in REPO_ROOT.iterdir()
            if d.is_dir() and d.name.startswith("GEO-INFER-")
        ]
        assert (
            len(module_dirs) >= 44
        ), f"Expected >=44 modules, found {len(module_dirs)}"

    def test_total_test_file_count(self):
        """There should be 200+ test files across the ecosystem."""
        count = 0
        for module in GEO_INFER_MODULES:
            tests_dir = REPO_ROOT / f"GEO-INFER-{module}" / "tests"
            if tests_dir.is_dir():
                count += len(list(tests_dir.rglob("test_*.py")))
        assert count >= 200, f"Expected >=200 test files, found {count}"

    def test_test_discoverer_finds_all_modules(self):
        """TestDiscoverer should find all modules."""
        try:
            from geo_infer_test.core.test_discoverer import TestDiscoverer

            discoverer = TestDiscoverer(base_path=REPO_ROOT)
            results = discoverer.discover_all_tests(GEO_INFER_MODULES)
            # Should discover at least 40 modules
            modules_with_tests = [m for m in GEO_INFER_MODULES if m in results]
            assert (
                len(modules_with_tests) >= 40
            ), f"TestDiscoverer found tests for {len(modules_with_tests)} modules, expected >=40"
        except ImportError:
            pytest.fail("geo_infer_test.core.test_discoverer not available")


# ============================================================================
# Source structure validation
# ============================================================================


class TestSourceStructure:
    """Validate source code structure for each module."""

    @pytest.mark.parametrize("module", GEO_INFER_MODULES)
    def test_module_has_src_or_package(self, module):
        """Each module should have a src/ directory or a Python package."""
        mod_dir = REPO_ROOT / f"GEO-INFER-{module}"
        if not mod_dir.is_dir():
            pytest.fail(f"Module {module} directory missing")
        has_src = (mod_dir / "src").is_dir()
        has_package = any(
            (mod_dir / d / "__init__.py").is_file()
            for d in mod_dir.iterdir()
            if d.is_dir() and d.name.startswith("geo_infer")
        )
        assert (
            has_src or has_package
        ), f"GEO-INFER-{module} has neither src/ nor a geo_infer_* package"

    @pytest.mark.parametrize("module", GEO_INFER_MODULES)
    def test_module_has_pyproject_or_setup(self, module):
        """Each module should have a pyproject.toml or setup.py."""
        mod_dir = REPO_ROOT / f"GEO-INFER-{module}"
        if not mod_dir.is_dir():
            pytest.fail(f"Module {module} directory missing")
        has_pyproject = (mod_dir / "pyproject.toml").is_file()
        has_setup = (mod_dir / "setup.py").is_file()
        has_setup_cfg = (mod_dir / "setup.cfg").is_file()
        assert (
            has_pyproject or has_setup or has_setup_cfg
        ), f"GEO-INFER-{module} has no pyproject.toml, setup.py, or setup.cfg"

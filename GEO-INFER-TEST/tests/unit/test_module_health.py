"""
Unit tests for ModuleHealthChecker using standard and property-based testing.
"""

import shutil
import string
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest
from geo_infer_test.core.module_health import (
    DependencyChecker,
    HealthMetrics,
    ModuleHealthChecker,
    SystemValidator,
)
from hypothesis import given, settings
from hypothesis import strategies as st


class TestModuleHealthChecker:
    """Standard unit tests for ModuleHealthChecker."""

    @pytest.fixture
    def mock_repo(self):
        """Create a temporary mock repository structure."""
        tmp_dir = tempfile.mkdtemp()
        base = Path(tmp_dir)

        # Create a healthy module
        (base / "GEO-INFER-AAA").mkdir()
        (base / "GEO-INFER-AAA" / "README.md").touch()
        (base / "GEO-INFER-AAA" / "AGENTS.md").touch()
        (base / "GEO-INFER-AAA" / "tests").mkdir()
        (base / "GEO-INFER-AAA" / "tests" / "test_dummy.py").touch()
        (base / "GEO-INFER-AAA" / "tests" / "legacy_test.py").touch()
        (base / "GEO-INFER-AAA" / "pyproject.toml").write_text(
            'dependencies = ["numpy", "pandas"]'
        )

        # Create an unhealthy module (missing everything)
        (base / "GEO-INFER-ZZZ").mkdir()

        yield base
        shutil.rmtree(tmp_dir)

    def test_check_healthy_module(self, mock_repo):
        """Verify a fully compliant module passes health checks."""
        checker = ModuleHealthChecker(base_path=mock_repo)

        # We mock importlib because we can't easily make these temp dirs importable
        with patch("importlib.import_module"):
            metrics = checker.check_module("AAA")

        assert metrics.module_name == "AAA"
        assert metrics.importable is True
        assert metrics.has_readme is True
        assert metrics.has_tests is True
        assert metrics.dependency_status != "error"
        assert metrics.overall_status == "healthy"

    def test_check_counts_both_pytest_file_patterns(self, mock_repo):
        """Health counts include both supported pytest filename patterns."""
        checker = ModuleHealthChecker(base_path=mock_repo)

        with patch("importlib.import_module"):
            metrics = checker.check_module("AAA")

        assert metrics.test_count == 2

    def test_check_unhealthy_module(self, mock_repo):
        """Verify an empty module fails health checks."""
        checker = ModuleHealthChecker(base_path=mock_repo)

        with patch("importlib.import_module", side_effect=ImportError("No module")):
            metrics = checker.check_module("ZZZ")

        assert metrics.module_name == "ZZZ"
        assert metrics.importable is False
        assert metrics.has_readme is False
        assert metrics.overall_status == "unhealthy"

    def test_check_nonexistent_module(self, mock_repo):
        """Verify behavior for a non-existent directory."""
        checker = ModuleHealthChecker(base_path=mock_repo)
        metrics = checker.check_module("NONEXISTENT")

        assert metrics.overall_status == "unhealthy"
        assert "not found" in metrics.details.get("error", "")


class TestSystemValidator:
    """Tests for SystemValidator."""

    def test_system_validation_structure(self):
        """Verify the report structure contains expected keys."""
        validator = SystemValidator()
        report = validator.validate()

        assert "python_version" in report
        assert "platform" in report
        assert "disk_free_gb" in report
        assert isinstance(report["system_ok"], bool)


class TestDependencyChecker:
    """Tests for DependencyChecker dependency parsing."""

    def test_extract_dependencies_simple(self, tmp_path):
        """Test parsing a standard pyproject.toml."""
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text(
            """
        [project]
        name = "test_pkg"
        dependencies = [
            "numpy>=1.20.0",
            "pandas",
            "requests<3.0",
        ]
        """
        )

        deps = DependencyChecker._extract_dependencies(pyproject)
        assert "numpy" in deps
        assert "pandas" in deps
        assert "requests" in deps
        assert len(deps) == 3

    def test_extract_dependencies_complex(self, tmp_path):
        """Test parsing with comments and inline constraints."""
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text(
            """
        dependencies = [
            "scipy", # numeric
            "pytest>=7.0; python_version<'4.0'",
        ]
        """
        )

        deps = DependencyChecker._extract_dependencies(pyproject)
        # Should clean up to just package names
        assert "scipy" in deps
        assert "pytest" in deps

    def test_corrupt_pyproject_reports_unknown_status(self, tmp_path):
        """A malformed pyproject.toml is unknown, not a success-shaped 'ok'."""
        (tmp_path / "GEO-INFER-BROKEN").mkdir()
        (tmp_path / "GEO-INFER-BROKEN" / "pyproject.toml").write_text(
            "dependencies = [unclosed"
        )
        checker = DependencyChecker(base_path=tmp_path)
        result = checker.check_module_dependencies("BROKEN")
        assert result["status"] == "unknown"
        assert "parse failed" in result["reason"]

    def test_extract_dependencies_strips_extras(self, tmp_path):
        """GS19-87: extras markers are stripped, not probed as module names."""
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text(
            """
        dependencies = [
            "coverage[toml]>=7.6",
            "dask[dataframe]>=2024.2",
            "uvicorn[standard]>=0.30",
        ]
        """
        )

        deps = DependencyChecker._extract_dependencies(pyproject)
        assert deps == ["coverage", "dask", "uvicorn"]

    @pytest.mark.parametrize(
        ("distribution", "import_root"),
        [
            ("pyyaml", "yaml"),
            ("pyjwt", "jwt"),
            ("scikit-learn", "sklearn"),
            ("pillow", "PIL"),
            ("psycopg2-binary", "psycopg2"),
            ("GitPython", "git"),
            ("inferactively-pymdp", "pymdp"),
            ("z3-solver", "z3"),
            ("python-multipart", "multipart"),
            ("bayeux-ml", "bayeux"),
            ("mkdocs-material", "material"),
            ("pandas", "pandas"),
        ],
    )
    def test_normalize_dep_name_maps_import_roots(self, distribution, import_root):
        """GS19-87: known distributions probe their real import root."""
        assert DependencyChecker._normalize_dep_name(distribution) == import_root

    def test_check_module_dependencies_probes_import_roots(self, tmp_path, monkeypatch):
        """GS19-87: the full probe path strips extras and maps import roots.

        Pre-fix this module reported status "missing": pyyaml was probed as
        a "pyyaml" module and coverage[toml] as "coverage_toml".
        """
        (tmp_path / "GEO-INFER-SAMPLE").mkdir()
        (tmp_path / "GEO-INFER-SAMPLE" / "pyproject.toml").write_text(
            "[project]\n"
            'name = "sample"\n'
            'dependencies = ["pyyaml>=6.0", "coverage[toml]>=7.6"]\n'
        )
        probed = []

        def fake_import(name):
            probed.append(name)
            if name in {"yaml", "coverage"}:
                return object()
            raise ImportError(name)

        monkeypatch.setattr(
            "geo_infer_test.core.module_health.importlib.import_module",
            fake_import,
        )
        result = DependencyChecker(base_path=tmp_path).check_module_dependencies(
            "SAMPLE"
        )

        assert result["status"] == "ok"
        assert result["total"] == 2
        assert probed == ["yaml", "coverage"]


# ---------------------------------------------------------------------------
# Property-Based Tests (Hypothesis)
# ---------------------------------------------------------------------------


class TestHypothesisModuleHealth:
    """Property-based tests for ModuleHealthChecker logic."""

    @given(
        st.text(
            min_size=1,
            max_size=10,
            alphabet=st.characters(whitelist_categories=("L", "N")),
        )
    )
    def test_check_module_resilience(self, module_name):
        """
        Fuzz testing: verify check_module never crashes regardless of module name input.
        It should return a HealthMetrics object, even if 'unhealthy'.
        """
        with tempfile.TemporaryDirectory() as tmp_dir:
            base = Path(tmp_dir)
            checker = ModuleHealthChecker(base_path=base)

            # Create the directory sometimes
            if len(module_name) % 2 == 0:
                (base / f"GEO-INFER-{module_name}").mkdir()

            # Mock importlib to avoid side effects/flakiness from real imports
            with patch("importlib.import_module", side_effect=ImportError("Mocked")):
                try:
                    metrics = checker.check_module(module_name)
                    assert isinstance(metrics, HealthMetrics)
                    assert metrics.module_name == module_name
                except Exception as e:
                    pytest.fail(f"check_module crashed on input '{module_name}': {e}")

    @settings(max_examples=50)
    @given(
        st.lists(
            st.text(
                min_size=3,
                max_size=20,
                alphabet=string.ascii_letters,
            ),
            min_size=1,
            max_size=5,
            unique=True,
        )
    )
    def test_check_all_modules_consistency(self, module_names):
        """Verify check_all_modules returns results for every requested module."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            checker = ModuleHealthChecker(base_path=Path(tmp_dir))
            results = checker.check_all_modules(module_names)

            assert len(results) == len(module_names)
            for name in module_names:
                assert name in results
                assert isinstance(results[name], HealthMetrics)

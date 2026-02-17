"""Tests for GIT repo analyzer module."""
import pytest
import tempfile
from pathlib import Path

from geo_infer_git.core.repo_analyzer import DependencyAnalyzer


class TestDependencyAnalyzer:
    def test_init(self, tmp_path):
        analyzer = DependencyAnalyzer(repo_path=tmp_path)
        assert analyzer.repo_path == tmp_path
        assert len(analyzer.dependencies) == 0

    def test_analyze_requirements_files(self, tmp_path):
        # Create a requirements.txt file
        req_file = tmp_path / "requirements.txt"
        req_file.write_text("numpy>=1.20.0\npandas==1.3.0\nrequests\n# comment line\n")
        analyzer = DependencyAnalyzer(repo_path=tmp_path)
        analyzer._analyze_requirements_files()
        dep_names = [d.name for d in analyzer.dependencies]
        assert "numpy" in dep_names
        assert "pandas" in dep_names
        assert "requests" in dep_names

    def test_analyze_empty_requirements(self, tmp_path):
        req_file = tmp_path / "requirements.txt"
        req_file.write_text("")
        analyzer = DependencyAnalyzer(repo_path=tmp_path)
        analyzer._analyze_requirements_files()
        assert len(analyzer.dependencies) == 0

    def test_analyze_requirements_with_comments(self, tmp_path):
        req_file = tmp_path / "requirements.txt"
        req_file.write_text("# This is a comment\nnumpy\n-r other_requirements.txt\n")
        analyzer = DependencyAnalyzer(repo_path=tmp_path)
        analyzer._analyze_requirements_files()
        dep_names = [d.name for d in analyzer.dependencies]
        assert "numpy" in dep_names
        assert len(analyzer.dependencies) == 1  # Comment and -r lines should be skipped

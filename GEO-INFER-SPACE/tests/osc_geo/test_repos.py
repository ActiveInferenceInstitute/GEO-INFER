"""
Tests for the OSC-GEO repository cloning functionality.
"""

import os
import pytest
from unittest.mock import patch, MagicMock
import tempfile

from geo_infer_space.osc_geo.core.repos import (
    is_geo_infer_git_available,
    clone_osc_repos,
    get_repo_path,
    OSC_REPOS
)

class TestOscGeoRepos:
    """Test cases for OSC-GEO repository cloning functionality."""
    
    def test_is_geo_infer_git_available(self):
        """Test checking if GEO-INFER-GIT is available."""
        # This test assumes GEO-INFER-GIT is installed
        result = is_geo_infer_git_available()
        assert isinstance(result, bool)
    
    @patch('geo_infer_space.osc_geo.core.repos.is_geo_infer_git_available')
    def test_clone_osc_repos_git_not_available(self, mock_available):
        """Test cloning raises ImportError when git is not available."""
        mock_available.return_value = False
        
        with pytest.raises(ImportError):
            clone_osc_repos()
    
    @patch('geo_infer_space.osc_geo.core.repos.is_geo_infer_git_available')
    @patch('geo_infer_space.osc_geo.core.repos.subprocess.run')
    @patch('os.path.exists')
    def test_clone_osc_repos_success(self, mock_exists, mock_run, mock_available):
        """Test successful cloning of repositories."""
        mock_available.return_value = True
        mock_exists.return_value = False
        mock_run.return_value = MagicMock(returncode=0)
        with tempfile.TemporaryDirectory() as tmpdir:
            results = clone_osc_repos(output_dir=tmpdir)
            assert all(results.values())
            assert len(results) == len(OSC_REPOS)
            assert mock_run.call_count == len(OSC_REPOS)
    
    @patch('geo_infer_space.osc_geo.core.repos.is_geo_infer_git_available')
    @patch('geo_infer_space.osc_geo.core.repos.subprocess.run')
    @patch('os.path.exists')
    def test_clone_osc_repos_partial_failure(self, mock_exists, mock_run, mock_available):
        """Test partial failure when cloning repositories."""
        mock_available.return_value = True
        mock_exists.return_value = False
        mock_run.side_effect = [MagicMock(returncode=0), MagicMock(returncode=1)]
        with tempfile.TemporaryDirectory() as tmpdir:
            results = clone_osc_repos(output_dir=tmpdir)
            assert not all(results.values())
            assert len(results) == len(OSC_REPOS)
            assert mock_run.call_count == len(OSC_REPOS)
    
    @patch('os.path.exists')
    def test_get_repo_path_exists(self, mock_exists):
        """Test get_repo_path when repository exists."""
        mock_exists.return_value = True
        with tempfile.TemporaryDirectory() as tmpdir:
            os.environ['OSC_REPOS_DIR'] = tmpdir
            path = get_repo_path("h3grid-srv")
            assert path is not None
            assert "osc-geo-h3grid-srv" in path
    
    @patch('os.path.exists')
    def test_get_repo_path_not_exists(self, mock_exists):
        """Test get_repo_path when repository doesn't exist."""
        mock_exists.return_value = False
        with tempfile.TemporaryDirectory() as tmpdir:
            os.environ['OSC_REPOS_DIR'] = tmpdir
            path = get_repo_path("h3grid-srv")
            assert path is None
    
    def test_get_repo_path_unknown_repo(self):
        """Test get_repo_path with unknown repository key."""
        # Call function
        path = get_repo_path("unknown-repo")
        
        # Verify results
        assert path is None 
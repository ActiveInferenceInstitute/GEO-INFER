"""
Tests for the OSC-GEO repository cloning functionality.
"""

import os
import pytest
from unittest.mock import patch, MagicMock

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
        """Test cloning fails when GEO-INFER-GIT is not available."""
        mock_available.return_value = False
        
        with pytest.raises(ImportError):
            clone_osc_repos()
    
    @patch('geo_infer_space.osc_geo.core.repos.is_geo_infer_git_available')
    @patch('geo_infer_space.osc_geo.core.repos.RepoCloner')
    @patch('geo_infer_space.osc_geo.core.repos.load_clone_config')
    def test_clone_osc_repos_success(self, mock_load_config, mock_cloner_class, mock_available):
        """Test successful cloning of repositories."""
        # Mock dependencies
        mock_available.return_value = True
        mock_load_config.return_value = {
            "general": {"output_dir": "/tmp/repos"},
            "github": {"token": "fake-token"}
        }
        
        # Create mock repo cloner
        mock_cloner = MagicMock()
        mock_cloner.clone_repository.return_value = True
        mock_cloner_class.return_value = mock_cloner
        
        # Call function
        results = clone_osc_repos()
        
        # Verify results
        assert all(results.values())
        assert len(results) == len(OSC_REPOS)
        
        # Verify calls
        assert mock_cloner.clone_repository.call_count == len(OSC_REPOS)
        assert mock_cloner.close.call_count == 1
    
    @patch('geo_infer_space.osc_geo.core.repos.is_geo_infer_git_available')
    @patch('geo_infer_space.osc_geo.core.repos.RepoCloner')
    @patch('geo_infer_space.osc_geo.core.repos.load_clone_config')
    def test_clone_osc_repos_partial_failure(self, mock_load_config, mock_cloner_class, mock_available):
        """Test partial failure when cloning repositories."""
        # Mock dependencies
        mock_available.return_value = True
        mock_load_config.return_value = {
            "general": {"output_dir": "/tmp/repos"},
            "github": {"token": "fake-token"}
        }
        
        # Create mock repo cloner with one failure
        mock_cloner = MagicMock()
        mock_cloner.clone_repository.side_effect = [True, False]
        mock_cloner_class.return_value = mock_cloner
        
        # Call function
        results = clone_osc_repos()
        
        # Verify results
        assert not all(results.values())
        assert len(results) == len(OSC_REPOS)
        
        # Verify calls
        assert mock_cloner.clone_repository.call_count == len(OSC_REPOS)
        assert mock_cloner.close.call_count == 1
    
    @patch('geo_infer_space.osc_geo.core.repos.os.path.exists')
    @patch('geo_infer_space.osc_geo.core.repos.load_clone_config')
    def test_get_repo_path_exists(self, mock_load_config, mock_exists):
        """Test get_repo_path when repository exists."""
        # Mock dependencies
        mock_load_config.return_value = {
            "general": {"output_dir": "/tmp/repos"}
        }
        mock_exists.return_value = True
        
        # Call function
        path = get_repo_path("h3grid-srv")
        
        # Verify results
        assert path is not None
        assert "os-climate" in path
        assert "osc-geo-h3grid-srv" in path
    
    @patch('geo_infer_space.osc_geo.core.repos.os.path.exists')
    @patch('geo_infer_space.osc_geo.core.repos.load_clone_config')
    def test_get_repo_path_not_exists(self, mock_load_config, mock_exists):
        """Test get_repo_path when repository doesn't exist."""
        # Mock dependencies
        mock_load_config.return_value = {
            "general": {"output_dir": "/tmp/repos"}
        }
        mock_exists.return_value = False
        
        # Call function
        path = get_repo_path("h3grid-srv")
        
        # Verify results
        assert path is None
    
    def test_get_repo_path_unknown_repo(self):
        """Test get_repo_path with unknown repository key."""
        # Call function
        path = get_repo_path("unknown-repo")
        
        # Verify results
        assert path is None 
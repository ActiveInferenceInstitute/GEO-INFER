"""
import os
import pytest
import tempfile
import shutil
from geo_infer_space.osc_geo.core.repos import clone_osc_repos, OSC_REPOS
from geo_infer_space.osc_geo.core.status import check_integration_status

@pytest.mark.integration
def test_clone_and_status_integration():
    with tempfile.TemporaryDirectory() as tmpdir:
        # Clone the repositories
        results = clone_osc_repos(output_dir=tmpdir)
        
        # Verify cloning success
        assert all(results.values()), f"Cloning failed for some repos: {results}"
        assert len(results) == len(OSC_REPOS)
        
        # Check status
        status = check_integration_status(base_dir=tmpdir)
        assert status.all_repos_exist, "Not all repositories exist after cloning"
        
        # Optionally, check more details
        for repo_key in OSC_REPOS:
            assert repo_key in status.repositories
            repo_status = status.repositories[repo_key]
            assert repo_status.exists
            assert repo_status.is_git_repo
            assert repo_status.current_branch == OSC_REPOS[repo_key].get('branch', 'main')

        # Note: tests_passed may not be True since we didn't run setup, but existence is key

        # Test H3GridManager
        from geo_infer_space.osc_geo.core.h3grid import H3GridManager
        grid_manager = H3GridManager(repo_base_dir=tmpdir, auto_start=False)
        assert grid_manager.repo_path == os.path.join(tmpdir, 'os-climate', 'osc-geo-h3grid-srv')
        # Optionally start and stop if possible, but skip if complex

        # Test H3DataLoader
        from geo_infer_space.osc_geo.core.loader import H3DataLoader
        data_loader = H3DataLoader(repo_base_dir=tmpdir)
        assert data_loader.repo_path == os.path.join(tmpdir, 'os-climate', 'osc-geo-h3loader-cli')
        # Create a sample geojson file
        sample_file = os.path.join(tmpdir, 'sample.geojson')
        with open(sample_file, 'w') as f:
            f.write('{"type": "FeatureCollection", "features": [{"type": "Feature", "geometry": {"type": "Point", "coordinates": [0, 0]}, "properties": {}}]}')
        output_file = os.path.join(tmpdir, 'output.h3')
        success = data_loader.load_data(input_file=sample_file, output_file=output_file, resolution=8)
        assert success, "Failed to load sample data"
        assert os.path.exists(output_file)
""" 
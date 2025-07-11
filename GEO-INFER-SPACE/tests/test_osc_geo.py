import pytest
from pathlib import Path
from geo_infer_space.osc_geo.core.repos import clone_osc_repos
from geo_infer_space.osc_geo.utils.osc_simple_status import check_repo_status

@pytest.mark.integration
def test_clone_repos(tmp_path):
    """Test cloning of OSC repos into temp path."""
    success = clone_osc_repos(str(tmp_path))
    assert success
    assert len(list(tmp_path.iterdir())) > 0  # Check repos were cloned

def test_check_status():
    """Test status checking returns dict."""
    status = check_repo_status()
    assert isinstance(status, dict)
    assert 'repositories' in status 
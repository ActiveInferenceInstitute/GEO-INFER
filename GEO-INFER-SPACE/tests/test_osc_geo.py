import pytest
from geo_infer_space.osc_geo.core.repos import clone_osc_repos
from geo_infer_space.osc_geo.utils.osc_simple_status import check_repo_status

@pytest.mark.integration
def test_clone_repos(tmp_path):
    clone_osc_repos(str(tmp_path))
    assert (tmp_path / 'osc-geo-h3grid-srv').exists()
    assert (tmp_path / 'osc-geo-h3loader-cli').exists()

def test_check_status():
    status = check_repo_status()
    assert 'repositories' in status 
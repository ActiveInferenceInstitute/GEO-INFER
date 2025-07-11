#!/usr/bin/env python3
"""
Tests for UnifiedH3Backend
"""
import pytest
from pathlib import Path
import shutil
import os
from geo_infer_space.osc_geo.core.repos import clone_osc_repos, get_repo_path
from geo_infer_space.core.unified_backend import UnifiedH3Backend
from geo_infer_space.core.base_module import BaseAnalysisModule
from shapely.geometry import Polygon

@pytest.fixture(scope="module")
def temp_dir(tmp_path_factory):
    return tmp_path_factory.mktemp("test_unified")

@pytest.fixture(scope="module")
def cloned_repos(temp_dir):
    clone_osc_repos(output_dir=str(temp_dir))
    return str(temp_dir / 'os-climate')

@pytest.fixture(scope="module")
def sample_module(backend):
    class SampleModule(BaseAnalysisModule):
        def acquire_raw_data(self) -> Path:
            raw_path = self.data_dir / 'sample.geojson'
            with open(raw_path, 'w') as f:
                f.write('{"type": "FeatureCollection", "features": [{"type": "Feature", "geometry": {"type": "Point", "coordinates": [0, 0]}, "properties": {}}]}')
            return raw_path
        
        def run_final_analysis(self, h3_data: dict) -> dict:
            return {hex: {'analyzed': True} for hex in h3_data}
    
    return SampleModule(backend, 'sample')

@pytest.fixture(scope="module")
def backend(cloned_repos, temp_dir):
    data_dir = temp_dir / 'data'
    data_dir.mkdir()
    modules = {}  # Will add sample later
    # Setup venv for h3loader-cli
    import subprocess
    repo_path = get_repo_path("h3loader-cli", cloned_repos)
    venv_path = os.path.join(repo_path, 'venv')
    subprocess.run(['python3', '-m', 'venv', venv_path], check=True)
    pip_path = os.path.join(venv_path, 'bin', 'pip')
    subprocess.run([pip_path, 'install', '-e', repo_path], check=True)
    backend = UnifiedH3Backend(
        modules=modules,
        resolution=9,  # Smaller for testing
        target_region='Test',
        target_areas={'Test': ['all']},
        base_data_dir=data_dir,
        osc_repo_dir=cloned_repos
    )
    return backend

def test_backend_init(backend):
    assert backend.resolution == 9
    assert backend.target_region == 'Test'
    assert backend.h3_loader is not None

def test_run_analysis(backend, sample_module):
    backend.modules['sample'] = sample_module
    backend.run_comprehensive_analysis()
    assert len(backend.unified_data) > 0
    for data in backend.unified_data.values():
        assert 'sample' in data
        assert data['sample'].get('analyzed') == True 
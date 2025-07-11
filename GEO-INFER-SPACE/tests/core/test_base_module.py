#!/usr/bin/env python3
"""
Tests for BaseAnalysisModule
"""
import pytest
from pathlib import Path
import json
from geo_infer_space.core.base_module import BaseAnalysisModule
from geo_infer_space.core.unified_backend import UnifiedH3Backend  # Assume imported
import subprocess
import os
from geo_infer_space.osc_geo.core.repos import clone_osc_repos, get_repo_path

@pytest.fixture
def temp_backend(tmp_path):
    data_dir = tmp_path / 'data'
    data_dir.mkdir()
    repo_dir = tmp_path / 'repos'
    repo_dir.mkdir()
    clone_osc_repos(output_dir=str(repo_dir))
    osc_repo_dir = str(repo_dir / 'os-climate')
    # Setup venv
    repo_path = get_repo_path("h3loader-cli", osc_repo_dir)
    venv_path = os.path.join(repo_path, 'venv')
    subprocess.run(['python3', '-m', 'venv', venv_path], check=True)
    pip_path = os.path.join(venv_path, 'bin', 'pip')
    subprocess.run([pip_path, 'install', '-e', repo_path], check=True)
    modules = {}
    return UnifiedH3Backend(modules, resolution=9, base_data_dir=data_dir, osc_repo_dir=osc_repo_dir)

@pytest.fixture
def test_module(temp_backend):
    class TestModule(BaseAnalysisModule):
        def acquire_raw_data(self) -> Path:
            raw_path = self.data_dir / 'test_raw.json'
            with open(raw_path, 'w') as f:
                json.dump({'data': 'raw'}, f)
            return raw_path
        
        def run_final_analysis(self, h3_data: dict) -> dict:
            return {'analyzed': len(h3_data)}
    
    return TestModule(temp_backend, 'test')

def test_run_analysis(test_module):
    result = test_module.run_analysis()
    assert 'analyzed' in result
    assert result['analyzed'] == 1  # Assuming sample data produces 1 hex
    # Add assertions based on real processing

def test_process_to_h3(test_module):
    raw_path = test_module.acquire_raw_data()
    h3_data = test_module.process_to_h3(raw_path)
    assert isinstance(h3_data, dict)
    assert len(h3_data) > 0
    # Assert specific keys or values based on sample 
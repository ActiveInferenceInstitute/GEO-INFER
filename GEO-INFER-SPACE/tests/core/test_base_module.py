#!/usr/bin/env python3
"""
Tests for BaseAnalysisModule
"""
import pytest
from unittest.mock import MagicMock, patch
from pathlib import Path
import logging
import json
from geo_infer_space.core.base_module import BaseAnalysisModule

class TestBaseAnalysisModule:
    @pytest.fixture
    def mock_backend(self):
        backend = MagicMock()
        backend.resolution = 8
        backend.target_hexagons = ['hex1', 'hex2']
        backend.base_data_dir = Path('test_data')
        backend.h3_loader = MagicMock()
        return backend
    
    @pytest.fixture
    def analysis_module(self, mock_backend):
        class TestModule(BaseAnalysisModule):
            def acquire_raw_data(self) -> Path:
                return Path('raw_data.json')
            def run_final_analysis(self, h3_data: dict) -> dict:
                return {'result': 'analyzed'}
        return TestModule(mock_backend, 'test_module')
    
    def test_init(self, analysis_module, mock_backend):
        assert analysis_module.backend == mock_backend
        assert analysis_module.module_name == 'test_module'
        assert analysis_module.resolution == 8
        assert analysis_module.target_hexagons == ['hex1', 'hex2']
        assert analysis_module.data_dir == Path('test_data/test_module')
        assert analysis_module.h3_cache_path == Path('test_data/test_module/test_module_h3_res8.json')
    
    @patch('geo_infer_space.core.base_module.json')
    @patch('builtins.open')
    def test_run_analysis_cached(self, mock_open, mock_json, analysis_module):
        analysis_module.h3_cache_path.exists.return_value = True
        mock_json.load.return_value = {'cached': 'data'}
        result = analysis_module.run_analysis()
        assert result == {'result': 'analyzed'}
    
    def test_process_to_h3(self, analysis_module):
        # Add test for process_to_h3
        pass 
#!/usr/bin/env python3
"""
Tests for API Clients
"""
import pytest
from unittest.mock import patch
from geo_infer_space.core.api_clients import BaseAPIManager

class TestBaseAPIManager:
    @pytest.fixture
    def manager(self):
        return BaseAPIManager('https://test-api.com')
    
    @patch('requests.Session.get')
    def test_fetch_data(self, mock_get, manager):
        mock_get.return_value.json.return_value = {'data': 'test'}
        result = manager.fetch_data('endpoint')
        assert result == {'data': 'test'} 
import pytest
from unittest.mock import MagicMock, patch
from geo_infer_space.osc_geo import create_h3_data_loader

@pytest.fixture(autouse=True)
def mock_h3_loader():
    mock_loader = MagicMock()
    mock_loader.load_data.return_value = {'test_hex': {'value': 1}}
    with patch('geo_infer_space.core.unified_backend.create_h3_data_loader', return_value=mock_loader):
        yield 
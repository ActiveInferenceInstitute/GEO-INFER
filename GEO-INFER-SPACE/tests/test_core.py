import pytest
import json
from pathlib import Path
from geo_infer_space.core.unified_backend import UnifiedH3Backend

def test_backend_init():
    """Test UnifiedH3Backend initialization with real parameters."""
    backend = UnifiedH3Backend(modules={}, resolution=8, target_region='Test', base_data_dir=Path('test_data'))
    assert backend.resolution == 8
    assert backend.target_region == 'Test'
    assert isinstance(backend.base_data_dir, Path)

def test_calculate_scores():
    """Test score calculation with real small data."""
    backend = UnifiedH3Backend(modules={}, resolution=8)
    backend.unified_data = {'hex1': {'module1': {'score': 0.5}, 'module2': {'score': 0.7}}}
    scores = backend.calculate_analysis_scores()
    assert scores['hex1']['composite_score'] == pytest.approx(0.6) 
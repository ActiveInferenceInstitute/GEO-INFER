import pytest
from geo_infer_space.core.unified_backend import UnifiedH3Backend
from geo_infer_space.core.visualization_engine import InteractiveVisualizationEngine

@pytest.fixture
def sample_backend():
    return UnifiedH3Backend(modules={}, resolution=8)

def test_backend_init(sample_backend):
    assert sample_backend.resolution == 8

def test_calculate_scores(sample_backend):
    # Add mock data
    sample_backend.unified_data = {'hex1': {'module1': {'score': 0.5}, 'module2': {'score': 0.7}}}
    scores = sample_backend.calculate_analysis_scores()
    assert scores['hex1']['composite_score'] == 0.6 
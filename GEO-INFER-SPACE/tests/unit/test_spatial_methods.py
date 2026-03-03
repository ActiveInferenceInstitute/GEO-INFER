import pytest
from geo_infer_space.core.spatial_methods import SpatialMethods

# Instead of relying on a real H3 backend being available, we can test
# that the SpatialMethods gracefully handles missing backends or propagates valid parameters.

class MockH3Backend:
    def get_cell_ring(self, cell, ring):
        return {f"ring_{cell}_{ring}"}
        
    def get_cell_resolution(self, cell):
        return 9
        
    def get_cell_parent(self, cell, res):
        return f"parent_{cell}_{res}"
        
    def get_cell_children(self, cell, res):
        return [f"child1_{cell}_{res}", f"child2_{cell}_{res}"]
        
    def get_cell_area(self, cell, unit):
        return 10.0
        
    def get_cell_neighbors(self, cell, k):
        return [f"neighbor_{cell}"]
        
    def get_cell_distance(self, cell, other):
        return 1

@pytest.fixture
def spatial_methods():
    return SpatialMethods(h3_backend=MockH3Backend())

def test_buffer_analysis(spatial_methods):
    res = spatial_methods.buffer_analysis(["cell_1"], buffer_rings=1)
    assert "center_cells" in res
    assert res["buffer_rings"] == 1
    
    with pytest.raises(ValueError):
        spatial_methods.buffer_analysis([])

def test_overlay_cells(spatial_methods):
    res = spatial_methods.overlay_cells(["a", "b"], ["b", "c"], "intersection")
    assert res["result_cells"] == ["b"]
    
    res = spatial_methods.overlay_cells(["a"], ["b"], "union")
    assert set(res["result_cells"]) == {"a", "b"}

    with pytest.raises(ValueError):
        spatial_methods.overlay_cells([], [], "invalid")

def test_spatial_filter(spatial_methods):
    res = spatial_methods.spatial_filter(["a", "b", "c"], [10, 20, 30], filter_type="threshold", threshold=15)
    assert set(res["filtered_cells"]) == {"b", "c"}

    with pytest.raises(ValueError):
        spatial_methods.spatial_filter(["a"], [1, 2])
        
    with pytest.raises(ValueError):
        spatial_methods.spatial_filter(["a"], [1], filter_type="invalid")

def test_aggregate_to_region(spatial_methods):
    res = spatial_methods.aggregate_to_region(["cell_1", "cell_2"], [10.0, 20.0], target_resolution=8, aggregation="mean")
    assert "output_cells" in res
    
    with pytest.raises(ValueError):
        spatial_methods.aggregate_to_region(["a"], [1, 2], 5)

def test_disaggregate_to_cells(spatial_methods):
    res = spatial_methods.disaggregate_to_cells(["parent1"], [100.0], target_resolution=10, method="equal")
    assert "output_cells" in res

def test_calculate_coverage(spatial_methods):
    res = spatial_methods.calculate_coverage(["cell1"], ["region1"])
    assert res["num_cells"] == 1
    assert "coverage_ratio" in res

def test_find_spatial_outliers(spatial_methods):
    # This will use the mock
    res = spatial_methods.find_spatial_outliers(["cell1", "neighbor_cell1"], [100.0, 10.0])
    assert "outliers" in res

def test_compute_accessibility(spatial_methods):
    res = spatial_methods.compute_accessibility(["orig1"], ["dest1"])
    assert res["num_origins"] == 1

def test_calculate_spatial_weights(spatial_methods):
    res = spatial_methods.calculate_spatial_weights(["cell1", "neighbor_cell1"], weight_type="queen")
    assert "weights" in res

"""Tests for exposure model."""

from geo_infer_risk.core.exposure_model import EnhancedExposureModel


class TestEnhancedExposureModel:
    """Tests for the enhanced exposure model."""

    def setup_method(self) -> None:
        self.model = EnhancedExposureModel(
            exposure_type="property",
            params={
                "value_type": "replacement_cost",
                "aggregation_level": "building",
            },
        )

    def test_initialization(self) -> None:
        assert self.model.exposure_type == "property"
        assert self.model.value_type == "replacement_cost"
        assert self.model.aggregation_level == "building"

    def test_different_exposure_types(self) -> None:
        for etype in ["property", "population", "infrastructure", "business"]:
            m = EnhancedExposureModel(exposure_type=etype, params={})
            assert m.exposure_type == etype

    def test_default_time_scenarios(self) -> None:
        m = EnhancedExposureModel(exposure_type="population", params={})
        assert "day" in m.time_scenarios
        assert "night" in m.time_scenarios

    def test_spatial_resolution_default(self) -> None:
        m = EnhancedExposureModel(exposure_type="property", params={})
        assert m.spatial_resolution == 9


class TestExposureDataFailureSurfacing:
    """Malformed or unmergeable exposure data must surface, not silently
    disable the model (GS-141)."""

    def test_malformed_exposure_source_raises_value_error(self, tmp_path) -> None:
        """A configured source missing required columns must raise the
        validation ValueError instead of degrading to an empty model."""
        bad_csv = tmp_path / "bad.csv"
        bad_csv.write_text("lon,value\n0.0,100.0\n")
        try:
            EnhancedExposureModel("property", {"data_sources": [f"file://{bad_csv}"]})
        except ValueError as exc:
            assert "Required column missing" in str(exc)
        else:
            raise AssertionError("Malformed exposure source did not raise ValueError")

    def test_merge_failure_raises_instead_of_dropping_source(self, tmp_path) -> None:
        """A source that cannot be merged must raise RuntimeError, not be
        silently discarded while the first source keeps loading."""
        primary = tmp_path / "primary.csv"
        primary.write_text("id,longitude,latitude\na,0.0,0.0\n")
        foreign = tmp_path / "foreign.csv"
        foreign.write_text("x\n1\n")
        try:
            EnhancedExposureModel(
                "property",
                {"data_sources": [f"file://{primary}", f"file://{foreign}"]},
            )
        except RuntimeError as exc:
            assert "Failed to merge exposure data" in str(exc)
        else:
            raise AssertionError(
                "Merge failure was silently swallowed and second source dropped"
            )

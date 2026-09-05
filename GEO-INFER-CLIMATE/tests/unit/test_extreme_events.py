"""Unit tests for extreme events module."""

import numpy as np
import pytest
import xarray as xr


from geo_infer_climate.core.extreme_events import (
    ExtremeEventAnalyzer,
    ExtremeEventType,
    ExtremeEvent,
    Severity,
)


@pytest.fixture
def analyzer():
    return ExtremeEventAnalyzer()


class TestHeatwaveDetection:
    def test_detect_heatwave_in_hot_spell(self, analyzer):
        values = np.array([20.0] * 30 + [38.0] * 7 + [20.0] * 30)
        temp = xr.DataArray(values, dims=["time"])
        result = analyzer.detect_heatwaves(temp)
        assert result["events_detected"] >= 1

    def test_no_heatwave_in_mild_data(self, analyzer):
        values = np.full(60, 22.0)
        temp = xr.DataArray(values, dims=["time"])
        result = analyzer.detect_heatwaves(temp)
        assert result["events_detected"] == 0

    def test_heatwave_result_fields(self, analyzer):
        np.random.seed(42)
        values = 20 + 10 * np.sin(np.linspace(0, 4 * np.pi, 365)) + np.random.normal(0, 3, 365)
        temp = xr.DataArray(values, dims=["time"])
        result = analyzer.detect_heatwaves(temp)
        assert "events_detected" in result
        assert "threshold_temp" in result
        assert "events" in result


class TestColdSpellDetection:


    def test_detect_cold_spell(self, analyzer):
        # Use gradual data so -10 is well below the 10th percentile
        np.random.seed(42)
        normal_temps = np.random.normal(15, 3, 60).tolist()
        cold_spell = [-10.0] * 5
        values = np.array(normal_temps[:30] + cold_spell + normal_temps[30:])
        temp = xr.DataArray(values, dims=["time"])
        result = analyzer.detect_cold_spells(temp)
        assert result["events_detected"] >= 1

    def test_cold_spell_min_duration(self, analyzer):
        np.random.seed(42)
        normal_temps = np.random.normal(15, 3, 60).tolist()
        cold_spell = [-10.0] * 5
        values = np.array(normal_temps[:30] + cold_spell + normal_temps[30:])
        temp = xr.DataArray(values, dims=["time"])
        result = analyzer.detect_cold_spells(temp, min_duration=3)
        if result["events"]:
            for event in result["events"]:
                assert event["duration_days"] >= 3

class TestDroughtDetection:
    def test_detect_drought_in_dry_spell(self, analyzer):
        # A 40-step near-zero dry spell embedded in variable rainfall must
        # be detected as one long consecutive drought run.
        np.random.seed(42)
        wet = np.random.exponential(10, 60).tolist()
        dry = [0.0] * 40
        values = np.array(wet[:30] + dry + wet[30:])
        precip = xr.DataArray(values, dims=["time"])
        result = analyzer.detect_droughts(precip, min_duration=30)
        assert result["events_detected"] == 1
        event = result["events"][0]
        assert event["duration_days"] >= 30
        assert event["min_precip"] <= event["mean_precip"]
        assert result["total_dry_days"] >= 40

    def test_drought_min_duration_filters_short_runs(self, analyzer):
        # Only a 5-step dry spell: with min_duration=30 nothing qualifies.
        np.random.seed(42)
        wet = np.random.exponential(10, 80).tolist()
        values = np.array(wet[:40] + [0.0] * 5 + wet[40:])
        precip = xr.DataArray(values, dims=["time"])
        result = analyzer.detect_droughts(precip, min_duration=30)
        assert result["events_detected"] == 0

    def test_droughts_per_grid_cell(self, analyzer):
        # (time, lat, lon) input: only one cell has a long dry run.
        np.random.seed(42)
        n = 90
        wet = np.random.exponential(10, n)
        data = np.stack([wet, wet + 5.0], axis=1)[:, None, :]  # (time, lat, lon)
        data[:, 0, 1] = 0.0  # second cell permanently dry
        precip = xr.DataArray(data, dims=["time", "lat", "lon"])
        result = analyzer.detect_droughts(precip, min_duration=60)
        assert result["events_detected"] >= 1
        assert any(e["duration_days"] >= 60 for e in result["events"])


class TestFloodDetection:
    def test_detect_flood_peak(self, analyzer):
        # Need enough variation so 200 is clearly above 95th percentile
        np.random.seed(42)
        base_flow = np.random.uniform(30, 80, 90).tolist()
        flood_flow = [200.0] * 5
        values = np.array(base_flow[:45] + flood_flow + base_flow[45:])
        flow = xr.DataArray(values, dims=["time"])
        result = analyzer.detect_floods(flow)
        assert result["events_detected"] >= 1

    def test_flood_peak_value(self, analyzer):
        np.random.seed(42)
        base_flow = np.random.uniform(30, 80, 90).tolist()
        flood_flow = [200.0] * 5
        values = np.array(base_flow[:45] + flood_flow + base_flow[45:])
        flow = xr.DataArray(values, dims=["time"])
        result = analyzer.detect_floods(flow)
        if result["events"]:
            assert result["max_peak"] == pytest.approx(200.0)


class TestReturnPeriod:
    def test_empirical_return_period(self, analyzer):
        np.random.seed(42)
        data = xr.DataArray(np.random.normal(100, 20, 1000), dims=["time"])
        result = analyzer.calculate_return_period(data, value=150, method="empirical")
        assert "return_period_years" in result
        assert result["return_period_years"] > 0

    def test_gumbel_return_period(self, analyzer):
        np.random.seed(42)
        data = xr.DataArray(np.random.normal(100, 20, 1000), dims=["time"])
        result = analyzer.calculate_return_period(data, value=150, method="gumbel")
        assert "return_period_years" in result
        assert result["return_period_years"] is not None

    def test_severity_extreme_value(self, analyzer):
        np.random.seed(42)
        data = xr.DataArray(np.random.normal(100, 20, 1000), dims=["time"])
        result = analyzer.calculate_return_period(data, value=200, method="gev")
        assert result["severity"] in ["severe", "extreme", "catastrophic"]


class TestCompoundEvents:
    def test_detect_compound_hot_dry(self, analyzer):
        temp = xr.DataArray([20, 35, 36, 35, 20, 20], dims=["time"])
        precip = xr.DataArray([10, 0, 0.5, 0.2, 10, 5], dims=["time"])
        result = analyzer.detect_compound_events(temp, precip)
        assert "compound_type" in result
        assert "compound_days" in result
        assert "correlation" in result

    def test_compound_frequency(self, analyzer):
        # Need continuous variation so hot days are above 90th pctl
        np.random.seed(42)
        temps = np.concatenate([np.random.normal(38, 1, 20), np.random.normal(15, 2, 80)])
        precips = np.concatenate([np.random.uniform(0, 0.5, 20), np.random.uniform(5, 20, 80)])
        temp = xr.DataArray(temps, dims=["time"])
        precip = xr.DataArray(precips, dims=["time"])
        result = analyzer.detect_compound_events(temp, precip)
        assert result["compound_frequency"] > 0


class TestClimateIndices:
    def test_temperature_indices(self, analyzer):
        temp = xr.DataArray(np.random.uniform(-5, 35, 365), dims=["time"])
        result = analyzer.calculate_climate_indices(temp)
        assert "TXx" in result["indices"]
        assert "TNn" in result["indices"]
        assert "SU25" in result["indices"]
        assert "FD0" in result["indices"]

    def test_precipitation_indices(self, analyzer):
        temp = xr.DataArray(np.random.uniform(10, 30, 365), dims=["time"])
        precip = xr.DataArray(np.random.exponential(5, 365), dims=["time"])
        result = analyzer.calculate_climate_indices(temp, precip)
        assert "PRCPTOT" in result["indices"]
        assert "RX1day" in result["indices"]
        assert "CDD" in result["indices"]
        assert "CWD" in result["indices"]


class TestEventRegistry:
    def test_register_and_retrieve(self, analyzer):
        event = ExtremeEvent(
            event_id="HW_2024_001",
            event_type=ExtremeEventType.HEATWAVE,
            start_date="2024-07-15",
            end_date="2024-07-20",
            duration_days=5,
            peak_value=42.5,
            severity=Severity.SEVERE,
        )
        result = analyzer.register_event(event)
        assert result == "HW_2024_001"

    def test_event_statistics(self, analyzer):
        events = [
            ExtremeEvent("HW1", ExtremeEventType.HEATWAVE, "2024-06", "2024-06", 5, 40, Severity.MODERATE),
            ExtremeEvent("HW2", ExtremeEventType.HEATWAVE, "2024-07", "2024-07", 7, 42, Severity.SEVERE),
            ExtremeEvent("DR1", ExtremeEventType.DROUGHT, "2024-08", "2024-09", 30, 0.5, Severity.SEVERE),
        ]
        for event in events:
            analyzer.register_event(event)
        stats = analyzer.get_event_statistics()
        assert stats["total_events"] == 3
        assert "heatwave" in stats["by_type"]


class TestEnums:
    def test_event_types_exist(self):
        assert ExtremeEventType.HEATWAVE is not None
        assert ExtremeEventType.DROUGHT is not None
        assert ExtremeEventType.FLOOD is not None
        assert ExtremeEventType.COMPOUND is not None

    def test_severity_levels_exist(self):
        assert Severity.MINOR is not None
        assert Severity.MODERATE is not None
        assert Severity.SEVERE is not None
        assert Severity.EXTREME is not None
        assert Severity.CATASTROPHIC is not None

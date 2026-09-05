"""Tests for climate classification module."""

import numpy as np
import pytest

from geo_infer_climate.core.classification import ClimateClassifier


@pytest.fixture
def classifier():
    return ClimateClassifier()


class TestKoppenGeiger:
    def test_tropical_rainforest(self, classifier):
        temps = np.full(12, 26.0)
        precip = np.full(12, 200.0)
        result = classifier.koppen_geiger_classify(temps, precip)
        assert result["main_group"] == "A"
        assert result["code"] == "Af"

    def test_hot_desert(self, classifier):
        temps = np.array([15, 17, 22, 27, 32, 37, 40, 39, 35, 28, 21, 16], dtype=float)
        precip = np.array([5, 3, 2, 1, 0, 0, 0, 0, 1, 2, 3, 4], dtype=float)
        result = classifier.koppen_geiger_classify(temps, precip)
        assert result["main_group"] == "B"
        assert "desert" in result["description"].lower() or result["code"].startswith("BW")

    def test_humid_subtropical(self, classifier):
        temps = np.array([2, 4, 10, 16, 21, 26, 29, 28, 23, 17, 10, 4], dtype=float)
        precip = np.array([80, 70, 90, 100, 110, 120, 130, 120, 100, 90, 80, 70], dtype=float)
        result = classifier.koppen_geiger_classify(temps, precip)
        assert result["main_group"] in ("C", "D")

    def test_subarctic(self, classifier):
        temps = np.array([-30, -25, -15, -5, 5, 12, 16, 14, 5, -5, -18, -28], dtype=float)
        precip = np.full(12, 30.0)
        result = classifier.koppen_geiger_classify(temps, precip)
        assert result["main_group"] == "D"

    def test_tundra(self, classifier):
        temps = np.array([-25, -22, -18, -10, -2, 3, 7, 5, 0, -8, -16, -22], dtype=float)
        precip = np.full(12, 20.0)
        result = classifier.koppen_geiger_classify(temps, precip)
        assert result["main_group"] == "E"
        assert result["code"] == "ET"

    def test_ice_cap(self, classifier):
        temps = np.array([-40, -38, -35, -30, -20, -10, -5, -8, -15, -25, -33, -38], dtype=float)
        precip = np.full(12, 10.0)
        result = classifier.koppen_geiger_classify(temps, precip)
        assert result["main_group"] == "E"
        assert result["code"] == "EF"

    def test_result_contains_all_fields(self, classifier):
        temps = np.full(12, 20.0)
        precip = np.full(12, 80.0)
        result = classifier.koppen_geiger_classify(temps, precip)
        assert "code" in result
        assert "description" in result
        assert "main_group" in result
        assert "annual_temp_c" in result
        assert "annual_precip_mm" in result

    def test_mediterranean_dry_summer(self, classifier):
        # Strongly winter-dominant precipitation (>= 70% in the cooler
        # half) keeps this profile above the low winter-wet aridity
        # threshold, so it must classify as Cs, not B.
        temps = np.array([10, 11, 14, 17, 21, 26, 30, 29, 25, 20, 15, 11], dtype=float)
        precip = np.array([95, 85, 60, 30, 15, 5, 2, 5, 20, 55, 75, 90], dtype=float)
        result = classifier.koppen_geiger_classify(temps, precip)
        assert result["main_group"] == "C"
        assert result["code"].startswith("Cs")

    def test_summer_wet_raises_aridity_threshold(self, classifier):
        # Same annual total regime, opposite seasonality: summer-dominant
        # precipitation raises the aridity threshold (+280 mm) enough to
        # make the site arid, while winter-dominant precipitation (low
        # threshold) keeps it humid.
        temps = np.array([5, 5, 8, 12, 17, 22, 28, 27, 22, 15, 9, 6], dtype=float)
        assert 11.0 <= float(np.mean(temps)) <= 25.0
        summer_heavy = np.array([10, 10, 10, 30, 60, 80, 90, 80, 60, 30, 20, 20], dtype=float)
        result_summer = classifier.koppen_geiger_classify(temps, summer_heavy)
        assert result_summer["main_group"] == "B"
        winter_heavy = np.array([120, 110, 70, 20, 10, 5, 5, 5, 10, 30, 55, 60], dtype=float)
        result_winter = classifier.koppen_geiger_classify(temps, winter_heavy)
        assert result_winter["main_group"] != "B"

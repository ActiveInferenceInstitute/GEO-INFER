"""Unit tests for the agricultural API resource classes (M1-01).

Covers FieldsResource, CropsResource and YieldResource — the CRUD/estimate
resources re-exported at both ``geo_infer_ag`` and ``geo_infer_ag.api``.
"""

import pytest

from geo_infer_ag import CropsResource, FieldsResource, YieldResource
from geo_infer_ag.api.resources import ResourceResponse


class TestFieldsResource:
    """CRUD behaviour of the fields resource."""

    def setup_method(self) -> None:
        self.resource = FieldsResource()

    def test_create_returns_record_with_id(self) -> None:
        record = self.resource.create(
            name="North Parcel",
            area_hectares=12.5,
            location={"lat": 40.0, "lon": -95.0},
            crop_type="corn",
        )

        assert record["name"] == "North Parcel"
        assert record["area_hectares"] == 12.5
        assert record["location"] == {"lat": 40.0, "lon": -95.0}
        assert record["crop_type"] == "corn"
        assert record["soil_type"] == "loam"  # default applied
        assert record["metadata"] == {}
        assert record["id"]  # generated id present
        assert self.resource.get(record["id"]) is record

    def test_create_rejects_non_positive_area(self) -> None:
        with pytest.raises(ValueError, match="area_hectares must be positive"):
            self.resource.create(
                name="Bad", area_hectares=0.0, location={"lat": 1.0, "lon": 2.0}
            )

    def test_create_rejects_missing_location_keys(self) -> None:
        with pytest.raises(ValueError, match="'lat' and 'lon'"):
            self.resource.create(name="Bad", area_hectares=1.0, location={"lat": 1.0})

    def test_get_unknown_field_returns_none(self) -> None:
        assert self.resource.get("does-not-exist") is None

    def test_list_filters_by_soil_crop_and_area(self) -> None:
        corn = self.resource.create(
            name="Corn Field",
            area_hectares=10.0,
            location={"lat": 40, "lon": -95},
            soil_type="clay",
            crop_type="corn",
        )
        small_sandy = self.resource.create(
            name="Sandy Patch",
            area_hectares=2.0,
            location={"lat": 41, "lon": -96},
            soil_type="sand",
            crop_type="corn",
        )
        self.resource.create(
            name="Big Loam",
            area_hectares=20.0,
            location={"lat": 42, "lon": -97},
            soil_type="loam",
            crop_type="wheat",
        )

        by_soil = self.resource.list(soil_type="clay")
        assert isinstance(by_soil, ResourceResponse)
        assert by_soil.resource_type == "fields"
        assert by_soil.count == 1
        assert [f["id"] for f in by_soil.data] == [corn["id"]]
        assert by_soil.filters_applied == {"soil_type": "clay"}

        by_crop_and_area = self.resource.list(crop_type="corn", min_area=5.0)
        assert [f["id"] for f in by_crop_and_area.data] == [corn["id"]]
        assert small_sandy["id"] not in [f["id"] for f in by_crop_and_area.data]
        assert by_crop_and_area.filters_applied == {
            "crop_type": "corn",
            "min_area": 5.0,
        }

        everything = self.resource.list()
        assert everything.count == 3
        assert everything.filters_applied == {}

    def test_update_merges_but_preserves_id(self) -> None:
        record = self.resource.create(
            name="Old Name", area_hectares=5.0, location={"lat": 40, "lon": -95}
        )
        updated = self.resource.update(
            record["id"], {"name": "New Name", "id": "forged"}
        )

        assert updated["name"] == "New Name"
        assert updated["id"] == record["id"]  # id cannot be rewritten
        assert self.resource.get(record["id"])["name"] == "New Name"

    def test_update_unknown_field_returns_none(self) -> None:
        assert self.resource.update("ghost", {"name": "x"}) is None

    def test_delete_round_trip(self) -> None:
        record = self.resource.create(
            name="Temp", area_hectares=1.0, location={"lat": 0, "lon": 0}
        )
        assert self.resource.delete(record["id"]) is True
        assert self.resource.get(record["id"]) is None
        # Second delete of the same id finds nothing.
        assert self.resource.delete(record["id"]) is False


class TestCropsResource:
    """Reference-data behaviour of the crops resource."""

    def setup_method(self) -> None:
        self.resource = CropsResource()

    def test_builtin_crop_lookup_is_case_insensitive(self) -> None:
        corn = self.resource.get("CORN")
        assert corn is not None
        assert corn["name"] == "corn"
        assert corn["scientific_name"] == "Zea mays"
        assert corn["base_yield_tonnes_ha"] == 9.5
        assert corn["water_requirement_mm"] == 500

    def test_unknown_crop_returns_none(self) -> None:
        assert self.resource.get("martian_rice") is None

    def test_list_filters_by_category(self) -> None:
        cereals = self.resource.list(category="cereal")
        names = {crop["name"] for crop in cereals.data}
        assert names == {"corn", "wheat", "rice"}
        assert cereals.resource_type == "crops"
        assert cereals.filters_applied == {"category": "cereal"}

        legumes = self.resource.list(category="legume")
        assert legumes.count == 1
        assert legumes.data[0]["name"] == "soybean"

    def test_register_custom_crop_overrides_lookup(self) -> None:
        registered = self.resource.register(
            "  Quinoa ", {"water_requirement_mm": 300, "category": "pseudocereal"}
        )
        assert registered["name"] == "quinoa"  # lowercased and stripped

        assert self.resource.get("quinoa")["water_requirement_mm"] == 300

        custom_only = self.resource.list(category="pseudocereal")
        assert [c["name"] for c in custom_only.data] == ["quinoa"]

    def test_register_rejects_blank_name(self) -> None:
        with pytest.raises(ValueError, match="non-empty"):
            self.resource.register("   ", {"water_requirement_mm": 100})

    def test_agronomic_accessors(self) -> None:
        assert self.resource.get_water_requirement("rice") == 1200
        assert self.resource.get_water_requirement("unknown_crop") is None

        temp_range = self.resource.get_optimal_temperature_range("wheat")
        assert temp_range == {"min": 12.0, "max": 25.0}
        assert self.resource.get_optimal_temperature_range("unknown_crop") is None


class TestYieldResource:
    """Estimation and history behaviour of the yield resource."""

    def setup_method(self) -> None:
        self.resource = YieldResource()

    def test_estimate_known_crop_hand_computed(self) -> None:
        # Corn base yield 9.5 t/ha, soil 0.8, weather 1.0 → 7.6 t/ha.
        result = self.resource.estimate(
            crop_name="corn", area_hectares=10.0, soil_quality=0.8, weather_factor=1.0
        )

        assert result["crop"] == "corn"
        assert result["yield_per_hectare"] == pytest.approx(7.6)
        assert result["total_tonnes"] == pytest.approx(76.0)
        # Deviation |0.8-1| = 0.2 → confidence 1 - 0.2*0.25 = 0.95.
        assert result["confidence"] == pytest.approx(0.95)

    def test_estimate_unknown_crop_uses_default_base(self) -> None:
        result = self.resource.estimate(crop_name="dragonfruit", area_hectares=2.0)
        assert result["yield_per_hectare"] == pytest.approx(5.0)  # default base
        assert result["total_tonnes"] == pytest.approx(10.0)
        assert result["confidence"] == pytest.approx(1.0)  # no deviation

    def test_estimate_validates_inputs(self) -> None:
        with pytest.raises(ValueError, match="area_hectares must be positive"):
            self.resource.estimate("corn", area_hectares=0.0)
        with pytest.raises(ValueError, match="soil_quality"):
            self.resource.estimate("corn", area_hectares=1.0, soil_quality=2.5)
        with pytest.raises(ValueError, match="weather_factor"):
            self.resource.estimate("corn", area_hectares=1.0, weather_factor=-0.1)

    def test_record_and_filter_history(self) -> None:
        obs = self.resource.record_observation(
            crop_name="corn",
            area_hectares=10.0,
            actual_yield_tonnes=70.0,
            season="summer",
            year=2024,
            notes="dry year",
        )
        self.resource.record_observation(
            crop_name="wheat",
            area_hectares=5.0,
            actual_yield_tonnes=17.5,
            season="summer",
            year=2024,
        )

        assert obs["yield_per_hectare"] == pytest.approx(7.0)
        assert obs["season"] == "summer"

        by_crop = self.resource.get_history(crop_name="corn")
        assert by_crop.resource_type == "yield_observations"
        assert by_crop.count == 1
        assert by_crop.data[0]["id"] == obs["id"]
        assert by_crop.filters_applied == {"crop": "corn"}

        by_year = self.resource.get_history(year=2025)
        assert by_year.count == 0
        assert by_year.filters_applied == {"year": 2025}

    def test_average_yield_none_without_records(self) -> None:
        assert self.resource.average_yield("corn") is None

        self.resource.record_observation(
            crop_name="corn",
            area_hectares=10.0,
            actual_yield_tonnes=60.0,
            season="summer",
            year=2023,
        )
        self.resource.record_observation(
            crop_name="corn",
            area_hectares=10.0,
            actual_yield_tonnes=80.0,
            season="summer",
            year=2024,
        )
        assert self.resource.average_yield("corn") == pytest.approx(7.0)
        # Wheat observations do not leak into corn's average.
        self.resource.record_observation(
            crop_name="wheat",
            area_hectares=5.0,
            actual_yield_tonnes=10.0,
            season="summer",
            year=2024,
        )
        assert self.resource.average_yield("corn") == pytest.approx(7.0)

    def test_two_level_reexport_consistency(self) -> None:
        """The classes re-exported at package root alias the api-level ones."""
        import geo_infer_ag
        import geo_infer_ag.api

        assert geo_infer_ag.FieldsResource is FieldsResource
        assert geo_infer_ag.CropsResource is CropsResource
        assert geo_infer_ag.YieldResource is YieldResource
        assert geo_infer_ag.api.FieldsResource is FieldsResource

"""
Integration tests for GEO-INFER-HEALTH API endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timezone
import json

# Import the FastAPI app and models
try:
    from geo_infer_health.api import router
    from geo_infer_health.models import (
        DiseaseReport, HealthFacility, PopulationData, EnvironmentalData, Location
    )
    from fastapi import FastAPI
except ImportError:
    pytest.skip("Cannot import geo_infer_health modules", allow_module_level=True)


@pytest.fixture
def test_app():
    """Create test FastAPI application."""
    app = FastAPI()
    app.include_router(router, prefix="/api/v1")
    return app


@pytest.fixture
def client(test_app):
    """Create test client."""
    return TestClient(test_app)


@pytest.fixture
def sample_api_data():
    """Create sample data for API testing."""
    base_time = datetime.now(timezone.utc)
    base_location = Location(latitude=34.0522, longitude=-118.2437)

    # Disease reports
    disease_reports = []
    for i in range(10):
        location = Location(
            latitude=base_location.latitude + (i % 4 - 2) * 0.01,
            longitude=base_location.longitude + (i // 4 - 1) * 0.01
        )

        report = DiseaseReport(
            report_id=f"api_report_{i}",
            disease_code="COVID-19" if i % 2 == 0 else "FLU",
            location=location,
            report_date=base_time,
            case_count=1 + (i % 3),
            source="API Test"
        )
        disease_reports.append(report)

    # Health facilities
    facilities = []
    for i in range(5):
        location = Location(
            latitude=base_location.latitude + (i % 3 - 1) * 0.02,
            longitude=base_location.longitude + (i // 3 - 1) * 0.02
        )

        facility = HealthFacility(
            facility_id=f"api_facility_{i}",
            name=f"API Test Facility {i}",
            facility_type="Hospital" if i % 2 == 0 else "Clinic",
            location=location,
            capacity=100 + i * 20,
            services_offered=["Emergency", "General Checkup"]
        )
        facilities.append(facility)

    # Environmental data
    env_data = []
    for i in range(8):
        location = Location(
            latitude=base_location.latitude + (i % 3 - 1) * 0.005,
            longitude=base_location.longitude + (i // 3 - 1) * 0.005
        )

        reading = EnvironmentalData(
            data_id=f"api_env_{i}",
            parameter_name="PM2.5" if i % 2 == 0 else "Temperature",
            value=10 + i * 2,
            unit="µg/m³" if i % 2 == 0 else "°C",
            location=location,
            timestamp=base_time
        )
        env_data.append(reading)

    # Population data
    population_data = [
        PopulationData(
            area_id="api_test_area",
            population_count=100000,
            age_distribution={"0-18": 25000, "19-65": 60000, "65+": 15000}
        )
    ]

    return {
        "disease_reports": disease_reports,
        "facilities": facilities,
        "env_data": env_data,
        "population_data": population_data,
        "base_location": base_location
    }


class TestDiseaseSurveillanceAPI:
    """Test disease surveillance API endpoints."""

    def test_submit_disease_report(self, client, sample_api_data):
        """Test submitting a disease report via API."""
        report = sample_api_data["disease_reports"][0]

        response = client.post(
            "/api/v1/surveillance/reports/",
            json=report.model_dump()
        )

        assert response.status_code == 201
        data = response.json()
        assert data["report_id"] == report.report_id
        assert data["disease_code"] == report.disease_code

    def test_get_disease_reports(self, client, sample_api_data):
        """Test retrieving disease reports via API."""
        # First submit some reports
        for report in sample_api_data["disease_reports"][:3]:
            client.post("/api/v1/surveillance/reports/", json=report.model_dump())

        # Then retrieve them
        response = client.get("/api/v1/surveillance/reports/")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 3

    def test_identify_hotspots(self, client, sample_api_data):
        """Test hotspot identification via API."""
        # Submit reports first
        for report in sample_api_data["disease_reports"]:
            client.post("/api/v1/surveillance/reports/", json=report.model_dump())

        # Submit population data
        for pop_data in sample_api_data["population_data"]:
            client.post("/api/v1/surveillance/population_data/", json=pop_data.model_dump())

        # Identify hotspots
        response = client.post(
            "/api/v1/surveillance/hotspots/identify",
            params={
                "threshold_case_count": 2,
                "scan_radius_km": 2.0
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

        # Check hotspot structure
        if data:
            hotspot = data[0]
            assert "location" in hotspot
            assert "case_count" in hotspot
            assert "radius_km" in hotspot

    def test_calculate_incidence_rate(self, client, sample_api_data):
        """Test incidence rate calculation via API."""
        # Submit reports and population data
        for report in sample_api_data["disease_reports"]:
            client.post("/api/v1/surveillance/reports/", json=report.model_dump())

        for pop_data in sample_api_data["population_data"]:
            client.post("/api/v1/surveillance/population_data/", json=pop_data.model_dump())

        base_location = sample_api_data["base_location"]

        response = client.post(
            "/api/v1/surveillance/incidence_rate/local",
            params={
                "latitude": base_location.latitude,
                "longitude": base_location.longitude,
                "radius_km": 5.0,
                "time_window_days": 7
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert "incidence_rate_per_100k" in data
        assert "total_cases_in_area" in data
        assert "estimated_population_in_area" in data

        assert data["incidence_rate_per_100k"] >= 0
        assert data["total_cases_in_area"] >= 0


class TestHealthcareAccessibilityAPI:
    """Test healthcare accessibility API endpoints."""

    def test_add_health_facility(self, client, sample_api_data):
        """Test adding a health facility via API."""
        facility = sample_api_data["facilities"][0]

        response = client.post(
            "/api/v1/accessibility/facilities/",
            json=facility.model_dump()
        )

        assert response.status_code == 201
        data = response.json()
        assert data["facility_id"] == facility.facility_id
        assert data["name"] == facility.name

    def test_get_health_facilities(self, client, sample_api_data):
        """Test retrieving health facilities via API."""
        # First add some facilities
        for facility in sample_api_data["facilities"][:3]:
            client.post("/api/v1/accessibility/facilities/", json=facility.model_dump())

        # Then retrieve them
        response = client.get("/api/v1/accessibility/facilities/")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 3

    def test_find_nearby_facilities(self, client, sample_api_data):
        """Test finding nearby facilities via API."""
        # Add facilities first
        for facility in sample_api_data["facilities"]:
            client.post("/api/v1/accessibility/facilities/", json=facility.model_dump())

        base_location = sample_api_data["base_location"]

        response = client.post(
            "/api/v1/accessibility/facilities/nearby",
            params={
                "latitude": base_location.latitude,
                "longitude": base_location.longitude,
                "radius_km": 10.0
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

        # Facilities should be sorted by distance
        if len(data) > 1:
            for i in range(len(data) - 1):
                # Each facility should have location info for distance calculation
                assert "location" in data[i]

    def test_get_nearest_facility(self, client, sample_api_data):
        """Test finding nearest facility via API."""
        # Add facilities first
        for facility in sample_api_data["facilities"]:
            client.post("/api/v1/accessibility/facilities/", json=facility.model_dump())

        base_location = sample_api_data["base_location"]

        response = client.post(
            "/api/v1/accessibility/facilities/nearest",
            params={
                "latitude": base_location.latitude,
                "longitude": base_location.longitude
            }
        )

        assert response.status_code == 200
        data = response.json()

        if data is not None:
            assert "facility" in data
            assert "distance_km" in data
            assert data["distance_km"] >= 0

    def test_facility_population_ratio(self, client, sample_api_data):
        """Test facility-to-population ratio calculation via API."""
        # Add facilities and population data
        for facility in sample_api_data["facilities"]:
            client.post("/api/v1/accessibility/facilities/", json=facility.model_dump())

        for pop_data in sample_api_data["population_data"]:
            client.post("/api/v1/accessibility/population_data/", json=pop_data.model_dump())

        response = client.get("/api/v1/accessibility/facility_population_ratio/api_test_area")

        assert response.status_code == 200
        data = response.json()

        assert "area_id" in data
        assert "facility_count" in data
        assert "population" in data
        assert "ratio_per_1000_pop" in data

        # Verify calculation
        expected_ratio = data["facility_count"] / data["population"] * 1000
        assert data["ratio_per_1000_pop"] == pytest.approx(expected_ratio)


class TestEnvironmentalHealthAPI:
    """Test environmental health API endpoints."""

    def test_submit_environmental_reading(self, client, sample_api_data):
        """Test submitting environmental data via API."""
        reading = sample_api_data["env_data"][0]

        response = client.post(
            "/api/v1/environment/readings/",
            json=reading.model_dump()
        )

        assert response.status_code == 201
        data = response.json()
        assert data["data_id"] == reading.data_id
        assert data["parameter_name"] == reading.parameter_name

    def test_get_environmental_readings(self, client, sample_api_data):
        """Test retrieving environmental readings via API."""
        # First submit some readings
        for reading in sample_api_data["env_data"][:3]:
            client.post("/api/v1/environment/readings/", json=reading.model_dump())

        # Then retrieve them
        response = client.get("/api/v1/environment/readings/")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 3

    def test_get_readings_with_parameter_filter(self, client, sample_api_data):
        """Test retrieving readings with parameter filter."""
        # Submit readings with different parameters
        for reading in sample_api_data["env_data"]:
            client.post("/api/v1/environment/readings/", json=reading.model_dump())

        # Filter by parameter
        response = client.get(
            "/api/v1/environment/readings/",
            params={"parameter_name": "PM2.5"}
        )

        assert response.status_code == 200
        data = response.json()

        # All returned readings should be PM2.5
        for reading in data:
            assert reading["parameter_name"] == "PM2.5"

    def test_get_readings_near_location(self, client, sample_api_data):
        """Test getting readings near a location via API."""
        # Submit readings first
        for reading in sample_api_data["env_data"]:
            client.post("/api/v1/environment/readings/", json=reading.model_dump())

        base_location = sample_api_data["base_location"]

        response = client.post(
            "/api/v1/environment/readings/near_location",
            params={
                "latitude": base_location.latitude,
                "longitude": base_location.longitude,
                "radius_km": 5.0,
                "parameter_name": "PM2.5"
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_calculate_average_exposure(self, client, sample_api_data):
        """Test average exposure calculation via API."""
        # Submit readings first
        for reading in sample_api_data["env_data"]:
            client.post("/api/v1/environment/readings/", json=reading.model_dump())

        base_location = sample_api_data["base_location"]
        target_locations = [
            {"latitude": base_location.latitude, "longitude": base_location.longitude},
            {"latitude": base_location.latitude + 0.01, "longitude": base_location.longitude + 0.01}
        ]

        response = client.post(
            "/api/v1/environment/exposure/average",
            json={
                "target_locations_query": target_locations,
                "radius_km": 5.0,
                "parameter_name": "PM2.5",
                "time_window_days": 7
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert len(data) == len(target_locations)

        # Check result structure
        for loc_key in data:
            assert loc_key in data
            # Value can be None or a number
            assert data[loc_key] is None or isinstance(data[loc_key], (int, float))


class TestAPIErrorHandling:
    """Test API error handling."""

    def test_invalid_disease_report(self, client):
        """Test submitting invalid disease report."""
        invalid_report = {
            "report_id": "test",
            "disease_code": "TEST",
            # Missing required location field
            "case_count": 1
        }

        response = client.post("/api/v1/surveillance/reports/", json=invalid_report)

        # Should return validation error
        assert response.status_code == 422

    def test_hotspots_no_data(self, client):
        """Test hotspot identification with no data."""
        response = client.post(
            "/api/v1/surveillance/hotspots/identify",
            params={"threshold_case_count": 1, "scan_radius_km": 1.0}
        )

        assert response.status_code == 404

    def test_facility_not_found(self, client):
        """Test accessing nonexistent facility."""
        response = client.get("/api/v1/accessibility/facility_population_ratio/nonexistent")

        assert response.status_code == 404

    def test_invalid_location_coordinates(self, client):
        """Test API with invalid coordinates."""
        # Test with latitude > 90
        response = client.post(
            "/api/v1/surveillance/incidence_rate/local",
            params={
                "latitude": 91.0,  # Invalid
                "longitude": 0.0,
                "radius_km": 1.0
            }
        )

        # Should handle gracefully or return validation error
        assert response.status_code in [200, 422]

    def test_missing_parameters(self, client):
        """Test API calls with missing required parameters."""
        # Missing latitude/longitude
        response = client.post("/api/v1/surveillance/incidence_rate/local")

        assert response.status_code == 422


class TestAPIIntegration:
    """Test integration between different API endpoints."""

    def test_cross_module_data_consistency(self, client, sample_api_data):
        """Test data consistency across different API modules."""
        # Submit data to different modules
        disease_report = sample_api_data["disease_reports"][0]
        facility = sample_api_data["facilities"][0]
        env_reading = sample_api_data["env_data"][0]

        # Submit to respective endpoints
        client.post("/api/v1/surveillance/reports/", json=disease_report.model_dump())
        client.post("/api/v1/accessibility/facilities/", json=facility.model_dump())
        client.post("/api/v1/environment/readings/", json=env_reading.model_dump())

        # Verify data was stored by retrieving it
        disease_response = client.get("/api/v1/surveillance/reports/")
        accessibility_response = client.get("/api/v1/accessibility/facilities/")
        environment_response = client.get("/api/v1/environment/readings/")

        assert disease_response.status_code == 200
        assert accessibility_response.status_code == 200
        assert environment_response.status_code == 200

        disease_data = disease_response.json()
        accessibility_data = accessibility_response.json()
        environment_data = environment_response.json()

        assert len(disease_data) >= 1
        assert len(accessibility_data) >= 1
        assert len(environment_data) >= 1

    def test_spatial_query_integration(self, client, sample_api_data):
        """Test spatial queries across different modules."""
        base_location = sample_api_data["base_location"]

        # Submit data first
        for report in sample_api_data["disease_reports"]:
            client.post("/api/v1/surveillance/reports/", json=report.model_dump())

        for facility in sample_api_data["facilities"]:
            client.post("/api/v1/accessibility/facilities/", json=facility.model_dump())

        for reading in sample_api_data["env_data"]:
            client.post("/api/v1/environment/readings/", json=reading.model_dump())

        # Test spatial queries
        params = {
            "latitude": base_location.latitude,
            "longitude": base_location.longitude,
            "radius_km": 10.0
        }

        # Disease hotspots (different endpoint structure)
        hotspots_response = client.post(
            "/api/v1/surveillance/hotspots/identify",
            params={"threshold_case_count": 1, "scan_radius_km": 5.0}
        )

        # Nearby facilities
        facilities_response = client.post("/api/v1/accessibility/facilities/nearby", params=params)

        # Nearby environmental readings
        env_params = params.copy()
        env_params["parameter_name"] = "PM2.5"
        readings_response = client.post("/api/v1/environment/readings/near_location", params=env_params)

        # All should succeed
        assert hotspots_response.status_code == 200
        assert facilities_response.status_code == 200
        assert readings_response.status_code == 200

        # Check result structures
        hotspots = hotspots_response.json()
        facilities = facilities_response.json()
        readings = readings_response.json()

        assert isinstance(hotspots, list)
        assert isinstance(facilities, list)
        assert isinstance(readings, list)


class TestAPIPerformance:
    """Test API performance characteristics."""

    def test_bulk_data_submission(self, client, sample_api_data):
        """Test performance with bulk data submission."""
        import time

        # Time bulk submission of disease reports
        reports = sample_api_data["disease_reports"]

        start_time = time.time()
        for report in reports:
            response = client.post("/api/v1/surveillance/reports/", json=report.model_dump())
            assert response.status_code == 201
        end_time = time.time()

        submission_time = end_time - start_time
        avg_time_per_report = submission_time / len(reports)

        # Should be reasonably fast (< 0.1s per report on average)
        assert avg_time_per_report < 0.1

    def test_concurrent_spatial_queries(self, client, sample_api_data):
        """Test performance with concurrent spatial queries."""
        import time

        # Submit data first
        for report in sample_api_data["disease_reports"]:
            client.post("/api/v1/surveillance/reports/", json=report.model_dump())

        for facility in sample_api_data["facilities"]:
            client.post("/api/v1/accessibility/facilities/", json=facility.model_dump())

        base_location = sample_api_data["base_location"]

        # Perform multiple spatial queries
        query_count = 10
        start_time = time.time()

        for i in range(query_count):
            # Vary the query location slightly
            lat_offset = (i % 3 - 1) * 0.005
            lon_offset = (i // 3 - 1) * 0.005

            params = {
                "latitude": base_location.latitude + lat_offset,
                "longitude": base_location.longitude + lon_offset,
                "radius_km": 5.0
            }

            # Query facilities
            facilities_response = client.post(
                "/api/v1/accessibility/facilities/nearby",
                params=params
            )
            assert facilities_response.status_code == 200

        end_time = time.time()
        total_time = end_time - start_time
        avg_time_per_query = total_time / query_count

        # Should be reasonably fast (< 0.2s per query on average)
        assert avg_time_per_query < 0.2

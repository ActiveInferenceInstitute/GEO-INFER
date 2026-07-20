"""
Unit tests for multi-source data ingestion.

This module tests the MultiSourceDataIngestion class and related
functionality for ingesting data from multiple geospatial sources.
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock
import pandas as pd
import numpy as np

from geo_infer_data.core.ingestion import (
    MultiSourceDataIngestion,
    IngestionConfig,
    SatelliteDataConnector,
    SensorDataConnector,
    CrowdsourcedDataConnector,
)
from geo_infer_data.models.schemas import QualityCheck, QualityStatus


class TestMultiSourceDataIngestion:
    """Test cases for MultiSourceDataIngestion."""

    @pytest.fixture
    def ingestion_config(self):
        """Create test ingestion configuration."""
        return IngestionConfig(
            data_sources=["satellite", "sensors", "crowdsourced"],
            format_detection="automatic",
            validation_enabled=True,
            quality_threshold=0.8,
            parallel_processing=False,  # Disable for testing
        )

    @pytest.fixture
    def ingestion_system(self, ingestion_config):
        """Create test ingestion system."""
        return MultiSourceDataIngestion(
            data_sources=ingestion_config.data_sources,
            format_detection=ingestion_config.format_detection,
            validation_enabled=ingestion_config.validation_enabled,
            quality_threshold=ingestion_config.quality_threshold,
            parallel_processing=ingestion_config.parallel_processing,
        )

    @pytest.fixture
    def mock_satellite_data(self):
        """Create mock satellite data."""
        return {
            "bbox": [-122.5, 37.7, -122.3, 37.9],
            "date_range": "2023-01-01/2023-01-31",
            "bands": ["red", "green", "blue"],
        }

    @pytest.fixture
    def mock_sensor_data(self):
        """Create mock sensor data."""
        return {
            "time_range": "2023-01-01/2023-01-31",
            "sensor_types": ["temperature", "humidity"],
        }

    @pytest.fixture
    def mock_crowdsourced_data(self):
        """Create mock crowdsourced data."""
        return {"category": "environment", "time_range": "2023-01-01/2023-01-31"}

    def test_ingestion_initialization(self, ingestion_system):
        """Test ingestion system initialization."""
        assert len(ingestion_system.connectors) == 3
        assert "satellite" in ingestion_system.connectors
        assert "sensors" in ingestion_system.connectors
        assert "crowdsourced" in ingestion_system.connectors
        assert ingestion_system.config.quality_threshold == 0.8

    def test_unsupported_data_source(self, ingestion_system, mock_satellite_data):
        """Test handling of unsupported data sources."""
        with pytest.raises(ValueError, match="not supported"):
            asyncio.run(
                ingestion_system.ingest_multi_source(
                    satellite=mock_satellite_data, unsupported_source={"data": "test"}
                )
            )

    @pytest.mark.asyncio
    async def test_single_source_ingestion(self, ingestion_system, mock_satellite_data):
        """Test ingestion from single source."""
        # Mock connector methods
        connector = ingestion_system.connectors["satellite"]
        connector.connect = AsyncMock(return_value=True)
        connector.fetch_data = AsyncMock(
            return_value={
                "imagery": np.random.rand(100, 100, 3),
                "metadata": {"satellite": "Landsat-8"},
            }
        )
        connector.validate_data = AsyncMock(
            return_value=QualityCheck(score=0.9, status=QualityStatus.PASS, issues=[])
        )

        result = await ingestion_system.ingest_multi_source(
            satellite=mock_satellite_data
        )

        assert "ingested_data" in result
        assert "satellite" in result["ingested_data"]
        assert "quality_reports" in result
        assert result["ingestion_metadata"]["sources_processed"] == 1

    @pytest.mark.asyncio
    async def test_multi_source_ingestion(
        self, ingestion_system, mock_satellite_data, mock_sensor_data
    ):
        """Test ingestion from multiple sources."""
        # Mock connectors
        for source_name in ["satellite", "sensors"]:
            connector = ingestion_system.connectors[source_name]
            connector.connect = AsyncMock(return_value=True)
            connector.fetch_data = AsyncMock(
                return_value={"data": f"mock_{source_name}_data"}
            )
            connector.validate_data = AsyncMock(
                return_value=QualityCheck(
                    score=0.9, status=QualityStatus.PASS, issues=[]
                )
            )

        result = await ingestion_system.ingest_multi_source(
            satellite=mock_satellite_data, sensors=mock_sensor_data
        )

        assert result["ingestion_metadata"]["sources_processed"] == 2
        assert "satellite" in result["ingested_data"]
        assert "sensors" in result["ingested_data"]

    def test_quality_report_generation(self, ingestion_system):
        """Test quality report generation."""
        # Mock ingested data
        ingested_data = {
            "ingested_data": {
                "satellite": {
                    "data": pd.DataFrame(
                        {
                            "temperature": np.random.normal(20, 5, 1000),
                            "humidity": np.random.normal(60, 10, 1000),
                        }
                    )
                }
            },
            "quality_reports": {
                "satellite": QualityCheck(
                    score=0.9, status=QualityStatus.PASS, issues=[]
                )
            },
        }

        report = ingestion_system.generate_quality_report(ingested_data)

        assert "overall_score" in report
        assert "source_scores" in report
        assert report["validation_enabled"] is True
        assert report["quality_threshold"] == 0.8

    def test_completeness_calculation(self, ingestion_system):
        """Test completeness calculation."""
        # Test with complete data
        complete_data = {
            "data": pd.DataFrame({"col1": range(100), "col2": range(100, 200)})
        }
        completeness = ingestion_system._calculate_completeness(complete_data)
        assert completeness >= 0.9  # Should be high for complete data

        # Test with missing data
        incomplete_data = {
            "data": pd.DataFrame(
                {"col1": [1, 2, None, 4, None], "col2": [None, 2, 3, None, 5]}
            )
        }
        completeness = ingestion_system._calculate_completeness(incomplete_data)
        assert completeness < 0.9  # Should be lower for incomplete data

    def test_accuracy_calculation(self, ingestion_system):
        """Test accuracy calculation."""
        # Test with clean data
        clean_data = {
            "data": pd.DataFrame(
                {
                    "temperature": np.random.normal(
                        20, 1, 1000
                    ),  # Low variance = high accuracy
                    "humidity": np.random.normal(60, 2, 1000),
                }
            )
        }
        accuracy = ingestion_system._calculate_accuracy(clean_data)
        assert accuracy >= 0.8  # Should be high for clean data

    def test_consistency_calculation(self, ingestion_system):
        """Test consistency calculation."""
        # Test with consistent data
        consistent_data = {
            "data": pd.DataFrame(
                {"temperature": range(100), "humidity": range(100, 200)}
            )
        }
        consistency = ingestion_system._calculate_consistency(consistent_data)
        assert consistency >= 0.8  # Should be high for consistent data


class TestSatelliteDataConnector:
    """Test cases for SatelliteDataConnector."""

    @pytest.fixture
    def connector_config(self):
        """Create test connector configuration."""
        return {"api_key": "test_key", "base_url": "https://api.test.com"}

    @pytest.fixture
    def connector(self, connector_config):
        """Create test satellite connector."""
        return SatelliteDataConnector(connector_config)

    def test_connector_initialization(self, connector, connector_config):
        """Test connector initialization."""
        assert connector.api_key == connector_config["api_key"]
        assert connector.base_url == connector_config["base_url"]

    @pytest.mark.asyncio
    async def test_connector_connection(self, connector):
        """Test connector connection."""
        # Mock successful connection
        import unittest.mock

        with unittest.mock.patch("requests.get") as mock_get:
            mock_get.return_value.status_code = 200
            connected = await connector.connect()
            assert connected is True

        # Mock failed connection
        with unittest.mock.patch("requests.get") as mock_get:
            mock_get.return_value.status_code = 500
            connected = await connector.connect()
            assert connected is False

    @pytest.mark.asyncio
    async def test_data_fetching(self, connector):
        """Test data fetching."""
        query = {
            "bbox": [-122.5, 37.7, -122.3, 37.9],
            "date_range": "2023-01-01/2023-01-31",
        }

        # Mock requests
        import unittest.mock

        with unittest.mock.patch("requests.get") as mock_get:
            mock_get.return_value.status_code = 200
            mock_get.return_value.json.return_value = {
                "imagery": "mock_imagery_data",
                "metadata": {"satellite": "Landsat-8"},
            }

            data = await connector.fetch_data(query)

            assert "imagery" in data
            assert "metadata" in data
            assert data["metadata"]["satellite"] == "Landsat-8"


class TestSensorDataConnector:
    """Test cases for SensorDataConnector."""

    @pytest.fixture
    def connector_config(self):
        """Create test connector configuration."""
        return {
            "host": "localhost",
            "port": 1883,
            "topic": "sensors/temperature",
            "data_url": "https://api.test.com/sensors",
        }

    @pytest.fixture
    def connector(self, connector_config):
        """Create test sensor connector."""
        return SensorDataConnector(connector_config)

    def test_connector_initialization(self, connector, connector_config):
        """Test connector initialization."""
        assert connector.host == connector_config["host"]
        assert connector.port == connector_config["port"]
        assert connector.topic == connector_config["topic"]

    @pytest.mark.asyncio
    async def test_sensor_connection(self, connector):
        """Test sensor connection."""
        # Mock MQTT connection - simplified test
        connected = await connector.connect()
        assert connected is True  # Mock implementation always returns True

    @pytest.mark.asyncio
    async def test_sensor_data_fetching(self, connector):
        """Test sensor data fetching."""
        query = {"time_range": "2023-01-01/2023-01-31"}

        with pytest.MonkeyPatch.context() as monkeypatch:
            response = Mock()
            response.json.return_value = {
                "measurements": [
                    {"timestamp": "2023-01-01T00:00:00Z", "temperature": 20.0}
                ],
                "sensor_ids": ["sensor_1"],
            }
            monkeypatch.setattr("requests.get", Mock(return_value=response))
            data = await connector.fetch_data(query)

        assert "measurements" in data
        assert "sensor_ids" in data
        assert isinstance(data["measurements"], pd.DataFrame)


class TestCrowdsourcedDataConnector:
    """Test cases for CrowdsourcedDataConnector."""

    @pytest.fixture
    def connector_config(self):
        """Create test connector configuration."""
        return {"api_endpoint": "https://api.crowdsourcing.com", "api_key": "test_key"}

    @pytest.fixture
    def connector(self, connector_config):
        """Create test crowdsourced connector."""
        return CrowdsourcedDataConnector(connector_config)

    def test_connector_initialization(self, connector, connector_config):
        """Test connector initialization."""
        assert connector.api_endpoint == connector_config["api_endpoint"]
        assert connector.api_key == connector_config["api_key"]

    @pytest.mark.asyncio
    async def test_crowdsourced_connection(self, connector):
        """Test crowdsourced connection."""
        # Mock successful connection
        import unittest.mock

        with unittest.mock.patch("requests.get") as mock_get:
            mock_get.return_value.status_code = 200
            connected = await connector.connect()
            assert connected is True

    @pytest.mark.asyncio
    async def test_crowdsourced_data_fetching(self, connector):
        """Test crowdsourced data fetching."""
        query = {"category": "environment"}

        with pytest.MonkeyPatch.context() as monkeypatch:
            response = Mock()
            response.json.return_value = {
                "reports": [
                    {
                        "timestamp": "2023-01-01T00:00:00Z",
                        "latitude": 37.7,
                        "longitude": -122.4,
                        "category": "environment",
                    }
                ]
            }
            monkeypatch.setattr("requests.get", Mock(return_value=response))
            data = await connector.fetch_data(query)

        assert "reports" in data
        assert isinstance(data["reports"], pd.DataFrame)
        assert "category" in data["reports"].columns

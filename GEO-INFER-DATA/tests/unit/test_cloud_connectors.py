"""
Tests for cloud storage connectors in geo_infer_data.connectors.cloud.
"""

import asyncio
import pytest

from geo_infer_data.connectors.cloud import (
    CloudConnector,
    S3Connector,
    GCSConnector,
    AzureConnector,
)


def _run(coro):
    return asyncio.get_event_loop().run_until_complete(coro)


# ---------------------------------------------------------------------------
# CloudConnector base class
# ---------------------------------------------------------------------------


class TestCloudConnectorBase:
    def test_connect_raises_not_implemented(self):
        connector = CloudConnector()
        with pytest.raises(RuntimeError):
            _run(connector.connect())

    def test_upload_file_raises_not_implemented(self):
        connector = CloudConnector()
        with pytest.raises(RuntimeError):
            _run(connector.upload_file("/local", "/remote"))

    def test_download_file_raises_not_implemented(self):
        connector = CloudConnector()
        with pytest.raises(RuntimeError):
            _run(connector.download_file("/remote", "/local"))

    def test_list_files_raises_not_implemented(self):
        connector = CloudConnector()
        with pytest.raises(RuntimeError):
            _run(connector.list_files())

    def test_delete_file_raises_not_implemented(self):
        connector = CloudConnector()
        with pytest.raises(RuntimeError):
            _run(connector.delete_file("/remote"))

    def test_disconnect_does_not_raise(self):
        connector = CloudConnector()
        _run(connector.disconnect())


# ---------------------------------------------------------------------------
# S3Connector
# ---------------------------------------------------------------------------


class TestS3Connector:
    def test_init_defaults(self):
        config = {}
        connector = S3Connector(config)
        assert connector.bucket == "geo-infer-data"
        assert connector.region == "us-east-1"

    def test_init_custom(self):
        config = {"bucket": "my-bucket", "region": "eu-west-1"}
        connector = S3Connector(config)
        assert connector.bucket == "my-bucket"
        assert connector.region == "eu-west-1"

    def test_connect(self):
        connector = S3Connector({})
        result = _run(connector.connect())
        assert result is True

    def test_upload_file(self):
        connector = S3Connector({})
        result = _run(connector.upload_file("/local/data.geojson", "data/data.geojson"))
        assert result == "data/data.geojson"

    def test_download_file(self):
        connector = S3Connector({})
        result = _run(
            connector.download_file("data/data.geojson", "/local/data.geojson")
        )
        assert result == "/local/data.geojson"

    def test_list_files(self):
        connector = S3Connector({})
        result = _run(connector.list_files("prefix/"))
        assert isinstance(result, list)
        assert len(result) == 5
        assert all("prefix/" in f for f in result)

    def test_delete_file(self):
        connector = S3Connector({})
        result = _run(connector.delete_file("data/data.geojson"))
        assert result is True

    def test_disconnect(self):
        connector = S3Connector({})
        _run(connector.disconnect())

    def test_read_byte_range_local_file(self, tmp_path):
        connector = S3Connector({})
        file_path = tmp_path / "test.geoparquet"
        file_path.write_bytes(b"PAR1_GEOPARQUET_MAGIC_BYTES_FOOTER_PAR1")
        data = _run(connector.read_byte_range(str(file_path), start_byte=0, end_byte=3))
        assert data == b"PAR1"
        data_footer = _run(connector.read_byte_range(str(file_path), start_byte=35, end_byte=38))
        assert data_footer == b"PAR1"

        with pytest.raises(ValueError):
            _run(connector.read_byte_range(str(file_path), start_byte=-1, end_byte=5))


# ---------------------------------------------------------------------------
# GCSConnector
# ---------------------------------------------------------------------------


class TestGCSConnector:
    def test_init(self):
        config = {"bucket": "gcs-bucket", "project": "my-project"}
        connector = GCSConnector(config)
        assert connector.bucket == "gcs-bucket"
        assert connector.project == "my-project"

    def test_connect(self):
        connector = GCSConnector({})
        assert _run(connector.connect()) is True

    def test_upload_file(self):
        connector = GCSConnector({})
        result = _run(connector.upload_file("/local/f.tif", "remote/f.tif"))
        assert result == "remote/f.tif"

    def test_list_files(self):
        connector = GCSConnector({})
        result = _run(connector.list_files("prefix/"))
        assert isinstance(result, list)
        assert len(result) == 3


# ---------------------------------------------------------------------------
# AzureConnector
# ---------------------------------------------------------------------------


class TestAzureConnector:
    def test_init(self):
        config = {"container": "az-container", "account_name": "myaccount"}
        connector = AzureConnector(config)
        assert connector.container == "az-container"
        assert connector.account_name == "myaccount"

    def test_connect(self):
        connector = AzureConnector({})
        assert _run(connector.connect()) is True

    def test_upload_file(self):
        connector = AzureConnector({})
        result = _run(connector.upload_file("/local/f.parquet", "remote/f.parquet"))
        assert result == "remote/f.parquet"

    def test_list_files(self):
        connector = AzureConnector({})
        result = _run(connector.list_files("prefix/"))
        assert isinstance(result, list)
        assert len(result) == 4

    def test_delete_file(self):
        connector = AzureConnector({})
        assert _run(connector.delete_file("remote/f.parquet")) is True

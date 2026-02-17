"""
Tests for DataCompressor in geo_infer_data.utils.compression.
"""

import numpy as np
import pandas as pd
import pytest

from geo_infer_data.utils.compression import DataCompressor


class TestDataCompressor:
    def test_gzip_round_trip(self):
        compressor = DataCompressor(algorithm="gzip", level=6)
        data = {"key": "value", "numbers": [1, 2, 3]}
        compressed = compressor.compress_data(data)
        assert isinstance(compressed, bytes)
        decompressed = compressor.decompress_data(compressed)
        assert decompressed == data

    def test_lzma_round_trip(self):
        compressor = DataCompressor(algorithm="lzma", level=3)
        data = {"key": "hello"}
        compressed = compressor.compress_data(data)
        decompressed = compressor.decompress_data(compressed)
        assert decompressed == data

    def test_bz2_round_trip(self):
        compressor = DataCompressor(algorithm="bz2", level=5)
        data = [1, 2, 3, 4, 5]
        compressed = compressor.compress_data(data)
        decompressed = compressor.decompress_data(compressed)
        assert decompressed == data

    def test_none_algorithm_passthrough(self):
        compressor = DataCompressor(algorithm="none")
        data = {"x": 42}
        compressed = compressor.compress_data(data)
        decompressed = compressor.decompress_data(compressed)
        assert decompressed == data

    def test_unknown_algorithm_raises(self):
        compressor = DataCompressor(algorithm="unknown")
        with pytest.raises(ValueError, match="Unknown compression algorithm"):
            compressor.compress_data({"a": 1})

    def test_is_enabled(self):
        assert DataCompressor(algorithm="gzip").is_enabled() is True
        assert DataCompressor(algorithm="none").is_enabled() is False

    def test_dataframe_compression(self):
        compressor = DataCompressor(algorithm="gzip")
        df = pd.DataFrame({"a": range(100), "b": np.random.rand(100)})
        compressed = compressor.compress_data(df)
        assert isinstance(compressed, bytes)
        assert len(compressed) > 0

    def test_numpy_array_compression(self):
        compressor = DataCompressor(algorithm="gzip")
        arr = np.random.rand(50, 50)
        compressed = compressor.compress_data(arr)
        decompressed = compressor.decompress_data(compressed)
        np.testing.assert_array_almost_equal(arr, decompressed)

    def test_compression_stats(self):
        compressor = DataCompressor(algorithm="gzip")
        compressor.compress_data({"data": list(range(1000))})
        stats = compressor.get_compression_stats()
        assert stats["compression_count"] == 1
        assert stats["total_original_bytes"] > 0
        assert stats["total_compressed_bytes"] > 0
        assert stats["compression_ratio"] >= 1.0

    def test_optimize_for_storage_dataframe(self):
        compressor = DataCompressor(algorithm="gzip")
        df = pd.DataFrame({"a": range(100)})
        recs = compressor.optimize_for_storage(df)
        assert "recommended_compression" in recs
        assert "estimated_savings" in recs
        assert "format_recommendation" in recs

    def test_optimize_for_storage_large_dataframe(self):
        compressor = DataCompressor()
        df = pd.DataFrame({"a": range(20000)})
        recs = compressor.optimize_for_storage(df)
        assert recs["estimated_savings"] > 0

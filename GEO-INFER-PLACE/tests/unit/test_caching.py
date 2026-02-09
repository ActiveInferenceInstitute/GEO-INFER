#!/usr/bin/env python3
"""
Tests for GEO-INFER-PLACE CachedAPIWrapper.

Validates caching behaviour: write/read, TTL expiry,
key generation, cache stats, and clear_cache.
"""

import json
import time
from datetime import timedelta
from pathlib import Path

import pytest

from geo_infer_place.utils.caching import CachedAPIWrapper


@pytest.fixture
def wrapper(tmp_path):
    """Create a CachedAPIWrapper with a very short TTL for testing."""
    return CachedAPIWrapper(cache_dir=tmp_path, cache_ttl=timedelta(seconds=2))


class TestCacheLifecycle:
    """Test cache write / read / expire / clear cycle."""

    def test_write_and_read(self, wrapper):
        """Written data should be readable immediately."""
        key = wrapper._cache_key("test", param="a")
        wrapper._write_cache(key, {"temperature": 18.5})
        result = wrapper._read_cache(key)
        assert result == {"temperature": 18.5}

    def test_cache_miss_returns_none(self, wrapper):
        """A key that was never written should return None."""
        result = wrapper._read_cache("nonexistent_key")
        assert result is None

    def test_ttl_expiry(self, wrapper):
        """After TTL expires the cache should return None."""
        key = wrapper._cache_key("ttl_test")
        wrapper._write_cache(key, {"value": 42})
        
        time.sleep(3)  # TTL is 2 seconds
        
        result = wrapper._read_cache(key)
        assert result is None

    def test_clear_cache(self, wrapper, tmp_path):
        """clear_cache() should remove all cached files."""
        wrapper._write_cache(wrapper._cache_key("a"), {"a": 1})
        wrapper._write_cache(wrapper._cache_key("b"), {"b": 2})
        
        count = wrapper.clear_cache()
        assert count == 2
        
        cached = list(tmp_path.glob("*.json"))
        assert len(cached) == 0

    def test_cache_stats(self, wrapper):
        """cache_stats should report correct entry count."""
        wrapper._write_cache(wrapper._cache_key("s1"), {"x": 1})
        wrapper._write_cache(wrapper._cache_key("s2"), {"y": 2})
        
        stats = wrapper.cache_stats()
        assert stats["entries"] == 2
        assert stats["total_bytes"] > 0


class TestCacheKeyGeneration:
    """Test deterministic key generation."""

    def test_same_params_same_key(self, wrapper):
        k1 = wrapper._cache_key("fetch", loc="del_norte")
        k2 = wrapper._cache_key("fetch", loc="del_norte")
        assert k1 == k2

    def test_different_params_different_key(self, wrapper):
        k1 = wrapper._cache_key("fetch", loc="del_norte")
        k2 = wrapper._cache_key("fetch", loc="humboldt")
        assert k1 != k2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

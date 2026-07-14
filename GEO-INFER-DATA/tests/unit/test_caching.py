"""
Tests for CacheManager and CacheEntry in geo_infer_data.utils.caching.
"""

import asyncio
from datetime import datetime, timedelta, timezone

from geo_infer_data.utils.caching import CacheEntry, CacheManager


# ---------------------------------------------------------------------------
# CacheEntry
# ---------------------------------------------------------------------------


class TestCacheEntry:
    def test_not_expired_without_ttl(self):
        entry = CacheEntry(key="k", data="v")
        assert entry.is_expired() is False

    def test_not_expired_within_ttl(self):
        entry = CacheEntry(key="k", data="v", ttl=3600)
        assert entry.is_expired() is False

    def test_expired_entry(self):
        entry = CacheEntry(
            key="k",
            data="v",
            ttl=1,
            created_at=datetime.now(timezone.utc) - timedelta(seconds=5),
        )
        assert entry.is_expired() is True

    def test_update_access(self):
        entry = CacheEntry(key="k", data="v")
        assert entry.access_count == 0
        entry.update_access()
        assert entry.access_count == 1

    def test_legacy_naive_timestamp_is_normalised(self):
        entry = CacheEntry(
            key="k",
            data="v",
            ttl=1,
            created_at=datetime.now() - timedelta(seconds=5),
        )
        assert entry.is_expired() is True


# ---------------------------------------------------------------------------
# CacheManager
# ---------------------------------------------------------------------------


class TestCacheManager:
    def _run(self, coro):
        return asyncio.get_event_loop().run_until_complete(coro)

    def test_set_and_get(self):
        cache = CacheManager(max_size=10)
        self._run(cache.set("key1", {"data": 42}))
        result = self._run(cache.get("key1"))
        assert result == {"data": 42}

    def test_zero_ttl_expires_immediately(self):
        cache = CacheManager(max_size=10, default_ttl=3600)
        self._run(cache.set("key1", "value", ttl=0))
        assert self._run(cache.get("key1")) is None

    def test_persistent_keys_stay_inside_cache_directory(self, tmp_path):
        cache = CacheManager(
            max_size=10,
            enable_persistence=True,
            persistence_path=tmp_path,
        )
        self._run(cache.set("../../outside", "value"))
        files = list(tmp_path.glob("*.pkl"))
        assert len(files) == 1
        assert files[0].parent == tmp_path

    def test_invalid_max_size_is_rejected(self):
        try:
            CacheManager(max_size=0)
        except ValueError as exc:
            assert "max_size" in str(exc)
        else:
            raise AssertionError("CacheManager accepted max_size=0")

    def test_get_missing_key_returns_none(self):
        cache = CacheManager(max_size=10)
        result = self._run(cache.get("nonexistent"))
        assert result is None

    def test_delete_key(self):
        cache = CacheManager(max_size=10)
        self._run(cache.set("key1", "value"))
        deleted = self._run(cache.delete("key1"))
        assert deleted is True
        assert self._run(cache.get("key1")) is None

    def test_delete_nonexistent_returns_false(self):
        cache = CacheManager(max_size=10)
        assert self._run(cache.delete("missing")) is False

    def test_clear(self):
        cache = CacheManager(max_size=10)
        self._run(cache.set("a", 1))
        self._run(cache.set("b", 2))
        self._run(cache.clear())
        assert self._run(cache.get("a")) is None
        assert self._run(cache.get("b")) is None

    def test_expired_entry_returns_none(self):
        cache = CacheManager(max_size=10, default_ttl=1)
        self._run(cache.set("k", "v", ttl=1))
        # Manually expire
        cache.cache["k"].created_at = datetime.now(timezone.utc) - timedelta(seconds=10)
        result = self._run(cache.get("k"))
        assert result is None

    def test_lru_eviction(self):
        cache = CacheManager(max_size=3)
        self._run(cache.set("a", 1))
        self._run(cache.set("b", 2))
        self._run(cache.set("c", 3))
        # Cache is full, adding one more should evict the oldest
        self._run(cache.set("d", 4))
        # At least one early key should be evicted
        remaining = sum(
            1 for k in ["a", "b", "c", "d"] if self._run(cache.get(k)) is not None
        )
        assert remaining <= 3

    def test_stats(self):
        cache = CacheManager(max_size=10)
        self._run(cache.set("k", "v"))
        self._run(cache.get("k"))
        self._run(cache.get("missing"))
        stats = cache.get_stats()
        assert stats["total_hits"] == 1
        assert stats["total_misses"] == 1
        assert stats["total_sets"] == 1
        assert stats["hit_rate"] == 0.5

    def test_generate_cache_key(self):
        cache = CacheManager()
        key = cache.generate_cache_key(
            spatial_bounds=[-122.0, 37.0, -121.0, 38.0],
            temporal_range=(datetime(2023, 1, 1), datetime(2023, 6, 1)),
        )
        assert "spatial_" in key
        assert "temporal_" in key

    def test_generate_cache_key_hashing_for_long_keys(self):
        cache = CacheManager()
        key = cache.generate_cache_key(
            spatial_bounds=[-122.0, 37.0, -121.0, 38.0],
            temporal_range=(datetime(2023, 1, 1), datetime(2023, 6, 1)),
            query_params={f"param_{i}": f"value_{i}" for i in range(20)},
        )
        # Long keys get hashed
        assert key.startswith("hash_") or len(key) <= 200

    def test_optimize_cache(self):
        cache = CacheManager(max_size=5, default_ttl=1)
        for i in range(5):
            self._run(cache.set(f"k{i}", i))
        # Expire all
        for entry in cache.cache.values():
            entry.created_at = datetime.now(timezone.utc) - timedelta(seconds=10)
        cache.optimize_cache()
        assert len(cache.cache) == 0

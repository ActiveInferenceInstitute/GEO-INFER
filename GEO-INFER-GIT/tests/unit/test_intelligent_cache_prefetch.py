"""Behavior tests for IntelligentCache relatedness and prefetching.

Relatedness previously returned nothing, which made the prefetch queue
permanently empty; these tests fail if it regresses to that.
"""

import pytest

from geo_infer_git.utils.advanced_cache import IntelligentCache


@pytest.fixture(name="cache")
def _cache():
    return IntelligentCache()


class TestKeyNamespace:
    @pytest.mark.parametrize(
        "key,expected",
        [
            ("repo:acme/x:commits", "repo:acme/x"),
            ("repo/acme/commits", "repo/acme"),
            ("flat", ""),
            (":leading", ""),
        ],
    )
    def test_namespace_extraction(self, cache, key, expected):
        """The namespace is everything before the final separator."""
        assert cache._key_namespace(key) == expected


class TestFindRelatedKeys:
    def test_namespace_siblings_are_related(self, cache):
        """Facets of one entity are proposed together."""
        cache.access_patterns = {
            "repo:acme/x:commits": [100.0],
            "repo:acme/x:branches": [500.0],
            "repo:other/y:commits": [90000.0],
        }
        related = cache._find_related_keys("repo:acme/x:commits")
        assert "repo:acme/x:branches" in related
        assert "repo:other/y:commits" not in related

    def test_temporally_co_accessed_keys_are_related(self, cache):
        """Keys used together are related even across namespaces."""
        cache.access_patterns = {
            "alpha": [100.0, 200.0],
            "beta": [100.5, 200.5],
            "gamma": [9000.0],
        }
        related = cache._find_related_keys("alpha")
        assert related == ["beta"]

    def test_the_key_itself_is_never_returned(self, cache):
        """A key is not its own prefetch candidate."""
        cache.access_patterns = {"alpha": [100.0, 100.1, 100.2]}
        assert cache._find_related_keys("alpha") == []

    def test_unrelated_keys_are_excluded(self, cache):
        """Distant accesses in a different namespace score below threshold."""
        cache.access_patterns = {"alpha": [100.0], "zeta": [90000.0]}
        assert cache._find_related_keys("alpha") == []

    def test_results_are_ranked_by_strength(self, cache):
        """The most strongly co-accessed candidate comes first."""
        cache.access_patterns = {
            "alpha": [100.0, 200.0, 300.0],
            "strong": [100.1, 200.1, 300.1],
            "weak": [100.2, 200.2],
        }
        related = cache._find_related_keys("alpha")
        assert related.index("strong") < related.index("weak")

    def test_result_count_is_bounded(self, cache):
        """A prefetch pass never proposes an unbounded number of keys."""
        cache.access_patterns = {"ns:key": [100.0]}
        for index in range(50):
            cache.access_patterns[f"ns:sibling{index}"] = [100.0]
        assert len(cache._find_related_keys("ns:key")) == cache.MAX_RELATED_KEYS

    def test_unknown_key_yields_no_relations(self, cache):
        """A key with no recorded accesses and no namespace has no relations."""
        assert cache._find_related_keys("never-seen") == []


class TestTriggerPrefetch:
    def test_absent_related_keys_are_queued(self, cache):
        """A related key not resident in the cache is queued for warming."""
        cache.access_patterns = {
            "repo:acme/x:commits": [100.0],
            "repo:acme/x:branches": [100.1],
        }
        cache._trigger_prefetch("repo:acme/x:commits")
        assert cache.prefetch_queue.get_nowait() == "repo:acme/x:branches"

    def test_resident_related_keys_are_not_queued(self, cache):
        """Keys already cached need no prefetch."""
        cache.access_patterns = {
            "repo:acme/x:commits": [100.0],
            "repo:acme/x:branches": [100.1],
        }
        cache.cache.put("repo:acme/x:branches", "already here")
        cache._trigger_prefetch("repo:acme/x:commits")
        assert cache.prefetch_queue.empty()

    def test_a_cached_none_is_treated_as_absent(self, cache):
        """A stored None is indistinguishable from a miss at the cache layer.

        Documents the known MultiLevelCache.get limitation: such a key is
        re-queued rather than recognised as resident.
        """
        cache.access_patterns = {
            "repo:acme/x:commits": [100.0],
            "repo:acme/x:branches": [100.1],
        }
        cache.cache.put("repo:acme/x:branches", None)
        cache._trigger_prefetch("repo:acme/x:commits")
        assert cache.prefetch_queue.get_nowait() == "repo:acme/x:branches"

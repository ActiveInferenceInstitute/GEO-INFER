"""
Focused unit tests for the CacheManager envelope-rejection path.

Cached payloads are authenticated GISP1 envelopes produced by
``geo_infer_ops.core.secure_serialization``. These tests exercise the trust
boundary through the public ``get``/``set`` surface: a correctly signed
envelope round-trips; an unsigned or tampered Redis value is rejected before
deserialization, evicted, and either reported as a miss or raised depending
on ``raise_on_untrusted``.
"""

import json
import pickle
from unittest.mock import Mock, patch, MagicMock

import pytest

from geo_infer_ops.core.cache import CacheManager, CacheSerializer
from geo_infer_ops.core.secure_serialization import (
    CONTEXT_REDIS_CACHE,
    PayloadSecurityError,
    dumps_signed_text,
)

SIGNING_KEY = b"ops-cache-unit-envelope-signing-key"


def signed_json(value):
    """Return the text envelope a signed cache write would produce."""
    return dumps_signed_text(
        value, context=CONTEXT_REDIS_CACHE, key=SIGNING_KEY, serializer="json"
    )


def tamper(envelope: str) -> str:
    """Flip one character so the envelope fails signature verification."""
    idx = len(envelope) // 2
    replacement = "A" if envelope[idx] != "A" else "B"
    return envelope[:idx] + replacement + envelope[idx + 1 :]


@pytest.fixture
def mock_config():
    config = Mock()
    config.cache.redis.host = "localhost"
    config.cache.redis.port = 6379
    config.cache.redis.db = 0
    config.cache.redis.password = None
    return config


@pytest.fixture
def mock_redis():
    with patch("redis.Redis") as mock:
        redis_client = Mock()
        pipeline = MagicMock()
        pipeline.__enter__.return_value = pipeline
        pipeline.__exit__.return_value = None
        redis_client.pipeline.return_value = pipeline
        mock.return_value = redis_client
        yield redis_client


def make_manager(mock_config, mock_redis, **kwargs):
    with patch("geo_infer_ops.core.cache.get_config", return_value=mock_config):
        return CacheManager(signing_key=SIGNING_KEY, **kwargs)


@pytest.fixture
def cache_manager(mock_config, mock_redis):
    return make_manager(mock_config, mock_redis)


class TestCacheEnvelopeRejection:
    def test_signed_envelope_roundtrip(self, cache_manager, mock_redis):
        """A signed write reads back the original value."""
        assert cache_manager._serialize({"v": 42}).startswith("gisp1:")
        mock_redis.get.return_value = signed_json({"v": 42})
        assert cache_manager.get("k") == {"v": 42}

    def test_tampered_payload_rejected_and_evicted(
        self, cache_manager, mock_redis
    ):
        """A flipped-character envelope fails verification: miss + eviction."""
        mock_redis.get.return_value = tamper(signed_json({"v": 1}))

        assert cache_manager.get("k", default="MISS") == "MISS"
        mock_redis.delete.assert_called_once_with("geo_infer:k")

    def test_unsigned_payload_rejected_and_evicted(
        self, cache_manager, mock_redis
    ):
        """A plain JSON object is never deserialized, evicted instead."""
        mock_redis.get.return_value = json.dumps({"injected": True})
        assert cache_manager.get("k", default="MISS") == "MISS"
        mock_redis.delete.assert_called_once_with("geo_infer:k")

    def test_strict_mode_raises_payload_security_error(
        self, mock_config, mock_redis
    ):
        """raise_on_untrusted propagates PayloadSecurityError to the caller."""
        mock_redis.get.return_value = json.dumps({"injected": True})
        manager = make_manager(mock_config, mock_redis, raise_on_untrusted=True)
        with pytest.raises(PayloadSecurityError):
            manager.get("k")

    def test_wrong_signing_key_rejected(self, mock_config, mock_redis):
        """An envelope signed under a different key is untrusted here."""
        mock_redis.get.return_value = dumps_signed_text(
            {"v": 1},
            context=CONTEXT_REDIS_CACHE,
            key=b"another-master-key-entirely!!",
            serializer="json",
        )
        manager = make_manager(mock_config, mock_redis)
        assert manager.get("k", default="MISS") == "MISS"
        mock_redis.delete.assert_called_once_with("geo_infer:k")

    def test_pickle_mode_rejects_unsigned_bytes(self, cache_manager, mock_redis):
        """Pickle mode applies the same trust boundary to binary values."""
        cache_manager.serializer = CacheSerializer.PICKLE
        mock_redis.get.return_value = pickle.dumps({"injected": True})
        assert cache_manager.get("k", default="MISS") == "MISS"
        mock_redis.delete.assert_called_once_with("geo_infer:k")

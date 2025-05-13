"""
Tests for cache management module.
"""
import json
import pickle
from unittest.mock import Mock, patch, MagicMock, call
import pytest
from redis.exceptions import RedisError

from geo_infer_ops.core.cache import CacheManager, CacheSerializer

@pytest.fixture
def mock_config():
    """Create mock configuration."""
    config = Mock()
    config.cache.redis.host = "localhost"
    config.cache.redis.port = 6379
    config.cache.redis.db = 0
    config.cache.redis.password = None
    return config

@pytest.fixture
def mock_redis():
    """Create mock Redis client."""
    with patch("redis.Redis") as mock:
        redis_client = Mock()
        mock.return_value = redis_client
        yield redis_client

@pytest.fixture
def mock_pipeline():
    """Create mock Redis pipeline."""
    pipeline = MagicMock()
    pipeline.execute.return_value = [True, True]
    pipeline.__enter__.return_value = pipeline
    pipeline.__exit__.return_value = None
    return pipeline

@pytest.fixture
def cache_manager(mock_config, mock_redis):
    """Create cache manager instance."""
    with patch("geo_infer_ops.core.cache.get_config", return_value=mock_config):
        manager = CacheManager()
        yield manager

def test_cache_connection_success(cache_manager, mock_redis):
    """Test successful cache connection."""
    mock_redis.ping.return_value = True
    assert cache_manager.redis == mock_redis

def test_cache_connection_failure(mock_config, mock_redis):
    """Test failed cache connection."""
    mock_redis.ping.side_effect = RedisError("Connection failed")
    
    with patch("geo_infer_ops.core.cache.get_config", return_value=mock_config):
        with pytest.raises(RedisError):
            CacheManager()

def test_cache_serialization_json(cache_manager):
    """Test JSON serialization."""
    data = {"key": "value"}
    serialized = cache_manager._serialize(data)
    assert isinstance(serialized, str)
    assert json.loads(serialized) == data

def test_cache_serialization_pickle(cache_manager):
    """Test pickle serialization."""
    cache_manager.serializer = CacheSerializer.PICKLE
    data = {"key": "value"}
    serialized = cache_manager._serialize(data)
    assert isinstance(serialized, bytes)
    assert pickle.loads(serialized) == data

def test_cache_deserialization_json(cache_manager):
    """Test JSON deserialization."""
    data = {"key": "value"}
    serialized = json.dumps(data)
    deserialized = cache_manager._deserialize(serialized)
    assert deserialized == data

def test_cache_deserialization_pickle(cache_manager):
    """Test pickle deserialization."""
    cache_manager.serializer = CacheSerializer.PICKLE
    data = {"key": "value"}
    serialized = pickle.dumps(data)
    deserialized = cache_manager._deserialize(serialized)
    assert deserialized == data

def test_cache_deserialization_none(cache_manager):
    """Test deserialization of None value."""
    assert cache_manager._deserialize(None) is None

def test_cache_get_success(cache_manager, mock_redis):
    """Test successful cache get."""
    data = {"key": "value"}
    mock_redis.get.return_value = json.dumps(data)
    
    result = cache_manager.get("test_key")
    assert result == data
    mock_redis.get.assert_called_once_with("geo_infer:test_key")

def test_cache_get_missing(cache_manager, mock_redis):
    """Test cache get with missing key."""
    mock_redis.get.return_value = None
    
    result = cache_manager.get("test_key")
    assert result is None

def test_cache_get_default(cache_manager, mock_redis):
    """Test cache get with default value."""
    mock_redis.get.return_value = None
    
    result = cache_manager.get("test_key", default="default")
    assert result == "default"

def test_cache_set_success(cache_manager, mock_redis):
    """Test successful cache set."""
    data = {"key": "value"}
    mock_redis.set.return_value = True
    
    result = cache_manager.set("test_key", data)
    assert result is True
    mock_redis.set.assert_called_once()

def test_cache_set_with_expire(cache_manager, mock_redis):
    """Test cache set with expiration."""
    data = {"key": "value"}
    mock_redis.setex.return_value = True
    
    result = cache_manager.set("test_key", data, expire=60)
    assert result is True
    mock_redis.setex.assert_called_once()

def test_cache_set_with_nx(cache_manager, mock_redis):
    """Test cache set with NX flag."""
    data = {"key": "value"}
    mock_redis.setnx.return_value = True
    
    result = cache_manager.set("test_key", data, nx=True)
    assert result is True
    mock_redis.setnx.assert_called_once()

def test_cache_set_with_xx(cache_manager, mock_redis):
    """Test cache set with XX flag."""
    data = {"key": "value"}
    mock_redis.set.return_value = True
    
    result = cache_manager.set("test_key", data, xx=True)
    assert result is True
    mock_redis.set.assert_called_once_with("geo_infer:test_key", json.dumps(data), xx=True)

def test_cache_delete_success(cache_manager, mock_redis):
    """Test successful cache delete."""
    mock_redis.delete.return_value = 1
    
    result = cache_manager.delete("test_key")
    assert result is True
    mock_redis.delete.assert_called_once_with("geo_infer:test_key")

def test_cache_delete_missing(cache_manager, mock_redis):
    """Test cache delete with missing key."""
    mock_redis.delete.return_value = 0
    
    result = cache_manager.delete("test_key")
    assert result is False

def test_cache_exists_true(cache_manager, mock_redis):
    """Test cache exists with existing key."""
    mock_redis.exists.return_value = 1
    
    result = cache_manager.exists("test_key")
    assert result is True
    mock_redis.exists.assert_called_once_with("geo_infer:test_key")

def test_cache_exists_false(cache_manager, mock_redis):
    """Test cache exists with missing key."""
    mock_redis.exists.return_value = 0
    
    result = cache_manager.exists("test_key")
    assert result is False

def test_cache_expire_success(cache_manager, mock_redis):
    """Test successful cache expire."""
    mock_redis.expire.return_value = 1
    
    result = cache_manager.expire("test_key", 60)
    assert result is True
    mock_redis.expire.assert_called_once_with("geo_infer:test_key", 60)

def test_cache_expire_failure(cache_manager, mock_redis):
    """Test failed cache expire."""
    mock_redis.expire.return_value = 0
    
    result = cache_manager.expire("test_key", 60)
    assert result is False

def test_cache_ttl_exists(cache_manager, mock_redis):
    """Test cache TTL with existing key."""
    mock_redis.ttl.return_value = 30
    
    result = cache_manager.ttl("test_key")
    assert result == 30
    mock_redis.ttl.assert_called_once_with("geo_infer:test_key")

def test_cache_ttl_missing(cache_manager, mock_redis):
    """Test cache TTL with missing key."""
    mock_redis.ttl.return_value = -2
    
    result = cache_manager.ttl("test_key")
    assert result is None

def test_cache_increment_success(cache_manager, mock_redis):
    """Test successful cache increment."""
    mock_redis.incrby.return_value = 2
    
    result = cache_manager.increment("test_key", amount=1)
    assert result == 2
    mock_redis.incrby.assert_called_once_with("geo_infer:test_key", 1)

def test_cache_decrement_success(cache_manager, mock_redis):
    """Test successful cache decrement."""
    mock_redis.decrby.return_value = 1
    
    result = cache_manager.decrement("test_key", amount=1)
    assert result == 1
    mock_redis.decrby.assert_called_once_with("geo_infer:test_key", 1)

def test_cache_get_many_success(cache_manager, mock_redis):
    """Test successful cache get_many."""
    data = {
        "key1": json.dumps({"value": 1}),
        "key2": json.dumps({"value": 2}),
        "key3": None
    }
    mock_redis.mget.return_value = list(data.values())
    
    result = cache_manager.get_many(["key1", "key2", "key3"])
    assert result == {
        "key1": {"value": 1},
        "key2": {"value": 2}
    }
    mock_redis.mget.assert_called_once()

def test_cache_get_many_with_invalid_value(cache_manager, mock_redis):
    """Test get_many with invalid value."""
    data = {
        "key1": json.dumps({"value": 1}),
        "key2": "invalid_json",
        "key3": None
    }
    mock_redis.mget.return_value = list(data.values())
    
    result = cache_manager.get_many(["key1", "key2", "key3"])
    assert result == {
        "key1": {"value": 1}
    }

def test_cache_set_many_success(cache_manager, mock_redis, mock_pipeline):
    """Test successful cache set_many."""
    data = {
        "key1": {"value": 1},
        "key2": {"value": 2}
    }
    mock_redis.pipeline.return_value = mock_pipeline
    
    result = cache_manager.set_many(data)
    assert result is True
    assert mock_pipeline.set.call_count == 2
    assert mock_pipeline.execute.call_count == 1

def test_cache_set_many_with_expire(cache_manager, mock_redis, mock_pipeline):
    """Test cache set_many with expiration."""
    data = {
        "key1": {"value": 1},
        "key2": {"value": 2}
    }
    mock_redis.pipeline.return_value = mock_pipeline
    
    result = cache_manager.set_many(data, expire=60)
    assert result is True
    assert mock_pipeline.setex.call_count == 2
    assert mock_pipeline.execute.call_count == 1

def test_cache_set_many_partial_failure(cache_manager, mock_redis, mock_pipeline):
    """Test cache set_many with partial failure."""
    data = {
        "key1": {"value": 1},
        "key2": {"value": 2}
    }
    mock_pipeline.execute.return_value = [True, False]
    mock_redis.pipeline.return_value = mock_pipeline
    
    result = cache_manager.set_many(data)
    assert result is False

def test_cache_delete_many_success(cache_manager, mock_redis):
    """Test successful cache delete_many."""
    mock_redis.delete.return_value = 2
    
    result = cache_manager.delete_many(["key1", "key2"])
    assert result is True
    mock_redis.delete.assert_called_once_with("geo_infer:key1", "geo_infer:key2")

def test_cache_clear_success(cache_manager, mock_redis):
    """Test successful cache clear."""
    mock_redis.scan.side_effect = [
        ("1", ["geo_infer:key1", "geo_infer:key2"]),
        ("0", ["geo_infer:key3"])
    ]
    mock_redis.delete.return_value = True
    
    result = cache_manager.clear()
    assert result is True
    assert mock_redis.scan.call_count == 2
    assert mock_redis.delete.call_count == 2

def test_cache_clear_empty(cache_manager, mock_redis):
    """Test cache clear with no keys."""
    mock_redis.scan.return_value = ("0", [])
    
    result = cache_manager.clear()
    assert result is True
    mock_redis.scan.assert_called_once()
    mock_redis.delete.assert_not_called()

def test_cache_clear_partial_failure(cache_manager, mock_redis):
    """Test cache clear with partial failure."""
    mock_redis.scan.side_effect = [
        ("1", ["geo_infer:key1"]),
        ("0", ["geo_infer:key2"])
    ]
    mock_redis.delete.side_effect = [True, False]
    
    result = cache_manager.clear()
    assert result is False

def test_cache_get_size_success(cache_manager, mock_redis):
    """Test successful cache get_size."""
    mock_redis.scan.side_effect = [
        ("1", ["geo_infer:key1", "geo_infer:key2"]),
        ("0", ["geo_infer:key3"])
    ]
    
    result = cache_manager.get_size()
    assert result == 3
    assert mock_redis.scan.call_count == 2

def test_cache_get_size_empty(cache_manager, mock_redis):
    """Test get_size with no keys."""
    mock_redis.scan.return_value = ("0", [])
    
    result = cache_manager.get_size()
    assert result == 0
    mock_redis.scan.assert_called_once()

def test_cache_error_handling(cache_manager, mock_redis):
    """Test error handling in cache operations."""
    mock_redis.get.side_effect = RedisError("Test error")
    mock_redis.set.side_effect = RedisError("Test error")
    mock_redis.delete.side_effect = RedisError("Test error")
    mock_redis.exists.side_effect = RedisError("Test error")
    mock_redis.expire.side_effect = RedisError("Test error")
    mock_redis.ttl.side_effect = RedisError("Test error")
    mock_redis.incrby.side_effect = RedisError("Test error")
    mock_redis.decrby.side_effect = RedisError("Test error")
    mock_redis.mget.side_effect = RedisError("Test error")
    mock_redis.pipeline.side_effect = RedisError("Test error")
    mock_redis.scan.side_effect = RedisError("Test error")
    
    assert cache_manager.get("test_key") is None
    assert cache_manager.set("test_key", "value") is False
    assert cache_manager.delete("test_key") is False
    assert cache_manager.exists("test_key") is False
    assert cache_manager.expire("test_key", 60) is False
    assert cache_manager.ttl("test_key") is None
    assert cache_manager.increment("test_key") is None
    assert cache_manager.decrement("test_key") is None
    assert cache_manager.get_many(["test_key"]) == {}
    assert cache_manager.set_many({"test_key": "value"}) is False
    assert cache_manager.delete_many(["test_key"]) is False
    assert cache_manager.clear() is False
    assert cache_manager.get_size() == 0 
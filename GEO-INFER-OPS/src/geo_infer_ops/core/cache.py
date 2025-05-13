"""
Caching management for GEO-INFER-OPS.
"""
import json
import pickle
from datetime import datetime, timedelta
from typing import Optional, Any, Union, Dict, List, Tuple
from enum import Enum

import redis
from redis.exceptions import RedisError

from geo_infer_ops.core.config import get_config
from geo_infer_ops.core.logging import get_logger

logger = get_logger(__name__)

class CacheSerializer(Enum):
    """Cache serialization formats."""
    JSON = "json"
    PICKLE = "pickle"

class CacheManager:
    """Manages caching operations for GEO-INFER-OPS."""
    
    def __init__(
        self,
        serializer: CacheSerializer = CacheSerializer.JSON,
        prefix: str = "geo_infer:"
    ):
        """
        Initialize cache manager.
        
        Args:
            serializer: Serialization format to use
            prefix: Key prefix for all cache entries
        """
        self.config = get_config()
        self.serializer = serializer
        self.prefix = prefix
        self._connect()
    
    def _connect(self) -> None:
        """Connect to Redis server."""
        try:
            self.redis = redis.Redis(
                host=self.config.cache.redis.host,
                port=self.config.cache.redis.port,
                db=self.config.cache.redis.db,
                password=self.config.cache.redis.password,
                decode_responses=(self.serializer == CacheSerializer.JSON)
            )
            self.redis.ping()
            logger.info("cache_connected")
        except RedisError as e:
            logger.error("cache_connection_failed", error=str(e))
            raise
    
    def _serialize(self, value: Any) -> Union[str, bytes]:
        """
        Serialize value for storage.
        
        Args:
            value: Value to serialize
            
        Returns:
            Serialized value
        """
        try:
            if self.serializer == CacheSerializer.JSON:
                return json.dumps(value)
            else:
                return pickle.dumps(value)
        except Exception as e:
            logger.error("cache_serialization_failed", error=str(e))
            raise
    
    def _deserialize(self, value: Union[str, bytes]) -> Any:
        """
        Deserialize value from storage.
        
        Args:
            value: Value to deserialize
            
        Returns:
            Deserialized value
        """
        if value is None:
            return None
        try:
            if self.serializer == CacheSerializer.JSON:
                return json.loads(value)
            else:
                return pickle.loads(value)
        except Exception as e:
            logger.error("cache_deserialization_failed", error=str(e))
            raise
    
    def _get_key(self, key: str) -> str:
        """
        Get full cache key with prefix.
        
        Args:
            key: Cache key
            
        Returns:
            Full cache key
        """
        return f"{self.prefix}{key}"
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get value from cache.
        
        Args:
            key: Cache key
            default: Default value if key not found
            
        Returns:
            Cached value or default
        """
        try:
            full_key = self._get_key(key)
            value = self.redis.get(full_key)
            
            if value is None:
                return default
            
            return self._deserialize(value)
        except RedisError as e:
            logger.error("cache_get_failed", key=key, error=str(e))
            return default
    
    def set(
        self,
        key: str,
        value: Any,
        expire: Optional[int] = None,
        nx: bool = False,
        xx: bool = False
    ) -> bool:
        """
        Set value in cache.
        
        Args:
            key: Cache key
            value: Value to cache
            expire: Expiration time in seconds
            nx: Only set if key doesn't exist
            xx: Only set if key exists
            
        Returns:
            bool: True if successful
        """
        try:
            full_key = self._get_key(key)
            serialized = self._serialize(value)
            
            if expire is not None:
                return bool(self.redis.setex(
                    full_key,
                    expire,
                    serialized
                ))
            elif nx:
                return bool(self.redis.setnx(
                    full_key,
                    serialized
                ))
            elif xx:
                return bool(self.redis.set(
                    full_key,
                    serialized,
                    xx=True
                ))
            else:
                return bool(self.redis.set(
                    full_key,
                    serialized
                ))
        except RedisError as e:
            logger.error("cache_set_failed", key=key, error=str(e))
            return False
    
    def delete(self, key: str) -> bool:
        """
        Delete value from cache.
        
        Args:
            key: Cache key
            
        Returns:
            bool: True if successful
        """
        try:
            full_key = self._get_key(key)
            return bool(self.redis.delete(full_key))
        except RedisError as e:
            logger.error("cache_delete_failed", key=key, error=str(e))
            return False
    
    def exists(self, key: str) -> bool:
        """
        Check if key exists in cache.
        
        Args:
            key: Cache key
            
        Returns:
            bool: True if key exists
        """
        try:
            full_key = self._get_key(key)
            return bool(self.redis.exists(full_key))
        except RedisError as e:
            logger.error("cache_exists_failed", key=key, error=str(e))
            return False
    
    def expire(self, key: str, seconds: int) -> bool:
        """
        Set expiration time for key.
        
        Args:
            key: Cache key
            seconds: Expiration time in seconds
            
        Returns:
            bool: True if successful
        """
        try:
            full_key = self._get_key(key)
            return bool(self.redis.expire(full_key, seconds))
        except RedisError as e:
            logger.error("cache_expire_failed", key=key, error=str(e))
            return False
    
    def ttl(self, key: str) -> Optional[int]:
        """
        Get time to live for key.
        
        Args:
            key: Cache key
            
        Returns:
            Time to live in seconds or None if key doesn't exist
        """
        try:
            full_key = self._get_key(key)
            ttl = self.redis.ttl(full_key)
            return ttl if ttl >= 0 else None
        except RedisError as e:
            logger.error("cache_ttl_failed", key=key, error=str(e))
            return None
    
    def increment(self, key: str, amount: int = 1) -> Optional[int]:
        """
        Increment value in cache.
        
        Args:
            key: Cache key
            amount: Amount to increment by
            
        Returns:
            New value or None if operation failed
        """
        try:
            full_key = self._get_key(key)
            return self.redis.incrby(full_key, amount)
        except RedisError as e:
            logger.error("cache_increment_failed", key=key, error=str(e))
            return None
    
    def decrement(self, key: str, amount: int = 1) -> Optional[int]:
        """
        Decrement value in cache.
        
        Args:
            key: Cache key
            amount: Amount to decrement by
            
        Returns:
            New value or None if operation failed
        """
        try:
            full_key = self._get_key(key)
            return self.redis.decrby(full_key, amount)
        except RedisError as e:
            logger.error("cache_decrement_failed", key=key, error=str(e))
            return None
    
    def get_many(self, keys: List[str]) -> Dict[str, Any]:
        """
        Get multiple values from cache.
        
        Args:
            keys: List of cache keys
            
        Returns:
            Dict mapping keys to values (excluding missing keys)
        """
        try:
            full_keys = [self._get_key(key) for key in keys]
            values = self.redis.mget(full_keys)
            
            result = {}
            for key, value in zip(keys, values):
                if value is not None:
                    try:
                        result[key] = self._deserialize(value)
                    except Exception:
                        logger.warning("cache_deserialization_failed", key=key)
                        continue
            return result
        except RedisError as e:
            logger.error("cache_get_many_failed", error=str(e))
            return {}
    
    def set_many(
        self,
        mapping: Dict[str, Any],
        expire: Optional[int] = None
    ) -> bool:
        """
        Set multiple values in cache.
        
        Args:
            mapping: Dict mapping keys to values
            expire: Optional expiration time in seconds
            
        Returns:
            bool: True if all operations were successful
        """
        try:
            with self.redis.pipeline() as pipe:
                for key, value in mapping.items():
                    full_key = self._get_key(key)
                    serialized = self._serialize(value)
                    
                    if expire is not None:
                        pipe.setex(full_key, expire, serialized)
                    else:
                        pipe.set(full_key, serialized)
                
                results = pipe.execute()
                return all(bool(result) for result in results)
        except RedisError as e:
            logger.error("cache_set_many_failed", error=str(e))
            return False
    
    def delete_many(self, keys: List[str]) -> bool:
        """
        Delete multiple values from cache.
        
        Args:
            keys: List of cache keys
            
        Returns:
            bool: True if all operations were successful
        """
        try:
            full_keys = [self._get_key(key) for key in keys]
            deleted = self.redis.delete(*full_keys)
            return bool(deleted)
        except RedisError as e:
            logger.error("cache_delete_many_failed", error=str(e))
            return False
    
    def clear(self) -> bool:
        """
        Clear all cache entries with prefix.
        
        Returns:
            bool: True if successful
        """
        try:
            pattern = f"{self.prefix}*"
            cursor = "0"
            success = True
            
            while cursor != 0:
                cursor, keys = self.redis.scan(cursor=cursor, match=pattern)
                if keys:
                    if not self.redis.delete(*keys):
                        success = False
                cursor = int(cursor)
            
            return success
        except RedisError as e:
            logger.error("cache_clear_failed", error=str(e))
            return False
    
    def get_size(self) -> int:
        """
        Get number of cache entries with prefix.
        
        Returns:
            Number of entries
        """
        try:
            pattern = f"{self.prefix}*"
            cursor = "0"
            count = 0
            
            while cursor != 0:
                cursor, keys = self.redis.scan(cursor=cursor, match=pattern)
                count += len(keys)
                cursor = int(cursor)
            
            return count
        except RedisError as e:
            logger.error("cache_size_failed", error=str(e))
            return 0 
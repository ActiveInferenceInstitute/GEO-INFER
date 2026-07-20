"""
Redis storage implementation for GEO-INFER-DATA.

This module provides Redis storage for caching, session management,
and high-speed geospatial data access.
"""

import asyncio
import json
import logging
from typing import Dict, Optional, Any


logger = logging.getLogger(__name__)


class RedisStorage:
    """
    Redis storage and caching implementation.

    This class provides Redis connectivity for high-speed caching,
    session management, and geospatial data access.

    Args:
        config: Redis configuration

    Examples:
        >>> storage = RedisStorage({
        ...     'host': 'localhost',
        ...     'port': 6379,
        ...     'db': 0
        ... })
        >>>
        >>> await storage.set('key', data, ttl=3600)
        >>> data = await storage.get('key')
    """

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.host = config.get("host", "localhost")
        self.port = config.get("port", 6379)
        self.db = config.get("db", 0)

        import redis

        self.client = redis.Redis(
            host=self.host,
            port=self.port,
            db=self.db,
            password=config.get("password"),
            decode_responses=True,
        )

        logger.info(f"Initialized RedisStorage for {self.host}:{self.port}")

    async def set(self, key: str, data: Any, ttl: Optional[int] = None) -> bool:
        """
        Set data in Redis.

        Args:
            key: Redis key
            data: Data to store
            ttl: Time to live in seconds

        Returns:
            True if successful
        """
        encoded = json.dumps(data, default=str)
        result = await asyncio.to_thread(self.client.set, key, encoded, ex=ttl)
        logger.info(f"Set Redis key: {key}")
        return bool(result)

    async def get(self, key: str) -> Optional[Any]:
        """
        Get data from Redis.

        Args:
            key: Redis key

        Returns:
            Stored data or None
        """
        value = await asyncio.to_thread(self.client.get, key)
        logger.info(f"Read Redis key: {key}")
        return json.loads(value) if value is not None else None

    async def delete(self, key: str) -> bool:
        """
        Delete data from Redis.

        Args:
            key: Redis key

        Returns:
            True if successful
        """
        result = await asyncio.to_thread(self.client.delete, key)
        logger.info(f"Deleted Redis key: {key}")
        return bool(result)

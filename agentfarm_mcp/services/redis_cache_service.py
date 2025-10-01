"""Redis-based cache service for high-performance caching.

This module provides Redis caching for query results with automatic serialization.
"""

import hashlib
import json
import logging
from typing import Any, Dict, Optional

import redis
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class RedisCacheConfig(BaseModel):
    """Redis cache configuration."""

    enabled: bool = Field(True, description="Enable Redis caching")
    host: str = Field("localhost", description="Redis host")
    port: int = Field(6379, ge=1, le=65535, description="Redis port")
    db: int = Field(0, ge=0, le=15, description="Redis database number")
    password: Optional[str] = Field(None, description="Redis password")
    ttl_seconds: int = Field(300, ge=0, description="Time to live in seconds")
    key_prefix: str = Field("mcp:", description="Key prefix for namespacing")
    max_connections: int = Field(10, ge=1, le=100, description="Max connection pool size")
    socket_timeout: int = Field(5, ge=1, le=60, description="Socket timeout in seconds")
    socket_connect_timeout: int = Field(5, ge=1, le=60, description="Connection timeout in seconds")


class RedisCacheService:
    """Redis-based cache with automatic serialization and TTL.

    This cache provides:
    - Distributed caching via Redis
    - Automatic JSON serialization
    - Time-to-live (TTL) expiration
    - Connection pooling
    - Hit/miss statistics
    - Fallback to in-memory on Redis unavailable
    """

    def __init__(self, config: RedisCacheConfig) -> None:
        """Initialize Redis cache service.

        Args:
            config: Redis cache configuration
        """
        self.config = config
        self.enabled = config.enabled
        self._redis_client: Optional[redis.Redis] = None
        self._hits = 0
        self._misses = 0
        self._fallback_mode = False

        if self.enabled:
            self._initialize_redis()

    def _initialize_redis(self) -> None:
        """Initialize Redis connection with error handling."""
        try:
            self._redis_client = redis.Redis(
                host=self.config.host,
                port=self.config.port,
                db=self.config.db,
                password=self.config.password,
                socket_timeout=self.config.socket_timeout,
                socket_connect_timeout=self.config.socket_connect_timeout,
                max_connections=self.config.max_connections,
                decode_responses=True,
            )
            # Test connection
            self._redis_client.ping()
            logger.info(
                "Redis cache initialized: %s:%d (db=%d)",
                self.config.host,
                self.config.port,
                self.config.db,
            )
        except (redis.ConnectionError, redis.TimeoutError) as exc:
            logger.warning("Redis unavailable, falling back to in-memory cache: %s", exc)
            self._fallback_mode = True
            self._redis_client = None
            # Could initialize in-memory cache here as fallback

    def _make_key(self, key: str) -> str:
        """Create namespaced cache key.

        Args:
            key: Base cache key

        Returns:
            Namespaced key with prefix
        """
        return f"{self.config.key_prefix}{key}"

    def get(self, key: str) -> Optional[Any]:
        """Get value from Redis cache.

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found/expired

        Example:
            >>> value = cache_service.get("query:agents:123")
            >>> if value is not None:
            ...     print("Cache hit!")
        """
        if not self.enabled or self._fallback_mode:
            self._misses += 1
            return None

        try:
            namespaced_key = self._make_key(key)
            value = self._redis_client.get(namespaced_key)

            if value is None:
                self._misses += 1
                logger.debug("Redis cache miss: %s", key)
                return None

            # Deserialize JSON
            self._hits += 1
            logger.debug("Redis cache hit: %s", key)
            return json.loads(value)

        except (redis.ConnectionError, redis.TimeoutError, json.JSONDecodeError) as exc:
            logger.warning("Redis get error for key %s: %s", key, exc)
            self._misses += 1
            return None

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in Redis cache.

        Args:
            key: Cache key
            value: Value to cache (must be JSON-serializable)
            ttl: Optional TTL override in seconds

        Returns:
            True if successful, False otherwise

        Example:
            >>> cache_service.set("query:agents:123", {"data": [1, 2, 3]})
        """
        if not self.enabled or self._fallback_mode:
            return False

        try:
            namespaced_key = self._make_key(key)
            serialized = json.dumps(value, default=str)
            ttl_seconds = ttl if ttl is not None else self.config.ttl_seconds

            if ttl_seconds > 0:
                self._redis_client.setex(namespaced_key, ttl_seconds, serialized)
            else:
                self._redis_client.set(namespaced_key, serialized)

            logger.debug("Redis cache set: %s (ttl=%d)", key, ttl_seconds)
            return True

        except (redis.ConnectionError, redis.TimeoutError, TypeError) as exc:
            logger.warning("Redis set error for key %s: %s", key, exc)
            return False

    def delete(self, key: str) -> bool:
        """Delete key from Redis cache.

        Args:
            key: Cache key to delete

        Returns:
            True if key was deleted, False otherwise

        Example:
            >>> cache_service.delete("query:agents:123")
        """
        if not self.enabled or self._fallback_mode:
            return False

        try:
            namespaced_key = self._make_key(key)
            result = self._redis_client.delete(namespaced_key)
            logger.debug("Redis cache delete: %s (result=%d)", key, result)
            return result > 0

        except (redis.ConnectionError, redis.TimeoutError) as exc:
            logger.warning("Redis delete error for key %s: %s", key, exc)
            return False

    def clear(self) -> bool:
        """Clear all cached data with this prefix.

        Returns:
            True if successful, False otherwise

        Example:
            >>> cache_service.clear()
        """
        if not self.enabled or self._fallback_mode:
            return False

        try:
            # Use SCAN to find all keys with prefix
            pattern = f"{self.config.key_prefix}*"
            keys = []
            for key in self._redis_client.scan_iter(match=pattern, count=100):
                keys.append(key)

            if keys:
                self._redis_client.delete(*keys)
                logger.info("Redis cache cleared: %d keys", len(keys))

            self._hits = 0
            self._misses = 0
            return True

        except (redis.ConnectionError, redis.TimeoutError) as exc:
            logger.warning("Redis clear error: %s", exc)
            return False

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics.

        Returns:
            Dictionary with cache statistics

        Example:
            >>> stats = cache_service.get_stats()
            >>> print(f"Hit rate: {stats['hit_rate']:.2%}")
        """
        total_requests = self._hits + self._misses
        hit_rate = self._hits / total_requests if total_requests > 0 else 0

        stats = {
            "enabled": self.enabled,
            "fallback_mode": self._fallback_mode,
            "hits": self._hits,
            "misses": self._misses,
            "hit_rate": hit_rate,
            "ttl_seconds": self.config.ttl_seconds,
            "host": self.config.host,
            "port": self.config.port,
        }

        # Add Redis-specific stats if available
        if not self._fallback_mode and self._redis_client:
            try:
                info = self._redis_client.info("stats")
                stats["redis_total_commands"] = info.get("total_commands_processed", 0)
                stats["redis_keyspace_hits"] = info.get("keyspace_hits", 0)
                stats["redis_keyspace_misses"] = info.get("keyspace_misses", 0)
            except (redis.ConnectionError, redis.TimeoutError):
                pass

        return stats

    @staticmethod
    def generate_key(tool_name: str, params: dict) -> str:
        """Generate cache key from tool name and parameters.

        Args:
            tool_name: Name of the tool
            params: Tool parameters

        Returns:
            Cache key string

        Example:
            >>> key = RedisCacheService.generate_key("query_agents", {"limit": 100})
        """
        # Sort parameters for consistent hashing
        param_str = json.dumps(params, sort_keys=True, default=str)
        param_hash = hashlib.md5(param_str.encode()).hexdigest()
        return f"{tool_name}:{param_hash}"

    def close(self) -> None:
        """Close Redis connections.

        Example:
            >>> cache_service.close()
        """
        if self._redis_client:
            self._redis_client.close()
            logger.info("Redis cache service closed")

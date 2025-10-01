"""In-memory cache service for MCP server."""

import hashlib
import json
import time
from collections import OrderedDict
from typing import Any

from structlog import get_logger

from ..config import CacheConfig

logger = get_logger(__name__)


class CacheService:
    """In-memory cache with TTL and LRU eviction.

    This cache provides:
    - Time-to-live (TTL) expiration
    - Least Recently Used (LRU) eviction
    - Hit/miss statistics
    - Configurable size limits
    """

    def __init__(self, config: CacheConfig) -> None:
        """Initialize cache service.

        Args:
            config: Cache configuration
        """
        self.config = config
        self.enabled = config.enabled
        self._cache: OrderedDict[str, Any] = OrderedDict()
        self._timestamps: dict[str, float] = {}
        self._hits = 0
        self._misses = 0

    def get(self, key: str) -> Any | None:
        """Get value from cache if valid.

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found/expired

        Example:
            >>> value = cache_service.get("my_key")
            >>> if value is not None:
            ...     print("Cache hit!")
        """
        if not self.enabled:
            return None

        if key not in self._cache:
            self._misses += 1
            logger.debug(f"Cache miss: {key}")
            return None

        # Check TTL
        if self.config.ttl_seconds > 0:
            age = time.time() - self._timestamps[key]
            if age > self.config.ttl_seconds:
                self._evict(key)
                self._misses += 1
                logger.debug(f"Cache miss (expired): {key}")
                return None

        # Move to end (LRU)
        self._cache.move_to_end(key)
        self._hits += 1

        logger.debug("cache_hit", key=key)
        return self._cache[key]

    def set(self, key: str, value: Any) -> None:
        """Set value in cache.

        Args:
            key: Cache key
            value: Value to cache

        Example:
            >>> cache_service.set("my_key", {"data": [1, 2, 3]})
        """
        if not self.enabled:
            return

        # Evict oldest if at capacity
        if len(self._cache) >= self.config.max_size and key not in self._cache:
            oldest_key = next(iter(self._cache))
            self._evict(oldest_key)
            logger.debug("cache_eviction_lru", key=oldest_key)

        self._cache[key] = value
        self._timestamps[key] = time.time()
        self._cache.move_to_end(key)

        logger.debug("cache_set", key=key)

    def _evict(self, key: str) -> None:
        """Remove key from cache.

        Args:
            key: Cache key to evict
        """
        if key in self._cache:
            del self._cache[key]
            del self._timestamps[key]

    def clear(self) -> None:
        """Clear entire cache.

        Example:
            >>> cache_service.clear()
        """
        self._cache.clear()
        self._timestamps.clear()
        self._hits = 0
        self._misses = 0
        logger.info("cache_cleared")

    def get_stats(self) -> dict[str, Any]:
        """Get cache statistics.

        Returns:
            Dictionary with cache statistics

        Example:
            >>> stats = cache_service.get_stats()
            >>> print(f"Hit rate: {stats['hit_rate']:.2%}")
        """
        total_requests = self._hits + self._misses
        hit_rate = self._hits / total_requests if total_requests > 0 else 0

        return {
            "enabled": self.enabled,
            "size": len(self._cache),
            "max_size": self.config.max_size,
            "hits": self._hits,
            "misses": self._misses,
            "hit_rate": hit_rate,
            "ttl_seconds": self.config.ttl_seconds,
        }

    @staticmethod
    def generate_key(tool_name: str, params: dict) -> str:
        """Generate cache key from tool name and parameters.

        Args:
            tool_name: Name of the tool
            params: Tool parameters

        Returns:
            Cache key string

        Example:
            >>> key = CacheService.generate_key("query_agents", {"limit": 100})
        """
        # Sort parameters for consistent hashing
        param_str = json.dumps(params, sort_keys=True, default=str)
        param_hash = hashlib.sha256(param_str.encode()).hexdigest()
        return f"{tool_name}:{param_hash}"
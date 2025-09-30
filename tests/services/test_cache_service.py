"""Unit tests for cache service."""

import pytest
import time

from mcp.config import CacheConfig
from mcp.services.cache_service import CacheService


def test_cache_service_initialization():
    """Test cache service initializes correctly."""
    config = CacheConfig(max_size=50, ttl_seconds=120, enabled=True)
    cache = CacheService(config)

    assert cache.enabled is True
    assert cache.config.max_size == 50
    assert cache.config.ttl_seconds == 120


def test_cache_set_and_get():
    """Test basic cache set and get operations."""
    config = CacheConfig(enabled=True)
    cache = CacheService(config)

    cache.set("key1", "value1")
    assert cache.get("key1") == "value1"


def test_cache_get_nonexistent():
    """Test getting nonexistent key returns None."""
    config = CacheConfig(enabled=True)
    cache = CacheService(config)

    assert cache.get("nonexistent_key") is None


def test_cache_disabled():
    """Test that cache can be disabled."""
    config = CacheConfig(enabled=False)
    cache = CacheService(config)

    cache.set("key1", "value1")
    assert cache.get("key1") is None  # Disabled cache returns None


def test_cache_ttl_expiration():
    """Test that cache entries expire after TTL."""
    config = CacheConfig(max_size=10, ttl_seconds=1, enabled=True)
    cache = CacheService(config)

    cache.set("key1", "value1")
    assert cache.get("key1") == "value1"

    # Wait for TTL to expire
    time.sleep(1.1)
    assert cache.get("key1") is None


def test_cache_lru_eviction():
    """Test LRU eviction when cache is full."""
    config = CacheConfig(max_size=3, ttl_seconds=0, enabled=True)  # TTL=0 means no expiration
    cache = CacheService(config)

    # Fill cache to max size
    cache.set("key1", "value1")
    cache.set("key2", "value2")
    cache.set("key3", "value3")

    # Access key2 to make it recently used
    assert cache.get("key2") == "value2"

    # Add one more - should evict oldest unused (key1)
    cache.set("key4", "value4")

    assert cache.get("key1") is None  # Evicted
    assert cache.get("key2") == "value2"  # Still there (recently used)
    assert cache.get("key3") == "value3"  # Still there
    assert cache.get("key4") == "value4"  # Newly added


def test_cache_update_existing():
    """Test updating existing cache entry."""
    config = CacheConfig(enabled=True)
    cache = CacheService(config)

    cache.set("key1", "value1")
    cache.set("key1", "value2")  # Update

    assert cache.get("key1") == "value2"


def test_cache_clear():
    """Test clearing entire cache."""
    config = CacheConfig(enabled=True)
    cache = CacheService(config)

    cache.set("key1", "value1")
    cache.set("key2", "value2")
    cache.get("key1")  # Hit

    # Get stats before clear
    stats_before = cache.get_stats()
    assert stats_before["size"] == 2
    assert stats_before["hits"] == 1

    cache.clear()

    # After clear, cache should be empty and stats reset
    assert cache.get("key1") is None
    assert cache.get("key2") is None
    stats = cache.get_stats()
    assert stats["size"] == 0
    assert stats["hits"] == 0
    assert stats["misses"] == 2  # The two get() calls above after clear


def test_cache_statistics():
    """Test cache statistics tracking."""
    config = CacheConfig(enabled=True)
    cache = CacheService(config)

    cache.set("key1", "value1")
    cache.get("key1")  # Hit
    cache.get("key2")  # Miss
    cache.get("key1")  # Hit

    stats = cache.get_stats()

    assert stats["enabled"] is True
    assert stats["size"] == 1
    assert stats["hits"] == 2
    assert stats["misses"] == 1
    assert stats["hit_rate"] == 2 / 3  # 2 hits out of 3 total


def test_cache_statistics_no_requests():
    """Test statistics with no requests."""
    config = CacheConfig(enabled=True)
    cache = CacheService(config)

    stats = cache.get_stats()

    assert stats["hits"] == 0
    assert stats["misses"] == 0
    assert stats["hit_rate"] == 0


def test_cache_generate_key_consistency():
    """Test that cache key generation is consistent."""
    key1 = CacheService.generate_key("tool1", {"a": 1, "b": 2})
    key2 = CacheService.generate_key("tool1", {"b": 2, "a": 1})  # Different order
    key3 = CacheService.generate_key("tool1", {"a": 1, "b": 3})  # Different value

    # Same params in different order should produce same key
    assert key1 == key2

    # Different params should produce different key
    assert key1 != key3


def test_cache_generate_key_different_tools():
    """Test that different tools produce different keys."""
    key1 = CacheService.generate_key("tool1", {"a": 1})
    key2 = CacheService.generate_key("tool2", {"a": 1})

    assert key1 != key2


def test_cache_generate_key_complex_params():
    """Test cache key generation with complex parameters."""
    params = {
        "simulation_id": "sim_001",
        "agent_type": "system",
        "limit": 100,
        "filters": ["type1", "type2"],
        "nested": {"key": "value"},
    }

    key = CacheService.generate_key("test_tool", params)

    assert isinstance(key, str)
    assert key.startswith("test_tool:")


def test_cache_move_to_end_on_access():
    """Test that accessing a key moves it to end (LRU)."""
    config = CacheConfig(max_size=3, ttl_seconds=0, enabled=True)
    cache = CacheService(config)

    cache.set("key1", "value1")
    cache.set("key2", "value2")
    cache.set("key3", "value3")

    # Access key1 to make it recently used
    cache.get("key1")

    # Add new item - should evict key2 (oldest unused)
    cache.set("key4", "value4")

    assert cache.get("key1") == "value1"  # Still there (recently accessed)
    assert cache.get("key2") is None  # Evicted
    assert cache.get("key3") == "value3"  # Still there
    assert cache.get("key4") == "value4"  # Newly added


def test_cache_ttl_zero_means_no_expiration():
    """Test that TTL=0 means no expiration."""
    config = CacheConfig(max_size=10, ttl_seconds=0, enabled=True)
    cache = CacheService(config)

    cache.set("key1", "value1")

    # Wait a bit
    time.sleep(0.5)

    # Should still be there with TTL=0
    assert cache.get("key1") == "value1"


def test_cache_stats_with_disabled_cache():
    """Test statistics when cache is disabled."""
    config = CacheConfig(enabled=False)
    cache = CacheService(config)

    cache.set("key1", "value1")
    cache.get("key1")

    stats = cache.get_stats()

    assert stats["enabled"] is False
    assert stats["size"] == 0
    assert stats["hits"] == 0
    assert stats["misses"] == 0
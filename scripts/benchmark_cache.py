#!/usr/bin/env python3
"""Benchmark script for cache performance testing.

This script helps measure the performance impact of caching on query operations.
"""

import argparse
import time
from typing import Dict, List

from agentfarm_mcp.config import CacheConfig, DatabaseConfig, MCPConfig
from agentfarm_mcp.services.cache_service import CacheService
from agentfarm_mcp.services.database_service import DatabaseService
from agentfarm_mcp.services.redis_cache_service import RedisCacheConfig, RedisCacheService


def benchmark_query(db_service: DatabaseService, iterations: int = 100) -> Dict[str, float]:
    """Benchmark database queries without caching.

    Args:
        db_service: Database service instance
        iterations: Number of iterations to run

    Returns:
        Dictionary with timing statistics
    """
    from agentfarm_mcp.models.database_models import AgentModel

    times = []

    for i in range(iterations):
        start = time.perf_counter()

        # Execute a sample query
        def query_func(session):
            return session.query(AgentModel).limit(100).all()

        db_service.execute_query(query_func)

        elapsed = (time.perf_counter() - start) * 1000  # Convert to ms
        times.append(elapsed)

        if (i + 1) % 10 == 0:
            print(f"  Progress: {i + 1}/{iterations} queries")

    return {
        "min": min(times),
        "max": max(times),
        "avg": sum(times) / len(times),
        "total": sum(times),
    }


def benchmark_with_cache(
    db_service: DatabaseService, cache_service: CacheService, iterations: int = 100
) -> Dict[str, float]:
    """Benchmark database queries with caching.

    Args:
        db_service: Database service instance
        cache_service: Cache service instance
        iterations: Number of iterations to run

    Returns:
        Dictionary with timing statistics
    """
    from agentfarm_mcp.models.database_models import AgentModel

    times = []
    cache_key = "benchmark:agents:100"

    for i in range(iterations):
        start = time.perf_counter()

        # Try cache first
        result = cache_service.get(cache_key)

        if result is None:
            # Cache miss - query database
            def query_func(session):
                return session.query(AgentModel).limit(100).all()

            result = db_service.execute_query(query_func)
            cache_service.set(cache_key, result)

        elapsed = (time.perf_counter() - start) * 1000  # Convert to ms
        times.append(elapsed)

        if (i + 1) % 10 == 0:
            print(f"  Progress: {i + 1}/{iterations} queries")

    stats = cache_service.get_stats()

    return {
        "min": min(times),
        "max": max(times),
        "avg": sum(times) / len(times),
        "total": sum(times),
        "hit_rate": stats["hit_rate"],
    }


def print_results(no_cache: Dict[str, float], with_cache: Dict[str, float]) -> None:
    """Print benchmark results in a formatted table.

    Args:
        no_cache: Results without caching
        with_cache: Results with caching
    """
    print("\n" + "=" * 70)
    print("BENCHMARK RESULTS")
    print("=" * 70)

    print("\nWithout Cache:")
    print(f"  Min:     {no_cache['min']:.2f} ms")
    print(f"  Max:     {no_cache['max']:.2f} ms")
    print(f"  Average: {no_cache['avg']:.2f} ms")
    print(f"  Total:   {no_cache['total']:.2f} ms")

    print("\nWith Cache:")
    print(f"  Min:     {with_cache['min']:.2f} ms")
    print(f"  Max:     {with_cache['max']:.2f} ms")
    print(f"  Average: {with_cache['avg']:.2f} ms")
    print(f"  Total:   {with_cache['total']:.2f} ms")
    print(f"  Hit Rate: {with_cache['hit_rate']:.1%}")

    # Calculate improvements
    avg_improvement = ((no_cache["avg"] - with_cache["avg"]) / no_cache["avg"]) * 100
    total_improvement = ((no_cache["total"] - with_cache["total"]) / no_cache["total"]) * 100

    print("\nPerformance Improvement:")
    print(f"  Average query: {avg_improvement:.1f}% faster")
    print(f"  Total time:    {total_improvement:.1f}% reduction")

    if with_cache["avg"] > 0:
        speedup = no_cache["avg"] / with_cache["avg"]
        print(f"  Speedup:       {speedup:.1f}x")

    print("\n" + "=" * 70)


def main() -> None:
    """Main benchmark execution."""
    parser = argparse.ArgumentParser(description="Benchmark cache performance")
    parser.add_argument(
        "--db",
        default="simulation.db",
        help="Database path (default: simulation.db)",
    )
    parser.add_argument(
        "--queries",
        type=int,
        default=100,
        help="Number of queries to run (default: 100)",
    )
    parser.add_argument(
        "--cache-backend",
        choices=["memory", "redis"],
        default="memory",
        help="Cache backend to test (default: memory)",
    )
    parser.add_argument(
        "--redis-host",
        default="localhost",
        help="Redis host (default: localhost)",
    )
    parser.add_argument(
        "--redis-port",
        type=int,
        default=6379,
        help="Redis port (default: 6379)",
    )

    args = parser.parse_args()

    print(f"\n🔍 Benchmarking cache performance with {args.queries} queries...")
    print(f"   Database: {args.db}")
    print(f"   Cache backend: {args.cache_backend}")

    # Setup database
    db_config = DatabaseConfig(path=args.db, read_only=True)
    db_service = DatabaseService(db_config)

    # Test without cache
    print("\n📊 Running queries WITHOUT cache...")
    no_cache_results = benchmark_query(db_service, args.queries)

    # Setup cache
    if args.cache_backend == "memory":
        cache_config = CacheConfig(enabled=True, max_size=1000, ttl_seconds=300)
        cache_service = CacheService(cache_config)
    else:
        redis_config = RedisCacheConfig(
            enabled=True,
            host=args.redis_host,
            port=args.redis_port,
            ttl_seconds=300,
        )
        cache_service = RedisCacheService(redis_config)

    # Test with cache
    print(f"\n📊 Running queries WITH {args.cache_backend} cache...")
    with_cache_results = benchmark_with_cache(db_service, cache_service, args.queries)

    # Print results
    print_results(no_cache_results, with_cache_results)

    # Cleanup
    db_service.close()
    if hasattr(cache_service, "close"):
        cache_service.close()


if __name__ == "__main__":
    main()

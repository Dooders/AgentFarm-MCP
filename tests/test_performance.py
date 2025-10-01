"""Performance benchmark tests for the MCP server."""

import pytest
import time
from typing import Dict, Any


@pytest.mark.performance
class TestPerformanceBenchmarks:
    """Performance benchmark test suite."""

    def test_metadata_query_performance(self, server, test_simulation_id):
        """Benchmark metadata query performance (target: <10ms)."""
        tool = server.get_tool("get_simulation_info")
        
        timings = []
        for _ in range(100):
            start = time.time()
            result = tool(simulation_id=test_simulation_id)
            elapsed = (time.time() - start) * 1000  # Convert to ms
            timings.append(elapsed)
            assert result["success"], "Query should succeed"
        
        avg_time = sum(timings) / len(timings)
        p50 = sorted(timings)[49]
        p95 = sorted(timings)[94]
        p99 = sorted(timings)[98]
        
        print(f"\nMetadata Query Performance:")
        print(f"  Average: {avg_time:.2f}ms")
        print(f"  P50: {p50:.2f}ms")
        print(f"  P95: {p95:.2f}ms")
        print(f"  P99: {p99:.2f}ms")
        
        # Assertions
        assert avg_time < 10, f"Average too slow: {avg_time:.2f}ms"
        assert p95 < 20, f"P95 too slow: {p95:.2f}ms"

    def test_simple_query_performance(self, server, test_simulation_id):
        """Benchmark simple query performance (target: <70ms)."""
        tool = server.get_tool("query_agents")
        
        timings = []
        for _ in range(50):
            start = time.time()
            result = tool(simulation_id=test_simulation_id, limit=100)
            elapsed = (time.time() - start) * 1000
            timings.append(elapsed)
            assert result["success"]
        
        avg_time = sum(timings) / len(timings)
        p95 = sorted(timings)[46]  # 95th percentile of 50 samples
        
        print(f"\nSimple Query Performance:")
        print(f"  Average: {avg_time:.2f}ms")
        print(f"  P95: {p95:.2f}ms")
        
        assert avg_time < 70, f"Average too slow: {avg_time:.2f}ms"
        assert p95 < 100, f"P95 exceeds target: {p95:.2f}ms"

    def test_analysis_query_performance(self, server, test_simulation_id):
        """Benchmark analysis query performance (target: <55ms)."""
        tool = server.get_tool("analyze_population_dynamics")
        
        timings = []
        for _ in range(30):
            start = time.time()
            result = tool(simulation_id=test_simulation_id)
            elapsed = (time.time() - start) * 1000
            timings.append(elapsed)
            assert result["success"]
        
        avg_time = sum(timings) / len(timings)
        max_time = max(timings)
        
        print(f"\nAnalysis Query Performance:")
        print(f"  Average: {avg_time:.2f}ms")
        print(f"  Max: {max_time:.2f}ms")
        
        assert avg_time < 55, f"Average too slow: {avg_time:.2f}ms"
        assert max_time < 100, f"Max exceeds limit: {max_time:.2f}ms"

    def test_cache_hit_performance(self, server, test_simulation_id):
        """Benchmark cache hit performance (should be <5ms)."""
        tool = server.get_tool("query_agents")
        
        # First query to populate cache
        result = tool(simulation_id=test_simulation_id, limit=50)
        assert result["success"]
        
        # Measure cache hit performance
        timings = []
        for _ in range(100):
            start = time.time()
            result = tool(simulation_id=test_simulation_id, limit=50)
            elapsed = (time.time() - start) * 1000
            timings.append(elapsed)
            assert result["metadata"]["from_cache"], "Should be from cache"
        
        avg_time = sum(timings) / len(timings)
        max_time = max(timings)
        
        print(f"\nCache Hit Performance:")
        print(f"  Average: {avg_time:.2f}ms")
        print(f"  Max: {max_time:.2f}ms")
        
        # Cache hits should be very fast
        assert avg_time < 5, f"Cache hits too slow: {avg_time:.2f}ms"

    def test_pagination_performance(self, server, test_simulation_id):
        """Benchmark pagination with different page sizes."""
        tool = server.get_tool("query_agents")
        
        results: Dict[int, Dict[str, float]] = {}
        
        for limit in [10, 50, 100, 500, 1000]:
            timings = []
            for _ in range(20):
                start = time.time()
                result = tool(simulation_id=test_simulation_id, limit=limit)
                elapsed = (time.time() - start) * 1000
                timings.append(elapsed)
                assert result["success"]
            
            results[limit] = {
                "avg": sum(timings) / len(timings),
                "max": max(timings),
            }
        
        print(f"\nPagination Performance:")
        for limit, metrics in results.items():
            print(f"  Limit {limit:4d}: avg={metrics['avg']:6.2f}ms, max={metrics['max']:6.2f}ms")
        
        # All should be under 100ms
        for limit, metrics in results.items():
            assert metrics["avg"] < 100, f"Limit {limit} too slow: {metrics['avg']:.2f}ms"

    def test_comparison_query_performance(self, server, test_simulation_id):
        """Benchmark comparison queries (target: <100ms for 2 sims)."""
        # Get multiple simulations
        list_tool = server.get_tool("list_simulations")
        list_result = list_tool(limit=5)
        
        if list_result["success"] and len(list_result["data"]["simulations"]) >= 2:
            sim_ids = [s["simulation_id"] for s in list_result["data"]["simulations"][:2]]
            
            compare_tool = server.get_tool("compare_simulations")
            
            timings = []
            for _ in range(20):
                start = time.time()
                result = compare_tool(simulation_ids=sim_ids)
                elapsed = (time.time() - start) * 1000
                timings.append(elapsed)
                assert result["success"]
            
            avg_time = sum(timings) / len(timings)
            max_time = max(timings)
            
            print(f"\nComparison Query Performance:")
            print(f"  Average: {avg_time:.2f}ms")
            print(f"  Max: {max_time:.2f}ms")
            
            assert avg_time < 100, f"Average too slow: {avg_time:.2f}ms"

    def test_cold_start_performance(self, server, test_simulation_id):
        """Benchmark cold start (cache miss) performance."""
        # Clear cache before each measurement
        timings = []
        
        tools_to_test = [
            ("query_agents", {"simulation_id": test_simulation_id, "limit": 10}),
            ("query_simulation_steps", {"simulation_id": test_simulation_id, "limit": 10}),
            ("get_simulation_info", {"simulation_id": test_simulation_id}),
        ]
        
        for tool_name, params in tools_to_test:
            server.cache_service.clear()  # Clear cache
            
            tool = server.get_tool(tool_name)
            start = time.time()
            result = tool(**params)
            elapsed = (time.time() - start) * 1000
            
            timings.append((tool_name, elapsed))
            assert result["success"]
            assert not result["metadata"]["from_cache"], "Should be cache miss"
        
        print(f"\nCold Start Performance:")
        for tool_name, elapsed in timings:
            print(f"  {tool_name:30s}: {elapsed:6.2f}ms")
        
        # All cold starts should be reasonable
        for tool_name, elapsed in timings:
            assert elapsed < 100, f"{tool_name} cold start too slow: {elapsed:.2f}ms"

    def test_cache_efficiency(self, server, test_simulation_id):
        """Test cache efficiency with mixed queries."""
        server.cache_service.clear()
        
        tool = server.get_tool("query_agents")
        
        # Make same query 50 times
        for _ in range(50):
            tool(simulation_id=test_simulation_id, limit=100)
        
        stats = server.cache_service.get_stats()
        hit_rate = stats["hits"] / stats["total_requests"] if stats["total_requests"] > 0 else 0
        
        print(f"\nCache Efficiency:")
        print(f"  Hits: {stats['hits']}")
        print(f"  Misses: {stats['misses']}")
        print(f"  Hit Rate: {hit_rate * 100:.1f}%")
        
        # Should have high hit rate for repeated queries
        assert hit_rate > 0.9, f"Cache hit rate too low: {hit_rate * 100:.1f}%"

    def test_memory_efficiency(self, server, test_simulation_id):
        """Test memory usage with large result sets."""
        import sys
        
        tool = server.get_tool("query_agents")
        
        # Query with large result set
        result = tool(simulation_id=test_simulation_id, limit=1000)
        assert result["success"]
        
        # Check result size
        result_size = sys.getsizeof(str(result))
        print(f"\nMemory Efficiency:")
        print(f"  Result size (1000 agents): {result_size / 1024:.2f} KB")
        
        # Should be reasonable size
        assert result_size < 5_000_000, f"Result too large: {result_size} bytes"

    @pytest.mark.slow
    def test_sustained_load_performance(self, server, test_simulation_id):
        """Test performance under sustained load."""
        tool = server.get_tool("query_agents")
        
        num_requests = 1000
        timings = []
        errors = 0
        
        start_overall = time.time()
        
        for i in range(num_requests):
            start = time.time()
            try:
                result = tool(simulation_id=test_simulation_id, limit=50)
                if not result["success"]:
                    errors += 1
            except Exception:
                errors += 1
            elapsed = (time.time() - start) * 1000
            timings.append(elapsed)
        
        total_time = time.time() - start_overall
        
        avg_time = sum(timings) / len(timings)
        p50 = sorted(timings)[499]
        p95 = sorted(timings)[949]
        p99 = sorted(timings)[989]
        throughput = num_requests / total_time
        
        print(f"\nSustained Load Performance ({num_requests} requests):")
        print(f"  Total time: {total_time:.2f}s")
        print(f"  Throughput: {throughput:.1f} req/s")
        print(f"  Average: {avg_time:.2f}ms")
        print(f"  P50: {p50:.2f}ms")
        print(f"  P95: {p95:.2f}ms")
        print(f"  P99: {p99:.2f}ms")
        print(f"  Errors: {errors}")
        
        assert errors == 0, f"Had {errors} errors under load"
        assert p95 < 150, f"P95 degraded under load: {p95:.2f}ms"
        assert throughput > 20, f"Throughput too low: {throughput:.1f} req/s"

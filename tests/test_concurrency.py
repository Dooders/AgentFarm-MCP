"""Concurrency tests to validate thread safety of the MCP server."""

import pytest
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
from typing import List, Dict, Any


class TestConcurrency:
    """Test suite for concurrent request handling."""

    def test_concurrent_query_agents(self, server, test_simulation_id):
        """Test handling 100 concurrent query_agents requests."""
        tool = server.get_tool("query_agents")
        
        def query():
            return tool(simulation_id=test_simulation_id, limit=10)
        
        # Execute 100 concurrent queries
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(query) for _ in range(100)]
            results = [f.result() for f in futures]
        
        # All should succeed
        assert all(r["success"] for r in results), "Some requests failed"
        
        # All should return data
        assert all(r["data"] is not None for r in results)
        
        # Cache should help (high hit rate expected after first few)
        stats = server.cache_service.get_stats()
        if stats["total_requests"] > 0:
            hit_rate = stats["hits"] / stats["total_requests"]
            assert hit_rate > 0.5, f"Cache hit rate too low: {hit_rate}"

    def test_concurrent_different_tools(self, server, test_simulation_id):
        """Test handling concurrent requests to different tools."""
        tools = [
            ("query_agents", {"simulation_id": test_simulation_id, "limit": 10}),
            ("get_simulation_info", {"simulation_id": test_simulation_id}),
            ("query_simulation_steps", {"simulation_id": test_simulation_id, "limit": 10}),
            ("analyze_population_dynamics", {"simulation_id": test_simulation_id}),
        ]
        
        results: List[Dict[str, Any]] = []
        
        with ThreadPoolExecutor(max_workers=20) as executor:
            futures = []
            # Submit 25 requests per tool (100 total)
            for tool_name, params in tools:
                tool = server.get_tool(tool_name)
                for _ in range(25):
                    futures.append(executor.submit(tool, **params))
            
            for future in as_completed(futures):
                results.append(future.result())
        
        # All should succeed
        assert len(results) == 100
        assert all(r["success"] for r in results)

    def test_concurrent_analysis_tools(self, server, test_simulation_id):
        """Test concurrent analysis tool execution."""
        analysis_tools = [
            "analyze_population_dynamics",
            "analyze_survival_rates", 
            "analyze_resource_efficiency",
        ]
        
        def run_analysis(tool_name: str):
            tool = server.get_tool(tool_name)
            params = {"simulation_id": test_simulation_id}
            if tool_name == "analyze_survival_rates":
                params["group_by"] = "generation"
            return tool(**params)
        
        # Run each analysis tool 30 times concurrently (90 total)
        with ThreadPoolExecutor(max_workers=15) as executor:
            futures = []
            for tool_name in analysis_tools:
                for _ in range(30):
                    futures.append(executor.submit(run_analysis, tool_name))
            
            results = [f.result() for f in futures]
        
        # All should succeed
        assert len(results) == 90
        assert all(r["success"] for r in results)

    def test_database_connection_pool_under_load(self, server, test_simulation_id):
        """Test database connection pool handles concurrent load."""
        tool = server.get_tool("query_agents")
        
        def query_with_delay():
            result = tool(simulation_id=test_simulation_id, limit=50)
            time.sleep(0.01)  # Small delay to hold connection briefly
            return result
        
        # Attempt to exceed pool size to test overflow handling
        num_requests = 50
        
        start_time = time.time()
        with ThreadPoolExecutor(max_workers=20) as executor:
            futures = [executor.submit(query_with_delay) for _ in range(num_requests)]
            results = [f.result() for f in futures]
        
        elapsed = time.time() - start_time
        
        # All should succeed despite connection pool limits
        assert all(r["success"] for r in results)
        
        # Should complete in reasonable time (not serialized)
        assert elapsed < 5.0, f"Took too long: {elapsed}s"

    def test_cache_thread_safety(self, server, test_simulation_id):
        """Test cache service is thread-safe under concurrent access."""
        tool = server.get_tool("get_simulation_info")
        
        # Same params = same cache key
        def cached_query():
            return tool(simulation_id=test_simulation_id)
        
        # Run 200 identical requests concurrently
        with ThreadPoolExecutor(max_workers=20) as executor:
            futures = [executor.submit(cached_query) for _ in range(200)]
            results = [f.result() for f in futures]
        
        # All should return same data
        first_data = results[0]["data"]
        assert all(r["data"] == first_data for r in results)
        
        # Cache stats should be consistent (no race conditions)
        stats = server.cache_service.get_stats()
        assert stats["hits"] + stats["misses"] > 0

    def test_error_handling_under_concurrency(self, server):
        """Test error handling works correctly with concurrent invalid requests."""
        tool = server.get_tool("query_agents")
        
        def query_invalid():
            # Invalid simulation ID
            return tool(simulation_id="invalid_sim_999", limit=10)
        
        # 50 concurrent requests with invalid ID
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(query_invalid) for _ in range(50)]
            results = [f.result() for f in futures]
        
        # All should fail gracefully
        assert all(r["success"] is False for r in results)
        assert all(r["error"]["type"] == "SimulationNotFoundError" for r in results)

    def test_concurrent_comparison_tools(self, server, test_simulation_id):
        """Test comparison tools handle concurrent requests."""
        # Get multiple simulations for comparison
        list_tool = server.get_tool("list_simulations")
        list_result = list_tool(limit=5)
        
        if list_result["success"] and len(list_result["data"]["simulations"]) >= 2:
            sim_ids = [s["simulation_id"] for s in list_result["data"]["simulations"][:2]]
            
            compare_tool = server.get_tool("compare_simulations")
            
            def compare():
                return compare_tool(simulation_ids=sim_ids)
            
            # 30 concurrent comparison requests
            with ThreadPoolExecutor(max_workers=10) as executor:
                futures = [executor.submit(compare) for _ in range(30)]
                results = [f.result() for f in futures]
            
            # All should succeed
            assert all(r["success"] for r in results)

    @pytest.mark.performance
    def test_throughput_under_load(self, server, test_simulation_id):
        """Benchmark throughput with concurrent requests."""
        tool = server.get_tool("query_agents")
        num_requests = 500
        
        start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=50) as executor:
            futures = [
                executor.submit(tool, simulation_id=test_simulation_id, limit=10)
                for _ in range(num_requests)
            ]
            results = [f.result() for f in futures]
        
        elapsed = time.time() - start_time
        
        # All should succeed
        successful = sum(1 for r in results if r["success"])
        assert successful == num_requests
        
        # Calculate throughput
        throughput = num_requests / elapsed
        
        # Should handle at least 50 requests/second under load
        assert throughput > 50, f"Throughput too low: {throughput:.1f} req/s"
        
        # Log performance metrics
        print(f"\nConcurrency Performance:")
        print(f"  Total requests: {num_requests}")
        print(f"  Elapsed time: {elapsed:.2f}s")
        print(f"  Throughput: {throughput:.1f} req/s")
        
        stats = server.cache_service.get_stats()
        if stats["total_requests"] > 0:
            hit_rate = stats["hits"] / stats["total_requests"] * 100
            print(f"  Cache hit rate: {hit_rate:.1f}%")

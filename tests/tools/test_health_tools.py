"""Tests for health check tools."""

from datetime import datetime
from unittest.mock import MagicMock, Mock, patch

import pytest

from agentfarm_mcp.config import CacheConfig
from agentfarm_mcp.services.cache_service import CacheService
from agentfarm_mcp.tools.health_tools import HealthCheckTool, SystemInfoTool
from agentfarm_mcp.utils.exceptions import ConnectionError as MCPConnectionError
from agentfarm_mcp.utils.exceptions import QueryExecutionError


class TestHealthCheckTool:
    """Test the HealthCheckTool."""

    @pytest.fixture
    def mock_db_service(self):
        """Create a mock database service."""
        mock_db = Mock()
        mock_db.config = Mock()
        mock_db.config.pool_size = 5
        mock_db.config.database_type = "sqlite"
        mock_db.config.read_only = True
        mock_db.config.query_timeout = 30
        mock_db.config.path = "/test/db.sqlite"

        # Mock session
        mock_session = Mock()
        mock_result = Mock()
        mock_result.fetchone.return_value = (1,)
        mock_session.execute.return_value = mock_result

        # Create a context manager mock
        mock_context_manager = Mock()
        mock_context_manager.__enter__ = Mock(return_value=mock_session)
        mock_context_manager.__exit__ = Mock(return_value=None)
        mock_db.get_session.return_value = mock_context_manager

        return mock_db

    @pytest.fixture
    def mock_cache_service(self):
        """Create a real cache service with cache disabled."""
        cache_config = CacheConfig(enabled=False)
        cache_service = CacheService(cache_config)
        return cache_service

    @pytest.fixture
    def health_tool(self, mock_db_service, mock_cache_service):
        """Create a HealthCheckTool instance."""
        return HealthCheckTool(mock_db_service, mock_cache_service)

    def test_health_check_tool_properties(self, health_tool):
        """Test tool properties."""
        assert health_tool.name == "health_check"
        assert "comprehensive health check" in health_tool.description.lower()
        assert health_tool.parameters_schema is not None

    def test_health_check_success(self, health_tool):
        """Test successful health check."""
        result = health_tool(include_details=False, timeout_seconds=5)

        assert result["success"] is True
        assert "data" in result
        assert result["data"]["status"] == "healthy"
        assert "timestamp" in result["data"]
        assert "uptime_seconds" in result["data"]
        assert "components" in result["data"]
        assert "summary" in result["data"]

    def test_health_check_with_details(self, health_tool):
        """Test health check with detailed information."""
        result = health_tool(include_details=True, timeout_seconds=5)

        assert result["success"] is True
        assert "data" in result
        assert "components" in result["data"]

        # Check that components are populated
        components = result["data"]["components"]
        assert "database" in components
        assert "cache" in components
        assert "tool_registry" in components

    def test_database_health_check_success(self, health_tool, mock_db_service):
        """Test successful database health check."""
        result = health_tool._check_database_health(include_details=False, timeout_seconds=5)

        assert result["status"] == "healthy"
        assert "response_time_ms" in result
        assert result["connection_pool_size"] == 5
        assert result["database_type"] == "sqlite"
        assert result["read_only"] is True

    def test_database_health_check_with_details(self, health_tool, mock_db_service):
        """Test database health check with details."""
        result = health_tool._check_database_health(include_details=True, timeout_seconds=5)

        assert result["status"] == "healthy"
        assert "details" in result
        assert result["details"]["query_timeout"] == 30
        assert result["details"]["database_path"] == "/test/db.sqlite"

    def test_database_health_check_connection_error(self, health_tool, mock_db_service):
        """Test database health check with connection error."""
        mock_db_service.get_session.side_effect = MCPConnectionError(
            "Connection failed", database_type="sqlite"
        )

        result = health_tool._check_database_health(include_details=False, timeout_seconds=5)

        assert result["status"] == "unhealthy"
        assert "error" in result
        assert result["error_type"] == "ConnectionError"

    def test_database_health_check_query_error(self, health_tool, mock_db_service):
        """Test database health check with query error."""
        mock_db_service.get_session.side_effect = QueryExecutionError(
            "Query failed", query="SELECT 1"
        )

        result = health_tool._check_database_health(include_details=False, timeout_seconds=5)

        assert result["status"] == "unhealthy"
        assert "error" in result
        assert result["error_type"] == "QueryExecutionError"

    def test_database_health_check_slow_response(self, health_tool, mock_db_service):
        """Test database health check with slow response."""
        with patch("agentfarm_mcp.tools.health_tools.datetime") as mock_datetime:
            # Mock slow response time
            mock_datetime.now.side_effect = [
                datetime(2023, 1, 1, 12, 0, 0),  # Start time
                datetime(2023, 1, 1, 12, 0, 6),  # End time (6 seconds later)
            ]

            result = health_tool._check_database_health(include_details=False, timeout_seconds=5)

            assert result["status"] == "warning"
            assert "warning" in result
            assert "slower than expected" in result["warning"]

    def test_cache_health_check_success(self, health_tool, mock_cache_service):
        """Test successful cache health check."""
        result = health_tool._check_cache_health(include_details=False)

        assert result["status"] == "healthy"
        assert result["enabled"] is True
        assert result["size"] == 5
        assert result["max_size"] == 100
        assert result["hit_rate"] == 0.8

    def test_cache_health_check_with_details(self, health_tool, mock_cache_service):
        """Test cache health check with details."""
        result = health_tool._check_cache_health(include_details=True)

        assert result["status"] == "healthy"
        assert "details" in result
        assert result["details"]["ttl_seconds"] == 300
        assert result["details"]["test_operation"] == "passed"

    def test_cache_health_check_disabled(self, health_tool, mock_cache_service):
        """Test cache health check when cache is disabled."""
        mock_cache_service.get_stats.return_value = {
            "enabled": False,
            "size": 0,
            "max_size": 100,
            "hit_rate": 0.0,
            "hits": 0,
            "misses": 0,
            "ttl_seconds": 300,
        }

        result = health_tool._check_cache_health(include_details=False)

        assert result["status"] == "warning"
        assert "warning" in result
        assert "disabled" in result["warning"]

    def test_cache_health_check_nearly_full(self, health_tool, mock_cache_service):
        """Test cache health check when cache is nearly full."""
        mock_cache_service.get_stats.return_value = {
            "enabled": True,
            "size": 95,
            "max_size": 100,
            "hit_rate": 0.8,
            "hits": 40,
            "misses": 10,
            "ttl_seconds": 300,
        }

        result = health_tool._check_cache_health(include_details=False)

        assert result["status"] == "warning"
        assert "warning" in result
        assert "nearly full" in result["warning"]

    def test_cache_health_check_error(self, health_tool, mock_cache_service):
        """Test cache health check with error."""
        mock_cache_service.set.side_effect = Exception("Cache operation failed")

        result = health_tool._check_cache_health(include_details=False)

        assert result["status"] == "unhealthy"
        assert "error" in result
        assert result["error_type"] == "CacheError"

    def test_tool_registry_health_check(self, health_tool):
        """Test tool registry health check."""
        result = health_tool._check_tool_registry_health(include_details=False)

        assert result["status"] == "healthy"
        assert "message" in result
        assert "not implemented" in result["message"]

    def test_tool_registry_health_check_with_details(self, health_tool):
        """Test tool registry health check with details."""
        result = health_tool._check_tool_registry_health(include_details=True)

        assert result["status"] == "healthy"
        assert "details" in result
        assert "note" in result["details"]

    def test_get_uptime(self, health_tool):
        """Test uptime calculation."""
        with patch("agentfarm_mcp.tools.health_tools.time") as mock_time:
            mock_time.time.return_value = 1000.0
            mock_time.monotonic.return_value = 100.0

            uptime = health_tool._get_uptime()
            assert uptime == 100.0


class TestSystemInfoTool:
    """Test the SystemInfoTool."""

    @pytest.fixture
    def mock_db_service(self):
        """Create a mock database service."""
        mock_db = Mock()
        mock_db.config = Mock()
        mock_db.config.database_type = "sqlite"
        mock_db.config.path = "/test/db.sqlite"
        mock_db.config.pool_size = 5
        mock_db.config.query_timeout = 30
        mock_db.config.read_only = True
        return mock_db

    @pytest.fixture
    def mock_cache_service(self):
        """Create a mock cache service."""
        mock_cache = Mock()
        mock_cache.get_stats.return_value = {
            "enabled": True,
            "size": 5,
            "max_size": 100,
            "hit_rate": 0.8,
            "hits": 40,
            "misses": 10,
            "ttl_seconds": 300,
        }
        return mock_cache

    @pytest.fixture
    def system_tool(self, mock_db_service):
        """Create a SystemInfoTool instance."""
        # Create a fresh cache service for each test
        cache_config = CacheConfig(enabled=False)
        cache_service = CacheService(cache_config)
        return SystemInfoTool(mock_db_service, cache_service)

    def test_system_info_tool_properties(self, system_tool):
        """Test tool properties."""
        assert system_tool.name == "system_info"
        assert "system information" in system_tool.description.lower()
        assert system_tool.parameters_schema is not None

    def test_system_info_basic(self, system_tool):
        """Test basic system info collection."""
        result = system_tool(include_performance=False)

        assert result["success"] is True
        assert "data" in result
        assert "timestamp" in result["data"]
        assert "server" in result["data"]
        assert "database" in result["data"]
        assert "cache" in result["data"]
        assert "performance" not in result["data"]

    def test_system_info_with_performance(self, system_tool):
        """Test system info with performance metrics."""
        result = system_tool(include_performance=True)

        assert result["success"] is True
        assert "data" in result
        assert "performance" in result["data"]
        assert "memory" in result["data"]["performance"]
        assert "cpu" in result["data"]["performance"]
        assert "system" in result["data"]["performance"]

    def test_get_python_version(self, system_tool):
        """Test Python version retrieval."""
        with patch("sys.version_info") as mock_version:
            mock_version.major = 3
            mock_version.minor = 9
            mock_version.micro = 7

            version = system_tool._get_python_version()
            assert version == "3.9.7"

    def test_get_platform_info(self, system_tool):
        """Test platform information retrieval."""
        with patch("platform.system", return_value="Linux"), patch(
            "platform.release", return_value="5.4.0"
        ), patch("platform.machine", return_value="x86_64"), patch(
            "platform.processor", return_value="Intel"
        ):

            platform_info = system_tool._get_platform_info()

            assert platform_info["system"] == "Linux"
            assert platform_info["release"] == "5.4.0"
            assert platform_info["machine"] == "x86_64"
            assert platform_info["processor"] == "Intel"

    def test_get_performance_metrics(self, system_tool):
        """Test performance metrics collection."""
        with patch("psutil.Process") as mock_process_class, patch(
            "psutil.cpu_count", return_value=8
        ), patch("psutil.virtual_memory") as mock_virtual_memory, patch(
            "os.getpid", return_value=1234
        ):

            # Mock process
            mock_process = Mock()
            mock_process.memory_info.return_value = Mock(
                rss=1024 * 1024 * 100, vms=1024 * 1024 * 200
            )  # 100MB RSS, 200MB VMS
            mock_process.memory_percent.return_value = 5.5
            mock_process.cpu_percent.return_value = 10.2
            mock_process.num_threads.return_value = 4
            mock_process_class.return_value = mock_process

            # Mock virtual memory
            mock_virtual_memory.return_value = Mock(
                total=1024 * 1024 * 1024 * 8,  # 8GB total
                available=1024 * 1024 * 1024 * 4,  # 4GB available
            )

            metrics = system_tool._get_performance_metrics()

            assert "memory" in metrics
            assert "cpu" in metrics
            assert "system" in metrics

            # Check memory metrics
            assert metrics["memory"]["rss_mb"] == 100.0
            assert metrics["memory"]["vms_mb"] == 200.0
            assert metrics["memory"]["percent"] == 5.5

            # Check CPU metrics
            assert metrics["cpu"]["percent"] == 10.2
            assert metrics["cpu"]["num_threads"] == 4

            # Check system metrics
            assert metrics["system"]["cpu_count"] == 8
            assert metrics["system"]["memory_total_gb"] == 8.0
            assert metrics["system"]["memory_available_gb"] == 4.0

    def test_database_info(self, system_tool, mock_db_service):
        """Test database information in system info."""
        result = system_tool(include_performance=False)

        db_info = result["data"]["database"]
        assert db_info["type"] == "sqlite"
        assert db_info["path"] == "/test/db.sqlite"
        assert db_info["pool_size"] == 5
        assert db_info["query_timeout"] == 30
        assert db_info["read_only"] is True

    def test_cache_info(self, system_tool, mock_cache_service):
        """Test cache information in system info."""
        result = system_tool(include_performance=False)

        cache_info = result["data"]["cache"]
        assert cache_info["enabled"] is False  # Cache is disabled in tests
        assert cache_info["size"] == 0
        assert cache_info["max_size"] == 100
        assert cache_info["hit_rate"] == 0.0

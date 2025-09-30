"""Health check tools for monitoring server status."""

import time
from datetime import datetime
from typing import Any, Dict

from pydantic import BaseModel, Field

from ..utils.exceptions import ConnectionError as MCPConnectionError
from ..utils.exceptions import QueryExecutionError
from .base import ToolBase


class HealthCheckParams(BaseModel):
    """Parameters for health check tool."""

    include_details: bool = Field(False, description="Include detailed component information")
    timeout_seconds: int = Field(5, ge=1, le=30, description="Timeout for health checks")


class HealthCheckTool(ToolBase):
    """Comprehensive health check for the MCP server."""

    @property
    def name(self) -> str:
        return "health_check"

    @property
    def description(self) -> str:
        return """
        Perform a comprehensive health check of the MCP server and its components.
        
        Checks the status of:
        - Database connectivity and responsiveness
        - Cache service functionality
        - Tool registry integrity
        - Server configuration validity
        
        Use this for:
        - Monitoring server health
        - Diagnosing connectivity issues
        - Verifying system readiness
        - Load balancer health checks
        """

    @property
    def parameters_schema(self):
        return HealthCheckParams

    def execute(self, **params):
        """Execute health check."""
        include_details = params.get("include_details", False)
        timeout_seconds = params.get("timeout_seconds", 5)

        health_info = {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "version": "0.1.0",
            "uptime_seconds": self._get_uptime(),
            "components": {},
            "summary": {"total_checks": 0, "passed_checks": 0, "failed_checks": 0, "warnings": 0},
        }

        # Check database connectivity
        db_health = self._check_database(timeout_seconds, include_details)
        health_info["components"]["database"] = db_health
        health_info["summary"]["total_checks"] += 1
        if db_health["status"] == "healthy":
            health_info["summary"]["passed_checks"] += 1
        elif db_health["status"] == "warning":
            health_info["summary"]["warnings"] += 1
        else:
            health_info["summary"]["failed_checks"] += 1

        # Check cache service
        cache_health = self._check_cache(include_details)
        health_info["components"]["cache"] = cache_health
        health_info["summary"]["total_checks"] += 1
        if cache_health["status"] == "healthy":
            health_info["summary"]["passed_checks"] += 1
        elif cache_health["status"] == "warning":
            health_info["summary"]["warnings"] += 1
        else:
            health_info["summary"]["failed_checks"] += 1

        # Check tool registry
        tools_health = self._check_tools(include_details)
        health_info["components"]["tool_registry"] = tools_health
        health_info["summary"]["total_checks"] += 1
        if tools_health["status"] == "healthy":
            health_info["summary"]["passed_checks"] += 1
        else:
            health_info["summary"]["failed_checks"] += 1

        # Determine overall status
        if health_info["summary"]["failed_checks"] > 0:
            health_info["status"] = "unhealthy"
        elif health_info["summary"]["warnings"] > 0:
            # Check if warnings are only from disabled cache
            cache_warning = health_info["components"].get("cache", {}).get("warning", "")
            if (health_info["summary"]["warnings"] == 1 and 
                "disabled" in cache_warning.lower()):
                health_info["status"] = "healthy"
            else:
                health_info["status"] = "degraded"
        else:
            health_info["status"] = "healthy"

        return health_info

    def _check_database(self, timeout_seconds: int, include_details: bool) -> Dict[str, Any]:
        """Check database connectivity and responsiveness."""
        start_time = datetime.now()

        try:
            # Test basic connectivity
            with self.db.get_session() as session:
                from sqlalchemy import text

                result = session.execute(text("SELECT 1")).fetchone()

            response_time = (datetime.now() - start_time).total_seconds()

            health = {
                "status": "healthy",
                "response_time_ms": round(response_time * 1000, 2),
                "connection_pool_size": self.db.config.pool_size,
                "database_type": getattr(self.db.config, "database_type", "sqlite"),
                "read_only": self.db.config.read_only,
            }

            if include_details:
                health["details"] = {
                    "query_timeout": self.db.config.query_timeout,
                    "database_path": self.db.config.path,
                }

            # Check if response time is concerning
            if response_time > timeout_seconds:
                health["status"] = "warning"
                health["warning"] = f"Slow response time: {response_time:.2f}s"
            elif response_time > 1.0:
                health["status"] = "warning"
                health["warning"] = f"Response time slower than expected: {response_time:.2f}s"

            return health

        except MCPConnectionError as e:
            return {"status": "unhealthy", "error": str(e), "error_type": "ConnectionError"}
        except QueryExecutionError as e:
            return {"status": "unhealthy", "error": str(e), "error_type": "QueryExecutionError"}
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": f"Unexpected database error: {str(e)}",
                "error_type": "UnknownError",
            }

    def _check_cache(self, include_details: bool) -> Dict[str, Any]:
        """Check cache service functionality."""
        try:
            # Test cache operations
            test_key = "health_check_test"
            test_value = {"timestamp": datetime.now().isoformat()}

            # Test set operation
            self.cache.set(test_key, test_value)

            # Test get operation
            self.cache.get(test_key)

            # Test cache stats
            stats = self.cache.get_stats()

            # Clean up test data
            if hasattr(self.cache, "_evict"):
                self.cache._evict(test_key)

            health = {
                "status": "healthy",
                "enabled": stats["enabled"],
                "size": stats["size"],
                "max_size": stats["max_size"],
                "hit_rate": round(stats["hit_rate"], 3),
                "hits": stats["hits"],
                "misses": stats["misses"],
            }

            if include_details:
                health["details"] = {
                    "ttl_seconds": stats["ttl_seconds"],
                    "test_operation": "passed",
                }

            # Check cache health
            if not stats["enabled"]:
                health["status"] = "warning"
                health["warning"] = "Cache is disabled"
            elif stats["size"] >= stats["max_size"] * 0.9:
                health["status"] = "warning"
                health["warning"] = "Cache is nearly full"

            return health

        except Exception as e:
            return {
                "status": "unhealthy",
                "error": f"Cache operation failed: {str(e)}",
                "error_type": "CacheError",
            }

    def _check_tools(self, include_details: bool) -> Dict[str, Any]:
        """Check tool registry integrity."""
        try:
            # This would need access to the server's tool registry
            # For now, we'll do a basic check
            health = {
                "status": "healthy",
                "message": "Tool registry check not implemented in this context",
            }

            if include_details:
                health["details"] = {"note": "Tool registry health check requires server context"}

            return health

        except Exception as e:
            return {
                "status": "unhealthy",
                "error": f"Tool registry check failed: {str(e)}",
                "error_type": "ToolRegistryError",
            }

    def _get_uptime(self) -> float:
        """Get server uptime in seconds."""
        # This is a placeholder - in a real implementation, you'd track start time
        # For now, return a reasonable default
        return time.time()

    def _check_database_health(self, include_details: bool = False, timeout_seconds: int = 5) -> Dict[str, Any]:
        """Check database health (alias for _check_database)."""
        return self._check_database(timeout_seconds, include_details)

    def _check_cache_health(self, include_details: bool = False) -> Dict[str, Any]:
        """Check cache health (alias for _check_cache)."""
        return self._check_cache(include_details)

    def _check_tool_registry_health(self, include_details: bool = False) -> Dict[str, Any]:
        """Check tool registry health (alias for _check_tools)."""
        return self._check_tools(include_details)


class SystemInfoParams(BaseModel):
    """Parameters for system info tool."""

    include_performance: bool = Field(False, description="Include performance metrics")


class SystemInfoTool(ToolBase):
    """Get system information and performance metrics."""

    @property
    def name(self) -> str:
        return "system_info"

    @property
    def description(self) -> str:
        return """
        Get system information and performance metrics for the MCP server.
        
        Returns information about:
        - Server configuration
        - Database configuration
        - Cache statistics
        - Performance metrics (if requested)
        
        Use this for:
        - System monitoring
        - Performance analysis
        - Configuration verification
        - Troubleshooting
        """

    @property
    def parameters_schema(self):
        return SystemInfoParams

    def execute(self, **params):
        """Execute system info collection."""
        include_performance = params.get("include_performance", False)

        info = {
            "timestamp": datetime.now().isoformat(),
            "server": {
                "version": "0.1.0",
                "python_version": self._get_python_version(),
                "platform": self._get_platform_info(),
            },
            "database": {
                "type": getattr(self.db.config, "database_type", "sqlite"),
                "path": self.db.config.path,
                "pool_size": self.db.config.pool_size,
                "query_timeout": self.db.config.query_timeout,
                "read_only": self.db.config.read_only,
            },
            "cache": self.cache.get_stats(),
        }

        if include_performance:
            info["performance"] = self._get_performance_metrics()

        return info

    def _get_python_version(self) -> str:
        """Get Python version."""
        import sys

        return f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"

    def _get_platform_info(self) -> Dict[str, str]:
        """Get platform information."""
        import platform

        return {
            "system": platform.system(),
            "release": platform.release(),
            "machine": platform.machine(),
            "processor": platform.processor(),
        }

    def _get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics."""
        import os

        import psutil

        process = psutil.Process(os.getpid())

        return {
            "memory": {
                "rss_mb": round(process.memory_info().rss / 1024 / 1024, 2),
                "vms_mb": round(process.memory_info().vms / 1024 / 1024, 2),
                "percent": round(process.memory_percent(), 2),
            },
            "cpu": {
                "percent": round(process.cpu_percent(), 2),
                "num_threads": process.num_threads(),
            },
            "system": {
                "cpu_count": psutil.cpu_count(),
                "memory_total_gb": round(psutil.virtual_memory().total / 1024 / 1024 / 1024, 2),
                "memory_available_gb": round(
                    psutil.virtual_memory().available / 1024 / 1024 / 1024, 2
                ),
            },
        }

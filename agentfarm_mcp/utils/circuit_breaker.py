"""Circuit breaker pattern implementation for fault tolerance."""

import time
from enum import Enum
from typing import Callable, TypeVar, Any
from structlog import get_logger

logger = get_logger(__name__)

T = TypeVar("T")


class CircuitState(Enum):
    """Circuit breaker states."""
    CLOSED = "closed"      # Normal operation, requests pass through
    OPEN = "open"          # Circuit is open, requests are rejected
    HALF_OPEN = "half_open"  # Testing if service recovered


class CircuitBreaker:
    """Circuit breaker to prevent cascade failures.
    
    The circuit breaker pattern prevents repeated attempts to execute operations
    that are likely to fail, allowing the system to recover gracefully.
    
    States:
    - CLOSED: Normal operation, all requests pass through
    - OPEN: Too many failures, requests are rejected immediately
    - HALF_OPEN: Testing recovery, limited requests pass through
    
    Example:
        >>> breaker = CircuitBreaker(failure_threshold=5, timeout=60)
        >>> def risky_operation():
        ...     # Some operation that might fail
        ...     return query_database()
        >>> result = breaker.call(risky_operation)
    """

    def __init__(
        self,
        failure_threshold: int = 5,
        timeout: int = 60,
        success_threshold: int = 2,
        name: str = "default",
    ):
        """Initialize circuit breaker.
        
        Args:
            failure_threshold: Number of failures before opening circuit
            timeout: Seconds to wait before attempting half-open state
            success_threshold: Successful calls needed in half-open to close circuit
            name: Name for logging and identification
        """
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.success_threshold = success_threshold
        self.name = name
        
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time: float | None = None
        self.state = CircuitState.CLOSED
        
        logger.info(
            "circuit_breaker_initialized",
            name=name,
            failure_threshold=failure_threshold,
            timeout=timeout,
        )

    def call(self, func: Callable[[], T]) -> T:
        """Execute function with circuit breaker protection.
        
        Args:
            func: Function to execute
            
        Returns:
            Function result
            
        Raises:
            CircuitOpenError: If circuit is open
            Exception: Any exception from the function
        """
        # Check current state and act accordingly
        if self.state == CircuitState.OPEN:
            # Check if timeout elapsed
            if self.last_failure_time and time.time() - self.last_failure_time > self.timeout:
                logger.info("circuit_breaker_half_open", name=self.name)
                self.state = CircuitState.HALF_OPEN
                self.success_count = 0
            else:
                logger.warning("circuit_breaker_open_reject", name=self.name)
                raise CircuitOpenError(
                    f"Circuit breaker '{self.name}' is open. "
                    f"Retry after {self.timeout}s timeout."
                )
        
        # Execute the function
        try:
            result = func()
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise

    def _on_success(self):
        """Handle successful execution."""
        if self.state == CircuitState.HALF_OPEN:
            self.success_count += 1
            logger.debug(
                "circuit_breaker_success_in_half_open",
                name=self.name,
                success_count=self.success_count,
                threshold=self.success_threshold,
            )
            
            if self.success_count >= self.success_threshold:
                # Enough successes to close circuit
                logger.info("circuit_breaker_closed", name=self.name)
                self.state = CircuitState.CLOSED
                self.failure_count = 0
                self.success_count = 0
                
        elif self.state == CircuitState.CLOSED:
            # Reset failure count on success
            if self.failure_count > 0:
                logger.debug("circuit_breaker_reset_failures", name=self.name)
                self.failure_count = 0

    def _on_failure(self):
        """Handle failed execution."""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        logger.warning(
            "circuit_breaker_failure",
            name=self.name,
            failure_count=self.failure_count,
            threshold=self.failure_threshold,
            state=self.state.value,
        )
        
        if self.state == CircuitState.HALF_OPEN:
            # Failure in half-open state -> back to open
            logger.warning("circuit_breaker_reopened", name=self.name)
            self.state = CircuitState.OPEN
            self.success_count = 0
            
        elif self.failure_count >= self.failure_threshold:
            # Too many failures -> open circuit
            logger.error("circuit_breaker_opened", name=self.name)
            self.state = CircuitState.OPEN

    def reset(self):
        """Manually reset the circuit breaker to closed state."""
        logger.info("circuit_breaker_manual_reset", name=self.name)
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = None

    def get_state(self) -> dict[str, Any]:
        """Get current circuit breaker state.
        
        Returns:
            Dictionary with state information
        """
        return {
            "name": self.name,
            "state": self.state.value,
            "failure_count": self.failure_count,
            "success_count": self.success_count,
            "last_failure_time": self.last_failure_time,
            "threshold": self.failure_threshold,
            "timeout": self.timeout,
        }


class CircuitOpenError(Exception):
    """Exception raised when circuit breaker is open."""
    pass

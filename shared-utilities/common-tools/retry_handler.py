"""
Retry handler with exponential backoff.
"""

import asyncio
import random
from functools import wraps
from typing import Callable, Type, Tuple, Any


def retry_with_backoff(
    max_retries: int = 3,
    initial_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_base: float = 2.0,
    jitter: bool = True,
    exceptions: Tuple[Type[Exception], ...] = (Exception,),
):
    """
    Decorator for retrying async functions with exponential backoff.

    Args:
        max_retries: Maximum number of retry attempts
        initial_delay: Initial delay in seconds
        max_delay: Maximum delay in seconds
        exponential_base: Base for exponential backoff calculation
        jitter: Add randomness to delay to prevent thundering herd
        exceptions: Tuple of exception types to catch and retry

    Example:
        @retry_with_backoff(max_retries=3, initial_delay=1.0)
        async def make_api_call():
            # Your API call here
            pass
    """

    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            retries = 0
            delay = initial_delay

            while retries <= max_retries:
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    retries += 1

                    if retries > max_retries:
                        raise

                    # Calculate delay with exponential backoff
                    current_delay = min(delay * (exponential_base ** (retries - 1)), max_delay)

                    # Add jitter if requested
                    if jitter:
                        current_delay *= random.uniform(0.5, 1.5)

                    print(
                        f"⚠️  Retry {retries}/{max_retries} after {current_delay:.2f}s "
                        f"due to: {type(e).__name__}: {str(e)}"
                    )

                    await asyncio.sleep(current_delay)

            # Should not reach here
            raise RuntimeError("Max retries exceeded")

        return wrapper

    return decorator


class CircuitBreaker:
    """
    Circuit breaker pattern for handling cascading failures.

    States:
    - CLOSED: Normal operation, requests pass through
    - OPEN: Failing, requests fail fast
    - HALF_OPEN: Testing if service recovered

    Example:
        circuit_breaker = CircuitBreaker(failure_threshold=5, timeout=60)

        async def call_external_service():
            async with circuit_breaker:
                # Make external call
                pass
    """

    def __init__(self, failure_threshold: int = 5, timeout: float = 60.0):
        """
        Initialize circuit breaker.

        Args:
            failure_threshold: Number of failures before opening circuit
            timeout: Time in seconds before attempting to close circuit
        """
        self.failure_threshold = failure_threshold
        self.timeout = timeout

        self.failure_count = 0
        self.last_failure_time: float | None = None
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN

    async def __aenter__(self):
        """Context manager entry."""
        if self.state == "OPEN":
            # Check if timeout has passed
            if self.last_failure_time and (time.time() - self.last_failure_time) > self.timeout:
                self.state = "HALF_OPEN"
                print("🔄 Circuit breaker: OPEN -> HALF_OPEN")
            else:
                raise RuntimeError("Circuit breaker is OPEN")

        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        import time

        if exc_type is not None:
            # Failure occurred
            self.failure_count += 1
            self.last_failure_time = time.time()

            if self.failure_count >= self.failure_threshold:
                self.state = "OPEN"
                print(f"🚨 Circuit breaker: {self.failure_count} failures -> OPEN")

            return False  # Re-raise exception
        else:
            # Success
            if self.state == "HALF_OPEN":
                self.state = "CLOSED"
                self.failure_count = 0
                print("✅ Circuit breaker: HALF_OPEN -> CLOSED")

            return True

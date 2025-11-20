"""
Rate limiter for controlling request frequency.
"""

import asyncio
import time
from collections import deque
from typing import Optional


class RateLimiter:
    """
    Token bucket rate limiter for controlling request rates.

    Example:
        limiter = RateLimiter(max_requests=10, time_window=60)

        async def make_request():
            async with limiter:
                # Make API call
                pass
    """

    def __init__(self, max_requests: int, time_window: float = 60.0):
        """
        Initialize rate limiter.

        Args:
            max_requests: Maximum number of requests allowed
            time_window: Time window in seconds
        """
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests: deque = deque()
        self._lock = asyncio.Lock()

    async def __aenter__(self):
        """Async context manager entry - wait if rate limit exceeded."""
        await self.acquire()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        pass

    async def acquire(self):
        """
        Acquire permission to make a request, waiting if necessary.
        """
        async with self._lock:
            now = time.time()

            # Remove expired requests
            while self.requests and self.requests[0] <= now - self.time_window:
                self.requests.popleft()

            # Check if we need to wait
            if len(self.requests) >= self.max_requests:
                # Calculate wait time
                oldest_request = self.requests[0]
                wait_time = oldest_request + self.time_window - now

                if wait_time > 0:
                    await asyncio.sleep(wait_time)
                    # Clean up again after waiting
                    now = time.time()
                    while self.requests and self.requests[0] <= now - self.time_window:
                        self.requests.popleft()

            # Record this request
            self.requests.append(time.time())

    def get_current_usage(self) -> int:
        """
        Get current number of requests in the time window.

        Returns:
            Number of active requests
        """
        now = time.time()
        # Clean up expired
        while self.requests and self.requests[0] <= now - self.time_window:
            self.requests.popleft()
        return len(self.requests)

    def get_wait_time(self) -> float:
        """
        Get estimated wait time before next request is allowed.

        Returns:
            Wait time in seconds (0 if no wait needed)
        """
        if len(self.requests) < self.max_requests:
            return 0.0

        now = time.time()
        oldest_request = self.requests[0]
        wait_time = oldest_request + self.time_window - now

        return max(0.0, wait_time)

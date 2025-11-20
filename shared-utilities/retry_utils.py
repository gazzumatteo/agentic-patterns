"""
Retry Utilities for Handling API Rate Limiting and Transient Errors

This module provides utilities for handling common API errors with exponential backoff retry logic.
Specifically designed for Google ADK and CrewAI examples that may encounter rate limiting.
"""

import asyncio
import time
from functools import wraps
from typing import Any, Callable, TypeVar, Optional
from google.genai.errors import ServerError

T = TypeVar('T')


async def run_with_retry(
    func: Callable[..., T],
    *args,
    max_retries: int = 3,
    base_delay: float = 2.0,
    max_delay: float = 60.0,
    **kwargs
) -> T:
    """
    Run async function with exponential backoff retry.

    Automatically retries on 503 (Service Unavailable) errors from Google AI API.

    Args:
        func: Async function to run
        *args: Positional arguments to pass to func
        max_retries: Maximum retry attempts (default: 3)
        base_delay: Base delay in seconds (default: 2.0)
        max_delay: Maximum delay in seconds (default: 60.0)
        **kwargs: Keyword arguments to pass to func

    Returns:
        Result from successful function call

    Raises:
        ServerError: If all retries exhausted or non-retryable error
        Exception: Any other exception from func
    """
    for attempt in range(max_retries):
        try:
            return await func(*args, **kwargs)

        except ServerError as e:
            # Only retry on 503 (Service Unavailable) errors
            if e.status_code == 503 and attempt < max_retries - 1:
                delay = min(base_delay * (2 ** attempt), max_delay)
                print(f"⚠️  API overloaded (503). Retrying in {delay:.1f}s... (attempt {attempt + 1}/{max_retries})")
                await asyncio.sleep(delay)
            else:
                # Non-retryable error or max retries reached
                raise

        except Exception as e:
            # Non-retryable error
            print(f"❌ Non-retryable error: {type(e).__name__}: {str(e)}")
            raise

    raise RuntimeError(f"Failed after {max_retries} attempts")


def sync_retry(
    func: Callable[..., T],
    *args,
    max_retries: int = 3,
    base_delay: float = 2.0,
    max_delay: float = 60.0,
    **kwargs
) -> T:
    """
    Synchronous version of run_with_retry for non-async functions.

    Args:
        func: Function to run
        *args: Positional arguments
        max_retries: Maximum retry attempts
        base_delay: Base delay in seconds
        max_delay: Maximum delay in seconds
        **kwargs: Keyword arguments

    Returns:
        Result from successful function call
    """
    for attempt in range(max_retries):
        try:
            return func(*args, **kwargs)

        except ServerError as e:
            if e.status_code == 503 and attempt < max_retries - 1:
                delay = min(base_delay * (2 ** attempt), max_delay)
                print(f"⚠️  API overloaded (503). Retrying in {delay:.1f}s... (attempt {attempt + 1}/{max_retries})")
                time.sleep(delay)
            else:
                raise

        except Exception as e:
            print(f"❌ Non-retryable error: {type(e).__name__}: {str(e)}")
            raise

    raise RuntimeError(f"Failed after {max_retries} attempts")


def retry_on_503(max_retries: int = 3, base_delay: float = 2.0):
    """
    Decorator for automatic retry on 503 errors.

    Usage:
        @retry_on_503(max_retries=3, base_delay=2.0)
        async def my_function():
            # Function that might hit API limits
            pass

    Args:
        max_retries: Maximum retry attempts
        base_delay: Base delay in seconds
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            return await run_with_retry(
                func,
                *args,
                max_retries=max_retries,
                base_delay=base_delay,
                **kwargs
            )
        return wrapper
    return decorator


# Example usage in agent code:
"""
from shared_utilities.retry_utils import run_with_retry, retry_on_503

# Option 1: Wrap individual calls
async def main():
    result = await run_with_retry(
        runner.run_async,
        app_name="demo",
        agent=my_agent,
        input_data=data
    )

# Option 2: Use as decorator
@retry_on_503(max_retries=3)
async def create_plan(description: str):
    events = runner.run_async(...)
    async for event in events:
        # Process events
        pass
"""

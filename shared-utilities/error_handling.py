"""
Error Handling Utilities for Agentic Pattern Examples

Provides common error handling patterns for both ADK and CrewAI examples,
including graceful degradation and informative error messages.
"""

import os
import asyncio
from typing import Any, Callable, Optional
from google.genai.errors import ServerError
from rich.console import Console

console = Console()


async def safe_run_async(
    func: Callable,
    *args,
    error_context: str = "Operation",
    **kwargs
) -> Optional[Any]:
    """
    Safely run an async function with comprehensive error handling.

    Args:
        func: Async function to run
        *args: Positional arguments
        error_context: Description of what's being attempted
        **kwargs: Keyword arguments

    Returns:
        Result if successful, None if failed
    """
    try:
        result = await func(*args, **kwargs)

        # Allow cleanup of aiohttp sessions
        await asyncio.sleep(0.25)

        return result

    except ServerError as e:
        if e.status_code == 503:
            console.print(f"[yellow]⚠️  {error_context} failed: API overloaded (503)[/yellow]")
            console.print("[yellow]   This is a temporary Google AI API issue, not a code error.[/yellow]")
        elif e.status_code == 429:
            console.print(f"[yellow]⚠️  {error_context} failed: Rate limit exceeded (429)[/yellow]")
        else:
            console.print(f"[red]❌ {error_context} failed: {e}[/red]")
        return None

    except KeyboardInterrupt:
        console.print(f"\n[yellow]⚠️  {error_context} interrupted by user[/yellow]")
        raise

    except Exception as e:
        console.print(f"[red]❌ {error_context} failed: {type(e).__name__}: {str(e)}[/red]")
        return None

    finally:
        # Ensure cleanup
        await asyncio.sleep(0.1)


def get_demo_config() -> dict:
    """
    Get configuration for demo/test mode.

    Returns:
        Dictionary with iteration counts based on DEMO_MODE
    """
    demo_mode = os.getenv("DEMO_MODE", "true").lower() == "true"

    if demo_mode:
        return {
            "max_generations": 3,
            "population_size": 10,
            "simulation_rounds": 100,
            "max_iterations": 3,
            "max_retries": 2
        }
    else:
        return {
            "max_generations": 50,
            "population_size": 100,
            "simulation_rounds": 5000,
            "max_iterations": 10,
            "max_retries": 5
        }


def print_demo_mode_notice():
    """Print notice if running in demo mode."""
    if os.getenv("DEMO_MODE", "true").lower() == "true":
        console.print("\n[yellow]ℹ️  Running in DEMO_MODE with reduced iterations[/yellow]")
        console.print("[yellow]   Set DEMO_MODE=false in .env for full execution[/yellow]\n")

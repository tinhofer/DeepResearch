"""Retry utility with exponential backoff for LLM and API calls."""

import asyncio
import logging
import functools
from typing import TypeVar, Callable, Any

from src.utils.exceptions import LLMConnectionError

logger = logging.getLogger(__name__)

T = TypeVar("T")


async def retry_async(
    func: Callable[..., Any],
    *args: Any,
    max_retries: int = 3,
    base_delay: float = 2.0,
    max_delay: float = 30.0,
    retryable_exceptions: tuple = (Exception,),
    **kwargs: Any,
) -> Any:
    """Call an async or sync function with exponential backoff on failure.

    Args:
        func: The function to call (async or sync).
        max_retries: Maximum number of retry attempts.
        base_delay: Initial delay in seconds between retries.
        max_delay: Maximum delay cap in seconds.
        retryable_exceptions: Tuple of exception types that trigger a retry.

    Returns:
        The return value of the function call.

    Raises:
        LLMConnectionError: If all retries are exhausted.
    """
    last_exception = None
    for attempt in range(max_retries + 1):
        try:
            if asyncio.iscoroutinefunction(func):
                return await func(*args, **kwargs)
            else:
                return func(*args, **kwargs)
        except retryable_exceptions as exc:
            last_exception = exc
            if attempt < max_retries:
                delay = min(base_delay * (2 ** attempt), max_delay)
                logger.warning(
                    "Attempt %d/%d failed for %s: %s. Retrying in %.1fs...",
                    attempt + 1,
                    max_retries + 1,
                    func.__name__ if hasattr(func, '__name__') else str(func),
                    exc,
                    delay,
                )
                await asyncio.sleep(delay)
            else:
                logger.error(
                    "All %d attempts failed for %s: %s",
                    max_retries + 1,
                    func.__name__ if hasattr(func, '__name__') else str(func),
                    exc,
                )

    raise LLMConnectionError(
        f"Failed after {max_retries + 1} attempts: {last_exception}"
    ) from last_exception


def llm_invoke_with_retry(
    llm: Any,
    messages: list,
    max_retries: int = 3,
    base_delay: float = 2.0,
) -> Any:
    """Synchronously invoke an LLM with retry logic.

    This is a convenience wrapper for the common pattern of calling llm.invoke().
    Since llm.invoke() is synchronous, this runs the retry loop synchronously too,
    but wraps via the async helper for consistency.
    """
    import asyncio

    return asyncio.get_event_loop().run_until_complete(
        retry_async(
            llm.invoke,
            messages,
            max_retries=max_retries,
            base_delay=base_delay,
        )
    )

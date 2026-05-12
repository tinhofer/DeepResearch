"""Tests for the retry utility."""

import pytest

from src.utils.exceptions import LLMConnectionError
from src.utils.retry import retry_async


class TestRetryAsync:
    @pytest.mark.asyncio
    async def test_succeeds_first_try(self):
        call_count = 0

        async def ok():
            nonlocal call_count
            call_count += 1
            return "done"

        result = await retry_async(ok, max_retries=3, base_delay=0.01)
        assert result == "done"
        assert call_count == 1

    @pytest.mark.asyncio
    async def test_retries_then_succeeds(self):
        call_count = 0

        async def flaky():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ConnectionError("transient")
            return "recovered"

        result = await retry_async(
            flaky, max_retries=3, base_delay=0.01,
            retryable_exceptions=(ConnectionError,),
        )
        assert result == "recovered"
        assert call_count == 3

    @pytest.mark.asyncio
    async def test_exhausts_retries(self):
        call_count = 0

        async def always_fail():
            nonlocal call_count
            call_count += 1
            raise ConnectionError("permanent")

        with pytest.raises(LLMConnectionError, match="Failed after 3 attempts"):
            await retry_async(
                always_fail, max_retries=2, base_delay=0.01,
                retryable_exceptions=(ConnectionError,),
            )
        assert call_count == 3  # 1 initial + 2 retries

    @pytest.mark.asyncio
    async def test_non_retryable_exception_not_retried(self):
        call_count = 0

        async def type_error():
            nonlocal call_count
            call_count += 1
            raise TypeError("not retryable")

        with pytest.raises(TypeError, match="not retryable"):
            await retry_async(
                type_error, max_retries=3, base_delay=0.01,
                retryable_exceptions=(ConnectionError,),
            )
        assert call_count == 1

    @pytest.mark.asyncio
    async def test_works_with_sync_function(self):
        call_count = 0

        def sync_fn():
            nonlocal call_count
            call_count += 1
            return 42

        result = await retry_async(sync_fn, max_retries=2, base_delay=0.01)
        assert result == 42
        assert call_count == 1

    @pytest.mark.asyncio
    async def test_passes_args_and_kwargs(self):
        async def add(a, b, extra=0):
            return a + b + extra

        result = await retry_async(add, 3, 4, extra=10, max_retries=1, base_delay=0.01)
        assert result == 17

    @pytest.mark.asyncio
    async def test_max_delay_caps_backoff(self):
        """Delay should not exceed max_delay regardless of attempt count."""
        call_count = 0

        async def fail_twice():
            nonlocal call_count
            call_count += 1
            if call_count <= 2:
                raise ValueError("fail")
            return "ok"

        result = await retry_async(
            fail_twice, max_retries=3, base_delay=0.01, max_delay=0.02,
        )
        assert result == "ok"

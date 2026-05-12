"""Tests for the token counting utilities."""

import pytest

from src.utils.tokens import count_tokens, truncate_to_token_limit, FALLBACK_CHARS_PER_TOKEN


class TestCountTokens:
    def test_fallback_without_model(self):
        text = "a" * 100
        tokens = count_tokens(text)
        assert tokens == 100 // FALLBACK_CHARS_PER_TOKEN

    def test_fallback_with_unknown_model(self):
        text = "hello world"
        tokens = count_tokens(text, model_name="totally-unknown-model-xyz")
        assert tokens == len(text) // FALLBACK_CHARS_PER_TOKEN

    def test_empty_string(self):
        assert count_tokens("") == 0

    def test_with_tiktoken_model(self):
        try:
            import tiktoken
            text = "Hello, world!"
            tokens = count_tokens(text, model_name="gpt-4")
            enc = tiktoken.encoding_for_model("gpt-4")
            expected = len(enc.encode(text))
            assert tokens == expected
        except ImportError:
            pytest.skip("tiktoken not installed")


class TestTruncateToTokenLimit:
    def test_short_text_unchanged(self):
        text = "short"
        result = truncate_to_token_limit(text, max_tokens=1000)
        assert result == text

    def test_truncates_long_text_fallback(self):
        text = "a" * 1000
        result = truncate_to_token_limit(text, max_tokens=10)
        assert len(result) == 10 * FALLBACK_CHARS_PER_TOKEN

    def test_truncates_with_tiktoken(self):
        try:
            import tiktoken
            text = "The quick brown fox jumps over the lazy dog. " * 100
            result = truncate_to_token_limit(text, max_tokens=10, model_name="gpt-4")
            enc = tiktoken.encoding_for_model("gpt-4")
            assert len(enc.encode(result)) <= 10
        except ImportError:
            pytest.skip("tiktoken not installed")

    def test_empty_string(self):
        assert truncate_to_token_limit("", max_tokens=100) == ""

"""Tests for the custom exception hierarchy."""

import pytest

from src.utils.exceptions import (
    BrowserError,
    BrowserSessionError,
    ConfigError,
    ContentExtractionError,
    DeepResearchError,
    LLMConnectionError,
    LLMError,
    LLMResponseParseError,
    ResearchError,
)


class TestExceptionHierarchy:
    def test_base_exception_is_exception(self):
        assert issubclass(DeepResearchError, Exception)

    def test_llm_errors_inherit_from_base(self):
        assert issubclass(LLMError, DeepResearchError)
        assert issubclass(LLMResponseParseError, LLMError)
        assert issubclass(LLMConnectionError, LLMError)

    def test_browser_errors_inherit_from_base(self):
        assert issubclass(BrowserError, DeepResearchError)
        assert issubclass(BrowserSessionError, BrowserError)

    def test_other_errors_inherit_from_base(self):
        assert issubclass(ContentExtractionError, DeepResearchError)
        assert issubclass(ConfigError, DeepResearchError)
        assert issubclass(ResearchError, DeepResearchError)

    def test_catch_all_deep_research_errors(self):
        """Catching DeepResearchError should catch any child."""
        errors = [
            LLMError("a"),
            LLMResponseParseError("b"),
            LLMConnectionError("c"),
            BrowserError("d"),
            BrowserSessionError("e"),
            ContentExtractionError("f"),
            ConfigError("g"),
            ResearchError("h"),
        ]
        for err in errors:
            with pytest.raises(DeepResearchError):
                raise err

    def test_exception_messages_preserved(self):
        msg = "something went wrong"
        err = LLMResponseParseError(msg)
        assert str(err) == msg

    def test_chained_exception(self):
        original = ValueError("bad value")
        wrapped = LLMResponseParseError("parse failed")
        wrapped.__cause__ = original
        assert wrapped.__cause__ is original

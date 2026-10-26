"""Custom exception types for DeepResearch.

Provides specific exception classes instead of catching broad Exception,
making error handling more precise and debugging easier.
"""


class DeepResearchError(Exception):
    """Base exception for all DeepResearch errors."""


class LLMError(DeepResearchError):
    """Error communicating with an LLM provider."""


class LLMResponseParseError(LLMError):
    """Failed to parse LLM response as expected format."""


class LLMConnectionError(LLMError):
    """Network/connection error when calling LLM API."""


class BrowserError(DeepResearchError):
    """Error related to browser operations."""


class BrowserSessionError(BrowserError):
    """Failed to create or manage a browser session."""


class ContentExtractionError(DeepResearchError):
    """Error extracting content from a web page (e.g. Jina reader failure)."""


class ConfigError(DeepResearchError):
    """Error related to configuration loading or validation."""


class ResearchError(DeepResearchError):
    """Error during the deep research pipeline."""

"""Token counting utilities.

Uses tiktoken for accurate counts with OpenAI-compatible models
and falls back to a character-based estimate for others.
"""

import logging
from functools import lru_cache
from typing import Optional

logger = logging.getLogger(__name__)

FALLBACK_CHARS_PER_TOKEN = 4


@lru_cache(maxsize=8)
def _get_encoding(model_name: str):
    """Return a tiktoken encoding for the given model, or None."""
    try:
        import tiktoken
        return tiktoken.encoding_for_model(model_name)
    except (ImportError, KeyError):
        return None


def count_tokens(text: str, model_name: Optional[str] = None) -> int:
    """Count the number of tokens in *text*.

    Uses tiktoken when available and the model is recognised.
    Falls back to ``len(text) // FALLBACK_CHARS_PER_TOKEN``.
    """
    if model_name:
        enc = _get_encoding(model_name)
        if enc is not None:
            return len(enc.encode(text))
    return len(text) // FALLBACK_CHARS_PER_TOKEN


def truncate_to_token_limit(
    text: str,
    max_tokens: int,
    model_name: Optional[str] = None,
) -> str:
    """Truncate *text* so it fits within *max_tokens*.

    When tiktoken is available, truncates at an exact token boundary.
    Otherwise approximates via characters.
    """
    if model_name:
        enc = _get_encoding(model_name)
        if enc is not None:
            tokens = enc.encode(text)
            if len(tokens) <= max_tokens:
                return text
            return enc.decode(tokens[:max_tokens])

    char_limit = max_tokens * FALLBACK_CHARS_PER_TOKEN
    return text[:char_limit]

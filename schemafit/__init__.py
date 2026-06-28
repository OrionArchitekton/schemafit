"""schemafit — provider-aware structured-output / JSON-Schema CI linter.

Statically lint a JSON Schema / tool definition / response_format against each
LLM provider's documented constraint surface (OpenAI, Anthropic, Gemini) and
fail CI *before* the schema 400s in production on provider X.
"""

from __future__ import annotations

__version__ = "0.4.0"

from .linter import PROVIDERS, has_errors, lint, lint_multi
from .model import Finding
from .repair import repair

__all__ = ["PROVIDERS", "Finding", "__version__", "has_errors", "lint", "lint_multi", "repair"]

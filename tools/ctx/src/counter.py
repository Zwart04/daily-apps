"""
Token and character counter for ctx.

Provides token estimation based on character count (4 chars / token)
and, if ``tiktoken`` is installed, exact token counts per model.
"""

from __future__ import annotations

from typing import Dict, List, Optional

from .types import FileContent, TokenCount

# Default tokens-per-character ratio for GPT-family models
_DEFAULT_CHARS_PER_TOKEN = 4.0


def count_tokens(
    content: str,
    files: List[FileContent],
    model: Optional[str] = None,
) -> TokenCount:
    """Count tokens in the extracted *content*.

    Tries to use ``tiktoken`` for exact counts (if installed), otherwise
    falls back to a character-based estimate.

    Args:
        content: The full formatted output string.
        files: List of file contents for per-file stats.
        model: Model name for exact tokenisation (e.g. ``"gpt-4"``).
            If *None*, uses ``"gpt-4"`` for tiktoken or the default
            estimator.

    Returns:
        A ``TokenCount`` with total token estimate, method used, and
        file-level stats (characters, words, lines).
    """
    total_chars = len(content)
    total_words = len(content.split())
    total_lines = sum(f.lines for f in files)

    # Try tiktoken for exact counting
    exact: Dict[str, int] = {}
    method = "estimated"
    _tiktoken_mod = None

    try:
        import tiktoken as _tiktoken_mod  # type: ignore[import-untyped]  # fmt: skip
    except ImportError:
        pass

    if _tiktoken_mod is not None:
        try:
            enc_name = _model_to_encoding(model or "gpt-4")
            enc = _tiktoken_mod.get_encoding(enc_name)
            exact[model or "default"] = len(enc.encode(content))
            method = "exact"
        except Exception:
            pass

    if method == "estimated":
        estimated = max(1, int(total_chars / _DEFAULT_CHARS_PER_TOKEN))
        exact["estimated"] = estimated

    # Prefer exact if available
    total = exact.get(model or "default") or exact.get("estimated", 0)

    return TokenCount(
        total=total,
        by_model=exact,
        method=method,
        characters=total_chars,
        words=total_words,
        lines=total_lines,
    )


def _model_to_encoding(model: str) -> str:
    """Map a model name to its tiktoken encoding name."""
    model_lower = model.lower().replace("-", "").replace("_", "")

    # OpenAI models
    if any(k in model_lower for k in ("gpt4o", "chatgpt4o")):
        return "o200k_base"
    if "gpt4" in model_lower:
        return "cl100k_base"
    if "gpt35" in model_lower or "gpt3" in model_lower:
        return "cl100k_base"
    if "textdavinci" in model_lower:
        return "p50k_base"
    if "textada" in model_lower or "textbabbage" in model_lower:
        return "r50k_base"
    if "codex" in model_lower:
        return "p50k_base"

    # Claude / Anthropic models
    if "claude" in model_lower:
        return "cl100k_base"

    return "cl100k_base"

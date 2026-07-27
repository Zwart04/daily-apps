"""
Output formatters for ctx.

Converts a list of FileContent objects into Markdown, Plain text, or
JSON output strings.
"""

from __future__ import annotations

import json
import sys
from typing import List

from .types import FileContent


def format_markdown(files: List[FileContent], tree: str = "") -> str:
    """Format extracted files as a Markdown document.

    Each file becomes a third-level heading followed by a fenced code
    block.  A directory tree is prepended when *tree* is non-empty.

    Args:
        files: List of file contents to format.
        tree: Optional directory tree string.

    Returns:
        A Markdown-formatted string ready for copying to an AI chat.
    """
    parts: List[str] = []

    if tree:
        parts.append("## Directory Structure\n")
        parts.append("```\n" + tree + "\n```\n")

    parts.append("## Files\n")

    for f in files:
        parts.append(f"### {f.path}\n")
        parts.append(f"```\n{f.content}```\n")

    return "\n".join(parts)


def format_plain(files: List[FileContent], tree: str = "") -> str:
    """Format extracted files as plain text with separators.

    Each file is delimited by its path and a horizontal rule.

    Args:
        files: List of file contents to format.
        tree: Optional directory tree string.

    Returns:
        A plain-text string.
    """
    parts: List[str] = []

    if tree:
        parts.append("Directory Structure:\n" + tree + "\n")

    for f in files:
        parts.append(f.path)
        parts.append("---")
        parts.append(f.content)
        parts.append("---")

    return "\n".join(parts)


def format_json(files: List[FileContent], tree: str = "") -> str:
    """Format extracted files as a JSON array.

    Each file object has the keys: path, content, size, lines, encoding.
    If *tree* is non-empty it is included in the top-level output.

    Args:
        files: List of file contents to format.
        tree: Optional directory tree string.

    Returns:
        A JSON string.
    """
    data: list[dict] = []
    for f in files:
        data.append(
            {
                "path": f.path,
                "content": f.content,
                "size": f.size,
                "lines": f.lines,
                "encoding": f.encoding,
            }
        )

    if tree:
        output = {"tree": tree, "files": data}
    else:
        output = {"files": data}

    return json.dumps(output, indent=2, ensure_ascii=False, default=str)

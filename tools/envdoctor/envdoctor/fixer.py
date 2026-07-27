"""
envdoctor.fixer — Auto-fix and suggestions for common issues.

Can generate .env.example files, detect missing variables,
and suggest fixes for hardcoded secrets.
"""

from __future__ import annotations

import pathlib
from typing import List, Optional

from envdoctor.types import ScanResult
from envdoctor.parser import generate_example_content


def fix_generate_example(result: ScanResult, output_path: Optional[str] = None) -> str:
    """
    Generate an .env.example file from used environment variables.

    The generator includes all vars referenced in code, plus any
    existing vars from .env.example that are NOT stale.

    Args:
        result: Scan result with all references
        output_path: Optional path to write the file

    Returns:
        The generated content as a string
    """
    # Start with vars referenced in code
    vars_set = set(result.referenced_in_code)

    # Add vars from existing .env.example that are NOT stale
    # (this preserves intentionally documented vars)
    for entry in result.dotenv_example_entries:
        if entry.key not in result.unused_in_example:
            vars_set.add(entry.key)

    # Add vars from existing .env
    for entry in result.dotenv_entries:
        if not entry.is_comment:
            vars_set.add(entry.key)

    content = generate_example_content(vars_set)

    if output_path:
        path = pathlib.Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return f"Generated {output_path} ({len(vars_set)} variables)"

    return content


def suggest_fixes(result: ScanResult) -> List[str]:
    """
    Generate shell commands to fix common issues.

    Args:
        result: Scan result to analyze

    Returns:
        List of fix command suggestions
    """
    fixes: List[str] = []

    if result.missing_from_env:
        # Suggest adding to .env with placeholder values
        missing = sorted(result.missing_from_env)[:10]
        for var in missing:
            fixes.append(f"echo '# Add {var} to .env' && echo '{var}=' >> .env")

    if result.missing_from_example:
        # Suggest updating .env.example
        fixes.append(f"envdoctor --fix .   # Auto-generate .env.example")

    if result.secret_candidates:
        for secret in result.secret_candidates[:5]:
            fixes.append(
                f"# {secret.file_path}:{secret.line_number} - replace {secret.secret_type} "
                f"with env var"
            )

    return fixes


def fix_empty_env_values(result: ScanResult) -> List[str]:
    """
    Generate suggestions for filling empty .env values.

    Args:
        result: Scan result

    Returns:
        List of suggestions
    """
    suggestions = []
    for var in sorted(result.empty_in_env):
        suggestions.append(
            f"Set {var} in .env to its proper value"
        )
    return suggestions

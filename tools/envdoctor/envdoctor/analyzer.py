"""
envdoctor.analyzer — Cross-reference engine.

Takes the scanner and parser results and computes the analysis:
- Which env vars are referenced but not defined in .env
- Which vars in .env.example are not actually used
- Which vars in .env are empty/placeholder
- Health score calculation
"""

from __future__ import annotations

from typing import List, Set

from envdoctor.types import (
    DotEnvEntry,
    EnvVarRef,
    ScanResult,
    SecretCandidate,
)


def analyze(
    project_path: str,
    env_var_refs: List[EnvVarRef],
    dotenv_entries: List[DotEnvEntry],
    dotenv_example_entries: List[DotEnvEntry],
    secret_candidates: List[SecretCandidate],
    files_scanned: int,
    errors: List[str],
) -> ScanResult:
    """
    Analyze scan results and compute all diagnostics.

    Args:
        project_path: Path to the scanned project
        env_var_refs: All environment variable references found in source
        dotenv_entries: All entries from .env files
        dotenv_example_entries: All entries from .env.example files
        secret_candidates: Potential hardcoded secrets found
        files_scanned: Number of files scanned
        errors: Any errors encountered during scanning

    Returns:
        Complete ScanResult with computed analysis fields
    """
    result = ScanResult(
        project_path=project_path,
        files_scanned=files_scanned,
        env_var_refs=env_var_refs,
        dotenv_entries=dotenv_entries,
        dotenv_example_entries=dotenv_example_entries,
        secret_candidates=secret_candidates,
        errors=errors,
    )

    # Collect defined variable names
    result.defined_in_env = {e.key for e in dotenv_entries if not e.is_comment}
    result.defined_in_example = {e.key for e in dotenv_example_entries}
    result.referenced_in_code = {r.name for r in env_var_refs}

    # Mark vars with their actual definition status from .env
    env_defs = {e.key: e for e in dotenv_entries}

    # Variables referenced in code but missing from .env
    result.missing_from_env = result.referenced_in_code - result.defined_in_env

    # Variables referenced in code but missing from .env.example
    result.missing_from_example = result.referenced_in_code - result.defined_in_example

    # Variables defined in .env.example but not referenced in code (stale docs)
    result.unused_in_example = result.defined_in_example - result.referenced_in_code

    # Variables defined in .env but not referenced anywhere (might be used
    # at runtime indirectly, so this is advisory)
    result.unused_in_env = result.defined_in_env - result.referenced_in_code

    # Variables in .env that are empty (placeholder with no value)
    result.empty_in_env = {
        e.key for e in dotenv_entries
        if not e.has_value and not e.is_comment
    }

    # Variables in .env that are commented out
    result.commented_in_env = {
        e.key for e in dotenv_entries if e.is_comment
    }

    return result

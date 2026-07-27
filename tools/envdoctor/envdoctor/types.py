"""
envdoctor.types — Type definitions for the entire package.

All data structures shared between modules are defined here
to avoid circular imports and ensure type safety.
"""

from __future__ import annotations

import dataclasses
from typing import Dict, List, Optional, Set, Tuple


@dataclasses.dataclass(frozen=True)
class EnvVarRef:
    """A single reference to an environment variable found in source code."""

    name: str
    file_path: str
    line_number: int
    context: str  # The relevant line of code
    pattern_type: str  # 'os.environ', 'process.env', '$VAR', '${VAR}', 'env:'


@dataclasses.dataclass(frozen=True)
class DotEnvEntry:
    """A single entry from a .env or .env.example file."""

    key: str
    value: str
    file_path: str
    line_number: int
    has_value: bool  # True if value is non-empty in .env
    is_comment: bool  # Whether the reference line itself was commented


@dataclasses.dataclass(frozen=True)
class SecretCandidate:
    """A potential hardcoded secret detected in source files."""

    file_path: str
    line_number: int
    context: str
    secret_type: str  # 'api_key', 'password', 'token', 'private_key', etc.
    confidence: str  # 'high', 'medium', 'low'


@dataclasses.dataclass
class ScanResult:
    """Complete scan result for a project directory."""

    project_path: str
    files_scanned: int
    env_var_refs: List[EnvVarRef]
    dotenv_entries: List[DotEnvEntry]
    dotenv_example_entries: List[DotEnvEntry]
    secret_candidates: List[SecretCandidate]
    errors: List[str]

    # Computed fields (populated by analyzer)
    defined_in_env: Set[str] = dataclasses.field(default_factory=set)
    defined_in_example: Set[str] = dataclasses.field(default_factory=set)
    referenced_in_code: Set[str] = dataclasses.field(default_factory=set)

    # Analysis results
    missing_from_env: Set[str] = dataclasses.field(default_factory=set)
    missing_from_example: Set[str] = dataclasses.field(default_factory=set)
    unused_in_env: Set[str] = dataclasses.field(default_factory=set)
    unused_in_example: Set[str] = dataclasses.field(default_factory=set)
    empty_in_env: Set[str] = dataclasses.field(default_factory=set)
    commented_in_env: Set[str] = dataclasses.field(default_factory=set)

    @property
    def total_issues(self) -> int:
        return (
            len(self.missing_from_env)
            + len(self.missing_from_example)
            + len(self.unused_in_example)
            + len(self.secret_candidates)
            + len(self.errors)
        )

    @property
    def health_score(self) -> float:
        """Calculate a health score from 0.0 to 100.0."""
        if not self.referenced_in_code and not self.defined_in_env:
            return 100.0

        documented = len(self.referenced_in_code & self.defined_in_example)
        total_refs = len(self.referenced_in_code) or 1
        doc_ratio = documented / total_refs

        defined = len(self.referenced_in_code & self.defined_in_env)
        defined_ratio = defined / total_refs

        secret_penalty = min(len(self.secret_candidates) * 5, 40)
        unused_penalty = min(len(self.unused_in_example) * 2, 20)

        score = (doc_ratio * 40) + (defined_ratio * 50) + 10
        score = max(0, score - secret_penalty - unused_penalty)
        return round(min(100, score), 1)

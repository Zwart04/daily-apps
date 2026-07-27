"""Configuration loader — env vars and defaults."""

import os
import sys
from typing import NamedTuple


class Config(NamedTuple):
    """Runtime configuration from environment variables."""

    warn_days: int
    crit_days: int
    timeout_seconds: int
    max_concurrent: int
    verbose: bool

    @classmethod
    def from_env(cls) -> "Config":
        """Load configuration from environment variables with sensible defaults."""
        return cls(
            warn_days=int(os.environ.get("CERTWATCH_WARN_DAYS", "30")),
            crit_days=int(os.environ.get("CERTWATCH_CRIT_DAYS", "7")),
            timeout_seconds=int(os.environ.get("CERTWATCH_TIMEOUT", "10")),
            max_concurrent=int(os.environ.get("CERTWATCH_CONCURRENT", "50")),
            verbose=os.environ.get("CERTWATCH_VERBOSE", "false").lower() == "true",
        )

    def validate(self) -> list[str]:
        """Validate config, returning list of error messages."""
        errors: list[str] = []
        if self.warn_days < 1:
            errors.append(f"CERTWATCH_WARN_DAYS must be >= 1, got {self.warn_days}")
        if self.crit_days < 1:
            errors.append(f"CERTWATCH_CRIT_DAYS must be >= 1, got {self.crit_days}")
        if self.crit_days >= self.warn_days:
            errors.append(
                f"CERTWATCH_CRIT_DAYS ({self.crit_days}) must be less than "
                f"CERTWATCH_WARN_DAYS ({self.warn_days})"
            )
        if self.timeout_seconds < 1 or self.timeout_seconds > 120:
            errors.append(
                f"CERTWATCH_TIMEOUT must be between 1 and 120, got {self.timeout_seconds}"
            )
        if self.max_concurrent < 1 or self.max_concurrent > 500:
            errors.append(
                f"CERTWATCH_CONCURRENT must be between 1 and 500, got {self.max_concurrent}"
            )
        return errors


def load_config() -> Config:
    """Load and validate configuration. Exit on invalid config."""
    config = Config.from_env()
    errors = config.validate()
    if errors:
        for err in errors:
            print(f"Config error: {err}", file=sys.stderr)
        sys.exit(2)
    return config

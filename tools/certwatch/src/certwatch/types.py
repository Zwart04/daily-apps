"""Type definitions for certwatch."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class CertInfo:
    """Information about a single SSL certificate check result."""

    hostname: str
    port: int
    status: str  # 'valid', 'expired', 'error', 'warning', 'critical'
    error: Optional[str] = None

    # Certificate details
    subject_cn: Optional[str] = None
    issuer_cn: Optional[str] = None
    serial_number: Optional[str] = None
    not_before: Optional[datetime] = None
    not_after: Optional[datetime] = None
    days_remaining: Optional[int] = None
    sans: list[str] = field(default_factory=list)

    # TLS details
    tls_version: Optional[str] = None
    ocsp_stapled: Optional[bool] = None

    # Timing
    check_duration_ms: Optional[float] = None

    @property
    def is_valid(self) -> bool:
        return self.status == "valid"

    @property
    def is_expired(self) -> bool:
        return self.status == "expired"

    @property
    def remaining_ratio(self) -> float:
        """Ratio of time remaining (0.0 to 1.0)."""
        if not self.not_before or not self.not_after:
            return 0.0
        total = (self.not_after - self.not_before).total_seconds()
        if total <= 0:
            return 0.0
        remaining = (self.not_after - datetime.now(self.not_after.tzinfo)).total_seconds()
        return max(0.0, min(1.0, remaining / total))


@dataclass
class CheckResult:
    """Aggregated result from checking one or more domains."""

    results: list[CertInfo] = field(default_factory=list)
    total_time_ms: float = 0.0
    domains_count: int = 0
    valid_count: int = 0
    warning_count: int = 0
    critical_count: int = 0
    expired_count: int = 0
    error_count: int = 0

    def aggregate(self) -> None:
        """Calculate summary counts from results."""
        self.domains_count = len(self.results)
        self.valid_count = sum(1 for r in self.results if r.status == "valid")
        self.warning_count = sum(1 for r in self.results if r.status == "warning")
        self.critical_count = sum(1 for r in self.results if r.status == "critical")
        self.expired_count = sum(1 for r in self.results if r.status == "expired")
        self.error_count = sum(1 for r in self.results if r.status == "error")

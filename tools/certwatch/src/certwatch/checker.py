"""Core SSL certificate checking logic.

Uses Python's ssl module for TLS connections and cryptography for
certificate parsing. Supports async bulk checks via asyncio.
"""

import asyncio
import logging
import socket
import ssl
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional

from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes

from certwatch.config import Config
from certwatch.types import CertInfo, CheckResult

logger = logging.getLogger("certwatch")

# Default system CA store path
SYSTEM_CA_PATHS = [
    "/etc/ssl/certs/ca-certificates.crt",
    "/etc/ssl/certs/ca-bundle.crt",
    "/etc/pki/tls/certs/ca-bundle.crt",
    "/etc/pki/ca-trust/extracted/pem/tls-ca-bundle.pem",
]


def _get_ca_bundle() -> Optional[str]:
    """Find the system CA bundle path."""
    for path in SYSTEM_CA_PATHS:
        try:
            if __import__("os").path.exists(path):
                return path
        except OSError:
            continue
    return None


def _build_ssl_context(config: Config) -> ssl.SSLContext:
    """Build a verified SSL context with reasonable defaults."""
    ctx = ssl.create_default_context(cafile=_get_ca_bundle())
    ctx.check_hostname = True
    ctx.verify_mode = ssl.CERT_REQUIRED
    ctx.load_default_certs()
    # Set reasonable options
    ctx.options |= ssl.OP_NO_TLSv1 | ssl.OP_NO_TLSv1_1  # Disable old TLS
    ctx.options |= ssl.OP_NO_COMPRESSION
    # Set cipher preference for speed over absolute security
    ctx.set_ciphers("DEFAULT:@SECLEVEL=1")
    return ctx


def _parse_cert_common_name(subject) -> str:
    """Extract common name from certificate subject."""
    try:
        cn = subject.get_attributes_for_oid(NameOID.COMMON_NAME)
        if cn:
            return cn[0].value
    except Exception:
        pass
    return ""


def _parse_cert_issuer_name(issuer) -> str:
    """Extract common name from certificate issuer."""
    try:
        cn = issuer.get_attributes_for_oid(NameOID.COMMON_NAME)
        if cn:
            return cn[0].value
    except Exception:
        pass
    # Fallback: return first OU or O
    for oid in [NameOID.ORGANIZATIONAL_UNIT_NAME, NameOID.ORGANIZATION_NAME]:
        try:
            attrs = issuer.get_attributes_for_oid(oid)
            if attrs:
                return attrs[0].value
        except Exception:
            continue
    return str(issuer)


def _parse_sans(cert: x509.Certificate) -> list[str]:
    """Extract Subject Alternative Names from certificate."""
    sans: list[str] = []
    try:
        ext = cert.extensions.get_extension_for_class(x509.SubjectAlternativeName)
        sans = list(ext.value.get_values_for_type(x509.DNSName))
    except x509.ExtensionNotFound:
        pass
    return sans


def _days_until(dt: datetime) -> int:
    """Calculate days between now and dt (UTC)."""
    now = datetime.now(timezone.utc)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    diff = dt - now
    return max(0, diff.days)


def check_certificate(
    hostname: str,
    port: int = 443,
    config: Optional[Config] = None,
) -> CertInfo:
    """Check SSL certificate for a single host:port.

    This is the synchronous entry point. For bulk checks use
    check_certificates_async().
    """
    cfg = config or Config.from_env()
    start = time.monotonic()
    info = CertInfo(hostname=hostname, port=port, status="error")

    try:
        ctx = _build_ssl_context(cfg)

        with socket.create_connection(
            (hostname, port), timeout=cfg.timeout_seconds
        ) as sock:
            with ctx.wrap_socket(sock, server_hostname=hostname) as tls_sock:
                # Get TLS version
                info.tls_version = tls_sock.version()

                # Get the peer certificate as DER bytes
                der_cert = tls_sock.getpeercert(binary_form=True)
                if not der_cert:
                    info.error = "No certificate returned by server"
                    return info

                # Parse with cryptography
                cert = x509.load_der_x509_certificate(der_cert)

                # Extract fields
                info.subject_cn = _parse_cert_common_name(cert.subject)
                info.issuer_cn = _parse_cert_issuer_name(cert.issuer)
                info.serial_number = format(cert.serial_number, "X")
                info.not_before = cert.not_valid_before_utc
                info.not_after = cert.not_valid_after_utc
                info.sans = _parse_sans(cert)

                # Check OCSP stapling
                try:
                    ocsp_resp = tls_sock.get_ocsp_response()
                    info.ocsp_stapled = ocsp_resp is not None
                except Exception:
                    info.ocsp_stapled = False

                # Determine status based on expiry
                now = datetime.now(timezone.utc)
                nb = (
                    cert.not_valid_before_utc
                    if cert.not_valid_before_utc.tzinfo
                    else cert.not_valid_before_utc.replace(tzinfo=timezone.utc)
                )
                na = (
                    cert.not_valid_after_utc
                    if cert.not_valid_after_utc.tzinfo
                    else cert.not_valid_after_utc.replace(tzinfo=timezone.utc)
                )

                if now < nb:
                    info.status = "error"
                    info.error = (
                        f"Certificate not yet valid (valid from {nb.isoformat()})"
                    )
                elif now > na:
                    info.status = "expired"
                else:
                    days_left = _days_until(na)
                    info.days_remaining = days_left
                    if days_left <= cfg.crit_days:
                        info.status = "critical"
                    elif days_left <= cfg.warn_days:
                        info.status = "warning"
                    else:
                        info.status = "valid"

    except ssl.SSLCertVerificationError as e:
        info.error = f"Certificate verification failed: {e}"
    except ssl.SSLError as e:
        info.error = f"SSL error: {e}"
    except socket.timeout:
        info.error = f"Connection timeout ({cfg.timeout_seconds}s)"
    except socket.gaierror as e:
        info.error = f"DNS resolution failed: {e}"
    except ConnectionRefusedError:
        info.error = "Connection refused"
    except OSError as e:
        info.error = f"Connection error: {e}"
    except Exception as e:
        info.error = f"Unexpected error: {e}"

    info.check_duration_ms = round((time.monotonic() - start) * 1000, 1)
    return info


async def _check_one_async(
    hostname: str,
    port: int,
    config: Config,
    semaphore: asyncio.Semaphore,
) -> CertInfo:
    """Check one certificate asynchronously (runs in executor)."""
    loop = asyncio.get_running_loop()
    async with semaphore:
        return await loop.run_in_executor(
            None, check_certificate, hostname, port, config
        )


async def check_certificates_async(
    targets: list[tuple[str, int]],
    config: Config,
) -> CheckResult:
    """Check multiple certificates concurrently."""
    start = time.monotonic()
    semaphore = asyncio.Semaphore(config.max_concurrent)
    result = CheckResult()

    tasks = [
        _check_one_async(hostname, port, config, semaphore)
        for hostname, port in targets
    ]

    results = await asyncio.gather(*tasks, return_exceptions=True)

    for r in results:
        if isinstance(r, Exception):
            result.results.append(
                CertInfo(
                    hostname="unknown",
                    port=0,
                    status="error",
                    error=str(r),
                )
            )
        else:
            result.results.append(r)

    result.total_time_ms = round((time.monotonic() - start) * 1000, 1)
    result.aggregate()
    return result


def parse_targets(
    domains: list[str],
    default_port: int = 443,
) -> list[tuple[str, int]]:
    """Parse domain[:port] strings into (hostname, port) tuples."""
    targets: list[tuple[str, int]] = []
    for domain in domains:
        domain = domain.strip()
        if not domain or domain.startswith("#"):
            continue
        if ":" in domain:
            parts = domain.rsplit(":", 1)
            hostname = parts[0]
            try:
                port = int(parts[1])
            except ValueError:
                logger.warning("Invalid port in '%s', using default %d", domain, default_port)
                port = default_port
        else:
            hostname = domain
            port = default_port
        targets.append((hostname, port))
    return targets

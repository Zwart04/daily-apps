"""CLI entry point — argument parsing and orchestration."""

import argparse
import asyncio
import sys
import textwrap

from rich.console import Console

from certwatch.checker import check_certificates_async, parse_targets
from certwatch.config import load_config
from certwatch.output import (
    output_detail,
    output_json,
    output_nagios,
    output_summary,
    output_table,
    output_yaml,
)
from certwatch.types import CheckResult

console = Console(stderr=True)

__all__ = ["main"]


def _build_parser() -> argparse.ArgumentParser:
    """Build the argument parser."""
    parser = argparse.ArgumentParser(
        prog="certwatch",
        description="SSL/TLS certificate expiry checker — beautiful CLI, bulk async checks",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent("""\
            Examples:
              certwatch example.com                          Check a single domain
              certwatch example.com google.com github.com    Check multiple domains
              certwatch --file domains.txt                   Bulk check from file
              certwatch --json example.com                   JSON output
              certwatch --warn 30 --crit 7 example.com       Custom thresholds
              certwatch --nagios example.com                 Nagios/Icinga output
              certwatch --all example.com                    Show even valid certs
              cat domains.txt | certwatch --file -            Read from stdin
        """),
    )

    parser.add_argument(
        "domains",
        nargs="*",
        metavar="DOMAIN",
        help="Domain names to check (domain:port for custom ports)",
    )

    parser.add_argument(
        "-f",
        "--file",
        metavar="FILE",
        help="File containing domains (one per line, '-' for stdin)",
    )

    parser.add_argument(
        "--port",
        type=int,
        default=443,
        help="Default port to connect to (default: 443)",
    )

    parser.add_argument(
        "--warn",
        type=int,
        default=None,
        dest="warn_days",
        help="Warning threshold in days (default: 30, env: CERTWATCH_WARN_DAYS)",
    )

    parser.add_argument(
        "--crit",
        type=int,
        default=None,
        dest="crit_days",
        help="Critical threshold in days (default: 7, env: CERTWATCH_CRIT_DAYS)",
    )

    parser.add_argument(
        "--timeout",
        type=int,
        default=None,
        help="Connection timeout in seconds (default: 10, env: CERTWATCH_TIMEOUT)",
    )

    parser.add_argument(
        "--concurrent",
        type=int,
        default=None,
        dest="max_concurrent",
        help="Max concurrent checks (default: 50, env: CERTWATCH_CONCURRENT)",
    )

    parser.add_argument(
        "--json",
        action="store_true",
        help="Output in JSON format",
    )

    parser.add_argument(
        "--yaml",
        action="store_true",
        help="Output in YAML format (requires PyYAML)",
    )

    parser.add_argument(
        "--nagios",
        action="store_true",
        help="Nagios/Icinga compatible output with exit codes",
    )

    parser.add_argument(
        "--all",
        action="store_true",
        dest="show_all",
        help="Show all certificates including valid ones (default: only warnings+)",
    )

    parser.add_argument(
        "--detail",
        action="store_true",
        help="Show detailed per-certificate information",
    )

    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Verbose output (env: CERTWATCH_VERBOSE)",
    )

    parser.add_argument(
        "--test",
        action="store_true",
        help="Run self-test",
    )

    return parser


def _read_domains_from_file(file_path: str) -> list[str]:
    """Read domains from a file or stdin."""
    domains: list[str] = []
    try:
        if file_path == "-":
            for line in sys.stdin:
                line = line.strip()
                if line and not line.startswith("#"):
                    domains.append(line)
        else:
            with open(file_path) as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        domains.append(line)
    except FileNotFoundError:
        print(f"Error: File not found: {file_path}", file=sys.stderr)
        sys.exit(1)
    except OSError as e:
        print(f"Error reading file: {e}", file=sys.stderr)
        sys.exit(1)
    return domains


def _run_self_test() -> None:
    """Run built-in self-test."""
    passed = 0
    failed = 0

    # Test 1: parse_targets
    targets = parse_targets(["example.com", "google.com:8443", "test.com:443"])
    assert targets == [("example.com", 443), ("google.com", 8443), ("test.com", 443)], f"Got {targets}"
    passed += 1
    print(f"[PASS] parse_targets basic: {targets}")

    # Test 2: parse_targets with port override
    targets = parse_targets(["example.com", "google.com:8443"], default_port=9090)
    assert targets == [("example.com", 9090), ("google.com", 8443)], f"Got {targets}"
    passed += 1
    print(f"[PASS] parse_targets with port override: {targets}")

    # Test 3: parse_targets empty
    targets = parse_targets([], default_port=443)
    assert targets == [], f"Got {targets}"
    passed += 1
    print(f"[PASS] parse_targets empty: {targets}")

    # Test 4: parse_targets with blank lines
    targets = parse_targets(["", "  ", "example.com", " # comment"], default_port=443)
    assert targets == [("example.com", 443)], f"Got {targets}"
    passed += 1
    print(f"[PASS] parse_targets filters blanks: {targets}")

    # Test 5: config validation
    from certwatch.config import Config
    cfg = Config(warn_days=30, crit_days=7, timeout_seconds=10, max_concurrent=50, verbose=False)
    errors = cfg.validate()
    assert errors == [], f"Got errors: {errors}"
    passed += 1
    print(f"[PASS] config validation: no errors")

    # Test 6: config validation catches crit > warn
    cfg = Config(warn_days=7, crit_days=30, timeout_seconds=10, max_concurrent=50, verbose=False)
    errors = cfg.validate()
    assert len(errors) > 0, "Should have caught crit > warn"
    passed += 1
    print(f"[PASS] config validation catches crit > warn: {errors}")

    # Test 7: CheckResult aggregation
    from certwatch.types import CertInfo, CheckResult
    cr = CheckResult()
    cr.results = [
        CertInfo(hostname="a.com", port=443, status="valid"),
        CertInfo(hostname="b.com", port=443, status="warning"),
        CertInfo(hostname="c.com", port=443, status="critical"),
        CertInfo(hostname="d.com", port=443, status="expired"),
        CertInfo(hostname="e.com", port=443, status="error"),
    ]
    cr.aggregate()
    assert cr.valid_count == 1, f"Got {cr.valid_count}"
    assert cr.warning_count == 1
    assert cr.critical_count == 1
    assert cr.expired_count == 1
    assert cr.error_count == 1
    assert cr.domains_count == 5
    passed += 1
    print(f"[PASS] CheckResult aggregation: valid={cr.valid_count} warn={cr.warning_count} crit={cr.critical_count} exp={cr.expired_count} err={cr.error_count}")

    # Test 8: CertInfo properties
    from datetime import datetime, timezone, timedelta
    ci = CertInfo(
        hostname="test.com", port=443, status="valid",
        not_before=datetime.now(timezone.utc) - timedelta(days=30),
        not_after=datetime.now(timezone.utc) + timedelta(days=60),
    )
    assert ci.is_valid is True
    assert ci.is_expired is False
    assert 0.6 < ci.remaining_ratio < 0.7
    passed += 1
    print(f"[PASS] CertInfo properties: is_valid={ci.is_valid} ratio={ci.remaining_ratio:.2f}")

    # Test 9: expired cert
    ci2 = CertInfo(
        hostname="expired.com", port=443, status="expired",
        not_before=datetime.now(timezone.utc) - timedelta(days=100),
        not_after=datetime.now(timezone.utc) - timedelta(days=10),
    )
    assert ci2.is_expired is True
    assert ci2.remaining_ratio == 0.0
    passed += 1
    print(f"[PASS] Expired cert properties: is_expired={ci2.is_expired} ratio={ci2.remaining_ratio}")

    # Test 10: parse_targets with invalid port
    targets = parse_targets(["bad:notaport"], default_port=443)
    assert targets == [("bad", 443)], f"Got {targets}"
    passed += 1
    print(f"[PASS] parse_targets invalid port falls back to default")

    total = passed + failed
    print(f"\nResults: {passed}/{total} passed, {failed} failed")
    sys.exit(0 if failed == 0 else 1)


def main() -> None:
    """Main entry point."""
    parser = _build_parser()
    args = parser.parse_args()

    # Self-test mode
    if args.test:
        _run_self_test()

    # Load config (env) and override with CLI args
    config = load_config()
    if args.warn_days is not None:
        config = config._replace(warn_days=args.warn_days)
    if args.crit_days is not None:
        config = config._replace(crit_days=args.crit_days)
    if args.timeout is not None:
        config = config._replace(timeout_seconds=args.timeout)
    if args.max_concurrent is not None:
        config = config._replace(max_concurrent=args.max_concurrent)
    if args.verbose:
        config = config._replace(verbose=True)

    # Collect domains
    domains: list[str] = []

    if args.file:
        domains.extend(_read_domains_from_file(args.file))

    if args.domains:
        # Only add non-stdin domains
        if args.file != "-":
            domains.extend(args.domains)

    if not domains:
        parser.print_help()
        console.print("\n[red]Error:[/red] No domains specified. Provide domains or use --file.")
        sys.exit(1)

    # Parse targets
    targets = parse_targets(domains, default_port=args.port)
    if not targets:
        console.print("[red]Error:[/red] No valid domains to check.")
        sys.exit(1)

    # Run checks
    try:
        result = asyncio.run(check_certificates_async(targets, config))
    except KeyboardInterrupt:
        console.print("\n[yellow]Interrupted.[/yellow]")
        sys.exit(130)

    # Output format
    if args.nagios:
        output_nagios(result)
    elif args.json:
        output_json(result)
    elif args.yaml:
        output_yaml(result)
    else:
        if args.detail:
            output_detail(result)
        output_table(result, show_all=args.show_all)
        output_summary(result)

    # Exit code for scripting
    if result.critical_count > 0 or result.expired_count > 0:
        sys.exit(2)
    if result.warning_count > 0 or result.error_count > 0:
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()

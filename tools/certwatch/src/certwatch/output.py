"""Output formatting — table, JSON, YAML, Nagios, plain text."""

import json
import sys
from datetime import datetime, timezone
from typing import Any, Optional

from rich.console import Console
from rich.table import Table
from rich.tree import Tree
from rich.panel import Panel
from rich.text import Text
from rich import box

from certwatch.types import CertInfo, CheckResult

console = Console(stderr=True)
_output_console = Console()


def _status_style(status: str) -> str:
    """Return rich style string for a status."""
    return {
        "valid": "bold green",
        "warning": "bold yellow",
        "critical": "bold red",
        "expired": "bold white on red",
        "error": "bold red",
    }.get(status, "white")


def _status_symbol(status: str) -> str:
    """Return a status symbol (no emoji)."""
    return {
        "valid": "[ OK ]",
        "warning": "[WARN]",
        "critical": "[CRIT]",
        "expired": "[EXP ]",
        "error": "[ERR ]",
    }.get(status, "[UNKN]")


def _progress_bar(ratio: float, width: int = 25) -> str:
    """Render a progress bar as a string."""
    filled = int(ratio * width)
    filled = max(0, min(width, filled))
    empty = width - filled
    bar = "█" * filled + "░" * empty
    return f"[{bar}]"


def output_table(result: CheckResult, show_all: bool = False) -> None:
    """Display results as a rich table."""
    table = Table(
        title=None,
        box=box.SIMPLE_HEAVY,
        border_style="dim",
        padding=(0, 1),
        show_edge=False,
    )
    table.add_column("Host", style="bold", no_wrap=True)
    table.add_column("Status", no_wrap=True)
    table.add_column("Days Left", justify="right", no_wrap=True)
    table.add_column("Expires", no_wrap=True)
    table.add_column("Issuer", no_wrap=True)

    for r in sorted(result.results, key=lambda x: (
        {"error": 0, "expired": 1, "critical": 2, "warning": 3, "valid": 4}.get(x.status, 5),
        x.hostname,
    )):
        if r.status == "valid" and not show_all:
            continue

        host_str = f"{r.hostname}:{r.port}" if r.port != 443 else r.hostname
        status_str = Text(
            _status_symbol(r.status), style=_status_style(r.status)
        )

        if r.error:
            days_str = "---"
            expires_str = f"[red]{r.error}[/red]"
        else:
            days_str = str(r.days_remaining) if r.days_remaining is not None else "---"
            expires_str = (
                r.not_after.strftime("%Y-%m-%d") if r.not_after else "---"
            )

        table.add_row(
            host_str,
            status_str,
            days_str,
            expires_str,
            r.issuer_cn or "---",
        )

    if table.row_count > 0:
        _output_console.print(table)


def output_detail(result: CheckResult) -> None:
    """Display detailed per-certificate information."""
    for r in sorted(result.results, key=lambda x: x.hostname):
        _print_cert_detail(r)


def _print_cert_detail(r: CertInfo) -> None:
    """Print detailed info for a single certificate."""
    if r.error:
        panel = Panel(
            f"[red]{r.error}[/red]",
            title=f"[bold]{r.hostname}:{r.port}[/bold]",
            border_style="red",
            box=box.ROUNDED,
        )
        _output_console.print("")
        _output_console.print(panel)
        return

    # Build info lines as a list of Rich renderables
    elements: list[Text | str] = []
    nl = "\n"

    elements.append(
        Text.assemble(
            ("Status:       ", "bold"),
            (_status_symbol(r.status) + "  ", _status_style(r.status)),
            (r.status.upper(), _status_style(r.status)),
        )
    )

    def line(label: str, value: str, style: str = "") -> Text:
        """Create a labeled line."""
        t = Text()
        t.append(f"{label:<14}", style="bold")
        if style:
            t.append(value, style=style)
        else:
            t.append(value)
        return t

    elements.append(nl)
    elements.append(line("Issuer:", r.issuer_cn or "---"))
    elements.append(nl)
    elements.append(line("Subject:", f"CN={r.subject_cn or '---'}"))
    elements.append(nl)
    elements.append(line("Serial:", r.serial_number or "---"))

    # SANS
    if r.sans:
        san_str = ", ".join(r.sans[:5])
        if len(r.sans) > 5:
            san_str += f" (+{len(r.sans) - 5} more)"
        elements.append(nl)
        elements.append(line("SANs:", san_str))

    # Dates
    if r.not_before:
        elements.append(nl)
        elements.append(
            line("Issued:", r.not_before.strftime("%Y-%m-%d %H:%M:%S UTC"))
        )
    if r.not_after:
        elements.append(nl)
        elements.append(
            line("Expires:", r.not_after.strftime("%Y-%m-%d %H:%M:%S UTC"))
        )

    if r.days_remaining is not None:
        elements.append(nl)
        elements.append(line("Days Left:", str(r.days_remaining)))
        elements.append(nl)
        bar = _progress_bar(r.remaining_ratio)
        elements.append(
            line(
                "Remaining:",
                f"{bar}  {r.days_remaining}/{_total_days(r)} days",
            )
        )

    # TLS info
    if r.tls_version:
        elements.append(nl)
        elements.append(line("TLS:", r.tls_version))
    if r.ocsp_stapled is not None:
        elements.append(nl)
        ocsp_str = "Yes" if r.ocsp_stapled else "No"
        ocsp_style = "green" if r.ocsp_stapled else "dim"
        elements.append(line("OCSP Stapled:", ocsp_str, ocsp_style))

    elements.append(nl)
    elements.append(line("Checked in:", f"{r.check_duration_ms}ms"))

    # Build the panel content as a Rich Text
    content = Text("")
    for elem in elements:
        if isinstance(elem, str):
            content.append(elem)
        else:
            content.append_text(elem)

    # Determine border style
    border_styles = {
        "valid": "green",
        "warning": "yellow",
        "critical": "red",
        "expired": "red",
        "error": "red",
    }

    panel = Panel(
        content,
        title=f"[bold]{r.hostname}:{r.port}[/bold]",
        border_style=border_styles.get(r.status, "dim"),
        box=box.ROUNDED,
        padding=(1, 2),
    )
    _output_console.print("")
    _output_console.print(panel)


def _total_days(r: CertInfo) -> int:
    """Calculate total validity period in days."""
    if not r.not_before or not r.not_after:
        return 0
    return (r.not_after - r.not_before).days


def output_summary(result: CheckResult) -> None:
    """Print a summary of check results."""
    total = len(result.results)
    valid = result.valid_count
    warning = result.warning_count
    critical = result.critical_count
    expired = result.expired_count
    errors = result.error_count

    status_text = Text()
    good = valid > 0
    bad = warning > 0 or critical > 0 or expired > 0 or errors > 0

    if not good and not bad:
        status_text.append("No results", style="dim")
    elif good and not bad:
        status_text.append(f"All {total} certificates valid", style="bold green")
    elif bad and not good:
        status_text.append("Issues found", style="bold red")
    else:
        status_text.append(
            f"{valid} valid", style="green"
        )
        if warning:
            status_text.append(f", {warning} warning", style="yellow")
        if critical:
            status_text.append(f", {critical} critical", style="red")
        if expired:
            status_text.append(f", {expired} expired", style="bold white on red")
        if errors:
            status_text.append(f", {errors} errors", style="red")

    status_text.append(f" | checked in {result.total_time_ms:.0f}ms", style="dim")

    _output_console.print(Text(""))
    _output_console.print(Panel(status_text, border_style="dim", box=box.ROUNDED))


def output_json(result: CheckResult) -> None:
    """Output results as JSON to stdout."""
    data = _result_to_dict(result)
    json.dump(data, sys.stdout, indent=2, default=str)
    sys.stdout.write("\n")


def _result_to_dict(result: CheckResult) -> dict[str, Any]:
    """Convert CheckResult to a JSON-serializable dict."""
    return {
        "summary": {
            "total": result.domains_count,
            "valid": result.valid_count,
            "warning": result.warning_count,
            "critical": result.critical_count,
            "expired": result.expired_count,
            "errors": result.error_count,
            "check_time_ms": result.total_time_ms,
        },
        "results": [
            {
                "hostname": r.hostname,
                "port": r.port,
                "status": r.status,
                "error": r.error,
                "subject_cn": r.subject_cn,
                "issuer_cn": r.issuer_cn,
                "serial_number": r.serial_number,
                "not_before": r.not_before.isoformat() if r.not_before else None,
                "not_after": r.not_after.isoformat() if r.not_after else None,
                "days_remaining": r.days_remaining,
                "sans": r.sans,
                "tls_version": r.tls_version,
                "ocsp_stapled": r.ocsp_stapled,
                "check_duration_ms": r.check_duration_ms,
            }
            for r in result.results
        ],
    }


def output_yaml(result: CheckResult) -> None:
    """Output results as YAML to stdout."""
    try:
        import yaml
    except ImportError:
        print("YAML output requires PyYAML: pip install pyyaml", file=sys.stderr)
        sys.exit(1)

    data = _result_to_dict(result)
    yaml.dump(data, sys.stdout, default_flow_style=False, sort_keys=False)


def output_nagios(result: CheckResult) -> None:
    """Nagios/Icinga compatible output with appropriate exit code."""
    # Count non-valid results
    has_critical = result.critical_count > 0 or result.expired_count > 0
    has_warning = result.warning_count > 0 or result.error_count > 0

    if has_critical:
        status = "CRITICAL"
        exit_code = 2
    elif has_warning:
        status = "WARNING"
        exit_code = 1
    else:
        status = "OK"
        exit_code = 0

    details = []
    for r in result.results:
        if r.error:
            details.append(f"{r.hostname}:{r.port} ERROR ({r.error})")
        elif r.status == "expired":
            details.append(f"{r.hostname}:{r.port} EXPIRED")
        elif r.status == "critical":
            details.append(f"{r.hostname}:{r.port} {r.days_remaining}d remaining")
        elif r.status == "warning":
            details.append(f"{r.hostname}:{r.port} {r.days_remaining}d remaining")
    detail_str = "; ".join(details) if details else f"All {result.domains_count} certs valid"

    print(f"CERTWATCH {status} - {detail_str}")
    sys.exit(exit_code)

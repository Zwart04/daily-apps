"""
envdoctor.reporter — Output formatting for scan results.

Supports multiple output formats:
- text: Human-readable terminal output with colors
- json: Machine-readable JSON for CI integration
- markdown: Formatted Markdown for documentation
"""

from __future__ import annotations

import json
import sys
from typing import List, Set

from envdoctor.types import (
    DotEnvEntry,
    EnvVarRef,
    ScanResult,
    SecretCandidate,
)


def _color(text: str, color_code: str, no_color: bool = False) -> str:
    """Apply ANSI color if supported."""
    if no_color or not sys.stdout.isatty():
        return text
    codes = {
        "red": "\033[91m",
        "green": "\033[92m",
        "yellow": "\033[93m",
        "blue": "\033[94m",
        "magenta": "\033[95m",
        "cyan": "\033[96m",
        "bold": "\033[1m",
        "dim": "\033[2m",
        "reset": "\033[0m",
    }
    return f"{codes.get(color_code, '')}{text}{codes['reset']}"


def _format_score(score: float) -> str:
    """Format health score with color."""
    if score >= 80:
        return _color(f"{score}/100", "green")
    elif score >= 50:
        return _color(f"{score}/100", "yellow")
    return _color(f"{score}/100", "red")


def _section_summary(
    title: str,
    items: set,
    formatter: callable = None,
    prefix: str = "  ",
) -> str:
    """Format a section of the report with optional item formatting."""
    if not items:
        return ""

    result = [_color(f"\n{title}", "bold")]
    for item in sorted(items):
        if formatter:
            result.append(f"{prefix}{formatter(item)}")
        else:
            result.append(f"{prefix}• {item}")
    return "\n".join(result)


def _format_env_var_ref(ref: EnvVarRef) -> str:
    """Format a single env var reference."""
    # Shorten file path
    path = ref.file_path
    if len(path) > 60:
        path = "..." + path[-57:]
    return f"{ref.name} → {path}:{ref.line_number} ({ref.pattern_type})"


def _format_env_var_ref_by_var(refs: List[EnvVarRef]) -> str:
    """Format grouped env var references."""
    if not refs:
        return "  (no references found)"
    lines = []
    seen = set()
    for ref in refs:
        key = (ref.file_path, ref.line_number)
        if key not in seen:
            seen.add(key)
            path = ref.file_path
            if len(path) > 50:
                path = "..." + path[-47:]
            lines.append(f"    {path}:{ref.line_number}")
    return "\n".join(lines)


def _format_secret(secret: SecretCandidate) -> str:
    """Format a secret candidate."""
    path = secret.file_path
    if len(path) > 50:
        path = "..." + path[-47:]
    return f"{_color(f'[!]', 'red')} {path}:{secret.line_number} [{_color(secret.secret_type, 'yellow')}]"


def _format_dotenv_entry(entry: DotEnvEntry) -> str:
    """Format a .env entry."""
    if entry.is_comment:
        return f"{entry.key} = (commented out)"
    if not entry.has_value:
        return f"{entry.key} = (empty)"
    # Don't expose actual values
    val = entry.value
    if len(val) > 30:
        val = val[:30] + "..."
    return f"{entry.key} = {_color(val, 'dim')}"


def report_text(result: ScanResult, no_color: bool = False, verbose: bool = False) -> str:
    """
    Generate a human-readable text report.

    Args:
        result: The scan result to report on
        no_color: Disable ANSI color codes
        verbose: Include detailed reference information

    Returns:
        Formatted report string
    """
    lines: List[str] = []
    c = lambda text, code: _color(text, code, no_color)
    b = lambda text: _color(text, "bold", no_color)

    # Header
    lines.append(b(f"🔍 envdoctor — Environment Variable Diagnostic"))
    lines.append(b(f"{'=' * 60}"))
    lines.append(f"Project   : {result.project_path}")
    lines.append(f"Files     : {result.files_scanned} scanned")
    lines.append(f"Issues    : {c(str(result.total_issues), 'red' if result.total_issues > 0 else 'green')}")
    lines.append(f"Health    : {_format_score(result.health_score)}")
    lines.append("")

    # Summary counts
    env_refs = len(result.env_var_refs)
    unique_refs = len(result.referenced_in_code)
    defined_env = len(result.defined_in_env)
    defined_ex = len(result.defined_in_example)

    lines.append(b("📊 Summary"))
    lines.append(f"  Environment variables referenced in code: {c(str(env_refs), 'cyan')} ({c(str(unique_refs), 'cyan')} unique)")
    lines.append(f"  Vars defined in .env:                   {c(str(defined_env), 'cyan')}")
    lines.append(f"  Vars defined in .env.example:           {c(str(defined_ex), 'cyan')}")
    lines.append(f"  Files scanned:                          {result.files_scanned}")

    # Issues sections
    if result.missing_from_env:
        lines.append(b(f"\n❌ Missing from .env ({len(result.missing_from_env)})"))
        lines.append(c("  These vars are used in code but NOT defined in .env", "yellow"))
        for var in sorted(result.missing_from_env):
            lines.append(f"    • {c(var, 'red')}")
            if verbose:
                refs = [r for r in result.env_var_refs if r.name == var]
                lines.append(_format_env_var_ref_by_var(refs))

    if result.missing_from_example:
        lines.append(b(f"\n⚠️  Missing from .env.example ({len(result.missing_from_example)})"))
        lines.append(c("  These vars are used in code but NOT in .env.example", "yellow"))
        for var in sorted(result.missing_from_example):
            lines.append(f"    • {c(var, 'yellow')}")

    if result.unused_in_example:
        lines.append(b(f"\n📌 Stale in .env.example ({len(result.unused_in_example)})"))
        lines.append(c("  These vars are in .env.example but never referenced in code", "dim"))
        for var in sorted(result.unused_in_example):
            lines.append(f"    • {c(var, 'dim')}")

    if result.empty_in_env:
        lines.append(b(f"\n⚠️  Empty values in .env ({len(result.empty_in_env)})"))
        lines.append(c("  These vars in .env have no value set (placeholder)", "yellow"))
        for var in sorted(result.empty_in_env):
            lines.append(f"    • {c(var, 'yellow')}")

    if result.commented_in_env:
        lines.append(b(f"\n💬 Commented out in .env ({len(result.commented_in_env)})"))
        for var in sorted(result.commented_in_env):
            lines.append(f"    • {c(var, 'dim')}")

    if result.secret_candidates:
        lines.append(b(f"\n🔑 Potential hardcoded secrets ({len(result.secret_candidates)})"))
        lines.append(c("  These files may contain hardcoded credentials", "red"))
        for secret in result.secret_candidates:
            lines.append(f"    {_format_secret(secret)}")

    if result.errors:
        lines.append(b(f"\n⚠️  Scan errors ({len(result.errors)})"))
        for err in result.errors:
            lines.append(f"    • {c(err, 'red')}")

    # Health assessment
    lines.append(b(f"\n📈 Health Assessment"))
    if result.health_score >= 80:
        lines.append(c(f"  Score: {_format_score(result.health_score)} — Good shape!", "green"))
    elif result.health_score >= 50:
        lines.append(c(f"  Score: {_format_score(result.health_score)} — Needs attention", "yellow"))
    else:
        lines.append(c(f"  Score: {_format_score(result.health_score)} — Critical issues", "red"))

    # Suggestions
    suggestions = _generate_suggestions(result)
    if suggestions:
        lines.append(b(f"\n💡 Suggestions"))
        for s in suggestions:
            lines.append(f"  • {s}")

    if verbose:
        # Detailed reference list
        if result.env_var_refs:
            lines.append(b(f"\n📄 All Environment Variable References"))
            for ref in result.env_var_refs[:100]:  # Limit to first 100
                lines.append(f"    {_format_env_var_ref(ref)}")
            if len(result.env_var_refs) > 100:
                lines.append(c(f"    ... and {len(result.env_var_refs) - 100} more (use --json for complete)", "dim"))

    lines.append("")
    return "\n".join(lines)


def _generate_suggestions(result: ScanResult) -> List[str]:
    """Generate actionable suggestions based on scan results."""
    suggestions = []

    if result.missing_from_env:
        vars_str = ", ".join(sorted(result.missing_from_env)[:5])
        count = len(result.missing_from_env)
        suggestions.append(
            f"Add missing vars to .env: {vars_str}"
            + (f" (+{count - 5} more)" if count > 5 else "")
        )

    if result.missing_from_example:
        suggestions.append(
            f"Run `envdoctor --fix .` to auto-generate .env.example "
            f"({len(result.missing_from_example)} missing vars)"
        )

    if result.unused_in_example:
        suggestions.append(
            f"Remove stale vars from .env.example: "
            f"{', '.join(sorted(result.unused_in_example)[:5])}"
        )

    if result.secret_candidates:
        suggestions.append(
            f"Move hardcoded secrets to environment variables "
            f"({len(result.secret_candidates)} candidates found)"
        )

    if result.empty_in_env:
        suggestions.append(
            f"Fill in empty values in .env "
            f"({len(result.empty_in_env)} empty)"
        )

    return suggestions


def report_json(result: ScanResult, indent: int = 2) -> str:
    """
    Generate a JSON report suitable for CI integration.

    Args:
        result: The scan result to serialize
        indent: JSON indentation level

    Returns:
        JSON string
    """

    def _dotenv_entries_to_dict(entries: List[DotEnvEntry]) -> list:
        return [
            {
                "key": e.key,
                "has_value": e.has_value,
                "is_comment": e.is_comment,
                "file": e.file_path,
                "line": e.line_number,
            }
            for e in entries
        ]

    def _secret_to_dict(s: SecretCandidate) -> dict:
        return {
            "file": s.file_path,
            "line": s.line_number,
            "type": s.secret_type,
            "confidence": s.confidence,
        }

    report = {
        "version": "1.0.0",
        "project_path": result.project_path,
        "summary": {
            "files_scanned": result.files_scanned,
            "issues_total": result.total_issues,
            "health_score": result.health_score,
            "vars_referenced_in_code": len(result.referenced_in_code),
            "vars_defined_in_env": len(result.defined_in_env),
            "vars_defined_in_example": len(result.defined_in_example),
        },
        "issues": {
            "missing_from_env": sorted(result.missing_from_env),
            "missing_from_env_count": len(result.missing_from_env),
            "missing_from_example": sorted(result.missing_from_example),
            "missing_from_example_count": len(result.missing_from_example),
            "unused_in_example": sorted(result.unused_in_example),
            "unused_in_example_count": len(result.unused_in_example),
            "empty_in_env": sorted(result.empty_in_env),
            "empty_in_env_count": len(result.empty_in_env),
            "commented_in_env": sorted(result.commented_in_env),
            "commented_in_env_count": len(result.commented_in_env),
            "secret_candidates": [_secret_to_dict(s) for s in result.secret_candidates],
            "secret_candidates_count": len(result.secret_candidates),
            "scan_errors": result.errors,
            "scan_errors_count": len(result.errors),
        },
        "health_assessment": {
            "score": result.health_score,
            "status": (
                "good"
                if result.health_score >= 80
                else "needs_attention" if result.health_score >= 50 else "critical"
            ),
        },
    }

    return json.dumps(report, indent=indent)


def report_markdown(result: ScanResult) -> str:
    """
    Generate a Markdown report suitable for documentation or CI.

    Args:
        result: The scan result to format

    Returns:
        Markdown string
    """
    lines: List[str] = []

    lines.append("# Environment Variable Report")
    lines.append("")
    lines.append(f"- **Project**: `{result.project_path}`")
    lines.append(f"- **Files Scanned**: {result.files_scanned}")
    lines.append(f"- **Health Score**: {result.health_score}/100")
    lines.append(f"- **Total Issues**: {result.total_issues}")
    lines.append("")

    # Issues table
    lines.append("## Issues Summary")
    lines.append("")
    lines.append("| Category | Count |")
    lines.append("|----------|-------|")
    lines.append(f"| Missing from `.env` | {len(result.missing_from_env)} |")
    lines.append(f"| Missing from `.env.example` | {len(result.missing_from_example)} |")
    lines.append(f"| Stale in `.env.example` | {len(result.unused_in_example)} |")
    lines.append(f"| Empty in `.env` | {len(result.empty_in_env)} |")
    lines.append(f"| Commented out in `.env` | {len(result.commented_in_env)} |")
    lines.append(f"| Hardcoded secrets | {len(result.secret_candidates)} |")
    lines.append(f"| Scan errors | {len(result.errors)} |")
    lines.append("")

    if result.missing_from_env:
        lines.append("## ❌ Missing from `.env`")
        lines.append("")
        lines.append("These variables are used in the codebase but not defined in `.env`:")
        lines.append("")
        for var in sorted(result.missing_from_env):
            lines.append(f"- `{var}`")

    if result.missing_from_example:
        lines.append("")
        lines.append("## ⚠️  Missing from `.env.example`")
        lines.append("")
        for var in sorted(result.missing_from_example):
            lines.append(f"- `{var}`")

    if result.unused_in_example:
        lines.append("")
        lines.append("## 📌 Stale in `.env.example`")
        lines.append("")
        lines.append("These variables are in `.env.example` but not referenced in code:")
        lines.append("")
        for var in sorted(result.unused_in_example):
            lines.append(f"- `{var}`")

    if result.secret_candidates:
        lines.append("")
        lines.append("## 🔑 Hardcoded Secrets Detected")
        lines.append("")
        lines.append("| File | Line | Type |")
        lines.append("|------|------|------|")
        for s in result.secret_candidates:
            lines.append(f"| `{s.file_path}` | {s.line_number} | {s.secret_type} |")

    lines.append("")
    lines.append("---")
    lines.append(f"*Generated by envdoctor v1.0.0*")

    return "\n".join(lines)

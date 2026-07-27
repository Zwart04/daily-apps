"""
envdoctor.cli — Command-line interface.

Handles argument parsing and orchestrates the scan-analysis-report pipeline.
"""

from __future__ import annotations

import argparse
import pathlib
import sys
from typing import NoReturn, Optional

from envdoctor import __version__
from envdoctor.types import ScanResult
from envdoctor.scanner import scan_directory
from envdoctor.parser import parse_dotenv, find_dotenv_files
from envdoctor.analyzer import analyze
from envdoctor.reporter import report_text, report_json, report_markdown
from envdoctor.fixer import fix_generate_example, suggest_fixes


def build_parser() -> argparse.ArgumentParser:
    """Build the argument parser."""
    parser = argparse.ArgumentParser(
        prog="envdoctor",
        description="Environment Variable Diagnostic Tool — scan, validate, and document "
                    "all environment variables used in your project.",
        epilog="Examples:\n"
               "  envdoctor .                        # Scan current directory\n"
               "  envdoctor /path/to/project          # Scan specific project\n"
               "  envdoctor . --json                  # JSON output (for CI)\n"
               "  envdoctor . --markdown              # Markdown report\n"
               "  envdoctor . --fix                   # Generate .env.example\n"
               "  envdoctor . --verbose               # Detailed output\n"
               "  envdoctor . --no-color              # No ANSI colors\n"
               "  envdoctor --version                 # Show version\n"
               "  envdoctor --test                    # Run self-test\n",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "path",
        nargs="?",
        default=".",
        help="Project directory to scan (default: current directory)",
    )

    parser.add_argument(
        "--json",
        action="store_true",
        help="Output in JSON format (for CI integration)",
    )

    parser.add_argument(
        "--markdown",
        action="store_true",
        help="Output in Markdown format",
    )

    parser.add_argument(
        "--fix",
        action="store_true",
        help="Generate/update .env.example from scan results",
    )

    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Show detailed reference information",
    )

    parser.add_argument(
        "--no-color",
        action="store_true",
        help="Disable ANSI color codes in output",
    )

    parser.add_argument(
        "--max-files",
        type=int,
        default=5000,
        help="Maximum number of files to scan (default: 5000)",
    )

    parser.add_argument(
        "--test",
        action="store_true",
        help="Run self-test suite and exit",
    )

    parser.add_argument(
        "--version",
        action="store_true",
        help="Show version and exit",
    )

    return parser


def run_scan(project_path: str, max_files: int, verbose: bool) -> ScanResult:
    """
    Execute the full scan-analysis pipeline.

    Args:
        project_path: Directory to scan
        max_files: Maximum files to scan
        verbose: Verbose output

    Returns:
        Complete ScanResult
    """
    if verbose:
        print(f"Scanning {project_path} ...", file=sys.stderr)

    # Phase 1: Scan source files for env var references
    env_var_refs, secret_candidates, files_scanned, errors = scan_directory(
        project_path, verbose=verbose, max_files=max_files,
    )

    # Phase 2: Parse .env files
    dotenv_files = find_dotenv_files(project_path)
    dotenv_entries = []
    dotenv_example_entries = []

    for f in dotenv_files:
        entries = parse_dotenv(f)
        if "example" in f or "sample" in f or "dist" in f or "template" in f:
            dotenv_example_entries.extend(entries)
        else:
            dotenv_entries.extend(entries)

    # Phase 3: Analyze
    result = analyze(
        project_path=project_path,
        env_var_refs=env_var_refs,
        dotenv_entries=dotenv_entries,
        dotenv_example_entries=dotenv_example_entries,
        secret_candidates=secret_candidates,
        files_scanned=files_scanned,
        errors=errors,
    )

    return result


def run_test() -> int:
    """Run self-test suite."""
    import doctest
    import envdoctor.types
    import envdoctor.scanner
    import envdoctor.parser
    import envdoctor.analyzer
    import envdoctor.reporter
    import envdoctor.fixer

    modules = [
        envdoctor.types,
        envdoctor.scanner,
        envdoctor.parser,
        envdoctor.analyzer,
        envdoctor.reporter,
        envdoctor.fixer,
    ]

    failed = 0
    for module in modules:
        results = doctest.testmod(module, verbose=False)
        if results.failed:
            print(f"  FAIL: {module.__name__} ({results.failed} tests)", file=sys.stderr)
            failed += results.failed

    # Run functional tests
    print("Running functional tests...", file=sys.stderr)
    func_failed = _run_functional_tests()
    failed += func_failed

    if failed == 0:
        print("✅ All tests passed", file=sys.stderr)
        return 0
    else:
        print(f"❌ {failed} test(s) failed", file=sys.stderr)
        return 1


def _run_functional_tests() -> int:
    """Run functional integration tests against temporary fixtures."""
    import tempfile
    import os

    failed = 0

    # Test 1: Basic env var scanning
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create a test Python file
        test_file = os.path.join(tmpdir, "config.py")
        with open(test_file, "w") as f:
            f.write("import os\n")
            f.write("API_KEY = os.environ.get('MY_API_KEY')\n")
            f.write("DB_URL = os.environ['DATABASE_URL']\n")
            f.write("SECRET = os.getenv('APP_SECRET')\n")

        # Create a Node.js file
        test_js = os.path.join(tmpdir, "app.js")
        with open(test_js, "w") as f:
            f.write("const port = process.env.PORT;\n")
            f.write("const host = process.env.HOST || 'localhost';\n")
            f.write("const apiKey = process.env['API_KEY'];\n")

        # Create a shell script
        test_sh = os.path.join(tmpdir, "deploy.sh")
        with open(test_sh, "w") as f:
            f.write("#!/bin/bash\n")
            f.write("echo $DEPLOY_ENV\n")
            f.write("echo ${BUILD_NUMBER}\n")

        # Create .env.example
        with open(os.path.join(tmpdir, ".env.example"), "w") as f:
            f.write("MY_API_KEY=\n")
            f.write("DATABASE_URL=\n")
            f.write("PORT=3000\n")
            f.write("UNUSED_VAR=\n")

        # Create .env
        with open(os.path.join(tmpdir, ".env"), "w") as f:
            f.write("MY_API_KEY=test123\n")
            f.write("DATABASE_URL=postgres://localhost/db\n")
            f.write("PORT=3000\n")
            f.write("EMPTY_VAR=\n")
            f.write("#COMMENTED_VAR=value\n")

        result = run_scan(tmpdir, max_files=1000, verbose=False)

        tests = [
            ("found MY_API_KEY", "MY_API_KEY" in result.referenced_in_code),
            ("found DATABASE_URL", "DATABASE_URL" in result.referenced_in_code),
            ("found APP_SECRET", "APP_SECRET" in result.referenced_in_code),
            ("found PORT", "PORT" in result.referenced_in_code),
            ("found HOST", "HOST" in result.referenced_in_code),
            ("found DEPLOY_ENV", "DEPLOY_ENV" in result.referenced_in_code),
            ("found BUILD_NUMBER", "BUILD_NUMBER" in result.referenced_in_code),
            ("MY_API_KEY in defined_in_env", "MY_API_KEY" in result.defined_in_env),
            ("EMPTY_VAR in empty_in_env", "EMPTY_VAR" in result.empty_in_env),
            ("COMMENTED_VAR in commented_in_env", "COMMENTED_VAR" in result.commented_in_env),
            ("APP_SECRET missing_from_env", "APP_SECRET" in result.missing_from_env),
            ("UNUSED_VAR unused_in_example", "UNUSED_VAR" in result.unused_in_example),
            ("APP_SECRET missing_from_example", "APP_SECRET" in result.missing_from_example),
            ("files_scanned > 0", result.files_scanned > 0),
        ]

        for name, passed in tests:
            if not passed:
                print(f"  FAIL: {name}", file=sys.stderr)
                failed += 1

        if failed:
            print(f"  DEBUG: referenced_in_code={result.referenced_in_code}", file=sys.stderr)
            print(f"  DEBUG: defined_in_env={result.defined_in_env}", file=sys.stderr)
            print(f"  DEBUG: defined_in_example={result.defined_in_example}", file=sys.stderr)
            print(f"  DEBUG: missing_from_env={result.missing_from_env}", file=sys.stderr)

    return failed


def main(argv: Optional[list] = None) -> int:
    """
    Main entry point for envdoctor CLI.

    Args:
        argv: Command-line arguments (defaults to sys.argv[1:])

    Returns:
        Exit code (0 = success, 1 = issues found, 2 = error)
    """
    parser = build_parser()
    args = parser.parse_args(argv)

    # Handle special flags
    if args.version:
        print(f"envdoctor v{__version__}")
        return 0

    if args.test:
        return run_test()

    # Resolve path
    try:
        project_path = str(pathlib.Path(args.path).resolve())
    except (OSError, ValueError) as e:
        print(f"Error: Invalid path '{args.path}': {e}", file=sys.stderr)
        return 2

    # Run scan
    try:
        result = run_scan(project_path, args.max_files, args.verbose)
    except (FileNotFoundError, NotADirectoryError) as e:
        print(f"Error: {e}", file=sys.stderr)
        return 2
    except PermissionError as e:
        print(f"Error: Permission denied: {e}", file=sys.stderr)
        return 2

    # Handle --fix mode
    if args.fix:
        if result.missing_from_example or result.missing_from_env:
            example_path = pathlib.Path(project_path) / ".env.example"
            content = fix_generate_example(result, str(example_path))
            print(f"✅ Generated .env.example with {len(result.referenced_in_code | result.defined_in_env)} variables")
        else:
            print("✅ .env.example is already up-to-date")
        return 0

    # Generate report
    if args.json:
        output = report_json(result)
    elif args.markdown:
        output = report_markdown(result)
    else:
        output = report_text(result, no_color=args.no_color, verbose=args.verbose)

    print(output)

    # Return exit code based on findings
    if result.total_issues > 0:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())

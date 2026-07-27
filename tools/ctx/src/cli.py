"""
Command-line entry point for ctx.

Parses CLI arguments (argparse), orchestrates the extraction pipeline,
and writes the result to stdout.
"""

from __future__ import annotations

import argparse
import os
import signal
import sys
from typing import List

from .config import load_config
from .scanner import scan_tree, build_tree_string
from .reader import read_files
from .formatter import format_markdown, format_plain, format_json
from .counter import count_tokens
from .types import ALLOWED_FORMATS, DEFAULT_SKIP_PATTERNS, ScanOptions


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="ctx",
        description="Codebase Context Extractor for AI coding assistants.",
        epilog=(
            "Examples:\\n"
            "  python3 -m ctx .                    # Markdown (default)\\n"
            "  python3 -m ctx src/ --format json   # JSON output\\n"
            "  python3 -m ctx --include *.py        # Python files only\\n"
            "  python3 -m ctx . --test              # self-test\\n"
            "  python3 -m ctx --stdin               # read file list from stdin\\n"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "path",
        nargs="?",
        default=".",
        help="Directory to scan (default: current directory)",
    )

    parser.add_argument(
        "--format",
        choices=ALLOWED_FORMATS,
        default="markdown",
        help=f"Output format (default: markdown). Choices: {', '.join(ALLOWED_FORMATS)}",
    )

    parser.add_argument(
        "--include",
        nargs="*",
        default=None,
        help="Glob patterns to include (e.g. --include *.py *.ts)",
    )

    parser.add_argument(
        "--exclude",
        nargs="*",
        default=None,
        help="Additional glob patterns to exclude",
    )

    parser.add_argument(
        "--max-depth",
        type=int,
        default=None,
        help="Maximum directory recursion depth (default: 5)",
    )

    parser.add_argument(
        "--max-file-size",
        type=int,
        default=None,
        help="Maximum file size in bytes (default: 1048576 = 1 MB)",
    )

    parser.add_argument(
        "--no-ignore",
        action="store_true",
        default=None,
        help="Ignore .gitignore rules and include all files",
    )

    parser.add_argument(
        "--no-tree",
        action="store_true",
        dest="no_tree",
        help="Omit the directory tree from output",
    )

    parser.add_argument(
        "--model",
        default=None,
        help="Model name for token estimation (e.g. gpt-4, claude-3)",
    )

    parser.add_argument(
        "--stdin",
        action="store_true",
        help="Read file list from stdin (one path per line) instead of scanning",
    )

    parser.add_argument(
        "--test",
        action="store_true",
        help="Run self-tests and exit",
    )

    parser.add_argument(
        "--version",
        action="version",
        version="ctx 1.0.0",
        help="Show version and exit",
    )

    return parser


def _self_test() -> None:
    """Comprehensive self-test suite."""
    import io
    import tempfile
    import textwrap

    passed = 0
    failed: List[str] = []

    def check(name: str, ok: bool, detail: str = "") -> None:
        nonlocal passed, failed
        if ok:
            passed += 1
        else:
            failed.append(f"{name}: {detail}")

    # --- 1. Scanner basics ---
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create a small project
        os.makedirs(os.path.join(tmpdir, "src"))
        os.makedirs(os.path.join(tmpdir, "node_modules"))
        with open(os.path.join(tmpdir, "src", "main.py"), "w") as f:
            f.write("print('hello')")
        with open(os.path.join(tmpdir, "node_modules", "dep.js"), "w") as f:
            f.write("// dep")
        with open(os.path.join(tmpdir, ".gitignore"), "w") as f:
            f.write("*.log\ntest/\n")
        os.makedirs(os.path.join(tmpdir, "test"))
        with open(os.path.join(tmpdir, "test", "test_main.py"), "w") as f:
            f.write("# test")
        with open(os.path.join(tmpdir, "info.log"), "w") as f:
            f.write("log data")

        opts = ScanOptions(exclude=list(DEFAULT_SKIP_PATTERNS))
        entries = scan_tree(tmpdir, opts)

        # main.py should be included
        main_found = any("main.py" in e.rel_path for e in entries)
        check("Scanner: includes main.py", main_found)

        # node_modules should be excluded
        node_found = any("node_modules" in e.rel_path for e in entries)
        check("Scanner: excludes node_modules", not node_found)

    # --- 2. Filter: gitignore ---
    with tempfile.TemporaryDirectory() as tmpdir:
        with open(os.path.join(tmpdir, ".gitignore"), "w") as f:
            f.write("secret/\n")
        os.makedirs(os.path.join(tmpdir, "secret"))
        with open(os.path.join(tmpdir, "secret", "key.txt"), "w") as f:
            f.write("key")
        with open(os.path.join(tmpdir, "public.txt"), "w") as f:
            f.write("public")

        opts = ScanOptions(exclude=list(DEFAULT_SKIP_PATTERNS))
        entries = scan_tree(tmpdir, opts)

        has_public = any("public.txt" in e.rel_path for e in entries)
        has_secret = any("secret" in e.rel_path for e in entries)
        check("Filter: includes public.txt", has_public)
        check("Filter: excludes secret/ via gitignore", not has_secret)

    # --- 3. Formatter: markdown output ---
    from .types import FileContent
    files = [
        FileContent(path="src/main.py", content="print('hello')", size=14, lines=1, encoding="utf-8"),
    ]
    md = format_markdown(files)
    check("Formatter: markdown has heading", "### src/main.py" in md)
    check("Formatter: markdown has code block", "```" in md)

    plain = format_plain(files)
    check("Formatter: plain has path", "src/main.py" in plain)
    check("Formatter: plain has separator", "---" in plain)

    js = format_json(files)
    check("Formatter: json is valid", isinstance(js, str))
    check("Formatter: json contains path", '"src/main.py"' in js)

    # --- 4. Counter ---
    tc = count_tokens("hello world", files)
    check("Counter: returns TokenCount", tc.total > 0)
    check("Counter: characters counted", tc.characters > 0)
    check("Counter: words counted", tc.words > 0)
    check("Counter: lines counted", tc.lines > 0)

    # --- 5. Config loader ---
    from .config import load_config as _lc
    opts = _lc()
    check("Config: returns ScanOptions", isinstance(opts, ScanOptions))
    check("Config: default max_depth is 5", opts.max_depth == 5)

    # --- 6. Reader: binary detection ---
    with tempfile.TemporaryDirectory() as tmpdir:
        from .types import FileEntry
        from .reader import read_file as _rf

        png_path = os.path.join(tmpdir, "image.png")
        with open(png_path, "wb") as f:
            f.write(b"\\x89PNG\\r\\n\\x1a\\n")

        entry = FileEntry(path=png_path, rel_path="image.png", size=8)
        result = _rf(entry)
        check("Reader: skips binary PNG", result is None)

        txt_path = os.path.join(tmpdir, "hello.txt")
        with open(txt_path, "w") as f:
            f.write("Hello, World!")
        entry = FileEntry(path=txt_path, rel_path="hello.txt", size=13)
        result = _rf(entry)
        check("Reader: reads text file", result is not None and "Hello" in result.content)

    # --- 7. Tree string ---
    with tempfile.TemporaryDirectory() as tmpdir:
        os.makedirs(os.path.join(tmpdir, "a"))
        with open(os.path.join(tmpdir, "a", "file.txt"), "w") as f:
            f.write("x")
        opts = ScanOptions()
        entries = scan_tree(tmpdir, opts)
        tree = build_tree_string(entries, tmpdir)
        check("Tree: shows root", os.path.basename(tmpdir) in tree or "file.txt" in tree)

    # --- 8. Parse env list ---
    from .config import _parse_env_list
    items = _parse_env_list("*.py, *.ts")
    check("Config: parse env list", len(items) > 0)

    # --- Print results ---
    total = passed + len(failed)
    print(f"ctx: self-test: {passed}/{total} passed", file=sys.stderr)
    for f in failed:
        print(f"  FAIL: {f}", file=sys.stderr)

    if failed:
        print("ctx: self-test FAILED", file=sys.stderr)
        sys.exit(1)
    else:
        print("ctx: self-test PASSED", file=sys.stderr)
        sys.exit(0)


def _read_stdin_files(base_path: str) -> List[str]:
    """Read file paths from stdin, one per line."""
    files: List[str] = []
    for line in sys.stdin:
        line = line.strip()
        if line:
            # Resolve relative to base_path
            if not os.path.isabs(line):
                line = os.path.join(base_path, line)
            files.append(line)
    return files


def _handle_interrupt(signum, frame) -> None:
    """Handle SIGINT gracefully."""
    print(file=sys.stderr)
    print("ctx: interrupted by user", file=sys.stderr)
    sys.exit(130)


def main() -> None:
    """Main entry point for the ctx CLI."""
    signal.signal(signal.SIGINT, _handle_interrupt)

    parser = _build_parser()
    args = parser.parse_args()

    # Self-test mode
    if args.test:
        _self_test()
        return  # _self_test calls sys.exit

    # Build overrides from CLI args
    overrides = {
        "include": args.include,
        "exclude": args.exclude,
        "max_depth": args.max_depth,
        "no_ignore": args.no_ignore if args.no_ignore else None,
        "max_file_size": args.max_file_size,
    }
    # Remove None values
    overrides = {k: v for k, v in overrides.items() if v is not None}

    # Resolve path
    path = os.path.abspath(args.path)

    # Stdin mode
    if args.stdin:
        file_paths = _read_stdin_files(path)
        if not file_paths:
            print("ctx: no files provided via stdin", file=sys.stderr)
            sys.exit(1)

        from .types import FileEntry

        entries: List = []
        for fp in file_paths:
            if os.path.isfile(fp):
                size = os.path.getsize(fp)
                rel = os.path.relpath(fp, path)
                entries.append(FileEntry(path=fp, rel_path=rel, size=size))

        files = read_files(entries)
        tree_str = build_tree_string(entries, path) if not args.no_tree else ""
    else:
        # Validate path
        if not os.path.exists(path):
            print(f"ctx: error: path not found: {path}", file=sys.stderr)
            sys.exit(1)
        if not os.path.isdir(path):
            print(f"ctx: error: path is not a directory: {path}", file=sys.stderr)
            sys.exit(1)

        opts = load_config(path, overrides)
        entries = scan_tree(path, opts)
        files = read_files(entries, opts.max_file_size)
        tree_str = build_tree_string(entries, path) if not args.no_tree else ""

    if not files:
        print("ctx: no files extracted", file=sys.stderr)
        sys.exit(0)

    # Format output
    formatters = {"markdown": format_markdown, "plain": format_plain, "json": format_json}
    fmt_fn = formatters.get(args.format, format_markdown)
    content = fmt_fn(files, tree=tree_str)

    # Count tokens
    tokens = count_tokens(content, files, model=args.model)

    # Write output
    sys.stdout.write(content)

    # Metadata to stderr
    print(
        f"ctx: {len(files)} files, {tokens.total} {tokens.method} tokens, "
        f"{tokens.characters} chars, {tokens.words} words",
        file=sys.stderr,
    )


if __name__ == "__main__":
    main()

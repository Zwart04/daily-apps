"""
envdoctor.scanner — Source file scanner for environment variable references.

Scans project directories for files containing environment variable
references using pattern matching for various languages and formats.
Zero dependencies — pure Python stdlib.
"""

from __future__ import annotations

import os
import re
import pathlib
from typing import Dict, List, Pattern, Set, Tuple

from envdoctor.types import EnvVarRef, SecretCandidate

# Default patterns to search for env var references
# Ordered by specificity (most specific first for context extraction)
ENV_PATTERNS: List[Tuple[str, Pattern[str]]] = [
    # Python: os.environ.get('VAR'), os.getenv('VAR')
    ("os.environ", re.compile(r"""os\.environ(?:\.get)?\s*\(\s*['"]([^'"]+)['"]""")),
    ("os.getenv", re.compile(r"""os\.getenv\s*\(\s*['"]([^'"]+)['"]""")),
    # Python: os.environ['VAR']
    ("os.environ_bracket", re.compile(r"""os\.environ\s*\[\s*['"]([^'"]+)['"]""")),
    # Node.js: process.env.VAR, process.env['VAR']
    ("process.env", re.compile(r"""process\.env\.([A-Z_][A-Z0-9_]*)""")),
    ("process.env_bracket", re.compile(r"""process\.env\[\s*['"]([^'"]+)['"]""")),
    # Deno/Bun: Deno.env.get('VAR')
    ("deno.env", re.compile(r"""Deno\.env\.(?:get|toObject)\s*\(\s*['"]([^'"]+)['"]""")),
    # Shell: $VAR (but not ${VAR:-default}), ${VAR}
    ("shell_var", re.compile(r"""\$([A-Z_][A-Z0-9_]*)""")),
    ("shell_brace", re.compile(r"""\$\{([A-Z_][A-Z0-9_]+)(?::[-+?].*?)?\}""")),
    # Docker Compose / YAML: ${VAR:-default}, ${VAR}
    ("compose_var", re.compile(r"""\$\{([A-Z_][A-Z0-9_]+)(?::[-+?].*?)?\}""")),
    # GitHub Actions: ${{ env.VAR }}, ${{ secrets.VAR }}
    ("github_actions", re.compile(r"""\${{?\s*env\.([A-Z_][A-Z0-9_]*)""")),
    ("github_secrets", re.compile(r"""\${{?\s*secrets\.([A-Z_][A-Z0-9_]*)""")),
    # Makefile: $(VAR), ${VAR}
    ("make_var", re.compile(r"""\$\(([A-Z_][A-Z0-9_]*)\)""")),
    # .env files: VAR=value
    ("dotenv_key", re.compile(r"""^([A-Z_][A-Z0-9_]*)\s*=""")),
    # env: in Dockerfile/Compose
    ("docker_env", re.compile(r"""ENV\s+([A-Z_][A-Z0-9_]*)""", re.IGNORECASE)),
    # env: ... - VAR in docker-compose
    ("compose_env_key", re.compile(r"""-\s*([A-Z_][A-Z0-9_]*)\s*=?\s*""")),
    # Spring Boot / Java: System.getenv("VAR")
    ("java_getenv", re.compile(r"""System\.(?:getenv|getProperty)\s*\(\s*['"]([^'"]+)['"]""")),
    # Java: @Value("${VAR:default}")
    ("spring_value", re.compile(r"""@Value\s*\(\s*['"]\$\{([^:}]+)""")),
    # .NET: Environment.GetEnvironmentVariable("VAR")
    ("dotnet_env", re.compile(r"""Environment\.GetEnvironmentVariable\s*\(\s*['"]([^'"]+)['"]""")),
    # Rails: ENV['VAR']
    ("ruby_env", re.compile(r"""ENV\[\s*['"]([^'"]+)['"]""")),
    # Go: os.Getenv("VAR")
    ("go_getenv", re.compile(r"""os\.Getenv\s*\(['"]([^'"]+)['"]""")),
    # Kubernetes YAML: $(VAR), $(VAR_NAME)
    ("k8s_var", re.compile(r"""\$\(([A-Z_][A-Z0-9_]*)\)""")),
    # Terraform: var.VAR_NAME
    ("tf_var", re.compile(r"""var\.([A-Z_][A-Z0-9_]*)""")),
    # Ansible: {{ lookup('env', 'VAR') }}
    ("ansible_env", re.compile(r"""lookup\s*\(\s*['"]env['"]\s*,\s*['"]([^'"]+)['"]""")),
    # PHP: getenv('VAR')
    ("php_getenv", re.compile(r"""getenv\s*\(\s*['"]([^'"]+)['"]""")),
    # PHP: $_ENV['VAR']
    ("php_env", re.compile(r"""\$_ENV\[\s*['"]([^'"]+)['"]""")),
]

# Patterns for detecting potential hardcoded secrets
SECRET_PATTERNS: List[Tuple[str, Pattern[str], str]] = [
    ("api_key", re.compile(r"""(?i)(api[_-]?key|apikey)\s*[:=]\s*['\"]([^'\"]{8,})['\"]"""), "high"),
    ("password", re.compile(r"""(?i)(password|passwd|pwd)\s*[:=]\s*['\"]([^'\"]{4,})['\"]"""), "high"),
    ("token", re.compile(r"""(?i)(token|access_token|auth_token|secret_token)\s*[:=]\s*['\"]([^'\"]{8,})['\"]"""), "high"),
    ("secret_key", re.compile(r"""(?i)(secret_key|secretkey|secret)\s*[:=]\s*['\"]([^'\"]{8,})['\"]"""), "high"),
    ("private_key", re.compile(r"""-----BEGIN\s+(?:RSA\s+)?PRIVATE\s+KEY-----"""), "high"),
    ("jwt_token", re.compile(r"""eyJ[A-Za-z0-9_-]{10,}\.eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}"""), "medium"),
    ("aws_key", re.compile(r"""(?:^|[^A-Z0-9])(AKIA[0-9A-Z]{16})(?:$|[^A-Z0-9])"""), "high"),
    ("connection_string", re.compile(r"""(?i)(postgresql|mysql|mongodb|redis|amqp)://[^:]+:[^@]+@"""), "high"),
]

# Files/directories to skip
IGNORE_PATTERNS: List[str] = [
    "node_modules",
    ".git",
    "__pycache__",
    ".venv",
    "venv",
    "env",
    ".env",
    "dist",
    "build",
    ".next",
    "target",
    "vendor",
    ".tox",
    ".eggs",
    "*.pyc",
    "*.pyo",
    ".DS_Store",
    "*.jpg",
    "*.jpeg",
    "*.png",
    "*.gif",
    "*.ico",
    "*.svg",
    "*.woff",
    "*.woff2",
    "*.ttf",
    "*.eot",
    "*.zip",
    "*.tar.gz",
    "*.gz",
    "*.min.js",
    "*.min.css",
    "*.map",
    "package-lock.json",
    "yarn.lock",
    "pnpm-lock.yaml",
    "*.lock",
]

# Binary file extensions to skip
BINARY_EXTENSIONS: Set[str] = {
    ".pyc", ".pyo", ".jpg", ".jpeg", ".png", ".gif", ".ico",
    ".woff", ".woff2", ".ttf", ".eot", ".zip", ".tar", ".gz",
    ".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx",
    ".mp3", ".mp4", ".avi", ".mov", ".bin", ".exe", ".dll",
    ".o", ".so", ".a", ".lib", ".dmg", ".iso",
}

# File patterns that are specifically interesting for env var scanning
TARGET_FILES: Set[str] = {
    ".py", ".js", ".ts", ".jsx", ".tsx", ".rb", ".go", ".java",
    ".kt", ".sh", ".bash", ".zsh", ".fish", ".env", ".yml",
    ".yaml", ".toml", ".json", ".tf", ".hcl", ".php", ".cs",
    ".cfg", ".conf", ".ini", ".env.example", ".env.sample",
    "Dockerfile", "docker-compose.yml", "docker-compose.yaml",
    "Makefile", "Makefile.*", ".gitlab-ci.yml", ".github/workflows/",
}


def _should_ignore(file_path: pathlib.Path) -> bool:
    """Check if a file or directory should be skipped."""
    str_path = str(file_path)
    name = file_path.name

    # Check ignore patterns
    for pattern in IGNORE_PATTERNS:
        if "*" in pattern:
            # Simple glob matching
            import fnmatch
            if fnmatch.fnmatch(name, pattern) or fnmatch.fnmatch(str_path, pattern):
                return True
        elif pattern in str_path:
            return True

    # Check binary extensions
    if file_path.suffix.lower() in BINARY_EXTENSIONS:
        return True

    # Skip hidden files (except .env*)
    if name.startswith(".") and not name.startswith(".env"):
        return True

    return False


def _detect_file_type(file_path: pathlib.Path) -> str:
    """Detect the type of file for language-specific parsing."""
    suffix = file_path.suffix.lower()
    name = file_path.name

    type_map = {
        ".py": "python",
        ".js": "javascript",
        ".jsx": "javascript",
        ".ts": "typescript",
        ".tsx": "typescript",
        ".rb": "ruby",
        ".go": "go",
        ".java": "java",
        ".kt": "kotlin",
        ".sh": "shell",
        ".bash": "shell",
        ".zsh": "shell",
        ".fish": "shell",
        ".yml": "yaml",
        ".yaml": "yaml",
        ".json": "json",
        ".tf": "terraform",
        ".hcl": "terraform",
        ".php": "php",
        ".cs": "csharp",
        ".env": "dotenv",
        ".toml": "toml",
    }

    if name == "Dockerfile":
        return "dockerfile"
    if name.startswith("Makefile"):
        return "makefile"

    return type_map.get(suffix, "unknown")


def scan_file(file_path: pathlib.Path, verbose: bool = False) -> Tuple[List[EnvVarRef], List[SecretCandidate], str]:
    """
    Scan a single file for environment variable references and secrets.

    Returns:
        Tuple of (env_var_refs, secret_candidates, file_type)
    """
    refs: List[EnvVarRef] = []
    secrets: List[SecretCandidate] = []
    errors: List[str] = []

    try:
        content = file_path.read_text(encoding="utf-8", errors="replace")
    except (OSError, UnicodeDecodeError) as e:
        if verbose:
            errors.append(f"Cannot read {file_path}: {e}")
        return refs, secrets, "unknown"

    lines = content.split("\n")
    file_type = _detect_file_type(file_path)

    # Scan each line for env var references
    for line_num, line in enumerate(lines, 1):
        trimmed = line.strip()

        for pattern_name, pattern in ENV_PATTERNS:
            for match in pattern.finditer(trimmed):
                var_name = match.group(1)
                # Filter out common false positives
                if var_name in ("PATH", "HOME", "USER", "PWD", "SHELL", "TERM"):
                    continue
                # Skip very short names for shell patterns
                if pattern_name in ("shell_var", "make_var") and len(var_name) <= 2:
                    continue

                refs.append(EnvVarRef(
                    name=var_name,
                    file_path=str(file_path),
                    line_number=line_num,
                    context=trimmed[:120],  # Max context length
                    pattern_type=pattern_name,
                ))

        # Scan for secrets
        for secret_name, secret_pattern, confidence in SECRET_PATTERNS:
            for match in secret_pattern.finditer(trimmed):
                # Extract the actual secret value (group 2 or just the match)
                secret_val = match.group(2) if match.lastindex and match.lastindex >= 2 else match.group(0)
                # Skip if it contains obvious placeholder
                if any(p in secret_val.lower() for p in ["your_", "placeholder", "changeme", "<your", "xxxx"]):
                    continue
                secrets.append(SecretCandidate(
                    file_path=str(file_path),
                    line_number=line_num,
                    context=trimmed[:120],
                    secret_type=secret_name,
                    confidence=confidence,
                ))

    # Remove duplicates while preserving order
    seen_refs: Set[Tuple[str, str, int, str]] = set()
    unique_refs = []
    for ref in refs:
        key = (ref.name, ref.file_path, ref.line_number, ref.pattern_type)
        if key not in seen_refs:
            seen_refs.add(key)
            unique_refs.append(ref)

    seen_secrets: Set[Tuple[str, int, str]] = set()
    unique_secrets = []
    for secret in secrets:
        key = (secret.file_path, secret.line_number, secret.secret_type)
        if key not in seen_secrets:
            seen_secrets.add(key)
            unique_secrets.append(secret)

    return unique_refs, unique_secrets, file_type


def scan_directory(
    project_path: str,
    verbose: bool = False,
    max_files: int = 5000,
) -> Tuple[List[EnvVarRef], List[SecretCandidate], int, List[str]]:
    """
    Recursively scan a directory for environment variable references.

    Args:
        project_path: Root directory to scan
        verbose: Print progress to stderr
        max_files: Maximum files to scan

    Returns:
        Tuple of (all_refs, all_secrets, files_scanned, errors)
    """
    root = pathlib.Path(project_path).resolve()
    if not root.exists():
        raise FileNotFoundError(f"Directory not found: {project_path}")
    if not root.is_dir():
        raise NotADirectoryError(f"Not a directory: {project_path}")

    all_refs: List[EnvVarRef] = []
    all_secrets: List[SecretCandidate] = []
    errors: List[str] = []
    files_scanned = 0

    # Walk directory tree
    for dirpath, dirnames, filenames in os.walk(str(root)):
        current_dir = pathlib.Path(dirpath)

        # Filter ignored directories in-place (os.walk uses this)
        dirnames[:] = [
            d for d in dirnames
            if not _should_ignore(current_dir / d)
        ]

        if files_scanned >= max_files:
            errors.append(f"Reached max file limit ({max_files}), scan incomplete")
            break

        for filename in sorted(filenames):
            if files_scanned >= max_files:
                break

            file_path = current_dir / filename

            if _should_ignore(file_path):
                continue

            refs, secrets, _ft = scan_file(file_path, verbose=verbose)
            if refs or secrets:
                all_refs.extend(refs)
                all_secrets.extend(secrets)

            files_scanned += 1
            if verbose and files_scanned % 500 == 0:
                print(f"  Scanned {files_scanned} files...", file=__import__("sys").stderr)

    return all_refs, all_secrets, files_scanned, errors

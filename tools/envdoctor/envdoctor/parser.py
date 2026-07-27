"""
envdoctor.parser — Parse .env and .env.example files.

Handles the standard .env file format: KEY=VALUE with
support for comments (#), empty lines, and quoted values.
"""

from __future__ import annotations

import pathlib
import re
from typing import List, Optional

from envdoctor.types import DotEnvEntry


def _parse_dotenv_line(
    line: str,
    line_number: int,
    file_path: str,
) -> Optional[DotEnvEntry]:
    """
    Parse a single line from a .env file.

    Returns None for blank lines or lines that aren't key=value.
    """
    stripped = line.strip()

    # Skip empty lines
    if not stripped:
        return None

    # Check if the whole line is a comment
    is_comment = stripped.startswith("#")
    if is_comment:
        # Check if there's a commented-out env var
        # Pattern: # VAR=value or # VAR=
        commented_match = re.match(r"#\s*([A-Z_][A-Z0-9_]*)\s*=", stripped, re.IGNORECASE)
        if commented_match:
            return DotEnvEntry(
                key=commented_match.group(1),
                value="",
                file_path=file_path,
                line_number=line_number,
                has_value=False,
                is_comment=True,
            )
        return None

    # Parse key=value (allow export prefix)
    match = re.match(
        r"(?:export\s+)?([A-Z_][A-Z0-9_]*)\s*=\s*(.*)",
        stripped,
        re.IGNORECASE,
    )
    if not match:
        return None

    key = match.group(1)
    value_raw = match.group(2).strip()

    has_value = bool(value_raw)
    value = ""

    if has_value:
        # Remove surrounding quotes
        value = value_raw
        if (value.startswith('"') and value.endswith('"')) or \
           (value.startswith("'") and value.endswith("'")):
            # Remove quotes but keep inner content
            # Handle escaped quotes inside
            inner = value[1:-1]
            if value.startswith('"'):
                inner = inner.replace('\\"', '"').replace('\\n', '\n')
            value = inner
        else:
            # Strip inline comments for unquoted values
            comment_pos = value.find(" #")
            if comment_pos > 0:
                value = value[:comment_pos].strip()

    return DotEnvEntry(
        key=key,
        value=value,
        file_path=file_path,
        line_number=line_number,
        has_value=has_value,
        is_comment=False,
    )


def parse_dotenv(file_path: str) -> List[DotEnvEntry]:
    """
    Parse a .env or .env.example file.

    Args:
        file_path: Path to the .env file

    Returns:
        List of DotEnvEntry objects

    Raises:
        FileNotFoundError: If the file doesn't exist
        PermissionError: If the file can't be read
    """
    path = pathlib.Path(file_path)
    if not path.exists():
        return []

    content = path.read_text(encoding="utf-8", errors="replace")
    entries: List[DotEnvEntry] = []

    for line_num, line in enumerate(content.split("\n"), 1):
        entry = _parse_dotenv_line(line, line_num, file_path)
        if entry is not None:
            entries.append(entry)

    return entries


def find_dotenv_files(project_path: str) -> List[str]:
    """
    Find all .env and .env.* files in a project directory.

    Args:
        project_path: Root directory to search

    Returns:
        List of file paths
    """
    root = pathlib.Path(project_path).resolve()

    dotenv_patterns = [
        ".env",
        ".env.*",  # .env.example, .env.local, .env.production, etc.
        ".env.sample",
        ".env.template",
        ".env.dist",
    ]

    found: List[str] = []

    for pattern in dotenv_patterns:
        for path in root.glob(pattern):
            if path.is_file() and "ignore" not in path.name and "skip" not in path.name:
                found.append(str(path))

    # Also check parent directories for shared .env
    parent_env = root.parent / ".env"
    if parent_env.exists() and parent_env.is_file():
        found.append(str(parent_env))

    return sorted(found)


def generate_example_content(env_vars: set) -> str:
    """
    Generate .env.example content from a set of environment variable names.

    Args:
        env_vars: Set of variable names

    Returns:
        Formatted .env.example content as a string
    """
    lines = [
        "# Environment Variables",
        "# =======================",
        "# Copy this file to .env and fill in the values.",
        "# Run `envdoctor .` to validate your .env file.",
        "",
    ]

    for var in sorted(env_vars):
        lines.append(f"# {_generate_var_comment(var)}")
        lines.append(f"{var}=")
        lines.append("")

    return "\n".join(lines)


def _generate_var_comment(var_name: str) -> str:
    """Generate a helpful comment for an environment variable."""
    hints: dict = {
        "API_KEY": "API authentication key",
        "DATABASE_URL": "Database connection string",
        "DATABASE_HOST": "Database server hostname",
        "DATABASE_PORT": "Database server port",
        "DATABASE_NAME": "Database name",
        "DATABASE_USER": "Database username",
        "DATABASE_PASSWORD": "Database password",
        "REDIS_URL": "Redis connection URL",
        "REDIS_HOST": "Redis server hostname",
        "REDIS_PORT": "Redis server port",
        "REDIS_PASSWORD": "Redis password",
        "PORT": "Server port number",
        "HOST": "Server hostname",
        "NODE_ENV": "Node environment (development|production|test)",
        "PYTHON_ENV": "Python environment (development|production)",
        "DEBUG": "Enable debug mode (true|false)",
        "LOG_LEVEL": "Logging level (debug|info|warn|error)",
        "SECRET_KEY": "Secret key for encryption/signing",
        "JWT_SECRET": "JWT signing secret",
        "JWT_EXPIRY": "JWT token expiration time",
        "SESSION_SECRET": "Session encryption secret",
        "COOKIE_SECRET": "Cookie signing secret",
        "CORS_ORIGIN": "Allowed CORS origin(s)",
        "NEXT_PUBLIC_": "Public variable exposed to the browser",
        "REACT_APP_": "Public variable exposed to the browser",
        "VITE_": "Public variable exposed to the browser",
        "STRIPE_KEY": "Stripe API key",
        "STRIPE_SECRET": "Stripe secret key",
        "STRIPE_WEBHOOK_SECRET": "Stripe webhook signing secret",
        "SENDGRID_API_KEY": "SendGrid API key",
        "TWILIO_ACCOUNT_SID": "Twilio account SID",
        "TWILIO_AUTH_TOKEN": "Twilio auth token",
        "AWS_ACCESS_KEY_ID": "AWS access key ID",
        "AWS_SECRET_ACCESS_KEY": "AWS secret access key",
        "AWS_REGION": "AWS region (e.g. us-east-1)",
        "AWS_S3_BUCKET": "AWS S3 bucket name",
        "GOOGLE_CLIENT_ID": "Google OAuth client ID",
        "GOOGLE_CLIENT_SECRET": "Google OAuth client secret",
        "GITHUB_TOKEN": "GitHub personal access token",
        "GITHUB_CLIENT_ID": "GitHub OAuth client ID",
        "GITHUB_CLIENT_SECRET": "GitHub OAuth client secret",
        "OPENAI_API_KEY": "OpenAI API key",
        "ANTHROPIC_API_KEY": "Anthropic API key",
        "TELEGRAM_BOT_TOKEN": "Telegram bot token",
        "SLACK_BOT_TOKEN": "Slack bot token",
        "SLACK_WEBHOOK_URL": "Slack webhook URL",
        "DISCORD_BOT_TOKEN": "Discord bot token",
        "SENTRY_DSN": "Sentry DSN for error tracking",
        "DATADOG_API_KEY": "Datadog API key",
        "NEW_RELIC_LICENSE_KEY": "New Relic license key",
        "ADMIN_EMAIL": "Administrator email address",
        "ADMIN_PASSWORD": "Administrator password",
        "SMTP_HOST": "SMTP server hostname",
        "SMTP_PORT": "SMTP server port",
        "SMTP_USER": "SMTP username",
        "SMTP_PASS": "SMTP password",
        "SMTP_FROM": "SMTP from address",
        "RABBITMQ_URL": "RabbitMQ connection URL",
        "ELASTICSEARCH_URL": "Elasticsearch connection URL",
        "MONGODB_URI": "MongoDB connection URI",
        "MYSQL_URL": "MySQL connection URL",
        "POSTGRES_URL": "PostgreSQL connection URL",
    }

    # Check for prefix-based hints
    for prefix, hint in hints.items():
        if var_name.startswith(prefix):
            return hint

    # Check for suffix-based patterns
    if var_name.endswith("_KEY"):
        return "API or service key"
    if var_name.endswith("_SECRET"):
        return "Secret key or credential"
    if var_name.endswith("_TOKEN"):
        return "Authentication token"
    if var_name.endswith("_URL") or var_name.endswith("_URI"):
        return "Connection URL/URI"
    if var_name.endswith("_HOST"):
        return "Server hostname"
    if var_name.endswith("_PORT"):
        return "Server port number"
    if var_name.endswith("_USER") or var_name.endswith("_USERNAME"):
        return "Username credential"
    if var_name.endswith("_PASSWORD") or var_name.endswith("_PASS"):
        return "Password credential"
    if var_name.endswith("_EMAIL"):
        return "Email address"
    if var_name.endswith("_ID") or var_name.endswith("_SID"):
        return "Identifier or account SID"
    if var_name.endswith("_ENABLED"):
        return "Toggle or feature flag (true|false)"
    if var_name.endswith("_DIR") or var_name.endswith("_PATH"):
        return "Filesystem path or directory"

    return "Environment variable"

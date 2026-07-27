"""Configuration loader — env vars + optional .gittreerc file."""

import os

DEFAULTS = {
    "depth": 3,
    "timeout": 30,
    "color": True,
    "skip_dirs": "node_modules,.cache,__pycache__,venv,.venv,.git,.hg,.svn,build,dist,target,.next,.turbo,.svelte-kit,.nx,coverage,.nyc_output,.pytest_cache,.mypy_cache,.ruff_cache,.tox,.eggs,*.egg-info",
}


class Config:
    """Immutable configuration object with sensible defaults."""

    __slots__ = ("depth", "timeout", "color", "skip_dirs", "skip_set")

    def __init__(self, **kwargs):
        for k, v in DEFAULTS.items():
            setattr(self, k, kwargs.get(k, v))
        if isinstance(self.skip_dirs, str):
            self.skip_set = set(d.strip() for d in self.skip_dirs.split(",") if d.strip())
        else:
            self.skip_set = set(self.skip_dirs)

    def __repr__(self):
        items = ", ".join(f"{s}={getattr(self, s)}" for s in self.__slots__ if s != "skip_set")
        return f"Config({items})"


def _env_bool(key: str, default: bool) -> bool:
    val = os.environ.get(key, "").strip().lower()
    if val in ("1", "true", "yes", "on"):
        return True
    if val in ("0", "false", "no", "off"):
        return False
    return default


def _env_int(key: str, default: int) -> int:
    val = os.environ.get(key, "").strip()
    try:
        return int(val) if val else default
    except ValueError:
        return default


def load_config(rc_path: str | None = None) -> Config:
    """Load configuration from environment variables and optional rc file."""
    kwargs = {
        "depth": _env_int("GITTREE_DEPTH", DEFAULTS["depth"]),
        "timeout": _env_int("GITTREE_TIMEOUT", DEFAULTS["timeout"]),
        "color": _env_bool("GITTREE_COLOR", DEFAULTS["color"]),
        "skip_dirs": os.environ.get("GITTREE_SKIP_DIRS", DEFAULTS["skip_dirs"]),
    }

    # Parse optional .gittreerc (simple KEY=VALUE format, no shell eval)
    if not rc_path:
        rc_path = os.environ.get("GITTREE_RC", "")
    if rc_path and os.path.isfile(rc_path):
        with open(rc_path) as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" not in line:
                    continue
                key, _, val = line.partition("=")
                key = key.strip().upper()
                val = val.strip()
                if key == "DEPTH":
                    kwargs["depth"] = int(val)
                elif key == "TIMEOUT":
                    kwargs["timeout"] = int(val)
                elif key == "COLOR":
                    kwargs["color"] = val.lower() in ("1", "true", "yes")
                elif key == "SKIP_DIRS":
                    kwargs["skip_dirs"] = val

    return Config(**kwargs)

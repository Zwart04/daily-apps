"""
Entry point for ``python3 -m ctx``.

Allows the package to be run as a module:
    python3 -m ctx .
"""

from __future__ import annotations

from .cli import main

main()

#!/usr/bin/env python3
"""
envdoctor.__main__ — Allow `python -m envdoctor` execution.

Usage:
    python -m envdoctor [options] <path>
"""

from envdoctor.cli import main

if __name__ == "__main__":
    main()

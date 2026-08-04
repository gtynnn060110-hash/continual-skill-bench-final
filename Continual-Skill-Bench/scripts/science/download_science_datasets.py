#!/usr/bin/env python3
"""Download or query science task candidate sources.

This is a naming-compatible wrapper around `scrape_science_tasks.py`; it keeps
the science folder close to the `scripts/law/download_*` pattern.
"""

from __future__ import annotations

from scrape_science_tasks import main


if __name__ == "__main__":
    raise SystemExit(main())

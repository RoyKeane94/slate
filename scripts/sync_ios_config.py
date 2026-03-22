#!/usr/bin/env python3
"""
Sync SLATE_API_BASE_URL from the repo root .env into the iOS Config.swift.

Usage (from repo root):
    python3 scripts/sync_ios_config.py

Railway: open your service → Settings → Networking / Domains and copy the
public HTTPS URL (no trailing slash).
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ENV_PATH = ROOT / ".env"
CONFIG_SWIFT = ROOT / "slate_swift" / "Slate" / "slate" / "slate" / "Config.swift"


def read_slate_api_base_url() -> str | None:
    if not ENV_PATH.is_file():
        return None
    for raw in ENV_PATH.read_text().splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("SLATE_API_BASE_URL="):
            val = line.split("=", 1)[1].strip().strip('"').strip("'")
            return val
    return None


def main() -> int:
    url = read_slate_api_base_url()
    if not url:
        print(
            f"Add SLATE_API_BASE_URL to {ENV_PATH} (your Railway HTTPS URL, no trailing slash).",
            file=sys.stderr,
        )
        return 1
    placeholders = ("YOUR_APP", "YOUR_RAILWAY_URL", "example.com")
    if any(p in url for p in placeholders):
        print(
            "SLATE_API_BASE_URL still looks like a placeholder. Set it to your real Railway URL.",
            file=sys.stderr,
        )
        return 1

    url = url.rstrip("/")
    if not url.startswith("https://"):
        print("SLATE_API_BASE_URL should start with https://", file=sys.stderr)
        return 1

    if not CONFIG_SWIFT.is_file():
        print(f"Missing {CONFIG_SWIFT}", file=sys.stderr)
        return 1

    text = CONFIG_SWIFT.read_text()
    new_text, n = re.subn(
        r'(static let baseURL = ")([^"]*)(")',
        rf"\1{url}\3",
        text,
        count=1,
    )
    if n != 1:
        print("Could not find `static let baseURL = \"...\"` in Config.swift", file=sys.stderr)
        return 1

    CONFIG_SWIFT.write_text(new_text)
    print(f"Updated Config.baseURL → {url}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

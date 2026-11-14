#!/usr/bin/env python3
"""Prepare InStat auth for CI / scheduled runs.

Enables live InStat when any of these are present:
  - INSTAT_X_AUTH_TOKEN + INSTAT_AUTHORIZATION
  - INSTAT_AUTH_JSON (base64 auth.json)
  - existing headers cache / auth.json
  - INSTAT_DEDICATED_ACCOUNT=1 with HUDL_USERNAME/PASSWORD

Returns True if a live pull should be attempted.
"""

from __future__ import annotations

import base64
import json
import os
from pathlib import Path


def _headers_cache_path() -> Path:
    override = os.getenv("INSTAT_HEADERS_CACHE", "").strip()
    if override:
        return Path(override).expanduser()
    return Path.home() / ".cache" / "player-cards" / "instat_headers_cache.json"


def _write_headers_from_jwt_env() -> bool:
    x_token = os.getenv("INSTAT_X_AUTH_TOKEN", "").strip()
    authorization = os.getenv("INSTAT_AUTHORIZATION", "").strip()
    if not x_token or not authorization:
        return False
    cache = _headers_cache_path()
    cache.parent.mkdir(parents=True, exist_ok=True)
    cache.write_text(
        json.dumps(
            {
                "x-auth-token": x_token,
                "authorization": authorization,
                "source": "ci_env",
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    print(f"✅ Wrote InStat headers cache from JWT env → {cache}")
    return True


def _restore_auth_json() -> bool:
    """Decode INSTAT_AUTH_JSON (base64) into hudl-scraping/auth.json."""
    blob = os.getenv("INSTAT_AUTH_JSON", "").strip()
    if not blob:
        return False
    scraping = Path(
        os.getenv(
            "AUTOMATED_SCRAPING_ROOT",
            "/Users/emilyfehr8/CascadeProjects/automated-scraping",
        )
    )
    dest = scraping / "hudl-scraping" / "auth.json"
    dest.parent.mkdir(parents=True, exist_ok=True)
    try:
        dest.write_bytes(base64.b64decode(blob))
        print(f"✅ Restored auth.json from INSTAT_AUTH_JSON → {dest}")
        return True
    except Exception as e:
        print(f"⚠️ Failed to decode INSTAT_AUTH_JSON: {e}")
        return False


def has_live_auth() -> bool:
    if os.getenv("INSTAT_X_AUTH_TOKEN", "").strip() and os.getenv("INSTAT_AUTHORIZATION", "").strip():
        return True
    if os.getenv("INSTAT_AUTH_JSON", "").strip():
        return True
    if os.getenv("INSTAT_DEDICATED_ACCOUNT", "").strip() == "1" and os.getenv("HUDL_USERNAME", "").strip():
        return True
    if os.getenv("ALLOW_INSTAT_LOGIN", "").strip() == "1" and os.getenv("HUDL_USERNAME", "").strip():
        return True
    if _headers_cache_path().is_file():
        return True
    scraping = Path(os.getenv("AUTOMATED_SCRAPING_ROOT", ""))
    if scraping and (scraping / "hudl-scraping" / "auth.json").is_file():
        return True
    # local default path
    if Path("/Users/emilyfehr8/CascadeProjects/automated-scraping/hudl-scraping/auth.json").is_file():
        return True
    return False


def prepare_instat_auth() -> bool:
    """Materialize secrets onto disk and decide whether to run live InStat."""
    if os.getenv("WAREHOUSE_SKIP_INSTAT", "").strip().lower() in ("1", "true", "yes"):
        print("⏭️ WAREHOUSE_SKIP_INSTAT set — skipping live InStat")
        return False
    if os.getenv("INSTAT_SKIP_LIVE", "").strip().lower() in ("1", "true", "yes"):
        # Only honor explicit skip — do not auto-set this in CI anymore
        print("⏭️ INSTAT_SKIP_LIVE set — skipping live InStat")
        return False

    restored = False
    restored |= _write_headers_from_jwt_env()
    restored |= _restore_auth_json()

    # Dedicated account mode for scheduled bots (same as goalie hub CI)
    if os.getenv("HUDL_USERNAME", "").strip() and os.getenv("HUDL_PASSWORD", "").strip():
        os.environ.setdefault("INSTAT_DEDICATED_ACCOUNT", "1")
        os.environ.setdefault("ALLOW_INSTAT_LOGIN", "1")
        os.environ["DISABLE_AUTO_LOGIN"] = "0"
        os.environ.pop("INSTAT_NEVER_LOGIN", None)

    ok = has_live_auth()
    if ok:
        print("✅ InStat live auth available — scheduled pull will run")
    else:
        print("⚠️ No InStat auth — will mirror LLD artifacts only")
    return ok

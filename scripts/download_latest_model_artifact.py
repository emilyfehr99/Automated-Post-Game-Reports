#!/usr/bin/env python3

"""
Download the latest `nhl-model-artifacts` Actions artifact from GitHub and extract it.

This is useful on "no-retrain" days or non-CI environments where model binaries
are not committed to git.

Requires:
  - GITHUB_TOKEN env var (repo-scoped)
  - `requests` installed
"""

from __future__ import annotations

import io
import os
import zipfile
from pathlib import Path

import requests


OWNER = "emilyfehr99"
REPO = "Automated-Post-Game-Reports"
ARTIFACT_NAME = "nhl-model-artifacts"


def main() -> None:
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if not token:
        raise SystemExit("Missing GITHUB_TOKEN/GH_TOKEN")

    headers = {"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json"}
    sess = requests.Session()
    sess.headers.update(headers)

    # List artifacts (most recent first)
    url = f"https://api.github.com/repos/{OWNER}/{REPO}/actions/artifacts?per_page=50"
    r = sess.get(url, timeout=30)
    r.raise_for_status()
    arts = r.json().get("artifacts", [])
    target = None
    for a in arts:
        if a.get("name") == ARTIFACT_NAME and not a.get("expired", False):
            target = a
            break
    if not target:
        raise SystemExit(f"No artifact found named {ARTIFACT_NAME}")

    download_url = target.get("archive_download_url")
    if not download_url:
        raise SystemExit("Artifact missing archive_download_url")

    zr = sess.get(download_url, timeout=60)
    zr.raise_for_status()

    zf = zipfile.ZipFile(io.BytesIO(zr.content))
    zf.extractall(Path("."))
    print(f"DOWNLOADED_ARTIFACT_ID={target.get('id')}")


if __name__ == "__main__":
    main()


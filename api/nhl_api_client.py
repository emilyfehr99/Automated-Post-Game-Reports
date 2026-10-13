"""Deprecated shim — canonical client lives in utils/nhl_api_client.py."""

try:
    from utils.nhl_api_client import NHLAPIClient
except Exception:  # pragma: no cover
    from nhl_api_client import NHLAPIClient  # type: ignore

__all__ = ["NHLAPIClient"]

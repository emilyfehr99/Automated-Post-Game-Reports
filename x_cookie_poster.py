"""
Post to X using browser session cookies (auth_token + ct0).

No official X API credits required — uses the same internal endpoints as x.com.
"""

import asyncio
import os
from pathlib import Path

import twikit_x_patch

twikit_x_patch.apply()

from twikit import Client


class XCookiePoster:
    """Post tweets with media via X session cookies."""

    def __init__(self):
        self.auth_token = os.getenv("X_AUTH_TOKEN", "").strip()
        self.ct0 = os.getenv("X_CT0", "").strip()
        if not self.auth_token or not self.ct0:
            raise ValueError(
                "X_AUTH_TOKEN and X_CT0 are required for free cookie-based posting. "
                "Extract both from x.com → DevTools → Application → Cookies."
            )

        self.client = Client("en-US")
        self.client.set_cookies(
            {
                "auth_token": self.auth_token,
                "ct0": self.ct0,
            }
        )

    async def _post_async(self, text: str, image_path: Path) -> str:
        media_id = await self.client.upload_media(str(image_path))
        media_entities = [{"media_id": media_id, "tagged_users": []}]
        response, _ = await self.client.gql.create_tweet(
            False,
            text,
            media_entities,
            None,
            None,
            None,
            None,
            False,
            None,
            None,
            None,
        )
        if "errors" in response:
            errors = response.get("errors") or []
            raise RuntimeError(
                errors[0].get("message", "Failed to post tweet")
                if errors
                else "Failed to post tweet"
            )

        result = response["data"]["create_tweet"]["tweet_results"]["result"]
        tweet_id = result.get("rest_id") or (result.get("legacy") or {}).get("id_str")
        if not tweet_id:
            raise RuntimeError(f"Could not parse tweet id from X response: {result}")
        return str(tweet_id)

    def post_with_media(self, text: str, image_path: Path) -> str:
        """Upload image and post tweet. Returns tweet ID."""
        return asyncio.run(self._post_async(text, image_path))

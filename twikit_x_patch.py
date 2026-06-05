"""
Patch twikit for X's March 2026 webpack change (KEY_BYTE indices error).

Upstream d60/twikit on PyPI is broken; unclecode/twikit has the fix but we
apply it at runtime so GitHub Actions always gets a working client.
"""

import re


def apply() -> None:
    tx = __import__(
        "twikit.x_client_transaction.transaction",
        fromlist=["ClientTransaction"],
    )

    tx.ON_DEMAND_FILE_REGEX = re.compile(
        r""",(\d+):["']ondemand\.s["']""",
        flags=(re.VERBOSE | re.MULTILINE),
    )
    tx.ON_DEMAND_HASH_PATTERN = r',{}:"([0-9a-f]+)"'
    tx.INDICES_REGEX = re.compile(r"\[(\d+)\],\s*16")

    async def patched_get_indices(self, home_page_response, session, headers):
        key_byte_indices = []
        response = self.validate_response(home_page_response) or self.home_page_response
        body = str(response)
        idx_match = tx.ON_DEMAND_FILE_REGEX.search(body)
        if idx_match:
            chunk_idx = idx_match.group(1)
            hash_regex = re.compile(tx.ON_DEMAND_HASH_PATTERN.format(chunk_idx))
            hash_match = hash_regex.search(body)
            if hash_match:
                on_demand_file_url = (
                    "https://abs.twimg.com/responsive-web/client-web/"
                    f"ondemand.s.{hash_match.group(1)}a.js"
                )
                on_demand_file_response = await session.request(
                    method="GET",
                    url=on_demand_file_url,
                    headers=headers,
                )
                for item in tx.INDICES_REGEX.finditer(str(on_demand_file_response.text)):
                    key_byte_indices.append(item.group(1))
        if not key_byte_indices:
            raise Exception("Couldn't get KEY_BYTE indices")
        key_byte_indices = list(map(int, key_byte_indices))
        return key_byte_indices[0], key_byte_indices[1:]

    tx.ClientTransaction.get_indices = patched_get_indices

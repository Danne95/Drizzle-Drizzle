"""Private local profile loader for the entertainment oracle.

The profile file is intentionally not snapshotted or rendered directly.
"""

from __future__ import annotations

import json

from config import BASE_DIR

PRIVATE_PROFILE_PATH = BASE_DIR / "private" / "oracle_profile.json"


def load_private_oracle_profile() -> dict:
    """Load optional private oracle inputs from an ignored local JSON file."""
    if not PRIVATE_PROFILE_PATH.exists():
        return {}
    try:
        payload = json.loads(PRIVATE_PROFILE_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return payload if isinstance(payload, dict) else {}

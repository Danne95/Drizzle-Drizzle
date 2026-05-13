"""Reddit momentum collector.

This mockable module models the shape expected from a future Reddit API client.
"""

from __future__ import annotations

from datetime import datetime, timezone


def fetch_reddit_signals() -> list[dict]:
    fetched_at = datetime.now(timezone.utc).isoformat()
    return [
        {
            "ticker": "OPEN",
            "mentions": 1240,
            "mention_change_percent": 340,
            "sentiment": 0.62,
            "squeeze_language": True,
            "top_phrase": "OPEN could squeeze hard if volume keeps stacking",
            "source": "Demo Reddit Scanner",
            "fetched_at": fetched_at,
        },
        {
            "ticker": "GME",
            "mentions": 980,
            "mention_change_percent": 185,
            "sentiment": 0.48,
            "squeeze_language": True,
            "top_phrase": "classic meme basket waking up again",
            "source": "Demo Reddit Scanner",
            "fetched_at": fetched_at,
        },
        {
            "ticker": "SOFI",
            "mentions": 410,
            "mention_change_percent": 76,
            "sentiment": 0.34,
            "squeeze_language": False,
            "top_phrase": "fintech earnings setup has retail attention",
            "source": "Demo Reddit Scanner",
            "fetched_at": fetched_at,
        },
    ]

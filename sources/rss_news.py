"""RSS financial news collector.

This module is isolated so feed changes or future paid news APIs do not affect
the rest of the scanner.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import feedparser

from config import BASE_DIR, MAX_RSS_ITEMS_PER_FEED, RSS_FEEDS


def _normalize_entry(entry: Any, source_name: str) -> dict:
    published = getattr(entry, "published", "") or getattr(entry, "updated", "")
    return {
        "type": "rss_news",
        "title": getattr(entry, "title", "").strip(),
        "link": getattr(entry, "link", "").strip(),
        "published": published,
        "source": source_name,
        "summary": getattr(entry, "summary", "").strip(),
        "fetched_at": datetime.now(timezone.utc).isoformat(),
    }


def _load_mock_news() -> list[dict]:
    mock_path = BASE_DIR / "samples" / "mock_news.json"
    return json.loads(mock_path.read_text(encoding="utf-8"))


def fetch_rss_news(use_mock: bool = False) -> list[dict]:
    """Fetch RSS news items, falling back to mock news when feeds are unavailable."""
    if use_mock:
        return _load_mock_news()

    items: list[dict] = []
    for feed in RSS_FEEDS:
        parsed = feedparser.parse(feed["url"])
        for entry in parsed.entries[:MAX_RSS_ITEMS_PER_FEED]:
            item = _normalize_entry(entry, feed["name"])
            if item["title"]:
                items.append(item)

    return items or _load_mock_news()

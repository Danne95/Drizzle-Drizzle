"""Ticker and company alias extraction."""

from __future__ import annotations

import re

from config import COMMON_FALSE_TICKERS, TICKER_ALIASES

TICKER_PATTERN = re.compile(r"(?<![A-Za-z])\$?([A-Z]{1,5})(?![A-Za-z])")


def extract_tickers(text: str) -> list[str]:
    """Extract tickers using explicit aliases plus conservative uppercase matching."""
    found: set[str] = set()
    normalized = text.lower()

    for ticker, aliases in TICKER_ALIASES.items():
        if ticker.lower() in normalized:
            found.add(ticker)
            continue
        for alias in aliases:
            if alias.lower() in normalized:
                found.add(ticker)
                break

    for match in TICKER_PATTERN.findall(text):
        if match not in COMMON_FALSE_TICKERS and match in TICKER_ALIASES:
            found.add(match)

    return sorted(found)


def attach_tickers(news_items: list[dict]) -> list[dict]:
    enriched = []
    for item in news_items:
        text = f"{item.get('title', '')} {item.get('summary', '')}"
        copy = dict(item)
        copy["tickers"] = extract_tickers(text)
        enriched.append(copy)
    return enriched

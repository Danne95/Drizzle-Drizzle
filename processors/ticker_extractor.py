"""Ticker and company alias extraction."""

from __future__ import annotations

import re

from config import COMMON_FALSE_TICKERS

CASHTAG_PATTERN = re.compile(r"(?<![A-Za-z0-9])\$([A-Z]{1,5})(?![A-Za-z0-9])")
UPPERCASE_TICKER_PATTERN = re.compile(r"(?<![A-Za-z])([A-Z]{2,5})(?![A-Za-z])")
GENERIC_ALIASES = {
    "holdings",
    "technology",
    "technologies",
    "energy",
    "capital",
    "group",
    "global",
    "resources",
    "financial",
    "systems",
    "solutions",
    "therapeutics",
    "health",
    "medical",
    "new",
    "first",
    "american",
    "united",
}


def _company_aliases(symbol_universe: list[dict] | None = None) -> dict[str, list[str]]:
    aliases: dict[str, list[str]] = {}
    for item in symbol_universe or []:
        ticker = item.get("ticker", "").upper()
        company = item.get("company", "")
        if not ticker or not company:
            continue
        aliases.setdefault(ticker, [])
        if company not in aliases[ticker]:
            aliases[ticker].append(company)
    return aliases


def _alias_matches(text: str, alias: str) -> bool:
    alias = alias.strip()
    if len(alias) < 3:
        return False
    alias_lower = alias.lower()
    if alias_lower in GENERIC_ALIASES:
        return False
    if " " not in alias and len(alias) < 8:
        return False
    pattern = re.compile(rf"(?<![a-z0-9]){re.escape(alias_lower)}(?![a-z0-9])")
    return bool(pattern.search(text))


def extract_tickers(text: str, symbol_universe: list[dict] | None = None) -> list[str]:
    """Extract tickers from cashtags, exact uppercase symbols, and listed company names."""
    found: set[str] = set()
    normalized = text.lower()
    aliases = _company_aliases(symbol_universe)
    known_symbols = set(aliases)

    for ticker, names in aliases.items():
        for alias in names:
            if _alias_matches(normalized, alias):
                found.add(ticker)
                break

    for match in CASHTAG_PATTERN.findall(text):
        if match not in COMMON_FALSE_TICKERS:
            found.add(match)

    for match in UPPERCASE_TICKER_PATTERN.findall(text):
        if match not in COMMON_FALSE_TICKERS and (not known_symbols or match in known_symbols):
            found.add(match)

    return sorted(found)


def attach_tickers(news_items: list[dict], symbol_universe: list[dict] | None = None) -> list[dict]:
    enriched = []
    for item in news_items:
        text = f"{item.get('title', '')} {item.get('summary', '')}"
        copy = dict(item)
        copy["tickers"] = extract_tickers(text, symbol_universe=symbol_universe)
        enriched.append(copy)
    return enriched

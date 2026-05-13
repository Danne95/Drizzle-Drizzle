"""Listed symbol universe collector.

This source expands ticker detection beyond the small fallback alias list in
config.py. It downloads public NasdaqTrader symbol directories when available
and caches the last successful result locally.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from urllib.error import URLError
from urllib.request import urlopen

from config import DATA_DIR

NASDAQ_LISTED_URL = "https://www.nasdaqtrader.com/dynamic/SymDir/nasdaqlisted.txt"
OTHER_LISTED_URL = "https://www.nasdaqtrader.com/dynamic/SymDir/otherlisted.txt"
CACHE_PATH = DATA_DIR / "symbol_universe_cache.json"

SECURITY_SUFFIX_PATTERN = re.compile(
    r"\b(common stock|ordinary shares|class [a-z]|inc\.?|corp\.?|corporation|company|"
    r"limited|ltd\.?|plc|holdings?|group|sa|adr|ads|unit|warrant|rights?)\b",
    re.IGNORECASE,
)


def _clean_company_name(name: str) -> str:
    name = name.split(" - ")[0]
    name = SECURITY_SUFFIX_PATTERN.sub("", name)
    name = re.sub(r"\s+", " ", name)
    return name.strip(" ,.-")


def _parse_pipe_file(text: str, symbol_key: str, name_key: str) -> list[dict]:
    lines = [line for line in text.splitlines() if line and not line.startswith("File Creation Time")]
    if not lines:
        return []
    headers = lines[0].split("|")
    symbol_idx = headers.index(symbol_key)
    name_idx = headers.index(name_key)
    rows = []
    for line in lines[1:]:
        parts = line.split("|")
        if len(parts) <= max(symbol_idx, name_idx):
            continue
        symbol = parts[symbol_idx].strip()
        if not symbol or "$" in symbol or "." in symbol or len(symbol) > 5:
            continue
        company = _clean_company_name(parts[name_idx].strip())
        if company:
            rows.append({"ticker": symbol, "company": company})
    return rows


def _download_universe() -> list[dict]:
    with urlopen(NASDAQ_LISTED_URL, timeout=12) as response:
        nasdaq_text = response.read().decode("utf-8", errors="replace")
    with urlopen(OTHER_LISTED_URL, timeout=12) as response:
        other_text = response.read().decode("utf-8", errors="replace")

    universe = _parse_pipe_file(nasdaq_text, "Symbol", "Security Name")
    universe.extend(_parse_pipe_file(other_text, "ACT Symbol", "Security Name"))
    return sorted({item["ticker"]: item for item in universe}.values(), key=lambda item: item["ticker"])


def _fallback_universe() -> list[dict]:
    return []


def fetch_symbol_universe() -> list[dict]:
    """Return a broad ticker universe, using cache/fallback if the network fails."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    try:
        universe = _download_universe()
        if universe:
            CACHE_PATH.write_text(json.dumps(universe, indent=2), encoding="utf-8")
            return universe
    except (OSError, URLError, ValueError):
        pass

    if CACHE_PATH.exists():
        return json.loads(CACHE_PATH.read_text(encoding="utf-8"))
    return _fallback_universe()

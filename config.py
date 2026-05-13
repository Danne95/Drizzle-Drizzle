"""Application configuration for the local market intelligence scanner."""

from __future__ import annotations

from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
REPORTS_DIR = BASE_DIR / "reports"

APP_NAME = "Drizzle Drizzle Market Oracle"

RSS_FEEDS = [
    {
        "name": "Yahoo Finance",
        "url": "https://finance.yahoo.com/news/rssindex",
    },
    {
        "name": "MarketWatch",
        "url": "https://feeds.marketwatch.com/marketwatch/topstories/",
    },
    {
        "name": "CNBC Markets",
        "url": "https://www.cnbc.com/id/100003114/device/rss/rss.html",
    },
]

MAX_RSS_ITEMS_PER_FEED = 15
HTTP_TIMEOUT_SECONDS = 12

SERIOUS_KEYWORDS = {
    "acquisition": 3.2,
    "merger": 3.0,
    "contract": 2.8,
    "partnership": 2.4,
    "earnings": 2.2,
    "guidance": 2.0,
    "upgrade": 1.9,
    "approval": 2.7,
    "fda": 2.8,
    "buyback": 2.0,
    "dividend": 1.4,
}

SPECULATIVE_KEYWORDS = {
    "short squeeze": 4.0,
    "squeeze": 3.3,
    "meme": 3.0,
    "rocket": 2.4,
    "yolo": 2.2,
    "halt": 2.1,
    "unusual volume": 2.8,
    "volume spike": 2.8,
    "bankruptcy": 2.2,
    "reverse split": 2.3,
    "penny stock": 2.5,
}

THEME_KEYWORDS = {
    "AI": ["ai", "artificial intelligence", "machine learning", "gpu", "data center"],
    "Defense": ["defense", "pentagon", "drone", "missile", "army", "navy"],
    "Biotech": ["fda", "trial", "drug", "therapy", "clinical", "approval"],
    "Energy": ["oil", "gas", "solar", "nuclear", "uranium", "battery"],
    "Crypto": ["bitcoin", "crypto", "ethereum", "blockchain"],
}

# Compact dictionary that keeps ticker extraction explainable and easy to extend.
TICKER_ALIASES = {
    "AAPL": ["Apple"],
    "AMD": ["AMD", "Advanced Micro Devices"],
    "AMZN": ["Amazon"],
    "BABA": ["Alibaba"],
    "COIN": ["Coinbase"],
    "IBM": ["IBM"],
    "GME": ["GameStop", "Gamestop"],
    "GOOGL": ["Alphabet", "Google"],
    "META": ["Meta", "Facebook"],
    "MSFT": ["Microsoft"],
    "NVDA": ["Nvidia", "NVIDIA"],
    "OKLO": ["Oklo"],
    "PLTR": ["Palantir"],
    "RIVN": ["Rivian"],
    "SMCI": ["Super Micro", "Supermicro"],
    "SOFI": ["SoFi"],
    "TSLA": ["Tesla"],
}

COMMON_FALSE_TICKERS = {
    "A",
    "AI",
    "AM",
    "CEO",
    "CFO",
    "ETF",
    "EV",
    "FDA",
    "IPO",
    "NYSE",
    "SEC",
    "USA",
}

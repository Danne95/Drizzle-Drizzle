"""Market movers collector.

The first version uses deterministic demo data. Replace this module with a
broker/data-provider API later without changing processors or reporting.
"""

from __future__ import annotations

from datetime import datetime, timezone


def fetch_market_movers() -> list[dict]:
    fetched_at = datetime.now(timezone.utc).isoformat()
    return [
        {
            "ticker": "NVDA",
            "company": "Nvidia",
            "move_percent": 4.8,
            "relative_volume": 2.1,
            "price": 945.20,
            "reason": "AI infrastructure demand and semiconductor strength",
            "source": "Demo Market Movers",
            "fetched_at": fetched_at,
        },
        {
            "ticker": "OPEN",
            "company": "Opendoor",
            "move_percent": 18.6,
            "relative_volume": 6.4,
            "price": 3.12,
            "reason": "Abnormal retail volume and squeeze chatter",
            "source": "Demo Market Movers",
            "fetched_at": fetched_at,
        },
        {
            "ticker": "PLTR",
            "company": "Palantir",
            "move_percent": 6.7,
            "relative_volume": 2.8,
            "price": 27.50,
            "reason": "Defense analytics contract speculation",
            "source": "Demo Market Movers",
            "fetched_at": fetched_at,
        },
        {
            "ticker": "GME",
            "company": "GameStop",
            "move_percent": 12.3,
            "relative_volume": 5.3,
            "price": 22.80,
            "reason": "Meme basket volatility and social mentions",
            "source": "Demo Market Movers",
            "fetched_at": fetched_at,
        },
    ]

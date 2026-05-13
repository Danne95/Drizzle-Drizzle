"""Market movers collector.

No preset ticker list is used here. Add a market data provider integration in
this isolated module when you are ready to collect live gainers and volume
spikes.
"""

from __future__ import annotations

def fetch_market_movers() -> list[dict]:
    return []

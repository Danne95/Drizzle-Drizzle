"""SEC filing signal collector.

This starter uses demo filings. A production replacement can call SEC company
facts or submissions endpoints while preserving this output schema.
"""

from __future__ import annotations

from datetime import datetime, timezone


def fetch_sec_filings() -> list[dict]:
    fetched_at = datetime.now(timezone.utc).isoformat()
    return [
        {
            "ticker": "PLTR",
            "form": "8-K",
            "filing_date": datetime.now().date().isoformat(),
            "headline": "Material agreement disclosed in new 8-K",
            "importance": 2.6,
            "source": "Demo SEC Filings",
            "fetched_at": fetched_at,
        },
        {
            "ticker": "RIVN",
            "form": "4",
            "filing_date": datetime.now().date().isoformat(),
            "headline": "Insider transaction detected",
            "importance": 1.7,
            "source": "Demo SEC Filings",
            "fetched_at": fetched_at,
        },
    ]

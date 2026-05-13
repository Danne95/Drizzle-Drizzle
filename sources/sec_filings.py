"""SEC filing signal collector.

No preset ticker list is used here. A production replacement can call SEC
company facts or submissions endpoints while preserving this output schema.
"""

from __future__ import annotations

def fetch_sec_filings() -> list[dict]:
    return []

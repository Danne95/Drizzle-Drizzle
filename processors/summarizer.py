"""Narrative summaries for the dashboard."""

from __future__ import annotations

from collections import Counter


def build_market_brief(news_items: list[dict], opportunities: list[dict]) -> dict:
    theme_counts = Counter(theme for item in opportunities for theme in item.get("themes", []))
    serious_count = sum(1 for item in opportunities if item["category"] == "serious")
    high_risk_count = sum(1 for item in opportunities if item["category"] == "high_risk")
    top = opportunities[0]["ticker"] if opportunities else "N/A"

    return {
        "headline": f"{len(opportunities)} tickers surfaced; top signal is {top}.",
        "news_items_scanned": len(news_items),
        "serious_count": serious_count,
        "high_risk_count": high_risk_count,
        "dominant_themes": [{"theme": theme, "count": count} for theme, count in theme_counts.most_common(5)],
        "narrative": (
            "Scanner blended RSS headlines, demo market mover data, social momentum, and SEC filing signals. "
            "Scores are relative and explainable, intended for watchlist research rather than trade execution."
        ),
    }

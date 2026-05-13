"""Transparent scoring and categorization for surfaced tickers."""

from __future__ import annotations

from collections import defaultdict

from config import SERIOUS_KEYWORDS, SPECULATIVE_KEYWORDS, THEME_KEYWORDS


def _add_signal(bucket: dict, signal_type: str, weight: float, evidence: dict) -> None:
    bucket["signals"].append({"type": signal_type, "weight": round(weight, 2)})
    bucket["top_sources"].append(evidence | {"weight": round(weight, 2)})
    bucket["score"] += weight


def _classify(signals: list[dict]) -> str:
    speculative = sum(signal["weight"] for signal in signals if signal["type"] in {"reddit_spike", "squeeze_language", "volume_spike", "meme_keyword"})
    serious = sum(signal["weight"] for signal in signals if signal["type"] in {"serious_keyword", "sec_filing", "news_velocity", "theme"})
    if speculative >= max(3.8, serious * 1.1):
        return "high_risk"
    return "serious"


def _theme_hits(text: str) -> list[str]:
    lowered = text.lower()
    themes = []
    for theme, keywords in THEME_KEYWORDS.items():
        if any(keyword in lowered for keyword in keywords):
            themes.append(theme)
    return themes


def score_opportunities(
    news_items: list[dict],
    market_movers: list[dict],
    reddit_signals: list[dict],
    sec_filings: list[dict],
) -> list[dict]:
    """Merge source signals into explainable ticker opportunity records."""
    buckets = defaultdict(lambda: {"ticker": "", "score": 0.0, "signals": [], "top_sources": [], "themes": set()})

    for item in news_items:
        tickers = item.get("tickers", [])
        if not tickers:
            continue
        text = f"{item.get('title', '')} {item.get('summary', '')}"
        lowered = text.lower()
        for ticker in tickers:
            bucket = buckets[ticker]
            bucket["ticker"] = ticker
            _add_signal(
                bucket,
                "news_velocity",
                0.8,
                {
                    "source": item.get("source", "RSS"),
                    "title": item.get("title", ""),
                    "snippet": item.get("summary", "")[:220],
                    "link": item.get("link", ""),
                },
            )
            for keyword, weight in SERIOUS_KEYWORDS.items():
                if keyword in lowered:
                    _add_signal(bucket, "serious_keyword", weight, {"source": item.get("source", "RSS"), "title": item.get("title", ""), "snippet": f"Keyword detected: {keyword}"})
            for keyword, weight in SPECULATIVE_KEYWORDS.items():
                if keyword in lowered:
                    _add_signal(bucket, "meme_keyword", weight, {"source": item.get("source", "RSS"), "title": item.get("title", ""), "snippet": f"Speculative keyword detected: {keyword}"})
            for theme in _theme_hits(text):
                bucket["themes"].add(theme)
                _add_signal(bucket, "theme", 0.7, {"source": "Theme Detector", "title": theme, "snippet": f"{theme} language appeared in coverage."})

            sentiment = item.get("sentiment", {}).get("score", 0)
            if sentiment:
                _add_signal(bucket, "headline_sentiment", abs(sentiment) * 0.8, {"source": "Sentiment Engine", "title": item.get("title", ""), "snippet": f"Headline sentiment score: {sentiment}"})

    for mover in market_movers:
        ticker = mover["ticker"]
        bucket = buckets[ticker]
        bucket["ticker"] = ticker
        move_weight = min(abs(mover["move_percent"]) / 4, 4.0)
        volume_weight = min(mover["relative_volume"] / 1.5, 4.5)
        _add_signal(bucket, "price_momentum", move_weight, {"source": mover["source"], "title": f"{ticker} moved {mover['move_percent']}%", "snippet": mover["reason"]})
        if mover["relative_volume"] >= 2:
            _add_signal(bucket, "volume_spike", volume_weight, {"source": mover["source"], "title": f"{ticker} relative volume {mover['relative_volume']}x", "snippet": mover["reason"]})

    for reddit in reddit_signals:
        ticker = reddit["ticker"]
        bucket = buckets[ticker]
        bucket["ticker"] = ticker
        mention_weight = min(reddit["mention_change_percent"] / 75, 5.0)
        _add_signal(bucket, "reddit_spike", mention_weight, {"source": reddit["source"], "title": f"{ticker} mentions +{reddit['mention_change_percent']}%", "snippet": reddit["top_phrase"]})
        if reddit.get("squeeze_language"):
            _add_signal(bucket, "squeeze_language", 2.8, {"source": reddit["source"], "title": f"{ticker} squeeze language detected", "snippet": reddit["top_phrase"]})

    for filing in sec_filings:
        ticker = filing["ticker"]
        bucket = buckets[ticker]
        bucket["ticker"] = ticker
        _add_signal(bucket, "sec_filing", filing.get("importance", 1.5), {"source": filing["source"], "title": f"{ticker} {filing['form']} filed", "snippet": filing["headline"]})

    opportunities = []
    for ticker, bucket in buckets.items():
        signals = bucket["signals"]
        score = round(bucket["score"], 1)
        category = _classify(signals)
        top_signal_names = ", ".join(sorted({signal["type"].replace("_", " ") for signal in signals[:5]}))
        opportunities.append(
            {
                "ticker": ticker,
                "category": category,
                "score": score,
                "risk": "High" if category == "high_risk" else "Moderate",
                "signals": sorted(signals, key=lambda signal: signal["weight"], reverse=True),
                "top_sources": sorted(bucket["top_sources"], key=lambda source: source["weight"], reverse=True)[:5],
                "themes": sorted(bucket["themes"]),
                "summary": f"{ticker} surfaced from {top_signal_names}. Total transparent signal score: {score}.",
            }
        )

    return sorted(opportunities, key=lambda item: item["score"], reverse=True)

"""Transparent scoring and categorization for surfaced tickers."""

from __future__ import annotations

from collections import defaultdict

from config import SERIOUS_KEYWORDS, SPECULATIVE_KEYWORDS, THEME_KEYWORDS

SIGNAL_LABELS = {
    "news_velocity": "News coverage",
    "serious_keyword": "Business catalyst",
    "meme_keyword": "Speculative language",
    "theme": "Market theme",
    "headline_sentiment": "Headline tone",
    "price_momentum": "Price move",
    "volume_spike": "Volume spike",
    "reddit_spike": "Social mention spike",
    "squeeze_language": "Squeeze chatter",
    "sec_filing": "SEC filing",
    "category_b_fallback": "Closest speculative candidate",
}

SIGNAL_EXPLANATIONS = {
    "news_velocity": "The ticker appeared in fresh financial headlines.",
    "serious_keyword": "The story contains business catalyst words such as contract, acquisition, approval, earnings, or upgrade.",
    "meme_keyword": "The story contains speculative terms such as meme, squeeze, unusual volume, or similar language.",
    "theme": "The story matches a broader market theme such as AI, defense, biotech, energy, or crypto.",
    "headline_sentiment": "The headline wording leaned positive or negative enough to affect attention.",
    "price_momentum": "The market mover source reported a notable price move.",
    "volume_spike": "The market mover source reported abnormal relative volume.",
    "reddit_spike": "The social source reported a jump in mentions.",
    "squeeze_language": "The social source detected short-squeeze style language.",
    "sec_filing": "A filing source reported a potentially relevant SEC filing.",
    "category_b_fallback": "No strong meme/squeeze signal fired, so this is the closest Category B candidate by weaker speculative evidence.",
}

SPECULATIVE_SIGNAL_TYPES = {"reddit_spike", "squeeze_language", "volume_spike", "meme_keyword", "price_momentum", "headline_sentiment"}


def _company_lookup(symbol_universe: list[dict] | None) -> dict[str, str]:
    return {
        item["ticker"].upper(): item["company"]
        for item in symbol_universe or []
        if item.get("ticker") and item.get("company")
    }


def _add_signal(bucket: dict, signal_type: str, weight: float, evidence: dict) -> None:
    bucket["signals"].append(
        {
            "type": signal_type,
            "label": SIGNAL_LABELS.get(signal_type, signal_type.replace("_", " ").title()),
            "description": SIGNAL_EXPLANATIONS.get(signal_type, "Signal detected by the scanner."),
            "weight": round(weight, 2),
        }
    )
    bucket["top_sources"].append(evidence | {"weight": round(weight, 2)})
    bucket["score"] += weight


def _classify(signals: list[dict]) -> str:
    speculative = sum(signal["weight"] for signal in signals if signal["type"] in {"reddit_spike", "squeeze_language", "volume_spike", "meme_keyword"})
    serious = sum(signal["weight"] for signal in signals if signal["type"] in {"serious_keyword", "sec_filing", "news_velocity", "theme"})
    if speculative >= max(3.8, serious * 1.1):
        return "high_risk"
    return "serious"


def _speculative_score(signals: list[dict]) -> float:
    return sum(signal["weight"] for signal in signals if signal["type"] in SPECULATIVE_SIGNAL_TYPES)


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
    symbol_universe: list[dict] | None = None,
) -> list[dict]:
    """Merge source signals into explainable ticker opportunity records."""
    company_names = _company_lookup(symbol_universe)
    buckets = defaultdict(lambda: {"ticker": "", "company": "", "score": 0.0, "signals": [], "top_sources": [], "themes": set()})

    for item in news_items:
        tickers = item.get("tickers", [])
        if not tickers:
            continue
        text = f"{item.get('title', '')} {item.get('summary', '')}"
        lowered = text.lower()
        for ticker in tickers:
            bucket = buckets[ticker]
            bucket["ticker"] = ticker
            bucket["company"] = company_names.get(ticker, "")
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
        bucket["company"] = mover.get("company") or company_names.get(ticker, "")
        move_weight = min(abs(mover["move_percent"]) / 4, 4.0)
        volume_weight = min(mover["relative_volume"] / 1.5, 4.5)
        _add_signal(bucket, "price_momentum", move_weight, {"source": mover["source"], "title": f"{ticker} moved {mover['move_percent']}%", "snippet": mover["reason"]})
        if mover["relative_volume"] >= 2:
            _add_signal(bucket, "volume_spike", volume_weight, {"source": mover["source"], "title": f"{ticker} relative volume {mover['relative_volume']}x", "snippet": mover["reason"]})

    for reddit in reddit_signals:
        ticker = reddit["ticker"]
        bucket = buckets[ticker]
        bucket["ticker"] = ticker
        bucket["company"] = company_names.get(ticker, "")
        mention_weight = min(reddit["mention_change_percent"] / 75, 5.0)
        _add_signal(bucket, "reddit_spike", mention_weight, {"source": reddit["source"], "title": f"{ticker} mentions +{reddit['mention_change_percent']}%", "snippet": reddit["top_phrase"]})
        if reddit.get("squeeze_language"):
            _add_signal(bucket, "squeeze_language", 2.8, {"source": reddit["source"], "title": f"{ticker} squeeze language detected", "snippet": reddit["top_phrase"]})

    for filing in sec_filings:
        ticker = filing["ticker"]
        bucket = buckets[ticker]
        bucket["ticker"] = ticker
        bucket["company"] = company_names.get(ticker, "")
        _add_signal(bucket, "sec_filing", filing.get("importance", 1.5), {"source": filing["source"], "title": f"{ticker} {filing['form']} filed", "snippet": filing["headline"]})

    opportunities = []
    for ticker, bucket in buckets.items():
        signals = sorted(bucket["signals"], key=lambda signal: signal["weight"], reverse=True)
        score = round(bucket["score"], 1)
        category = _classify(signals)
        top_signal = signals[0] if signals else {"label": "No major signal", "weight": 0, "description": ""}
        top_source = sorted(bucket["top_sources"], key=lambda source: source["weight"], reverse=True)[0] if bucket["top_sources"] else {}
        if score >= 12:
            score_label = "Strong watchlist signal"
            score_help = "Many or heavy signals stacked together. Worth a closer read, not a buy/sell instruction."
        elif score >= 7:
            score_label = "Notable watchlist signal"
            score_help = "Several signals point to rising attention. Useful for research triage."
        elif score >= 3:
            score_label = "Light watchlist signal"
            score_help = "One or two modest signals. Treat as a low-priority lead."
        else:
            score_label = "Weak signal"
            score_help = "Very limited evidence. Usually background noise unless the story matters to you."
        opportunities.append(
            {
                "ticker": ticker,
                "company": bucket["company"] or "Company name unavailable",
                "category": category,
                "score": score,
                "score_label": score_label,
                "score_help": score_help,
                "signals": signals,
                "top_sources": sorted(bucket["top_sources"], key=lambda source: source["weight"], reverse=True)[:5],
                "themes": sorted(bucket["themes"]),
                "top_reason": f"{top_signal['label']} contributed the most (+{top_signal['weight']}).",
                "summary": top_source.get("snippet") or top_signal.get("description") or "The scanner found enough evidence to place this ticker on the watchlist.",
                "category_note": "",
                "speculative_score": round(_speculative_score(signals), 2),
            }
        )

    opportunities = sorted(opportunities, key=lambda item: item["score"], reverse=True)
    if opportunities and not any(item["category"] == "high_risk" for item in opportunities):
        fallback = max(opportunities, key=lambda item: (item["speculative_score"], item["score"]))
        fallback["category"] = "high_risk"
        fallback["score_label"] = "Closest speculative candidate"
        fallback["category_note"] = "Fallback pick: no true meme/squeeze trigger appeared, so this is the riskiest-looking ticker in this run."
        fallback["top_reason"] = "Category B fallback: closest speculative candidate in this run."
        fallback["summary"] = "This is not a confirmed meme or squeeze signal. It is included so Category B always has one item to inspect."
        fallback["signals"] = [
            {
                "type": "category_b_fallback",
                "label": SIGNAL_LABELS["category_b_fallback"],
                "description": SIGNAL_EXPLANATIONS["category_b_fallback"],
                "weight": 0.0,
            },
            *fallback["signals"],
        ]

    return sorted(opportunities, key=lambda item: item["score"], reverse=True)

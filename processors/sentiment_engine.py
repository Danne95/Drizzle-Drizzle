"""Simple explainable sentiment scoring for headlines and snippets."""

from __future__ import annotations

POSITIVE_TERMS = {
    "beats": 0.8,
    "beat": 0.6,
    "upgrade": 0.7,
    "wins": 0.8,
    "contract": 0.5,
    "approval": 0.8,
    "partnership": 0.5,
    "surges": 0.7,
    "growth": 0.5,
}

NEGATIVE_TERMS = {
    "misses": -0.8,
    "downgrade": -0.7,
    "lawsuit": -0.6,
    "probe": -0.5,
    "bankruptcy": -0.9,
    "falls": -0.5,
    "cuts": -0.6,
    "warning": -0.5,
}


def score_sentiment(text: str) -> dict:
    lowered = text.lower()
    hits = []
    score = 0.0
    for term, weight in POSITIVE_TERMS.items():
        if term in lowered:
            score += weight
            hits.append({"term": term, "weight": weight})
    for term, weight in NEGATIVE_TERMS.items():
        if term in lowered:
            score += weight
            hits.append({"term": term, "weight": weight})
    return {"score": round(max(-1.0, min(1.0, score)), 2), "hits": hits}


def attach_sentiment(news_items: list[dict]) -> list[dict]:
    enriched = []
    for item in news_items:
        text = f"{item.get('title', '')} {item.get('summary', '')}"
        copy = dict(item)
        copy["sentiment"] = score_sentiment(text)
        enriched.append(copy)
    return enriched

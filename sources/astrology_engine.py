"""Comedic black magic finance oracle.

This output is intentionally entertainment, not analysis.
"""

from __future__ import annotations

import random
from datetime import datetime


ZODIAC = [
    "Aries",
    "Taurus",
    "Gemini",
    "Cancer",
    "Leo",
    "Virgo",
    "Libra",
    "Scorpio",
    "Sagittarius",
    "Capricorn",
    "Aquarius",
    "Pisces",
]

CHINESE_ZODIAC = ["Rat", "Ox", "Tiger", "Rabbit", "Dragon", "Snake", "Horse", "Goat", "Monkey", "Rooster", "Dog", "Pig"]
LUCKY_TICKERS = ["BABA", "PLTR", "SOFI", "NVDA", "GME", "OPEN", "TSLA", "COIN"]
WARNINGS = [
    "Avoid tickers containing the letter R until the vibes improve.",
    "Mercury retrograde suggests taking profits before bragging online.",
    "The candlestick spirits dislike revenge trading today.",
    "If a ticker has three consecutive green candles, ask whether it also has a business model.",
]
BLESSINGS = [
    "Today favors aggressive tech plays, but only after coffee and position sizing.",
    "The moon phase smiles upon disciplined dip buyers.",
    "A suspiciously lucky number favors tickers with four letters.",
    "The cosmic order book whispers: respect stop losses.",
]


def _moon_phase(day: int) -> str:
    phases = ["New Moon", "Waxing Crescent", "First Quarter", "Waxing Gibbous", "Full Moon", "Waning Gibbous", "Last Quarter", "Waning Crescent"]
    return phases[day % len(phases)]


def generate_black_magic_reading(now: datetime | None = None) -> dict:
    now = now or datetime.now()
    seed = int(now.strftime("%Y%m%d"))
    rng = random.Random(seed)
    numerology = sum(int(digit) for digit in now.strftime("%Y%m%d"))
    lucky_ticker = rng.choice(LUCKY_TICKERS)
    forbidden_letter = rng.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ")

    return {
        "category": "meme_black_magic",
        "disclaimer": "Entertainment only. This section is financial astrology satire, not financial advice.",
        "zodiac": rng.choice(ZODIAC),
        "chinese_zodiac": CHINESE_ZODIAC[(now.year - 4) % 12],
        "moon_phase": _moon_phase(now.day),
        "numerology_score": numerology,
        "lucky_ticker": lucky_ticker,
        "forbidden_letter": forbidden_letter,
        "blessing": rng.choice(BLESSINGS),
        "warning": rng.choice(WARNINGS),
        "recommendations": [
            f"Lucky ticker today: {lucky_ticker}. The spreadsheet candles demand tribute.",
            f"Avoid stocks containing the letter {forbidden_letter} unless the chart apologizes first.",
            "High beta names may levitate briefly if retail volume and lunar confidence align.",
        ],
    }

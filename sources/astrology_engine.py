"""Comedic black magic finance oracle.

This output is intentionally entertainment, not analysis.
"""

from __future__ import annotations

import random
from datetime import datetime, date


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


def _western_zodiac(month: int, day: int) -> str:
    signs = [
        ((1, 20), "Capricorn"),
        ((2, 19), "Aquarius"),
        ((3, 21), "Pisces"),
        ((4, 20), "Aries"),
        ((5, 21), "Taurus"),
        ((6, 21), "Gemini"),
        ((7, 23), "Cancer"),
        ((8, 23), "Leo"),
        ((9, 23), "Virgo"),
        ((10, 23), "Libra"),
        ((11, 22), "Scorpio"),
        ((12, 22), "Sagittarius"),
        ((12, 32), "Capricorn"),
    ]
    for (sign_month, sign_day), sign in signs:
        if (month, day) < (sign_month, sign_day):
            return sign
    return "Capricorn"


def _parse_birthdate(value: str | None) -> date | None:
    if not value:
        return None
    try:
        return date.fromisoformat(value)
    except ValueError:
        return None


def _moon_phase(day: int) -> str:
    phases = ["New Moon", "Waxing Crescent", "First Quarter", "Waxing Gibbous", "Full Moon", "Waning Gibbous", "Last Quarter", "Waning Crescent"]
    return phases[day % len(phases)]


def _base_reading(now: datetime, candidate_tickers: list[str] | None, seed_extra: int = 0) -> dict:
    seed = int(now.strftime("%Y%m%d")) + seed_extra
    rng = random.Random(seed)
    numerology = sum(int(digit) for digit in now.strftime("%Y%m%d"))
    candidates = sorted({ticker for ticker in candidate_tickers or [] if ticker})
    lucky_ticker = rng.choice(candidates) if candidates else "TBD"
    forbidden_letter = rng.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ")

    return {
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


def generate_black_magic_reading(now: datetime | None = None, candidate_tickers: list[str] | None = None, personal_profile: dict | None = None) -> dict:
    now = now or datetime.now()
    personal_profile = personal_profile or {}
    birthdate = _parse_birthdate(personal_profile.get("birthdate"))
    seed_extra = 0
    if birthdate:
        seed_extra += int(birthdate.strftime("%m%d"))
    if personal_profile.get("name"):
        seed_extra += sum(ord(char) for char in personal_profile["name"])
    generic = _base_reading(now, candidate_tickers)
    personal_rng = random.Random(int(now.strftime("%Y%m%d")) + seed_extra)
    numerology_seed = now.strftime("%Y%m%d")
    if birthdate:
        numerology_seed += birthdate.strftime("%Y%m%d")
    numerology = sum(int(digit) for digit in numerology_seed)
    candidates = sorted({ticker for ticker in candidate_tickers or [] if ticker})
    lucky_ticker = personal_rng.choice(candidates) if candidates else "TBD"
    forbidden_letter = personal_rng.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
    zodiac = personal_profile.get("zodiac") or (_western_zodiac(birthdate.month, birthdate.day) if birthdate else personal_rng.choice(ZODIAC))
    chinese_zodiac = personal_profile.get("chinese_zodiac") or (CHINESE_ZODIAC[(birthdate.year - 4) % 12] if birthdate else CHINESE_ZODIAC[(now.year - 4) % 12])
    personal_enabled = bool(personal_profile)
    personal_note = (
        f"Personal oracle blend enabled: {zodiac} chart energy and {chinese_zodiac} cycle bias the nonsense model toward asymmetric vibes."
        if personal_enabled
        else "Personal oracle blend not configured. Add your ignored local profile to customize this section."
    )
    personal = {
        "enabled": personal_enabled,
        "note": personal_note,
        "zodiac": zodiac,
        "chinese_zodiac": chinese_zodiac,
        "moon_phase": _moon_phase(now.day),
        "numerology_score": numerology,
        "lucky_ticker": lucky_ticker,
        "forbidden_letter": forbidden_letter,
        "blessing": personal_rng.choice(BLESSINGS),
        "warning": personal_rng.choice(WARNINGS),
        "recommendations": [
            f"Your personal lucky ticker today: {lucky_ticker}. The chart vibes have been personalized without exposing your details.",
            f"Your private numerology says avoid tickers containing {forbidden_letter} unless the setup is unusually convincing.",
            "Personal oracle says: smaller position sizes appease both Saturn and future regret.",
        ],
    }

    return {
        "category": "meme_black_magic",
        "disclaimer": "Entertainment only. This section is financial astrology satire, not financial advice.",
        "generic": generic,
        "personal": personal,
    }

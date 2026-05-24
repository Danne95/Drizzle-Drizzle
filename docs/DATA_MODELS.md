# Data Models

## Storage Model

There is no database. The project uses in-memory dictionaries and local JSON/HTML artifacts.

Generated JSON snapshots:

```text
data/news_YYYY-MM-DD_HHMM.json
data/market_movers_YYYY-MM-DD_HHMM.json
data/reddit_YYYY-MM-DD_HHMM.json
data/sec_filings_YYYY-MM-DD_HHMM.json
data/black_magic_YYYY-MM-DD_HHMM.json
data/symbol_universe_YYYY-MM-DD_HHMM.json
data/symbol_universe_cache.json
```

Generated HTML:

```text
reports/YYYY-MM-DD_HHMM.html
latest_report.html
```

## Core Records

### Symbol Universe Item

Produced by `sources/symbol_universe.fetch_symbol_universe()`.

| Field | Type | Required | Description |
|---|---:|---:|---|
| `ticker` | `str` | Yes | Uppercase listed symbol from NasdaqTrader. Symbols containing `$`, `.`, or length greater than 5 are filtered out. |
| `company` | `str` | Yes | Cleaned company/security name. Common security suffixes are removed. |

Constraints:

- Deduplicated by ticker.
- Sorted by ticker.
- Empty list is valid when download and cache are unavailable.

### RSS News Item

Produced by `sources/rss_news.fetch_rss_news()`.

| Field | Type | Required | Description |
|---|---:|---:|---|
| `type` | `str` | Yes | Always `"rss_news"` for live normalized entries and sample records. |
| `title` | `str` | Yes | Headline. Empty live titles are filtered out. |
| `link` | `str` | Yes | Source URL. |
| `published` | `str` | Yes | Feed-provided published or updated string. |
| `source` | `str` | Yes | Feed/source display name. |
| `summary` | `str` | Yes | Feed summary/snippet. |
| `fetched_at` | `str` | Live only | UTC ISO timestamp from `_normalize_entry()`. Sample records do not include this field. |

### News Item With Tickers

Produced by `processors.ticker_extractor.attach_tickers()`.

| Field | Type | Required | Description |
|---|---:|---:|---|
| RSS fields | varies | Yes | Original news item fields are preserved. |
| `tickers` | `list[str]` | Yes | Sorted ticker list extracted from title and summary. |

Ticker extraction sources:

- Listed company aliases from `symbol_universe`.
- Cashtags matching `$[A-Z]{1,5}`.
- Uppercase ticker-like tokens `[A-Z]{2,5}` only when there is no known universe or the match is in the universe.

False positives in `config.COMMON_FALSE_TICKERS` are excluded.

### Sentiment Result

Produced by `processors.sentiment_engine.score_sentiment()`.

| Field | Type | Required | Description |
|---|---:|---:|---|
| `score` | `float` | Yes | Sum of positive/negative term weights clamped to `[-1.0, 1.0]` and rounded to 2 decimals. |
| `hits` | `list[SentimentHit]` | Yes | Terms that contributed to the score. |

`SentimentHit`:

| Field | Type | Required | Description |
|---|---:|---:|---|
| `term` | `str` | Yes | Matched keyword. |
| `weight` | `float` | Yes | Positive or negative contribution. |

### News Item With Sentiment

Produced by `processors.sentiment_engine.attach_sentiment()`.

| Field | Type | Required | Description |
|---|---:|---:|---|
| News-with-tickers fields | varies | Yes | Original enriched news item fields are preserved. |
| `sentiment` | `SentimentResult` | Yes | Sentiment score for title plus summary. |

### Market Mover

Current `sources/market_movers.fetch_market_movers()` returns `[]`. The expected schema is inferred from `processors.scoring_engine.score_opportunities()` and historical snapshots.

| Field | Type | Required | Description |
|---|---:|---:|---|
| `ticker` | `str` | Yes | Symbol. |
| `company` | `str` | No | Company display name. Falls back to symbol universe company. |
| `move_percent` | `float` | Yes | Percent price move. Used as `min(abs(move_percent) / 4, 4.0)`. |
| `relative_volume` | `float` | Yes | Relative volume multiplier. Used as `min(relative_volume / 1.5, 4.5)`. Adds `volume_spike` only when `>= 2`. |
| `price` | `float` | No | Last/current price. Not consumed by current scoring code. |
| `reason` | `str` | Yes | Evidence snippet for price/volume signals. |
| `source` | `str` | Yes | Source label. |
| `fetched_at` | `str` | No | ISO timestamp. |

### Reddit Signal

Current `sources/reddit_scanner.fetch_reddit_signals()` returns `[]`. Expected schema is inferred from scoring code and historical snapshots.

| Field | Type | Required | Description |
|---|---:|---:|---|
| `ticker` | `str` | Yes | Symbol. |
| `mentions` | `int` | No | Current mention count. Not consumed by current scoring code. |
| `mention_change_percent` | `float` | Yes | Percent mention increase. Used as `min(value / 75, 5.0)`. |
| `sentiment` | `float` | No | Social sentiment. Not consumed by current scoring code. |
| `squeeze_language` | `bool` | No | Adds fixed `2.8` squeeze signal when truthy. |
| `top_phrase` | `str` | Yes | Evidence snippet. |
| `source` | `str` | Yes | Source label. |
| `fetched_at` | `str` | No | ISO timestamp. |

### SEC Filing Signal

Current `sources/sec_filings.fetch_sec_filings()` returns `[]`. Expected schema is inferred from scoring code and historical snapshots.

| Field | Type | Required | Description |
|---|---:|---:|---|
| `ticker` | `str` | Yes | Symbol. |
| `form` | `str` | Yes | SEC form type displayed in evidence title. |
| `filing_date` | `str` | No | Filing date. Not consumed by current scoring code. |
| `headline` | `str` | Yes | Evidence snippet. |
| `importance` | `float` | No | Signal weight. Defaults to `1.5`. |
| `source` | `str` | Yes | Source label. |
| `fetched_at` | `str` | No | ISO timestamp. |

### Signal

Created inside `processors.scoring_engine._add_signal()`.

| Field | Type | Required | Description |
|---|---:|---:|---|
| `type` | `str` | Yes | Internal signal key such as `news_velocity`, `serious_keyword`, `meme_keyword`, `theme`, `headline_sentiment`, `price_momentum`, `volume_spike`, `reddit_spike`, `squeeze_language`, `sec_filing`, `category_b_fallback`. |
| `label` | `str` | Yes | Human-readable label from `SIGNAL_LABELS`. |
| `description` | `str` | Yes | Explanation from `SIGNAL_EXPLANATIONS`. |
| `weight` | `float` | Yes | Rounded contribution. |

### Evidence Source

Stored in opportunity `top_sources`.

| Field | Type | Required | Description |
|---|---:|---:|---|
| `source` | `str` | Yes | Source label. |
| `title` | `str` | Yes | Evidence title/headline. |
| `snippet` | `str` | Yes | Supporting detail. RSS snippets are truncated to 220 characters for news velocity evidence. |
| `link` | `str` | Conditional | Present for RSS news velocity evidence. |
| `weight` | `float` | Yes | Rounded signal contribution. |

### Opportunity

Produced by `processors.scoring_engine.score_opportunities()`.

| Field | Type | Required | Description |
|---|---:|---:|---|
| `ticker` | `str` | Yes | Symbol. |
| `company` | `str` | Yes | Company name from universe/source or `"Company name unavailable"`. |
| `category` | `str` | Yes | `"serious"` or `"high_risk"`. |
| `score` | `float` | Yes | Rounded total signal score. |
| `score_label` | `str` | Yes | One of `"Strong watchlist signal"`, `"Notable watchlist signal"`, `"Light watchlist signal"`, `"Weak signal"`, or fallback label. |
| `score_help` | `str` | Yes | Human-readable score interpretation. |
| `signals` | `list[Signal]` | Yes | Signals sorted by weight descending, with fallback marker prepended if used. |
| `top_sources` | `list[EvidenceSource]` | Yes | Top 5 evidence records sorted by weight. |
| `themes` | `list[str]` | Yes | Sorted matched market themes. |
| `top_reason` | `str` | Yes | Explanation of highest-contributing signal or fallback. |
| `summary` | `str` | Yes | Primary snippet or signal description. |
| `category_note` | `str` | Yes | Empty unless Category B fallback was applied. |
| `speculative_score` | `float` | Yes | Sum of weights for speculative signal types. |

Category logic:

```python
speculative = sum(weights for reddit_spike, squeeze_language, volume_spike, meme_keyword)
serious = sum(weights for serious_keyword, sec_filing, news_velocity, theme)
category = "high_risk" if speculative >= max(3.8, serious * 1.1) else "serious"
```

If there are opportunities but none classify as `high_risk`, the highest `(speculative_score, score)` item is forced into `high_risk` as a fallback.

### Market Brief

Produced by `processors.summarizer.build_market_brief()`.

| Field | Type | Required | Description |
|---|---:|---:|---|
| `headline` | `str` | Yes | Summary string like `"N tickers surfaced; top signal is TICKER."` |
| `news_items_scanned` | `int` | Yes | Count of news items after ticker/sentiment enrichment. |
| `serious_count` | `int` | Yes | Count of opportunities categorized as `serious`. |
| `high_risk_count` | `int` | Yes | Count of opportunities categorized as `high_risk`. |
| `dominant_themes` | `list[dict]` | Yes | Up to 5 `{theme, count}` records. |
| `narrative` | `str` | Yes | Static dashboard narrative. |

### Black Magic Reading

Produced by `sources.astrology_engine.generate_black_magic_reading()`.

Top-level:

| Field | Type | Required | Description |
|---|---:|---:|---|
| `category` | `str` | Yes | Always `"meme_black_magic"`. |
| `disclaimer` | `str` | Yes | Entertainment-only disclaimer. |
| `generic` | `OracleReading` | Yes | Date-seeded generic reading. |
| `personal` | `PersonalOracleReading` | Yes | Date plus private-profile-seeded reading. |

`OracleReading`:

| Field | Type | Required | Description |
|---|---:|---:|---|
| `zodiac` | `str` | Yes | Random zodiac from fixed list for generic reading. |
| `chinese_zodiac` | `str` | Yes | Derived from current year for generic reading. |
| `moon_phase` | `str` | Yes | Deterministic from day-of-month modulo fixed phase list. |
| `numerology_score` | `int` | Yes | Sum of digits in date string. |
| `lucky_ticker` | `str` | Yes | Random candidate ticker or `"TBD"`. |
| `forbidden_letter` | `str` | Yes | Random uppercase letter. |
| `blessing` | `str` | Yes | Random fixed phrase. |
| `warning` | `str` | Yes | Random fixed phrase. |
| `recommendations` | `list[str]` | Yes | Three generated satire recommendations. |

`PersonalOracleReading` includes all `OracleReading` fields plus:

| Field | Type | Required | Description |
|---|---:|---:|---|
| `enabled` | `bool` | Yes | `true` if `private/oracle_profile.json` loaded to a non-empty dict. |
| `note` | `str` | Yes | Explains whether private oracle blend is active. |

### Private Oracle Profile

Loaded from ignored local path `private/oracle_profile.json`.

| Field | Type | Required | Description |
|---|---:|---:|---|
| `name` | `str` | No | Used only to modify deterministic seed. Not rendered directly. |
| `birthdate` | `str` | No | ISO date `YYYY-MM-DD`. Used for zodiac, Chinese zodiac, numerology, seed. Invalid values are ignored. |
| `zodiac` | `str` | No | Overrides calculated western zodiac if provided. |
| `chinese_zodiac` | `str` | No | Overrides calculated Chinese zodiac if provided. |

Invalid JSON, missing file, or non-object JSON returns `{}`.

## DB Schema

No DB schema is present.

<!-- UNCLEAR: There is no schema validation layer, so required fields for future integrations are inferred from direct dictionary indexing in processors/scoring_engine.py. -->


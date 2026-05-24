# Architecture

## System Type

This is a single-process local CLI application. There is no daemon, web server, database, queue, background worker, or authentication layer.

The main executable path is:

```text
main.py -> sources/* -> processors/* -> report/report_generator.py -> local files
```

## Layers

| Layer | Files | Responsibility |
|---|---|---|
| Configuration | `config.py` | Defines project paths, RSS feed URLs, feed limits, timeout constant, scoring keyword weights, theme keywords, and false ticker symbols. |
| Orchestration | `main.py` | Creates output directories, runs the scanner pipeline, snapshots source payloads, renders report, copies latest report. |
| Sources | `sources/*.py` | Collect external or local input records. Source outputs are plain dictionaries. |
| Processors | `processors/*.py` | Enrich, score, classify, and summarize source records. |
| Report | `report/report_generator.py`, `report/templates/*` | Convert scored records and summaries into a self-contained HTML dashboard. |
| Generated storage | `data/`, `reports/`, `latest_report.html` | Local artifacts produced by runs. Ignored by Git. |
| Tests | `tests/test_ticker_extractor.py` | Unit tests for ticker extraction. |

## Module Boundaries

### `main.py`

`main.run(use_mock_news: bool = False) -> Path` is the pipeline coordinator:

1. Ensures `data/` and `reports/` exist.
2. Creates a local timestamp `YYYY-MM-DD_HHMM`.
3. Fetches symbol universe, RSS news, market movers, Reddit signals, and SEC filings.
4. Enriches news with tickers and sentiment.
5. Scores opportunities from all signal sources.
6. Builds candidate ticker list for the oracle.
7. Loads optional private oracle profile.
8. Generates satire/oracle payload.
9. Builds market brief.
10. Snapshots raw source/oracle/universe payloads to JSON.
11. Renders timestamped report in `reports/`.
12. Copies the report to `latest_report.html`.

### `sources/`

Source modules hide collection mechanics behind small `fetch_*()` functions:

- `rss_news.fetch_rss_news(use_mock=False)`: fetches configured RSS feeds with mock fallback.
- `symbol_universe.fetch_symbol_universe()`: downloads public NasdaqTrader symbol lists, caches on success, falls back to cache or empty list.
- `market_movers.fetch_market_movers()`: integration stub returning `[]`.
- `reddit_scanner.fetch_reddit_signals()`: integration stub returning `[]`.
- `sec_filings.fetch_sec_filings()`: integration stub returning `[]`.
- `personal_oracle_profile.load_private_oracle_profile()`: loads ignored local profile JSON or returns `{}`.
- `astrology_engine.generate_black_magic_reading(...)`: builds deterministic entertainment-only oracle data.

### `processors/`

Processors are transformation modules:

- `ticker_extractor.py` extracts tickers from company aliases, cashtags, and uppercase mentions.
- `sentiment_engine.py` scores headline text with fixed positive/negative term weights.
- `scoring_engine.py` merges all source signals into opportunity records.
- `summarizer.py` creates aggregate counts and theme summary for the dashboard.

### `report/`

`report_generator.py` owns all chart creation and HTML rendering:

- Plotly charts are generated as offline HTML divs.
- Jinja2 renders `dashboard.html`.
- `dashboard.html` includes `styles.css` inline and includes `opportunity_card.html` for each opportunity.
- Reports are written as standalone local HTML files.

## Data Flow

```text
NasdaqTrader listed symbols
        |
        v
symbol_universe: [{ticker, company}]
        |
        +-------------------------+
                                  |
RSS feeds or samples/mock_news --> raw_news
                                  |
                                  v
                          attach_tickers()
                                  |
                                  v
                          attach_sentiment()
                                  |
                                  v
market_movers [] --------> score_opportunities() <-------- reddit_signals []
                                  ^
                                  |
sec_filings [] -------------------+
                                  |
                                  v
                          opportunities
                                  |
        +-------------------------+------------------+
        |                                            |
        v                                            v
build_market_brief()                    generate_black_magic_reading()
        |                                            |
        +-------------------------+------------------+
                                  |
                                  v
                          generate_report()
                                  |
                                  v
              reports/YYYY-MM-DD_HHMM.html + latest_report.html
```

Raw source payloads are snapshotted independently under `data/` before rendering.

## External Integrations

| Integration | File | Status | Failure Behavior |
|---|---|---|---|
| Yahoo Finance RSS | `config.py`, `sources/rss_news.py` | Active | If all feeds produce no items, load `samples/mock_news.json`. |
| MarketWatch RSS | `config.py`, `sources/rss_news.py` | Active | Same RSS fallback. |
| CNBC Markets RSS | `config.py`, `sources/rss_news.py` | Active | Same RSS fallback. |
| NasdaqTrader symbol directories | `sources/symbol_universe.py` | Active | Use `data/symbol_universe_cache.json`; if absent, return `[]`. |
| Market movers provider | `sources/market_movers.py` | Stub | Returns `[]`. |
| Reddit/social provider | `sources/reddit_scanner.py` | Stub | Returns `[]`. |
| SEC filings provider | `sources/sec_filings.py` | Stub | Returns `[]`. |
| Private oracle profile | `sources/personal_oracle_profile.py` | Optional local file | Invalid/missing/non-object JSON returns `{}`. |

## Why The Structure Exists

The code isolates volatile external integrations in `sources/` so providers can be replaced without changing scoring or reporting. Processing logic uses plain dictionaries to keep the pipeline lightweight and easy to snapshot. The report layer is separate because it combines chart construction, HTML templating, and styling concerns that should not leak into data collection or scoring.

The current stubs for market movers, Reddit, and SEC are deliberate extension points. The active scanner avoids injecting hardcoded demo tickers into normal runs.

## Current Limitations

- No persistent database or schema validation.
- No typed models beyond informal dictionary contracts.
- No retries or HTTP timeout handling in RSS fetches; `HTTP_TIMEOUT_SECONDS` exists in `config.py` but is not used by `feedparser.parse()`.
- `market_movers`, `reddit_signals`, and `sec_filings` are inactive stubs in current source code.
- Tests only cover ticker extraction.


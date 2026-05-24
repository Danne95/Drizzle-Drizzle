# API And Public Interfaces

This project exposes a CLI and module-level Python functions. It does not expose HTTP endpoints.

## CLI

### Generate Report

```powershell
python main.py [--mock-news]
```

| Argument | Type | Required | Purpose |
|---|---:|---:|---|
| `--mock-news` | flag | No | Use `samples/mock_news.json` instead of fetching configured RSS feeds. |

Output:

- Prints the timestamped report path.
- Prints the `latest_report.html` path.
- Writes raw snapshots to `data/`.
- Writes report to `reports/YYYY-MM-DD_HHMM.html`.
- Copies report to `latest_report.html`.

Auth:

- None.

## Main Orchestration

### `main.ensure_directories() -> None`

Creates `DATA_DIR` and `REPORTS_DIR` from `config.py`.

### `main.snapshot_json(name: str, payload: object, run_stamp: str) -> Path`

Writes JSON snapshot to:

```text
data/{name}_{run_stamp}.json
```

Serialization uses `json.dumps(..., indent=2, default=str)`.

### `main.run(use_mock_news: bool = False) -> Path`

Runs the full scanner pipeline and returns the timestamped report path.

Inputs:

| Parameter | Type | Default | Purpose |
|---|---:|---:|---|
| `use_mock_news` | `bool` | `False` | Passes through to `fetch_rss_news()`. |

Output:

| Type | Description |
|---|---|
| `Path` | Path to `reports/YYYY-MM-DD_HHMM.html`. |

Side effects:

- Creates `data/` and `reports/`.
- May update `data/symbol_universe_cache.json`.
- Writes raw snapshot JSON files.
- Writes a report HTML file.
- Copies report to `latest_report.html`.

### `main.parse_args() -> argparse.Namespace`

Defines CLI arguments. Current namespace field:

- `mock_news: bool`

## Source Interfaces

### `sources.rss_news.fetch_rss_news(use_mock: bool = False) -> list[dict]`

Purpose:

- Return RSS news records for scanner input.

Behavior:

- If `use_mock` is true, load `samples/mock_news.json`.
- Otherwise parse each feed in `config.RSS_FEEDS` using `feedparser`.
- Limit each feed to `config.MAX_RSS_ITEMS_PER_FEED`.
- Normalize entries via `_normalize_entry()`.
- Return mock news if all live feeds produce no usable titled items.

Auth:

- None.

### `sources.symbol_universe.fetch_symbol_universe() -> list[dict]`

Purpose:

- Return public listed symbols and company names for ticker extraction.

Behavior:

- Downloads NasdaqTrader `nasdaqlisted.txt` and `otherlisted.txt`.
- Parses pipe-delimited files.
- Filters unsupported symbols.
- Cleans company/security names.
- Caches successful result to `data/symbol_universe_cache.json`.
- On download/parse failure, returns cache if present, otherwise `[]`.

Auth:

- None.

### `sources.market_movers.fetch_market_movers() -> list[dict]`

Purpose:

- Extension point for gainers, price momentum, and volume spike data.

Current behavior:

- Returns `[]`.

Expected output schema:

- See `docs/DATA_MODELS.md#market-mover`.

### `sources.reddit_scanner.fetch_reddit_signals() -> list[dict]`

Purpose:

- Extension point for social mention momentum.

Current behavior:

- Returns `[]`.

Expected output schema:

- See `docs/DATA_MODELS.md#reddit-signal`.

### `sources.sec_filings.fetch_sec_filings() -> list[dict]`

Purpose:

- Extension point for SEC filing signals.

Current behavior:

- Returns `[]`.

Expected output schema:

- See `docs/DATA_MODELS.md#sec-filing-signal`.

### `sources.personal_oracle_profile.load_private_oracle_profile() -> dict`

Purpose:

- Load optional ignored local profile from `private/oracle_profile.json`.

Output:

- Profile dict if file exists, parses as JSON, and JSON root is an object.
- `{}` for missing file, invalid JSON, or non-object JSON.

### `sources.astrology_engine.generate_black_magic_reading(now: datetime | None = None, candidate_tickers: list[str] | None = None, personal_profile: dict | None = None) -> dict`

Purpose:

- Generate entertainment-only oracle payload for report Category C.

Inputs:

| Parameter | Type | Default | Purpose |
|---|---:|---:|---|
| `now` | `datetime | None` | `None` | Uses `datetime.now()` when omitted. Date drives deterministic seed. |
| `candidate_tickers` | `list[str] | None` | `None` | Candidate lucky tickers. |
| `personal_profile` | `dict | None` | `None` | Optional seed/zodiac override source. |

Output:

- Black Magic Reading dict. See `docs/DATA_MODELS.md#black-magic-reading`.

## Processor Interfaces

### `processors.ticker_extractor.extract_tickers(text: str, symbol_universe: list[dict] | None = None) -> list[str]`

Purpose:

- Extract sorted unique ticker symbols from text.

Rules:

- Company alias match from symbol universe.
- Cashtag match.
- Uppercase token match only if universe is empty or symbol exists in universe.
- Excludes `config.COMMON_FALSE_TICKERS`.
- Rejects generic aliases such as `"holdings"`, `"technology"`, `"group"`, `"new"`, etc.

### `processors.ticker_extractor.attach_tickers(news_items: list[dict], symbol_universe: list[dict] | None = None) -> list[dict]`

Purpose:

- Copy each news item and add `tickers`.

### `processors.sentiment_engine.score_sentiment(text: str) -> dict`

Purpose:

- Compute keyword-based sentiment score and hit list.

Output:

- `{"score": float, "hits": list[dict]}`

### `processors.sentiment_engine.attach_sentiment(news_items: list[dict]) -> list[dict]`

Purpose:

- Copy each news item and add `sentiment`.

### `processors.scoring_engine.score_opportunities(news_items: list[dict], market_movers: list[dict], reddit_signals: list[dict], sec_filings: list[dict], symbol_universe: list[dict] | None = None) -> list[dict]`

Purpose:

- Merge source records into explainable ticker opportunities.

Inputs:

- News items with `tickers` and optional `sentiment`.
- Market mover records.
- Reddit signal records.
- SEC filing records.
- Optional symbol universe for company names.

Output:

- List of opportunity dicts sorted by descending score.

### `processors.summarizer.build_market_brief(news_items: list[dict], opportunities: list[dict]) -> dict`

Purpose:

- Build aggregate dashboard summary.

Output:

- Market Brief dict. See `docs/DATA_MODELS.md#market-brief`.

## Report Interfaces

### `report.report_generator.generate_report(report_path: Path, generated_at: datetime, market_brief: dict, opportunities: list[dict], black_magic: dict, snapshot_paths: dict) -> Path`

Purpose:

- Render a self-contained HTML dashboard.

Inputs:

| Parameter | Type | Purpose |
|---|---:|---|
| `report_path` | `Path` | Destination HTML file. Parent is created. |
| `generated_at` | `datetime` | Display timestamp. |
| `market_brief` | `dict` | Summary panel and theme chart data. |
| `opportunities` | `list[dict]` | Cards and charts. |
| `black_magic` | `dict` | Category C oracle section. |
| `snapshot_paths` | `dict` | Footer display of raw snapshot paths. |

Output:

- Returns `report_path`.

### Chart Helpers

- `build_score_chart(opportunities: list[dict]) -> str`
- `build_risk_gauge(opportunities: list[dict]) -> str`
- `build_theme_chart(market_brief: dict) -> str`

These return Plotly offline HTML div strings for insertion into `dashboard.html`.


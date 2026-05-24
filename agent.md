# Agent Entrypoint

## Project Summary

Drizzle Drizzle Market Oracle is a local Python market intelligence scanner. It collects financial RSS headlines, builds or reuses a public listed-symbol universe, extracts tickers, attaches explainable sentiment, scores ticker opportunities, generates a comedic finance astrology section, snapshots raw inputs to JSON, and renders a local HTML dashboard.

The project is explicitly a research/reporting tool. It is not a trading bot, does not place trades, and does not provide financial advice.

## Read These Files First

- `agent.md`: operational entrypoint for future AI agents.
- `docs/ARCHITECTURE.md`: system layers, module boundaries, data flow, integrations.
- `docs/DATA_MODELS.md`: dictionary schemas passed between modules and generated snapshots.
- `docs/API.md`: CLI and public module interfaces.
- `docs/FLOWS.md`: main execution and edge-case flows.
- `docs/DECISIONS.md`: inferred technical decisions that should be preserved.
- `docs/TASKS.md`: user-managed task board template.
- `README.md`: human-facing setup/run overview.

## Tech Stack

| Area | Technology |
|---|---|
| Runtime | Python 3.10+ inferred from `str | None` union syntax |
| CLI | `argparse` in `main.py` |
| RSS parsing | `feedparser` |
| HTML templating | Jinja2 |
| Charts | Plotly offline divs embedded into HTML |
| Tests | Python `unittest` |
| Persistence | Local JSON and HTML files only |
| Database | None |
| Web server | None |

Dependencies are declared in `requirements.txt`:

```text
feedparser>=6.0.11
Jinja2>=3.1.4
plotly>=5.24.1
```

## Repository Layout

```text
.
├── main.py                         # CLI entrypoint and pipeline orchestration
├── config.py                       # paths, RSS feeds, scoring keyword weights
├── processors/
│   ├── ticker_extractor.py         # cashtag/symbol/company-name extraction
│   ├── sentiment_engine.py         # simple keyword sentiment scoring
│   ├── scoring_engine.py           # signal merge, scoring, category assignment
│   └── summarizer.py               # market brief summary object
├── sources/
│   ├── rss_news.py                 # live RSS fetch with mock fallback
│   ├── symbol_universe.py          # NasdaqTrader universe download/cache
│   ├── market_movers.py            # currently empty integration stub
│   ├── reddit_scanner.py           # currently empty integration stub
│   ├── sec_filings.py              # currently empty integration stub
│   ├── astrology_engine.py         # deterministic satire/oracle output
│   └── personal_oracle_profile.py  # ignored private profile loader
├── report/
│   ├── report_generator.py         # Jinja2 + Plotly report renderer
│   └── templates/                  # dashboard HTML, card partial, CSS
├── samples/                        # deterministic mock news and profile example
├── tests/                          # unittest tests
├── data/                           # generated JSON snapshots and symbol cache
├── reports/                        # generated timestamped HTML reports
└── latest_report.html              # generated latest dashboard copy
```

## Setup

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Run

Live RSS with local fallbacks:

```powershell
python main.py
```

Deterministic mock-news run:

```powershell
python main.py --mock-news
```

Outputs:

- `reports/YYYY-MM-DD_HHMM.html`: timestamped dashboard.
- `latest_report.html`: copy of the most recent dashboard.
- `data/{source}_YYYY-MM-DD_HHMM.json`: raw source snapshots.
- `data/symbol_universe_cache.json`: cached public symbol universe after a successful download.

## Test

```powershell
python -m unittest discover
```

Current tests cover ticker extraction behavior in `tests/test_ticker_extractor.py`.

## Environment Variables

No environment variables are required by the current code.

Optional local private data is read from `private/oracle_profile.json`. This path is ignored by Git and should not be snapshotted or rendered directly. Use `samples/oracle_profile.example.json` as the shape:

```json
{
  "name": "Your first name or nickname",
  "birthdate": "1990-01-31",
  "zodiac": "",
  "chinese_zodiac": ""
}
```

## External Network Dependencies

- RSS feeds configured in `config.RSS_FEEDS`:
  - Yahoo Finance: `https://finance.yahoo.com/news/rssindex`
  - MarketWatch: `https://feeds.marketwatch.com/marketwatch/topstories/`
  - CNBC Markets: `https://www.cnbc.com/id/100003114/device/rss/rss.html`
- Listed symbol universe from NasdaqTrader:
  - `https://www.nasdaqtrader.com/dynamic/SymDir/nasdaqlisted.txt`
  - `https://www.nasdaqtrader.com/dynamic/SymDir/otherlisted.txt`

If RSS returns no usable items, `sources/rss_news.py` falls back to `samples/mock_news.json`. If NasdaqTrader symbol download fails, `sources/symbol_universe.py` falls back to `data/symbol_universe_cache.json` if present, otherwise an empty universe.

## Coding Conventions Observed

- Modules pass plain dictionaries and `list[dict]` records rather than dataclasses or Pydantic models.
- Source modules isolate external collection logic and expose `fetch_*()` functions.
- Processor modules are pure or mostly pure transformations over dictionary lists.
- Report generation is centralized in `report/report_generator.py`; templates stay in `report/templates/`.
- Scoring is intentionally explainable: every added score has a signal label, description, weight, and evidence record.
- Generated files are ignored by Git via `.gitignore`; do not commit `data/`, `reports/`, `latest_report.html`, `private/`, virtualenvs, or cache directories.
- The project prefers local deterministic fallbacks over hard failure for unavailable external feeds.
- No preset active ticker list should be introduced into extraction logic. Ticker detection should use the downloaded/cached listed-symbol universe, cashtags, and validated uppercase symbol matches.

## Important Implementation Notes

- `sources/market_movers.py`, `sources/reddit_scanner.py`, and `sources/sec_filings.py` currently return empty lists by design. Their expected future schemas are inferred from `processors/scoring_engine.py` and historical snapshots; see `docs/DATA_MODELS.md`.
- `build_market_brief()` text still says it blends market mover, social, and SEC signals even when those sources return empty lists. Preserve or adjust this deliberately if source behavior changes.
- `score_opportunities()` promotes one opportunity to `high_risk` as a Category B fallback when no true speculative category exists.
- `generate_black_magic_reading()` is deterministic per date plus optional profile-derived seed data.


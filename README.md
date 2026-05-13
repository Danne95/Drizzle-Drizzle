# Drizzle Drizzle Market Oracle

Local Python market intelligence scanner that aggregates financial news, demo market movers, demo Reddit momentum, demo SEC filing signals, and a deliberately comedic finance astrology oracle.

This is a research and reporting tool. It is not a trading bot and does not provide financial advice.

## What It Generates

- Interactive HTML dashboard saved in `reports/`
- Raw JSON snapshots saved in `data/`
- Serious market signal section
- High-risk speculative momentum section
- Meme black magic finance section
- Explainable scores with weighted signals and evidence snippets

## Setup

```bash
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Run

Fetch live RSS feeds where possible, with local fallbacks:

```bash
python main.py
```

Use bundled mock news for a deterministic demo:

```bash
python main.py --mock-news
```

The generated report path is printed after each run.

## Project Structure

```text
.
├── main.py
├── config.py
├── sources/
│   ├── rss_news.py
│   ├── market_movers.py
│   ├── reddit_scanner.py
│   ├── sec_filings.py
│   └── astrology_engine.py
├── processors/
│   ├── ticker_extractor.py
│   ├── scoring_engine.py
│   ├── sentiment_engine.py
│   └── summarizer.py
├── report/
│   ├── report_generator.py
│   └── templates/
├── samples/
├── data/
├── reports/
└── requirements.txt
```

## Extending Sources

Each source module returns plain dictionaries. Replace demo implementations in `sources/market_movers.py`, `sources/reddit_scanner.py`, or `sources/sec_filings.py` with real API clients while keeping the same output keys.

Useful future upgrades:

- Add paid market data provider in `sources/market_movers.py`
- Add Reddit API or Pushshift-compatible source in `sources/reddit_scanner.py`
- Add SEC submissions API support in `sources/sec_filings.py`
- Expand `TICKER_ALIASES` in `config.py`
- Tune signal weights in `config.py`

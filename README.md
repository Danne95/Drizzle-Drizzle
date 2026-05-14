# Drizzle Drizzle Market Oracle

Local Python market intelligence scanner that aggregates financial news, dynamic listed-symbol detection, and a deliberately comedic finance astrology oracle.

This is a research and reporting tool. It is not a trading bot and does not provide financial advice.

## What It Generates

- Interactive HTML dashboard saved as `latest_report.html` in the project root
- Timestamped HTML dashboard copies saved in `reports/`
- Raw JSON snapshots saved in `data/`
- Serious market signal section
- High-risk speculative momentum section
- Meme black magic finance section
- Explainable scores with weighted signals and evidence snippets
- No preset closed ticker list in active extraction logic

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

Each run also replaces `latest_report.html` in the project root. Historical
copies use `YYYY-MM-DD_HHMM.html` naming inside `reports/`.

## Optional Private Oracle Profile

The entertainment oracle can use a private local profile without committing
personal data. Copy the template from `samples/oracle_profile.example.json` to
`private/oracle_profile.json` and edit it locally:

```json
{
  "name": "Your first name or nickname",
  "birthdate": "1990-01-31",
  "zodiac": "",
  "chinese_zodiac": ""
}
```

The `private/` folder is ignored by Git. The report does not print your name or
birthdate; it only uses derived oracle outputs for the comedy section.

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
│   ├── symbol_universe.py
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

Each source module returns plain dictionaries. `sources/market_movers.py`,
`sources/reddit_scanner.py`, and `sources/sec_filings.py` intentionally return
empty lists until you wire real APIs into them, so normal runs do not inject
preset tickers.

Useful future upgrades:

- Add paid market data provider in `sources/market_movers.py`
- Add Reddit API or Pushshift-compatible source in `sources/reddit_scanner.py`
- Add SEC submissions API support in `sources/sec_filings.py`
- Tune signal weights in `config.py`

Ticker detection does not use a preset ticker list in `config.py`. The scanner
downloads and caches a broad public listed-symbol universe in
`sources/symbol_universe.py`, then uses that universe plus cashtags and exact
uppercase ticker-like mentions.

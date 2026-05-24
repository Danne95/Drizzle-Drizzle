# Decisions

## Use A Local CLI Instead Of A Service

Evidence:

- `main.py` is the only executable entrypoint.
- No web framework or server dependency exists in `requirements.txt`.
- Reports are written to local HTML files.

Decision:

- Keep the scanner as a local batch-style report generator unless a user explicitly asks for service behavior.

Rationale inferred from code:

- The app is intended for personal research snapshots and local HTML review, not multi-user serving.

## Keep Source Integrations Isolated

Evidence:

- Each data source has a dedicated `sources/*.py` module.
- `rss_news.py` comment says feed changes or paid APIs should not affect the rest of the scanner.
- Stub modules for market movers, Reddit, and SEC preserve `fetch_*()` boundaries.

Decision:

- Add or replace integrations inside the matching source module while preserving downstream schemas.

Rationale inferred from code:

- External providers are volatile; processors and report generation should remain stable.

## Use Plain Dictionaries Instead Of Formal Models

Evidence:

- All source and processor functions accept and return `list[dict]` or `dict`.
- No dataclass, Pydantic, ORM, or schema dependency exists.
- Snapshots directly serialize payload dictionaries.

Decision:

- Continue using dictionary contracts unless the project grows enough to justify typed model validation.

Rationale inferred from code:

- Plain dictionaries make it easy to snapshot raw inputs and keep the pipeline lightweight.

## Avoid A Preset Active Ticker List

Evidence:

- `README.md` says there is no preset closed ticker list in active extraction logic.
- `sources/market_movers.py`, `reddit_scanner.py`, and `sec_filings.py` explicitly return empty lists until real APIs are wired.
- `ticker_extractor.py` uses symbol universe, cashtags, and uppercase validation instead of a hardcoded watchlist.

Decision:

- Do not add static demo ticker injection to normal runtime behavior.

Rationale inferred from code:

- The scanner should surface tickers from current data and public symbol listings, not from a biased built-in watchlist.

## Cache Symbol Universe Locally

Evidence:

- `sources/symbol_universe.py` writes successful downloads to `data/symbol_universe_cache.json`.
- On download failure it returns cache if present.

Decision:

- Preserve cache fallback for public symbol universe.

Rationale inferred from code:

- Ticker extraction quality depends heavily on symbol universe availability; cache avoids total degradation when NasdaqTrader is unavailable.

## Use Mock News As A Deterministic Fallback

Evidence:

- `fetch_rss_news(use_mock=True)` directly loads `samples/mock_news.json`.
- Live RSS flow returns mock news if all feeds produce no items.
- README documents `python main.py --mock-news`.

Decision:

- Maintain bundled mock news for demos and degraded external-feed behavior.

Rationale inferred from code:

- The report generator should remain usable when live feeds are unavailable.

## Make Scores Explainable

Evidence:

- `scoring_engine.py` defines `SIGNAL_LABELS` and `SIGNAL_EXPLANATIONS`.
- `_add_signal()` appends both signal metadata and evidence source records.
- Opportunity cards render "Why It Scored" and "Top Evidence".

Decision:

- Any new scoring input should add explicit signal type, label, description, weight, and evidence.

Rationale inferred from code:

- The app is a triage/research dashboard; visible evidence matters more than opaque ranking.

## Separate Serious And Speculative Categories

Evidence:

- `_classify()` compares speculative and serious signal weights.
- `dashboard.html` renders Category A "Serious Market Signals" and Category B "Degenerate Momentum Watch".
- `score_opportunities()` forces a Category B fallback when opportunities exist but no true high-risk item is classified.

Decision:

- Preserve the two-category report structure and its fallback behavior unless intentionally changing product semantics.

Rationale inferred from code:

- The report is designed to always make serious vs speculative review distinct.

## Treat The Oracle Section As Entertainment-Only

Evidence:

- `astrology_engine.py` docstring says the output is intentionally entertainment, not analysis.
- `generate_black_magic_reading()` returns an explicit disclaimer.
- README calls it a "deliberately comedic finance astrology oracle".

Decision:

- Keep Category C clearly separated from serious scoring and keep disclaimers visible.

Rationale inferred from code:

- The app intentionally blends serious market scanning with satire, but avoids presenting oracle output as analysis.

## Keep Private Profile Local And Non-Rendered

Evidence:

- `.gitignore` excludes `/private/`.
- `personal_oracle_profile.py` loads `private/oracle_profile.json`.
- README says the report does not print name or birthdate.
- `astrology_engine.py` uses profile data only for derived seed/zodiac outputs.

Decision:

- Never snapshot or render raw private profile data.

Rationale inferred from code:

- Profile data personalizes satire while avoiding accidental disclosure.

## Render Self-Contained HTML Reports

Evidence:

- `dashboard.html` includes `styles.css` inline.
- `report_generator.py` embeds Plotly charts as offline divs.
- `generate_report()` writes standalone HTML files.

Decision:

- Continue generating local standalone HTML artifacts rather than requiring an app server.

Rationale inferred from code:

- Reports should be easy to open and archive from the filesystem.

## Generated Artifacts Stay Out Of Git

Evidence:

- `.gitignore` excludes `/data/`, `/reports/`, `/latest_report.html`, `/private/`, virtualenvs, and caches.

Decision:

- Do not commit generated scanner output or private local state.

Rationale inferred from code:

- Outputs are run-specific and may include large snapshots; private profile data must stay local.

## Current Test Focus Is Ticker Extraction

Evidence:

- Only `tests/test_ticker_extractor.py` exists.
- Tests validate company alias, cashtag, universe-restricted uppercase symbols, and false positive avoidance.

Decision:

- When changing extraction logic, update or extend these tests first.
- When changing scoring/report behavior, add focused tests because none currently cover those areas.

Rationale inferred from code:

- Ticker extraction is the highest-risk text-parsing component currently covered by tests.

## Use Local Time For Report Names

Evidence:

- `main.run()` uses `datetime.now()` without timezone for `run_stamp` and display timestamp.
- RSS item fetch timestamps use UTC in `_normalize_entry()`.

Decision:

- Preserve local-time report naming unless changing timestamp semantics across the project.

Rationale inferred from code:

- Filenames and displayed generation time are meant for the local operator, while fetched records use UTC capture timestamps.


# Flows

## Full Report Generation

Entry:

```powershell
python main.py
```

Steps:

1. `parse_args()` reads `--mock-news`.
2. `run(use_mock_news=args.mock_news)` starts the pipeline.
3. `ensure_directories()` creates `data/` and `reports/`.
4. `run_stamp` is generated with local `datetime.now().strftime("%Y-%m-%d_%H%M")`.
5. `fetch_symbol_universe()` downloads or loads listed symbols.
6. `fetch_rss_news(use_mock=use_mock_news)` fetches live RSS records or mock records.
7. `fetch_market_movers()`, `fetch_reddit_signals()`, and `fetch_sec_filings()` return empty lists in current code.
8. `attach_tickers(raw_news, symbol_universe)` adds `tickers` to each news item.
9. `attach_sentiment(news_with_tickers)` adds `sentiment` to each news item.
10. `score_opportunities(...)` merges news, market movers, Reddit, and SEC signals into scored opportunity records.
11. `symbol_candidates` is set to opportunity tickers if any opportunities exist; otherwise all tickers from symbol universe.
12. `load_private_oracle_profile()` reads optional `private/oracle_profile.json`.
13. `generate_black_magic_reading(now, candidate_tickers=symbol_candidates, personal_profile=oracle_profile)` creates Category C content.
14. `build_market_brief(news_with_sentiment, opportunities)` creates dashboard summary data.
15. `snapshot_json()` writes raw source/oracle/universe payloads under `data/`.
16. `generate_report()` renders `reports/YYYY-MM-DD_HHMM.html`.
17. `shutil.copyfile()` updates `latest_report.html`.
18. CLI prints both generated paths.

## Mock News Flow

Entry:

```powershell
python main.py --mock-news
```

Differences from full flow:

1. `fetch_rss_news(use_mock=True)` skips live feeds.
2. News records come from `samples/mock_news.json`.
3. Symbol universe is still fetched or loaded from cache.
4. All downstream ticker extraction, sentiment, scoring, oracle generation, snapshots, and report rendering still run.

This flow is useful for deterministic demos, but ticker extraction can still vary if the symbol universe is unavailable or cache differs.

## RSS Fallback Flow

When `python main.py` runs without `--mock-news`:

1. `sources/rss_news.fetch_rss_news()` parses each configured feed.
2. Each feed contributes up to `MAX_RSS_ITEMS_PER_FEED` entries.
3. Entries without titles are skipped.
4. If at least one normalized item exists, those items are returned.
5. If no items exist, `_load_mock_news()` returns `samples/mock_news.json`.

Critical edge case:

- `feedparser.parse()` errors are not explicitly caught. If feedparser raises instead of returning an empty parsed object, the run may fail. <!-- UNCLEAR: feedparser.parse behavior for all network failures is not handled explicitly in this code. -->

## Symbol Universe Flow

1. `fetch_symbol_universe()` ensures `data/` exists.
2. `_download_universe()` reads both NasdaqTrader symbol directory URLs.
3. `_parse_pipe_file()` parses headers and rows.
4. Symbols are filtered out when empty, containing `$`, containing `.`, or longer than 5 characters.
5. `_clean_company_name()` removes security suffixes and normalizes whitespace.
6. Universe is deduplicated by ticker and sorted.
7. Successful non-empty universe is cached to `data/symbol_universe_cache.json`.
8. If download or parsing fails, cache is returned if it exists.
9. If cache does not exist, returns `[]`.

Impact:

- With an empty universe, company-name alias extraction cannot match.
- With an empty universe, uppercase ticker extraction becomes permissive except for `COMMON_FALSE_TICKERS` because `not known_symbols` is true.

## Ticker Extraction Flow

For each news item:

1. `attach_tickers()` concatenates `title` and `summary`.
2. `extract_tickers()` lowercases text for company alias matching.
3. `_company_aliases()` maps each universe ticker to company aliases.
4. `_alias_matches()` rejects short/generic aliases and uses word-boundary-style regex matching.
5. Matching company aliases add their ticker.
6. Cashtags like `$IONQ` add symbols unless in `COMMON_FALSE_TICKERS`.
7. Uppercase tokens like `XYZ` add symbols if not false positives and either:
   - no known symbol universe exists, or
   - token exists in the known universe.
8. Sorted tickers are returned.

Covered by tests:

- Company alias extraction for `Rocket Lab USA` -> `RKLB`.
- Cashtag extraction for `$IONQ`.
- Universe-validated uppercase extraction for `XYZ`.
- Avoiding false positives from generic macro text.

## Scoring Flow

`score_opportunities()` builds one bucket per ticker.

News signals:

1. Skip news items without `tickers`.
2. For every ticker in an item, add `news_velocity` with weight `0.8`.
3. Add `serious_keyword` for each matching `config.SERIOUS_KEYWORDS` term.
4. Add `meme_keyword` for each matching `config.SPECULATIVE_KEYWORDS` term.
5. Add `theme` with weight `0.7` for matching `config.THEME_KEYWORDS`.
6. Add `headline_sentiment` with weight `abs(sentiment) * 0.8` when sentiment score is non-zero.

Market mover signals:

1. Add `price_momentum` with `min(abs(move_percent) / 4, 4.0)`.
2. Add `volume_spike` with `min(relative_volume / 1.5, 4.5)` only when `relative_volume >= 2`.

Reddit signals:

1. Add `reddit_spike` with `min(mention_change_percent / 75, 5.0)`.
2. Add `squeeze_language` with `2.8` when truthy.

SEC filing signals:

1. Add `sec_filing` using `importance` or default `1.5`.

Finalization:

1. Sort signals by descending weight.
2. Sum total score and round to one decimal.
3. Classify as `high_risk` only if speculative weight is at least `3.8` and greater than or equal to `serious * 1.1`; otherwise classify as `serious`.
4. Derive score label/help.
5. Keep top 5 evidence sources.
6. Sort opportunities by descending score.
7. If no opportunity is `high_risk`, force the highest `(speculative_score, score)` opportunity into `high_risk` with a fallback marker.

Edge case:

- If there are no opportunities, no fallback is applied and reports render empty Category A/B sections.

## Report Rendering Flow

1. `generate_report()` creates a Jinja2 environment rooted at `report/templates`.
2. It builds three Plotly chart HTML divs:
   - `score_chart`
   - `risk_gauge`
   - `theme_chart`
3. `_split_categories()` separates opportunities into `serious` and `high_risk`.
4. `dashboard.html` renders:
   - Header and generated timestamp.
   - Market brief metrics.
   - Charts.
   - Category A opportunity cards.
   - Category B opportunity cards.
   - Category C black magic/oracle panels.
   - Snapshot path footer.
5. `styles.css` is included inline inside the HTML.
6. `opportunity_card.html` is included for each opportunity.
7. The final HTML is written to `report_path`.

## Private Oracle Flow

1. `load_private_oracle_profile()` checks `private/oracle_profile.json`.
2. Missing file returns `{}`.
3. Invalid JSON returns `{}`.
4. JSON whose root is not an object returns `{}`.
5. Valid object is passed to `generate_black_magic_reading()`.
6. `name` and `birthdate` affect deterministic random seed.
7. `birthdate` can derive western and Chinese zodiac if explicit values are absent.
8. `zodiac` and `chinese_zodiac` profile fields override derived values.
9. The report renders derived oracle output but not raw `name` or `birthdate`.


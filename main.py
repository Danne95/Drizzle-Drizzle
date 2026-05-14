"""Run the local market intelligence scanner and generate an HTML report."""

from __future__ import annotations

import argparse
import json
import shutil
from datetime import datetime
from pathlib import Path

from config import BASE_DIR, DATA_DIR, REPORTS_DIR
from processors.scoring_engine import score_opportunities
from processors.sentiment_engine import attach_sentiment
from processors.summarizer import build_market_brief
from processors.ticker_extractor import attach_tickers
from report.report_generator import generate_report
from sources.astrology_engine import generate_black_magic_reading
from sources.market_movers import fetch_market_movers
from sources.reddit_scanner import fetch_reddit_signals
from sources.rss_news import fetch_rss_news
from sources.sec_filings import fetch_sec_filings
from sources.symbol_universe import fetch_symbol_universe
from sources.personal_oracle_profile import load_private_oracle_profile


def ensure_directories() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)


def snapshot_json(name: str, payload: object, run_stamp: str) -> Path:
    path = DATA_DIR / f"{name}_{run_stamp}.json"
    path.write_text(json.dumps(payload, indent=2, default=str), encoding="utf-8")
    return path


def run(use_mock_news: bool = False) -> Path:
    ensure_directories()
    now = datetime.now()
    run_stamp = now.strftime("%Y-%m-%d_%H%M")
    report_name = f"{run_stamp}.html"
    latest_report_path = BASE_DIR / "latest_report.html"

    symbol_universe = fetch_symbol_universe()
    raw_news = fetch_rss_news(use_mock=use_mock_news)
    market_movers = fetch_market_movers()
    reddit_signals = fetch_reddit_signals()
    sec_filings = fetch_sec_filings()
    news_with_tickers = attach_tickers(raw_news, symbol_universe=symbol_universe)
    news_with_sentiment = attach_sentiment(news_with_tickers)

    opportunities = score_opportunities(
        news_items=news_with_sentiment,
        market_movers=market_movers,
        reddit_signals=reddit_signals,
        sec_filings=sec_filings,
        symbol_universe=symbol_universe,
    )
    symbol_candidates = [item["ticker"] for item in opportunities] or [item["ticker"] for item in symbol_universe if item.get("ticker")]
    oracle_profile = load_private_oracle_profile()
    black_magic = generate_black_magic_reading(now, candidate_tickers=symbol_candidates, personal_profile=oracle_profile)
    market_brief = build_market_brief(news_with_sentiment, opportunities)

    snapshot_paths = {
        "news": str(snapshot_json("news", raw_news, run_stamp)),
        "market_movers": str(snapshot_json("market_movers", market_movers, run_stamp)),
        "reddit": str(snapshot_json("reddit", reddit_signals, run_stamp)),
        "sec_filings": str(snapshot_json("sec_filings", sec_filings, run_stamp)),
        "black_magic": str(snapshot_json("black_magic", black_magic, run_stamp)),
        "symbol_universe": str(snapshot_json("symbol_universe", symbol_universe, run_stamp)),
    }

    report_path = generate_report(
        report_path=REPORTS_DIR / report_name,
        generated_at=now,
        market_brief=market_brief,
        opportunities=opportunities,
        black_magic=black_magic,
        snapshot_paths=snapshot_paths,
    )
    shutil.copyfile(report_path, latest_report_path)
    return report_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate a local market intelligence report.")
    parser.add_argument(
        "--mock-news",
        action="store_true",
        help="Use bundled example news instead of fetching RSS feeds.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    output = run(use_mock_news=args.mock_news)
    print(f"Report generated: {output}")
    print(f"Latest report copied to: {BASE_DIR / 'latest_report.html'}")

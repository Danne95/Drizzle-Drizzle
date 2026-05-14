"""HTML report generation with Jinja2 and Plotly."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

import plotly.graph_objects as go
from jinja2 import Environment, FileSystemLoader, select_autoescape
from plotly.offline import plot

from config import BASE_DIR, APP_NAME


def _plot_div(fig: go.Figure, include_plotlyjs: bool = False) -> str:
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=32, r=24, t=36, b=32),
        font=dict(color="#d8e1ff", family="Inter, Segoe UI, Arial"),
    )
    return plot(fig, include_plotlyjs=include_plotlyjs, output_type="div", config={"displayModeBar": False, "responsive": True})


def build_score_chart(opportunities: list[dict]) -> str:
    top = opportunities[:10]
    fig = go.Figure(
        data=[
            go.Bar(
                x=[item["ticker"] for item in top],
                y=[item["score"] for item in top],
                marker_color=["#ff4d7d" if item["category"] == "high_risk" else "#2dd4bf" for item in top],
                hovertext=[f"{item['company']}<br>{item['score_label']}<br>{item['top_reason']}" for item in top],
            )
        ]
    )
    fig.update_layout(
        title="Watchlist Attention Score",
        yaxis_title="Relative evidence score",
        xaxis_title="",
        annotations=[
            {
                "text": "Higher means more scanner evidence stacked up. It is a triage score, not a recommendation.",
                "xref": "paper",
                "yref": "paper",
                "x": 0,
                "y": 1.15,
                "showarrow": False,
                "align": "left",
                "font": {"size": 12, "color": "#91a1bd"},
            }
        ],
    )
    return _plot_div(fig, include_plotlyjs=True)


def build_risk_gauge(opportunities: list[dict]) -> str:
    high_risk = sum(1 for item in opportunities if item["category"] == "high_risk")
    total = max(len(opportunities), 1)
    risk_percent = round(high_risk / total * 100)
    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=risk_percent,
            number={"suffix": "%"},
            title={"text": "Speculative Share of This Report"},
            gauge={
                "axis": {"range": [0, 100]},
                "bar": {"color": "#ff4d7d"},
                "steps": [
                    {"range": [0, 35], "color": "#0f766e"},
                    {"range": [35, 70], "color": "#a16207"},
                    {"range": [70, 100], "color": "#991b1b"},
                ],
            },
        )
    )
    fig.update_layout(
        annotations=[
            {
                "text": "Percent of surfaced tickers classified as meme/speculative. 0% means no speculative signals passed the current rules.",
                "xref": "paper",
                "yref": "paper",
                "x": 0.5,
                "y": -0.08,
                "showarrow": False,
                "align": "center",
                "font": {"size": 12, "color": "#91a1bd"},
            }
        ]
    )
    return _plot_div(fig)


def build_theme_chart(market_brief: dict) -> str:
    themes = market_brief.get("dominant_themes", []) or [{"theme": "No Themes", "count": 0}]
    fig = go.Figure(
        data=go.Bar(
            x=[item["count"] for item in themes],
            y=[item["theme"] for item in themes],
            orientation="h",
            marker_color="#60a5fa",
            hovertext=[f"{item['count']} surfaced ticker(s) matched this theme" for item in themes],
        )
    )
    fig.update_layout(
        title="Theme Breakdown",
        height=250,
        xaxis_title="Tickers matched",
        yaxis_title="",
        annotations=[
            {
                "text": "Shows which broad story themes appeared in the current watchlist.",
                "xref": "paper",
                "yref": "paper",
                "x": 0,
                "y": 1.2,
                "showarrow": False,
                "align": "left",
                "font": {"size": 12, "color": "#91a1bd"},
            }
        ],
    )
    return _plot_div(fig)


def _split_categories(opportunities: list[dict]) -> dict:
    return {
        "serious": [item for item in opportunities if item["category"] == "serious"],
        "high_risk": [item for item in opportunities if item["category"] == "high_risk"],
    }


def generate_report(
    report_path: Path,
    generated_at: datetime,
    market_brief: dict,
    opportunities: list[dict],
    black_magic: dict,
    snapshot_paths: dict,
) -> Path:
    """Render a self-contained local HTML report."""
    env = Environment(
        loader=FileSystemLoader(BASE_DIR / "report" / "templates"),
        autoescape=select_autoescape(["html", "xml"]),
    )
    template = env.get_template("dashboard.html")
    charts = {
        "score_chart": build_score_chart(opportunities),
        "risk_gauge": build_risk_gauge(opportunities),
        "theme_chart": build_theme_chart(market_brief),
    }
    html = template.render(
        app_name=APP_NAME,
        generated_at=generated_at,
        market_brief=market_brief,
        opportunities=opportunities,
        categories=_split_categories(opportunities),
        black_magic=black_magic,
        snapshot_paths=snapshot_paths,
        charts=charts,
    )
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(html, encoding="utf-8")
    return report_path

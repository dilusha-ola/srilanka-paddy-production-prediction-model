"""Reusable Plotly visualizations for Sri Lankan paddy analytics. No Streamlit calls."""
from typing import Optional

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from config import settings

_SEASON_COLORS = {
    "Maha": settings.COLORS["maha"],
    "Yala": settings.COLORS["yala"],
}


def _apply_clean_layout(
    fig: go.Figure,
    title: str,
    x_title: str = "",
    y_title: str = "",
    height: int = 420,
    show_legend: bool = True,
) -> go.Figure:
    fig.update_layout(
        title=dict(
            text=title,
            font=dict(size=17, color=settings.COLORS["primary"], family="Inter, sans-serif"),
            x=0.0,
            xanchor="left",
            y=0.97,
            yanchor="top",
        ),
        height=height,
        margin=dict(l=64, r=24, t=72, b=48),
        paper_bgcolor="#FFFFFF",
        plot_bgcolor="#FFFFFF",
        font=dict(size=13, color=settings.COLORS["text"], family="Inter, sans-serif"),
        showlegend=show_legend,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.01,
            xanchor="right",
            x=1.0,
            title=None,
            font=dict(size=13),
        ),
        hovermode="x unified" if show_legend else "closest",
    )
    fig.update_xaxes(
        title=dict(text=x_title, font=dict(size=13, color=settings.COLORS["text"])),
        showgrid=True,
        gridcolor="#EEF4EE",
        linecolor="#DCE7DC",
        tickfont=dict(size=12),
        automargin=True,
    )
    fig.update_yaxes(
        title=dict(text=y_title, font=dict(size=13, color=settings.COLORS["text"])),
        showgrid=True,
        gridcolor="#EEF4EE",
        linecolor="#DCE7DC",
        tickfont=dict(size=12),
        automargin=True,
    )
    return fig


def historical_production_trend_chart(
    df: pd.DataFrame,
    split_by_season: bool = True,
    title: str = "Historical Paddy Production Trend (000 MT)",
    height: int = 420,
) -> go.Figure:
    """Line chart of yearly total paddy production (000 MT)."""
    if split_by_season and df["season"].nunique() > 1:
        agg = (
            df.groupby(["year", "season"], as_index=False)[settings.TARGET_COLUMN]
            .sum()
            .sort_values("year")
        )
        fig = px.line(
            agg,
            x="year",
            y=settings.TARGET_COLUMN,
            color="season",
            color_discrete_map=_SEASON_COLORS,
            markers=True,
            labels={
                "year": "Year",
                settings.TARGET_COLUMN: "Production (000 MT)",
                "season": "Season",
            },
        )
        fig.update_traces(line=dict(width=2.6), marker=dict(size=5))
        return _apply_clean_layout(
            fig,
            title=title,
            x_title="Year",
            y_title="Total Production (000 MT)",
            height=height,
            show_legend=True,
        )

    agg = (
        df.groupby("year", as_index=False)[settings.TARGET_COLUMN]
        .sum()
        .sort_values("year")
    )
    fig = px.area(
        agg,
        x="year",
        y=settings.TARGET_COLUMN,
        labels={"year": "Year", settings.TARGET_COLUMN: "Production (000 MT)"},
    )
    fig.update_traces(
        line=dict(color=settings.COLORS["primary"], width=2.8),
        fillcolor="rgba(34, 139, 34, 0.12)",
        mode="lines+markers",
        marker=dict(size=5, color=settings.COLORS["primary"]),
    )
    return _apply_clean_layout(
        fig,
        title=title,
        x_title="Year",
        y_title="Total Production (000 MT)",
        height=height,
        show_legend=False,
    )


def seasonal_comparison_chart(
    df: pd.DataFrame,
    title: str = "Maha vs Yala Season Production Comparison",
    height: int = 400,
) -> go.Figure:
    """Grouped bar comparison of mean and total production across seasons."""
    stats = (
        df.groupby("season", as_index=False)
        .agg(
            total_prod=(settings.TARGET_COLUMN, "sum"),
            avg_prod=(settings.TARGET_COLUMN, "mean"),
            avg_yield=("average_yield_kg_ha", "mean"),
        )
        .sort_values("total_prod", ascending=False)
    )
    fig = go.Figure()
    for _, row in stats.iterrows():
        season = row["season"]
        color = _SEASON_COLORS.get(season, settings.COLORS["secondary"])
        fig.add_trace(
            go.Bar(
                name=season,
                x=["Total Production (000 MT)", "Average per Record (000 MT)"],
                y=[row["total_prod"], row["avg_prod"]],
                marker_color=color,
                text=[f"{row['total_prod']:,.0f}", f"{row['avg_prod']:,.1f}"],
                textposition="outside",
            )
        )
    fig.update_layout(barmode="group")
    _apply_clean_layout(
        fig,
        title=title,
        x_title="Production Metric",
        y_title="Production (000 MT)",
        height=height,
        show_legend=True,
    )
    fig.update_layout(hovermode="closest")
    fig.update_yaxes(rangemode="tozero")
    return fig


def seasonal_average_chart(
    df: pd.DataFrame,
    title: str = "Average Production per Record by Season",
    height: int = 380,
) -> go.Figure:
    """Clean side-by-side comparison of Maha and Yala average production (000 MT)."""
    stats = (
        df.groupby("season", as_index=False)[settings.TARGET_COLUMN]
        .agg(["mean", "median", "sum", "count"])
        .reset_index()
    )
    fig = px.bar(
        stats,
        x="season",
        y="mean",
        color="season",
        color_discrete_map=_SEASON_COLORS,
        text=stats["mean"].map(lambda v: f"{v:,.1f}k MT"),
        labels={"season": "Season", "mean": "Mean Production (000 MT)"},
    )
    fig.update_traces(textposition="outside", width=0.48)
    _apply_clean_layout(
        fig,
        title=title,
        x_title="Cultivation Season",
        y_title="Mean Production (000 MT)",
        height=height,
        show_legend=False,
    )
    fig.update_yaxes(range=[0, float(stats["mean"].max()) * 1.18])
    return fig


def district_production_chart(
    df: pd.DataFrame,
    top_n: Optional[int] = None,
    title: str = "District-wise Total Paddy Production (000 MT)",
    height: int = 580,
) -> go.Figure:
    """Horizontal bar chart of total production across districts."""
    agg = (
        df.groupby("district", as_index=False)[settings.TARGET_COLUMN]
        .sum()
        .sort_values(settings.TARGET_COLUMN, ascending=True)
    )
    if top_n is not None and top_n > 0:
        agg = agg.tail(top_n)

    fig = px.bar(
        agg,
        x=settings.TARGET_COLUMN,
        y="district",
        orientation="h",
        text=agg[settings.TARGET_COLUMN].map(lambda v: f"{v:,.0f}"),
        labels={
            "district": "District",
            settings.TARGET_COLUMN: "Total Production (000 MT)",
        },
        color=settings.TARGET_COLUMN,
        color_continuous_scale=["#BBF7D0", "#228B22", "#14532D"],
    )
    fig.update_traces(textposition="outside")
    fig.update_coloraxes(showscale=False)
    _apply_clean_layout(
        fig,
        title=title,
        x_title="Total Production (000 MT)",
        y_title="District",
        height=height,
        show_legend=False,
    )
    fig.update_xaxes(range=[0, float(agg[settings.TARGET_COLUMN].max()) * 1.14])
    return fig


def production_distribution_chart(
    df: pd.DataFrame,
    title: str = "Paddy Production Distribution by Season (000 MT)",
    height: int = 430,
) -> go.Figure:
    """Histogram with box marginal showing distribution of production_000_mt."""
    fig = px.histogram(
        df,
        x=settings.TARGET_COLUMN,
        color="season",
        barmode="overlay",
        nbins=35,
        opacity=0.72,
        marginal="box",
        color_discrete_map=_SEASON_COLORS,
        labels={
            settings.TARGET_COLUMN: "Production (000 MT)",
            "season": "Season",
        },
    )
    _apply_clean_layout(
        fig,
        title=title,
        x_title="Production (000 MT)",
        y_title="Observation Count",
        height=height,
        show_legend=True,
    )
    fig.update_layout(hovermode="closest")
    return fig


def sown_vs_production_chart(
    df: pd.DataFrame,
    title: str = "Sown Extent vs Paddy Production",
    height: int = 440,
) -> go.Figure:
    """Scatter plot of sown extent (ha) against production (000 MT)."""
    plot_df = df.dropna(subset=["sown_extent_ha", settings.TARGET_COLUMN])
    fig = px.scatter(
        plot_df,
        x="sown_extent_ha",
        y=settings.TARGET_COLUMN,
        color="season",
        color_discrete_map=_SEASON_COLORS,
        hover_data=["district", "year", "season"],
        opacity=0.75,
        labels={
            "sown_extent_ha": "Sown Extent (ha)",
            settings.TARGET_COLUMN: "Production (000 MT)",
            "season": "Season",
        },
    )
    fig.update_traces(marker=dict(size=7))
    _apply_clean_layout(
        fig,
        title=title,
        x_title="Sown Extent (Hectares, ha)",
        y_title="Production (000 MT)",
        height=height,
        show_legend=True,
    )
    fig.update_layout(hovermode="closest")
    return fig


def average_yield_analysis_chart(
    df: pd.DataFrame,
    title: str = "Average Paddy Yield Trend (kg/ha)",
    height: int = 420,
) -> go.Figure:
    """Yearly mean yield (kg/ha) by cultivation season."""
    plot_df = df.dropna(subset=["average_yield_kg_ha"])
    agg = (
        plot_df.groupby(["year", "season"], as_index=False)["average_yield_kg_ha"]
        .mean()
        .sort_values("year")
    )
    fig = px.line(
        agg,
        x="year",
        y="average_yield_kg_ha",
        color="season",
        color_discrete_map=_SEASON_COLORS,
        markers=True,
        labels={
            "year": "Year",
            "average_yield_kg_ha": "Average Yield (kg/ha)",
            "season": "Season",
        },
    )
    fig.update_traces(line=dict(width=2.5), marker=dict(size=5))
    return _apply_clean_layout(
        fig,
        title=title,
        x_title="Year",
        y_title="Average Yield (kg/ha)",
        height=height,
        show_legend=True,
    )


def metric_comparison_chart(
    eval_df: pd.DataFrame,
    metric: str,
    title: str,
    y_title: str,
    higher_is_better: bool = False,
    height: int = 360,
) -> go.Figure:
    """Bar chart comparing Bagging, Boosting, and Stacking for one evaluation metric."""
    ordered = eval_df.sort_values(metric, ascending=not higher_is_better).copy()
    best_val = ordered[metric].max() if higher_is_better else ordered[metric].min()
    colors = [
        settings.COLORS["primary"] if val == best_val else "#86EFAC"
        for val in ordered[metric]
    ]
    fig = go.Figure(
        data=[
            go.Bar(
                x=ordered["Model"],
                y=ordered[metric],
                marker_color=colors,
                text=[f"{v:.4f}" for v in ordered[metric]],
                textposition="outside",
                width=0.5,
            )
        ]
    )
    _apply_clean_layout(
        fig,
        title=title,
        x_title="Ensemble Model",
        y_title=y_title,
        height=height,
        show_legend=False,
    )
    fig.update_layout(hovermode="closest")
    top_pad = 1.18 if not higher_is_better else 1.15
    fig.update_yaxes(range=[0, float(ordered[metric].max()) * top_pad])
    return fig

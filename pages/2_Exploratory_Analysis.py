"""Exploratory Analysis page: six interactive Plotly agricultural visualizations."""
import streamlit as st

from src.data.data_loader import filter_dataset, get_dataset_overview
from src.ui import layout, resources
from src.visualization import charts

layout.setup_page("Exploratory Analysis", icon="📈")
layout.render_sidebar(active_page="pages/2_Exploratory_Analysis.py")

layout.render_page_header(
    "Exploratory Data Analysis",
    "Examine long-term trends, seasonal differences, regional output, sown extent relationships, and yield evolution.",
    badge="AGRICULTURAL INSIGHTS",
)

df, _, _, _, errors = resources.load_all_resources()
if errors:
    resources.render_resource_errors([e for e in errors if "Dataset" in e[0]])

if df is None:
    st.stop()

overview = get_dataset_overview(df)

# ---- Filters -----------------------------------------------------------------
f1, f2, f3 = st.columns([1.4, 1, 1.3])
with f1:
    sel_districts = st.multiselect(
        "Filter Districts",
        options=overview["districts"],
        default=[],
        placeholder="All 25 districts",
    )
with f2:
    sel_seasons = st.multiselect(
        "Filter Seasons",
        options=overview["seasons"],
        default=overview["seasons"],
    )
with f3:
    year_range = st.slider(
        "Year Range",
        min_value=overview["min_year"],
        max_value=overview["max_year"],
        value=(overview["min_year"], overview["max_year"]),
    )

filtered = filter_dataset(
    df,
    districts=sel_districts or None,
    seasons=sel_seasons or None,
    year_range=year_range,
)

if filtered.empty:
    st.warning("No observations match the selected filters. Widen your filter criteria.")
    layout.render_footer()
    st.stop()

# ---- Quick filtered stats ----------------------------------------------------
k1, k2, k3, k4 = st.columns(4)
with k1:
    layout.render_kpi_card(
        "Filtered Records",
        f"{len(filtered):,}",
        f"{filtered['district'].nunique()} district(s) selected",
        icon="📄",
    )
with k2:
    layout.render_kpi_card(
        "Total Production",
        f"{filtered['production_000_mt'].sum():,.0f}k MT",
        "Cumulative 000 Metric Tons",
        icon="🌾",
    )
with k3:
    layout.render_kpi_card(
        "Mean Sown Extent",
        f"{filtered['sown_extent_ha'].mean():,.0f} ha",
        "Average sown area per record",
        icon="🌱",
    )
with k4:
    layout.render_kpi_card(
        "Mean Yield",
        f"{filtered['average_yield_kg_ha'].mean():,.0f} kg/ha",
        "Average paddy yield per hectare",
        icon="⚖️",
    )

# ---- 1 & 2: Historical Trend + Maha vs Yala Comparison -----------------------
layout.render_section_heading("1. Historical Trend & 2. Maha vs Yala Comparison")
c1, c2 = st.columns([1.35, 1])
with c1:
    st.plotly_chart(
        charts.historical_production_trend_chart(
            filtered,
            split_by_season=(filtered["season"].nunique() > 1),
            title="1. Historical Paddy Production Trend (000 MT)",
            height=410,
        ),
        width="stretch",
    )
with c2:
    st.plotly_chart(
        charts.seasonal_comparison_chart(
            filtered,
            title="2. Maha vs Yala Production Comparison (000 MT)",
            height=410,
        ),
        width="stretch",
    )

# ---- 3 & 4: District-wise Production + Distribution --------------------------
layout.render_section_heading("3. Regional Output & 4. Production Distribution")
c3, c4 = st.columns([1.15, 1])
with c3:
    st.plotly_chart(
        charts.district_production_chart(
            filtered,
            title="3. District-wise Total Paddy Production (000 MT)",
            height=560,
        ),
        width="stretch",
    )
with c4:
    st.plotly_chart(
        charts.production_distribution_chart(
            filtered,
            title="4. Production Distribution (000 MT)",
            height=560,
        ),
        width="stretch",
    )

# ---- 5 & 6: Sown Extent vs Production + Average Yield Analysis ---------------
layout.render_section_heading("5. Cultivation Area Impact & 6. Average Yield Evolution")
c5, c6 = st.columns(2)
with c5:
    st.plotly_chart(
        charts.sown_vs_production_chart(
            filtered,
            title="5. Sown Extent (ha) vs Paddy Production (000 MT)",
            height=430,
        ),
        width="stretch",
    )
with c6:
    st.plotly_chart(
        charts.average_yield_analysis_chart(
            filtered,
            title="6. Average Paddy Yield Analysis (kg/ha)",
            height=430,
        ),
        width="stretch",
    )

layout.render_footer()

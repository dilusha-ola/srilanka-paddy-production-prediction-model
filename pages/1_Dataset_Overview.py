"""Dataset Overview page: metrics, filters, missing values, preview, and schema."""
import pandas as pd
import plotly.express as px
import streamlit as st

from config import settings
from src.data.data_loader import filter_dataset, get_dataset_overview
from src.ui import layout, resources

layout.setup_page("Dataset Overview", icon="📊")
layout.render_sidebar(active_page="pages/1_Dataset_Overview.py")

layout.render_page_header(
    "Dataset Overview",
    "Inspect the historical Sri Lankan paddy production records, coverage, missing values, and column definitions.",
    badge="DATA EXPLORATION",
)

df, _, _, _, errors = resources.load_all_resources()
if errors:
    resources.render_resource_errors([e for e in errors if "Dataset" in e[0]])

if df is None:
    st.stop()

overview = get_dataset_overview(df)

# ---- Summary KPI Cards -------------------------------------------------------
c1, c2, c3, c4 = st.columns(4)
with c1:
    layout.render_kpi_card(
        "Dataset Dimensions",
        f"{overview['records']:,} × {overview['columns']}",
        "Rows × original columns (preserved)",
        icon="📐",
    )
with c2:
    layout.render_kpi_card(
        "District Count",
        str(overview["district_count"]),
        "Sri Lankan agricultural districts",
        icon="🗺️",
    )
with c3:
    layout.render_kpi_card(
        "Year Coverage",
        overview["year_range_label"],
        "Historical cultivation span",
        icon="📅",
    )
with c4:
    layout.render_kpi_card(
        "Missing Values",
        str(overview["total_missing"]),
        "Total NaN cells (not silently dropped)",
        icon="🔍",
    )

# ---- Interactive Filters -----------------------------------------------------
layout.render_section_heading(
    "Filter Historical Records",
    "Slice the table below without altering the underlying CSV dataset.",
)

f1, f2, f3 = st.columns([1.4, 1, 1.3])
with f1:
    sel_districts = st.multiselect(
        "District",
        options=overview["districts"],
        default=[],
        placeholder="All 25 districts",
    )
with f2:
    sel_seasons = st.multiselect(
        "Season",
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

st.caption(
    f"Showing **{len(filtered):,}** of **{len(df):,}** total records "
    f"across **{filtered['district'].nunique()}** district(s)."
)

# ---- Season Distribution & Missing Value Summary -----------------------------
layout.render_section_heading("Distribution & Data Quality Summary")
q1, q2 = st.columns(2)

with q1:
    season_counts = (
        filtered["season"]
        .value_counts(dropna=False)
        .rename_axis("Season")
        .reset_index(name="Records")
    )
    fig_season = px.bar(
        season_counts,
        x="Season",
        y="Records",
        color="Season",
        color_discrete_map={"Maha": settings.COLORS["maha"], "Yala": settings.COLORS["yala"]},
        text="Records",
        title="Season Distribution (Filtered Records)",
    )
    fig_season.update_traces(textposition="outside", width=0.45)
    fig_season.update_layout(
        height=340,
        paper_bgcolor="#FFFFFF",
        plot_bgcolor="#FFFFFF",
        showlegend=False,
        margin=dict(l=16, r=16, t=50, b=16),
    )
    if not season_counts.empty:
        fig_season.update_yaxes(range=[0, float(season_counts["Records"].max()) * 1.18])
    st.plotly_chart(fig_season, width="stretch")

with q2:
    st.markdown("**Missing Values by Column (Full Original Dataset)**")
    missing_rows = [
        {
            "Column": col,
            "Data Type": str(df[col].dtype),
            "Missing Count": count,
            "Missing %": round(100.0 * count / len(df), 2),
        }
        for col, count in overview["missing_by_column"].items()
    ]
    st.dataframe(pd.DataFrame(missing_rows), width="stretch", hide_index=True)

# ---- Data Preview Table ------------------------------------------------------
layout.render_section_heading(
    "Data Preview",
    "All seven original columns are preserved exactly as stored in data/sri_lanka_paddy_ml_training.csv.",
)
row_limit = st.selectbox("Rows to preview", options=[25, 50, 100, 250, 500], index=1)
st.dataframe(filtered.head(row_limit), width="stretch", hide_index=True)

# ---- Column Descriptions & Units ---------------------------------------------
layout.render_section_heading("Column Descriptions & Units")
schema_rows = []
for col in settings.DATASET_COLUMNS:
    label, desc, unit = settings.COLUMN_METADATA[col]
    if col == settings.TARGET_COLUMN:
        role = "Target"
    elif col in settings.LEAKAGE_COLUMNS:
        role = "Excluded (Leakage)"
    else:
        role = "ML Input Feature"
    schema_rows.append(
        {
            "Column Name": col,
            "Label": label,
            "Unit": unit,
            "Model Role": role,
            "Description": desc,
        }
    )
st.dataframe(pd.DataFrame(schema_rows), width="stretch", hide_index=True)

layout.render_footer()

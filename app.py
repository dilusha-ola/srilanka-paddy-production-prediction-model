"""Main Streamlit entry point (Home / Dashboard).

Presentation layer only: delegates loading and business logic to src/.
"""
import streamlit as st

from config import settings
from src.data.data_loader import filter_dataset, get_dataset_overview
from src.models.model_loader import get_available_models
from src.services.evaluation_service import get_evaluation_summary
from src.ui import layout, resources
from src.visualization import charts

layout.setup_page()
layout.render_sidebar(active_page="app.py")

df, models, features, eval_df, errors = resources.load_all_resources()
if errors:
    resources.render_resource_errors(errors)

# ---- Section A: Hero Banner --------------------------------------------------
layout.render_hero()

# ---- Section B: KPI Summary Cards --------------------------------------------
layout.render_section_heading(
    "National Dataset & Model Overview",
    "Live summary computed directly from the Sri Lankan paddy dataset and saved models.",
)

overview = get_dataset_overview(df) if df is not None else None
avail_models = get_available_models(models) if models is not None else []

k1, k2, k3, k4 = st.columns(4)
with k1:
    layout.render_kpi_card(
        "Total Records",
        f"{overview['records']:,}" if overview else "—",
        "Historical district-season observations",
        icon="📄",
    )
with k2:
    layout.render_kpi_card(
        "Districts",
        str(overview["district_count"]) if overview else "—",
        "Sri Lankan districts",
        icon="🗺️",
    )
with k3:
    layout.render_kpi_card(
        "Historical Coverage",
        overview["year_range_label"] if overview else "—",
        "Available historical records",
        icon="📅",
    )
with k4:
    layout.render_kpi_card(
        "Ensemble Models",
        str(len(avail_models)) if models is not None else "—",
        "Bagging, Boosting and Stacking",
        icon="🤖",
    )

# ---- Section C: Historical Paddy Production Insights -------------------------
layout.render_section_heading(
    "Historical Paddy Production Insights",
    "Interactive production trends (in thousand metric tons) filtered by cultivation season and district.",
)

if df is not None and overview is not None:
    f_col1, f_col2 = st.columns([1, 2])
    with f_col1:
        season_choice = st.selectbox(
            "Filter by Season",
            options=["All Seasons"] + overview["seasons"],
            index=0,
            key="home_season_filter",
        )
    with f_col2:
        selected_districts = st.multiselect(
            "Filter by District (leave empty for all districts)",
            options=overview["districts"],
            default=[],
            key="home_district_filter",
        )

    filtered_df = filter_dataset(
        df,
        districts=selected_districts or None,
        seasons=None if season_choice == "All Seasons" else [season_choice],
    )
    if filtered_df.empty:
        st.warning("No records match the selected Season and District filters.")
    else:
        fig_trend = charts.historical_production_trend_chart(
            filtered_df,
            split_by_season=(season_choice == "All Seasons"),
            title="Historical Paddy Production Trend (000 MT)",
            height=410,
        )
        st.plotly_chart(fig_trend, width="stretch")
else:
    st.info("Historical insights are unavailable because the dataset could not be loaded.")

# ---- Section D: Seasonal Analysis --------------------------------------------
layout.render_section_heading(
    "Seasonal Analysis: Maha vs Yala",
    "Comparison of production volume and yield across Sri Lanka's two main cultivation seasons.",
)

if df is not None:
    season_stats = (
        df.groupby("season", as_index=False)
        .agg(
            observations=(settings.TARGET_COLUMN, "count"),
            total_prod=(settings.TARGET_COLUMN, "sum"),
            mean_prod=(settings.TARGET_COLUMN, "mean"),
            mean_yield=("average_yield_kg_ha", "mean"),
        )
        .set_index("season")
    )

    s_col1, s_col2 = st.columns([1, 1.35], gap="large")
    with s_col1:
        for season_name, icon, note in [
            ("Maha", "🌧️", "Major cultivation season (Northeast monsoon)"),
            ("Yala", "☀️", "Minor cultivation season (Southwest monsoon)"),
        ]:
            if season_name in season_stats.index:
                row = season_stats.loc[season_name]
                layout.render_kpi_card(
                    f"{season_name} Season Total",
                    f"{row['total_prod']:,.1f}k MT",
                    (
                        f"{int(row['observations']):,} records · "
                        f"Avg {row['mean_prod']:,.1f}k MT/record · "
                        f"Avg yield {row['mean_yield']:,.0f} kg/ha — {note}"
                    ),
                    icon=icon,
                    extra_class="seasonal-card",
                )
    with s_col2:
        st.plotly_chart(
            charts.seasonal_average_chart(
                df,
                title="Average Production by Season (000 MT)",
                height=372,
            ),
            width="stretch",
        )

# ---- Section E: Model Performance Summary ------------------------------------
layout.render_section_heading(
    "Model Performance Summary",
    "Historical evaluation scores loaded from the saved evaluation table (not retrained).",
)

if eval_df is not None:
    eval_summary = get_evaluation_summary(eval_df)
    by_model = eval_summary["by_model"]
    best_rmse_model = eval_summary["best_rmse_model"]
    best_mae_model = eval_summary["best_mae_model"]

    m_cols = st.columns(len(settings.MODEL_NAMES))
    for col, model_name in zip(m_cols, settings.MODEL_NAMES):
        with col:
            if model_name in by_model:
                metrics = by_model[model_name]
                full_name = settings.MODEL_DESCRIPTIONS[model_name]["full_name"]
                layout.render_model_card(
                    name=model_name,
                    full_name=full_name,
                    mae=metrics["mae"],
                    rmse=metrics["rmse"],
                    r2=metrics["r2"],
                    is_best_rmse=(model_name == best_rmse_model),
                    is_best_mae=(model_name == best_mae_model),
                )

    st.info(
        f"**Evaluation insight:** **{best_rmse_model}** achieves the strongest overall fit by "
        f"**RMSE** ({eval_summary['best_rmse_value']:.4f}) and **R²** ({eval_summary['best_r2_value']:.4f}), "
        f"making it the preferred primary model. However, **{best_mae_model}** attains the lowest "
        f"**MAE** ({eval_summary['best_mae_value']:.4f}), meaning no single model dominates every metric."
    )

# ---- Section F: Quick Navigation Cards ---------------------------------------
layout.render_section_heading(
    "Explore Dashboard Modules",
    "Jump directly to detailed dataset inspection, exploratory charts, model benchmarks, or live predictions.",
)

nav_cards = [
    ("Dataset Overview", "Explore historical agricultural records.", "📊", "pages/1_Dataset_Overview.py"),
    ("Exploratory Analysis", "Discover production trends and seasonal patterns.", "📈", "pages/2_Exploratory_Analysis.py"),
    ("Model Comparison", "Compare the three ensemble learning algorithms.", "⚖️", "pages/3_Model_Comparison.py"),
    ("Production Prediction", "Estimate paddy production using trained models.", "🌾", "pages/4_Production_Prediction.py"),
]
n_cols = st.columns(4)
for col, (title, desc, icon, page_path) in zip(n_cols, nav_cards):
    with col:
        layout.render_nav_card(title, desc, icon, page_path)

layout.render_footer()

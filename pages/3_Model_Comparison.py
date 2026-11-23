"""Model Comparison page: evaluation table, separate metric charts, interpretation."""
import streamlit as st

from config import settings
from src.models.model_loader import get_model_metadata
from src.services.evaluation_service import get_evaluation_summary
from src.ui import layout, resources
from src.visualization import charts

layout.setup_page("Model Comparison", icon="⚖️")
layout.render_sidebar(active_page="pages/3_Model_Comparison.py")

layout.render_page_header(
    "Ensemble Model Comparison",
    "Compare saved evaluation metrics (MAE, RMSE, R²) across Bagging, Gradient Boosting, and Stacking regressors.",
    badge="MODEL BENCHMARK",
)

_, models, _, eval_df, errors = resources.load_all_resources()
if errors:
    resources.render_resource_errors([e for e in errors if "Dataset" not in e[0]])

if eval_df is None:
    st.stop()

summary = get_evaluation_summary(eval_df)
by_model = summary["by_model"]
best_rmse = summary["best_rmse_model"]
best_mae = summary["best_mae_model"]
best_r2 = summary["best_r2_model"]

# ---- Best Model Summary Banner -----------------------------------------------
layout.render_section_heading(
    "Best Model Summary",
    "Evaluation results loaded directly from models/model_evaluation_results.csv without retraining.",
)

s1, s2, s3 = st.columns(3)
with s1:
    layout.render_kpi_card(
        "Best by RMSE (Primary)",
        best_rmse,
        f"Lowest RMSE: {summary['best_rmse_value']:.4f} (000 MT)",
        icon="🏆",
    )
with s2:
    layout.render_kpi_card(
        "Best by R² Score",
        best_r2,
        f"Highest R²: {summary['best_r2_value']:.4f}",
        icon="🎯",
    )
with s3:
    layout.render_kpi_card(
        "Lowest MAE",
        best_mae,
        f"Lowest MAE: {summary['best_mae_value']:.4f} (000 MT)",
        icon="📉",
    )

st.info(
    f"**Metric ranking summary:** **{best_rmse}** is the best overall model based on **RMSE** "
    f"({summary['best_rmse_value']:.4f}) and **R²** ({summary['best_r2_value']:.4f}), indicating fewer "
    f"large prediction errors and the highest explained variance. Meanwhile, **{best_mae}** achieves "
    f"the lowest **MAE** ({summary['best_mae_value']:.4f}), reflecting slightly smaller average absolute "
    "residuals. Different metrics highlight different error profiles—no single model leads on every metric."
)

# ---- Model Performance Table -------------------------------------------------
layout.render_section_heading("Model Performance Table")
display_df = eval_df.copy()
display_df = display_df.sort_values("RMSE", ascending=True).reset_index(drop=True)
st.dataframe(
    display_df.style.format({"MAE": "{:.4f}", "RMSE": "{:.4f}", "R2 Score": "{:.4f}"}),
    width="stretch",
    hide_index=True,
)

# ---- Separate Comparison Charts (MAE, RMSE, R2) ------------------------------
layout.render_section_heading(
    "Separate Metric Comparisons",
    "Dark green highlights the top-performing model for each individual metric.",
)

c1, c2, c3 = st.columns(3)
with c1:
    st.plotly_chart(
        charts.metric_comparison_chart(
            eval_df,
            metric="MAE",
            title="MAE Comparison (Lower is Better)",
            y_title="MAE (000 MT)",
            higher_is_better=False,
            height=370,
        ),
        width="stretch",
    )
with c2:
    st.plotly_chart(
        charts.metric_comparison_chart(
            eval_df,
            metric="RMSE",
            title="RMSE Comparison (Lower is Better)",
            y_title="RMSE (000 MT)",
            higher_is_better=False,
            height=370,
        ),
        width="stretch",
    )
with c3:
    st.plotly_chart(
        charts.metric_comparison_chart(
            eval_df,
            metric="R2 Score",
            title="R² Score Comparison (Higher is Better)",
            y_title="R² Score",
            higher_is_better=True,
            height=370,
        ),
        width="stretch",
    )

# ---- Model Performance Interpretation ----------------------------------------
layout.render_section_heading(
    "Model Performance Interpretation",
    "How each ensemble architecture operates and how its metrics translate to paddy forecasting.",
)

meta_by_name = (
    {item["name"]: item for item in get_model_metadata(models)} if models else {}
)
interp_cols = st.columns(3)
for col, name in zip(interp_cols, settings.MODEL_NAMES):
    info = settings.MODEL_DESCRIPTIONS[name]
    metrics = by_model.get(name, {})
    estimator_name = meta_by_name.get(name, {}).get("estimator_type", "Trained Estimator")
    with col:
        layout.render_model_card(
            name=name,
            full_name=f"{info['full_name']} ({estimator_name})",
            mae=metrics.get("mae", 0.0),
            rmse=metrics.get("rmse", 0.0),
            r2=metrics.get("r2", 0.0),
            is_best_rmse=(name == best_rmse),
            is_best_mae=(name == best_mae),
        )
        st.caption(info["summary"])

layout.render_footer()

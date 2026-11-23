"""Production Prediction page: interactive inference with pre-trained models."""
import pandas as pd
import streamlit as st

from config import settings
from src.data.data_loader import get_dataset_overview
from src.services.prediction_service import (
    PredictionError,
    predict_all_models,
    predict_production,
)
from src.ui import layout, resources

layout.setup_page("Production Prediction", icon="🌾")
layout.render_sidebar(active_page="pages/4_Production_Prediction.py")

layout.render_page_header(
    "Paddy Production Prediction",
    "Estimate Sri Lankan paddy production (000 MT) using the pre-trained Bagging, Boosting, and Stacking models.",
    badge="ENSEMBLE INFERENCE",
)

df, models, features, _, errors = resources.load_all_resources()
if errors:
    resources.render_resource_errors(
        [e for e in errors if "Dataset" in e[0] or "models" in e[0]]
    )

if df is None or models is None:
    st.stop()

overview = get_dataset_overview(df)
districts = overview["districts"]
seasons = overview["seasons"]

# Compute sensible median sown extent for default form value
default_sown = float(df["sown_extent_ha"].median())

layout.render_section_heading(
    "Scenario Inputs",
    (
        "Model inputs are strictly limited to: "
        + ", ".join(settings.PREDICTION_FEATURES)
        + ". Leakage variables (harvested extent and average yield) are never used."
    ),
)

col_form, col_result = st.columns([1, 1.15], gap="large")

with col_form:
    with st.form("prediction_form"):
        selected_district = st.selectbox(
            "District",
            options=districts,
            index=districts.index("ANURADHAPURA") if "ANURADHAPURA" in districts else 0,
        )
        selected_season = st.selectbox(
            "Season",
            options=seasons,
            index=0,
        )
        selected_year = st.number_input(
            "Year",
            min_value=1978,
            max_value=2050,
            value=2025,
            step=1,
            help=(
                f"Training period: {settings.TRAIN_START_YEAR}–{settings.TRAIN_END_YEAR}. "
                f"Historical testing period: {settings.TEST_START_YEAR}–{settings.TEST_END_YEAR}."
            ),
        )
        sown_extent_ha = st.number_input(
            "Sown Extent (Hectares, ha)",
            min_value=1.0,
            max_value=500000.0,
            value=round(default_sown, 1),
            step=500.0,
            format="%.1f",
        )
        selected_model = st.selectbox(
            "Ensemble Model",
            options=settings.MODEL_NAMES,
            index=settings.MODEL_NAMES.index(settings.MODEL_STACKING),
            help="Stacking is the top-ranked model by RMSE; Bagging has the lowest MAE.",
        )

        submitted = st.form_submit_button(
            "Predict Production",
            type="primary",
            width="stretch",
        )

with col_result:
    if submitted:
        try:
            result = predict_production(
                models=models,
                model_name=selected_model,
                district=selected_district,
                year=int(selected_year),
                season=selected_season,
                sown_extent_ha=float(sown_extent_ha),
                features=features,
            )
            all_preds = predict_all_models(
                models=models,
                district=selected_district,
                year=int(selected_year),
                season=selected_season,
                sown_extent_ha=float(sown_extent_ha),
                features=features,
            )

            layout.render_html(
                f"""
                <div class="pred-result-card">
                    <div class="pred-result-label">Predicted Paddy Production</div>
                    <div class="pred-result-value">{result['predicted_production_000_mt']:,.2f} <span style="font-size:1.2rem;font-weight:600;">000 MT</span></div>
                    <div class="pred-meta-grid">
                        <div class="pred-meta-item">
                            <span>District</span>
                            <strong>{result['district']}</strong>
                        </div>
                        <div class="pred-meta-item">
                            <span>Season</span>
                            <strong>{result['season']}</strong>
                        </div>
                        <div class="pred-meta-item">
                            <span>Year</span>
                            <strong>{result['year']}</strong>
                        </div>
                        <div class="pred-meta-item">
                            <span>Selected Model</span>
                            <strong>{result['model']}</strong>
                        </div>
                        <div class="pred-meta-item">
                            <span>Input Sown Extent</span>
                            <strong>{result['sown_extent_ha']:,.1f} ha</strong>
                        </div>
                    </div>
                </div>
                """
            )

            st.markdown("**Cross-Model Estimate Comparison (Same Inputs)**")
            comp_rows = [
                {
                    "Model": name,
                    "Algorithm": settings.MODEL_DESCRIPTIONS[name]["full_name"],
                    "Predicted Production (000 MT)": round(val, 2),
                }
                for name, val in all_preds.items()
            ]
            st.dataframe(pd.DataFrame(comp_rows), width="stretch", hide_index=True)

            if result["horizon"]["is_beyond_history"]:
                st.warning(f"**Note:** {result['horizon']['message']}")

        except PredictionError as exc:
            st.error(f"Prediction could not be completed: {exc}")
    else:
        layout.render_html(
            """
            <div class="pred-result-card" style="border-style: dashed; border-color: #94A3B8; background: #FFFFFF;">
                <div class="pred-result-label" style="color: #64748B;">Ready for Inference</div>
                <div class="pred-result-value" style="font-size: 1.65rem; color: #1F2937;">
                    Enter cultivation details and click <em>Predict Production</em>
                </div>
                <p style="color: #64748B; margin: 0;">
                    The selected trained ensemble pipeline will estimate paddy output in thousand metric tons (000 MT)
                    using district, year, season, and sown extent.
                </p>
            </div>
            """
        )

    st.info(
        "**Disclaimer:** Predictions are machine learning estimates based on historical agricultural data "
        "(training period 1978–2015, historical testing period 2016–2025) and should not be treated as "
        "official agricultural forecasts."
    )

layout.render_footer()

"""Main Streamlit entry point (home page / application shell).

Other pages live in pages/ and are discovered by Streamlit automatically.
Data and model loading is delegated to src.data / src.models.
"""
import streamlit as st

from config import settings
from src.data.data_loader import DataLoadError, get_summary, load_dataset
from src.models.model_loader import (
    ModelLoadError,
    get_available_models,
    load_features,
    load_models,
)
from src.ui import layout

layout.setup_page()
layout.render_sidebar()


@st.cache_data(show_spinner=False)
def _cached_dataset():
    return load_dataset()


@st.cache_resource(show_spinner=False)
def _cached_models():
    return load_models(), load_features()


layout.render_header(
    settings.APP_TITLE,
    "Ensemble learning analytics for national paddy production.",
)

# ---- Load resources, showing friendly errors on failure ----------------------
df, models, features = None, None, None
errors = []

try:
    df = _cached_dataset()
except DataLoadError as exc:
    errors.append(("Dataset could not be loaded", str(exc)))

try:
    models, features = _cached_models()
except ModelLoadError as exc:
    errors.append(("Trained models could not be loaded", str(exc)))

for title, detail in errors:
    st.error(f"**{title}.** Check that the files exist in the `data/` and "
             f"`models/` folders and that library versions are compatible.")
    with st.expander("Technical details"):
        st.code(detail)

# ---- Status overview -----------------------------------------------------------
st.subheader("System status")
c1, c2, c3, c4 = st.columns(4)
if df is not None:
    summary = get_summary(df)
    c1.metric("Records", f"{summary['records']:,}")
    c2.metric("Columns", summary["columns"])
    c3.metric("Missing values", summary["total_missing"])
else:
    c1.metric("Records", "–")
    c2.metric("Columns", "–")
    c3.metric("Missing values", "–")
c4.metric(
    "Models available",
    f"{len(get_available_models(models))}/{len(settings.MODEL_NAMES)}" if models else "–",
)

# ---- Navigation guide ----------------------------------------------------------
st.subheader("Explore")
cols = st.columns(4)
cards = [
    ("Dataset Overview", "Browse the records, columns and data quality."),
    ("Exploratory Analysis", "Trends by district, season and year."),
    ("Model Comparison", "Compare Bagging, Boosting and Stacking."),
    ("Production Prediction", "Estimate production for chosen inputs."),
]
for col, (title, body) in zip(cols, cards):
    with col:
        layout.render_card(title, body)
st.caption("Use the sidebar to open each page. Pages are being built incrementally.")

layout.render_footer()

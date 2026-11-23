"""Cached Streamlit loaders delegating to src.data, src.models, and src.services."""
from typing import Dict, List, Optional, Tuple

import pandas as pd
import streamlit as st

from src.data.data_loader import DataLoadError, load_dataset
from src.models.model_loader import ModelLoadError, load_features, load_models
from src.services.evaluation_service import (
    EvaluationLoadError,
    load_evaluation_results,
)


@st.cache_data(show_spinner=False)
def get_dataset() -> pd.DataFrame:
    return load_dataset()


@st.cache_resource(show_spinner=False)
def get_models_and_features() -> Tuple[Dict[str, object], List[str]]:
    return load_models(), load_features()


@st.cache_data(show_spinner=False)
def get_evaluation_results() -> pd.DataFrame:
    return load_evaluation_results()


def load_all_resources() -> Tuple[
    Optional[pd.DataFrame],
    Optional[Dict[str, object]],
    Optional[List[str]],
    Optional[pd.DataFrame],
    List[Tuple[str, str]],
]:
    """Load dataset, models, features, and evaluation CSV with friendly error tuples."""
    df, models, features, eval_df = None, None, None, None
    errors: List[Tuple[str, str]] = []

    try:
        df = get_dataset()
    except DataLoadError as exc:
        errors.append(("Dataset could not be loaded", str(exc)))

    try:
        models, features = get_models_and_features()
    except ModelLoadError as exc:
        errors.append(("Trained models could not be loaded", str(exc)))

    try:
        eval_df = get_evaluation_results()
    except EvaluationLoadError as exc:
        errors.append(("Model evaluation results could not be loaded", str(exc)))

    return df, models, features, eval_df, errors


def render_resource_errors(errors: List[Tuple[str, str]]) -> None:
    """Display user-friendly error banners while exposing technical details."""
    for title, detail in errors:
        st.error(
            f"**{title}.** Verify that required files are present in `data/` and "
            "`models/` and that the `.venv` Python 3.12 environment (`scikit-learn==1.6.1`) is active."
        )
        with st.expander("Technical details"):
            st.code(detail)

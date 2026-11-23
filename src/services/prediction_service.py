"""Prediction business logic for trained ensemble models. No UI code."""
from typing import Dict, List, Optional

import pandas as pd

from config import settings


class PredictionError(Exception):
    """Raised when prediction inputs or model inference fail."""


def build_input_dataframe(
    district: str,
    year: int,
    season: str,
    sown_extent_ha: float,
    features: Optional[List[str]] = None,
) -> pd.DataFrame:
    """Validate inputs and construct a single-row DataFrame using only allowed features.

    Explicitly excludes leakage columns (harvested_extent_ha, average_yield_kg_ha).
    """
    if not district or not str(district).strip():
        raise PredictionError("District must be provided.")
    if not season or not str(season).strip():
        raise PredictionError("Season must be provided.")
    if year is None or int(year) < 1900 or int(year) > 2100:
        raise PredictionError("Year must be between 1900 and 2100.")
    if sown_extent_ha is None or float(sown_extent_ha) <= 0:
        raise PredictionError("Sown extent must be greater than 0 hectares.")

    expected = list(features) if features is not None else list(settings.PREDICTION_FEATURES)
    forbidden = [c for c in expected if c in settings.LEAKAGE_COLUMNS]
    if forbidden:
        raise PredictionError(
            f"Leakage columns are not permitted as prediction inputs: {forbidden}"
        )
    if set(expected) != set(settings.PREDICTION_FEATURES):
        raise PredictionError(
            f"Model features mismatch. Expected {settings.PREDICTION_FEATURES}, got {expected}."
        )

    row = {
        "district": str(district).strip(),
        "year": int(year),
        "season": str(season).strip(),
        "sown_extent_ha": float(sown_extent_ha),
    }
    return pd.DataFrame([row], columns=expected)


def classify_year_horizon(year: int) -> Dict[str, object]:
    """Describe whether a year falls inside training, historical testing, or extrapolation."""
    y = int(year)
    if settings.TRAIN_START_YEAR <= y <= settings.TRAIN_END_YEAR:
        return {
            "period": "training",
            "is_beyond_history": False,
            "message": (
                f"Year {y} falls within the model training period "
                f"({settings.TRAIN_START_YEAR}\u2013{settings.TRAIN_END_YEAR})."
            ),
        }
    if settings.TEST_START_YEAR <= y <= settings.TEST_END_YEAR:
        return {
            "period": "testing",
            "is_beyond_history": False,
            "message": (
                f"Year {y} falls within the historical testing period "
                f"({settings.TEST_START_YEAR}\u2013{settings.TEST_END_YEAR})."
            ),
        }
    return {
        "period": "out_of_range",
        "is_beyond_history": True,
        "message": (
            f"Year {y} is outside the available historical dataset period "
            f"({settings.TRAIN_START_YEAR}\u2013{settings.TEST_END_YEAR}: training "
            f"{settings.TRAIN_START_YEAR}\u2013{settings.TRAIN_END_YEAR}, testing "
            f"{settings.TEST_START_YEAR}\u2013{settings.TEST_END_YEAR}). "
            "Predictions beyond historical coverage carry higher uncertainty."
        ),
    }


def predict_production(
    models: Dict[str, object],
    model_name: str,
    district: str,
    year: int,
    season: str,
    sown_extent_ha: float,
    features: Optional[List[str]] = None,
) -> Dict[str, object]:
    """Run prediction for a single scenario with the chosen trained model."""
    if model_name not in models:
        raise PredictionError(
            f"Model '{model_name}' is not available. Choose from {list(models)}."
        )
    input_df = build_input_dataframe(
        district=district,
        year=year,
        season=season,
        sown_extent_ha=sown_extent_ha,
        features=features,
    )
    try:
        raw_pred = models[model_name].predict(input_df)
        predicted_value = float(raw_pred[0])
    except Exception as exc:
        raise PredictionError(
            f"Prediction failed for model '{model_name}': {exc}"
        ) from exc

    horizon = classify_year_horizon(int(year))
    return {
        "model": model_name,
        "predicted_production_000_mt": predicted_value,
        "district": str(district).strip(),
        "year": int(year),
        "season": str(season).strip(),
        "sown_extent_ha": float(sown_extent_ha),
        "horizon": horizon,
    }


def predict_all_models(
    models: Dict[str, object],
    district: str,
    year: int,
    season: str,
    sown_extent_ha: float,
    features: Optional[List[str]] = None,
) -> Dict[str, float]:
    """Compute predictions across all available models for side-by-side comparison."""
    input_df = build_input_dataframe(
        district=district,
        year=year,
        season=season,
        sown_extent_ha=sown_extent_ha,
        features=features,
    )
    results: Dict[str, float] = {}
    for name in settings.MODEL_NAMES:
        if name in models:
            results[name] = float(models[name].predict(input_df)[0])
    return results

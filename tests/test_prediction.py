"""Unit tests for model loading, validation, imputation, evaluation, and predictions."""
import math

import numpy as np
import pytest

from config import settings
from src.models.model_loader import ModelLoadError, get_available_models, load_features, load_models
from src.services.evaluation_service import get_evaluation_summary, load_evaluation_results
from src.services.prediction_service import (
    PredictionError,
    build_input_dataframe,
    classify_year_horizon,
    predict_all_models,
    predict_production,
)


def test_models_and_features_load():
    models = load_models()
    features = load_features()
    assert get_available_models(models) == settings.MODEL_NAMES
    for name in settings.MODEL_NAMES:
        assert name in models
        assert hasattr(models[name], "predict")
    assert features == ["district", "year", "season", "sown_extent_ha"]


def test_missing_model_file_raises():
    with pytest.raises(ModelLoadError):
        load_models("models/missing_file.joblib")


def test_prediction_inputs_use_exact_four_features():
    features = load_features()
    input_df = build_input_dataframe(
        district="AMPARA",
        year=2024,
        season="Maha",
        sown_extent_ha=45000.0,
        features=features,
    )
    assert list(input_df.columns) == ["district", "year", "season", "sown_extent_ha"]

    with pytest.raises(PredictionError):
        build_input_dataframe(
            district="AMPARA",
            year=2024,
            season="Maha",
            sown_extent_ha=45000.0,
            features=["district", "year", "season", "harvested_extent_ha"],
        )

    with pytest.raises(PredictionError):
        build_input_dataframe(
            district="AMPARA",
            year=2024,
            season="Maha",
            sown_extent_ha=45000.0,
            features=["district", "year", "season"],
        )


def test_invalid_prediction_inputs_raise():
    models = load_models()
    features = load_features()

    with pytest.raises(PredictionError):
        predict_production(models, "UnknownModel", "AMPARA", 2024, "Maha", 40000.0, features)

    with pytest.raises(PredictionError):
        predict_production(models, "Stacking", "", 2024, "Maha", 40000.0, features)

    with pytest.raises(PredictionError):
        predict_production(models, "Stacking", "AMPARA", 2024, "", 40000.0, features)

    with pytest.raises(PredictionError):
        predict_production(models, "Stacking", "AMPARA", 1800, "Maha", 40000.0, features)

    with pytest.raises(PredictionError):
        predict_production(models, "Stacking", "AMPARA", 2024, "Maha", 0.0, features)

    with pytest.raises(PredictionError):
        predict_production(models, "Stacking", "AMPARA", 2024, "Maha", -500.0, features)


def test_predict_production_valid_all_models():
    models = load_models()
    features = load_features()
    for model_name in settings.MODEL_NAMES:
        res = predict_production(
            models=models,
            model_name=model_name,
            district="ANURADHAPURA",
            year=2024,
            season="Maha",
            sown_extent_ha=65000.0,
            features=features,
        )
        assert res["model"] == model_name
        assert math.isfinite(res["predicted_production_000_mt"])
        assert res["predicted_production_000_mt"] > 0
        assert res["horizon"]["is_beyond_history"] is False

    all_res = predict_all_models(models, "ANURADHAPURA", 2024, "Maha", 65000.0, features)
    assert set(all_res.keys()) == set(settings.MODEL_NAMES)


def test_missing_sown_extent_handled_by_pipeline_imputer():
    models = load_models()
    features = load_features()
    for missing_val in (None, np.nan):
        input_df = build_input_dataframe(
            district="ANURADHAPURA",
            year=2024,
            season="Maha",
            sown_extent_ha=missing_val,
            features=features,
        )
        assert np.isnan(input_df["sown_extent_ha"].iloc[0])

        for model_name in settings.MODEL_NAMES:
            res = predict_production(
                models=models,
                model_name=model_name,
                district="ANURADHAPURA",
                year=2024,
                season="Maha",
                sown_extent_ha=missing_val,
                features=features,
            )
            assert math.isfinite(res["predicted_production_000_mt"])
            assert res["predicted_production_000_mt"] > 0
            assert res["sown_extent_ha"] is None


def test_classify_year_horizon_warns_beyond_2025():
    assert classify_year_horizon(2010)["period"] == "training"
    assert classify_year_horizon(2020)["period"] == "testing"
    future = classify_year_horizon(2028)
    assert future["period"] == "out_of_range"
    assert future["is_beyond_history"] is True


def test_evaluation_service_rankings():
    eval_df = load_evaluation_results()
    summary = get_evaluation_summary(eval_df)
    assert summary["best_rmse_model"] == "Stacking"
    assert summary["best_r2_model"] == "Stacking"
    assert summary["best_mae_model"] == "Bagging"

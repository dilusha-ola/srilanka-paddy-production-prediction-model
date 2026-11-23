"""Unit tests for model loading, evaluation results, and prediction service."""
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
    assert features == settings.PREDICTION_FEATURES


def test_missing_model_file_raises():
    with pytest.raises(ModelLoadError):
        load_models("models/missing_file.joblib")


def test_build_input_dataframe_rejects_leakage():
    with pytest.raises(PredictionError):
        build_input_dataframe(
            district="AMPARA",
            year=2024,
            season="Maha",
            sown_extent_ha=45000.0,
            features=["district", "year", "season", "harvested_extent_ha"],
        )


def test_predict_production_all_models():
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
        assert res["predicted_production_000_mt"] > 0
        assert res["horizon"]["is_beyond_history"] is False

    all_res = predict_all_models(models, "ANURADHAPURA", 2024, "Maha", 65000.0, features)
    assert set(all_res.keys()) == set(settings.MODEL_NAMES)


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

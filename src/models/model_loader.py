"""Loading of the pre-trained models and feature list. Contains no UI code."""
from pathlib import Path
from typing import Dict, List, Union

import joblib

from config import settings


class ModelLoadError(Exception):
    """Raised when model artifacts are missing, unreadable or invalid."""


def _load_joblib(path: Union[str, Path]):
    path = Path(path)
    if not path.is_file():
        raise ModelLoadError(f"Model file not found: {path}")
    try:
        return joblib.load(path)
    except Exception as exc:  # incompatible sklearn version, corrupt file, ...
        raise ModelLoadError(
            f"Could not load {path.name} (possibly incompatible library "
            f"version or corrupt file): {exc}"
        ) from exc


def validate_models(models) -> None:
    """Ensure the loaded object is a dict containing all required models."""
    if not isinstance(models, dict):
        raise ModelLoadError(
            f"Expected a dict of models, got {type(models).__name__}."
        )
    missing = [n for n in settings.MODEL_NAMES if n not in models]
    if missing:
        raise ModelLoadError(
            f"Missing models: {missing}. Available: {list(models)}"
        )
    for name in settings.MODEL_NAMES:
        if not hasattr(models[name], "predict"):
            raise ModelLoadError(f"Model '{name}' has no predict() method.")


def load_models(path: Union[str, Path, None] = None) -> Dict[str, object]:
    """Load and validate the Bagging, Boosting and Stacking models."""
    models = _load_joblib(path or settings.MODELS_PATH)
    validate_models(models)
    return models


def load_features(path: Union[str, Path, None] = None) -> List[str]:
    """Load the feature list the models were trained with."""
    features = _load_joblib(path or settings.FEATURES_PATH)
    if not isinstance(features, (list, tuple)) or not all(
        isinstance(f, str) for f in features
    ):
        raise ModelLoadError("Feature file must contain a list of column names.")
    return list(features)


def get_available_models(models: Dict[str, object]) -> List[str]:
    """Names of the required models that are present."""
    return [n for n in settings.MODEL_NAMES if n in models]


def get_model_metadata(models: Dict[str, object]) -> List[Dict[str, str]]:
    """Return display metadata for each loaded ensemble model."""
    rows = []
    for name in settings.MODEL_NAMES:
        if name not in models:
            continue
        desc = settings.MODEL_DESCRIPTIONS.get(name, {})
        rows.append(
            {
                "name": name,
                "full_name": desc.get("full_name", name),
                "estimator_type": type(models[name]).__name__,
                "summary": desc.get("summary", ""),
            }
        )
    return rows

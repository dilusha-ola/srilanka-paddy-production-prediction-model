"""Central project configuration: paths, column names and model names."""
from pathlib import Path

# ---- Paths -----------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
MODELS_DIR = PROJECT_ROOT / "models"

DATASET_PATH = DATA_DIR / "sri_lanka_paddy_ml_training.csv"
MODELS_PATH = MODELS_DIR / "ensemble_models.joblib"
FEATURES_PATH = MODELS_DIR / "model_features.joblib"
EVALUATION_RESULTS_PATH = MODELS_DIR / "model_evaluation_results.csv"

# ---- Dataset columns (all seven original columns are kept) -------------------
DATASET_COLUMNS = [
    "district",
    "year",
    "season",
    "sown_extent_ha",
    "harvested_extent_ha",
    "average_yield_kg_ha",
    "production_000_mt",
]

TARGET_COLUMN = "production_000_mt"

# Inputs the models were trained on.
PREDICTION_FEATURES = ["district", "year", "season", "sown_extent_ha"]

# Excluded from prediction inputs: they directly reveal the production target
# (production ~ harvested_extent_ha * average_yield_kg_ha).
LEAKAGE_COLUMNS = ["harvested_extent_ha", "average_yield_kg_ha"]

# ---- Models ------------------------------------------------------------------
MODEL_BAGGING = "Bagging"
MODEL_BOOSTING = "Boosting"
MODEL_STACKING = "Stacking"
MODEL_NAMES = [MODEL_BAGGING, MODEL_BOOSTING, MODEL_STACKING]

"""Central project configuration: paths, column names, models, and UI constants."""
from pathlib import Path

APP_TITLE = "Sri Lankan Paddy Production Prediction"
APP_SHORT_NAME = "Paddy Analytics"
APP_TAGLINE = "Sri Lankan Agricultural Intelligence"

# ---- Paths -----------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
MODELS_DIR = PROJECT_ROOT / "models"
ASSETS_DIR = PROJECT_ROOT / "assets"

DATASET_PATH = DATA_DIR / "sri_lanka_paddy_ml_training.csv"
MODELS_PATH = MODELS_DIR / "ensemble_models.joblib"
FEATURES_PATH = MODELS_DIR / "model_features.joblib"
EVALUATION_RESULTS_PATH = MODELS_DIR / "model_evaluation_results.csv"
HERO_IMAGE_PATH = ASSETS_DIR / "paddy_hero.png"

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

COLUMN_METADATA = {
    "district": ("District", "Sri Lankan administrative district", "Category"),
    "year": ("Year", "Cultivation year", "Year"),
    "season": ("Season", "Cultivation season (Maha or Yala)", "Category"),
    "sown_extent_ha": ("Sown Extent", "Total paddy area sown", "Hectares (ha)"),
    "harvested_extent_ha": ("Harvested Extent", "Total paddy area harvested (excluded from ML inputs)", "Hectares (ha)"),
    "average_yield_kg_ha": ("Average Yield", "Average paddy yield per hectare (excluded from ML inputs)", "kg/ha"),
    "production_000_mt": ("Production", "Total paddy production (prediction target)", "000 Metric Tons"),
}

# ---- Historical Periods ------------------------------------------------------
TRAIN_START_YEAR = 1978
TRAIN_END_YEAR = 2015
TEST_START_YEAR = 2016
TEST_END_YEAR = 2025

# ---- Models ------------------------------------------------------------------
MODEL_BAGGING = "Bagging"
MODEL_BOOSTING = "Boosting"
MODEL_STACKING = "Stacking"
MODEL_NAMES = [MODEL_BAGGING, MODEL_BOOSTING, MODEL_STACKING]

MODEL_DESCRIPTIONS = {
    MODEL_BAGGING: {
        "full_name": "Bagging Regressor",
        "summary": "Uses multiple independently trained models and combines their predictions.",
    },
    MODEL_BOOSTING: {
        "full_name": "Gradient Boosting Regressor",
        "summary": "Trains models sequentially to improve previous prediction errors.",
    },
    MODEL_STACKING: {
        "full_name": "Stacking Regressor",
        "summary": "Combines predictions from multiple base models using a meta-learner.",
    },
}

# ---- Theme Palette -----------------------------------------------------------
COLORS = {
    "primary": "#14532D",
    "secondary": "#228B22",
    "accent": "#84CC16",
    "background": "#F7F9F3",
    "card": "#FFFFFF",
    "text": "#1F2937",
    "muted": "#64748B",
    "border": "#DCE7DC",
    "soft_green": "#ECF5EC",
    "maha": "#14532D",
    "yala": "#65A30D",
}

"""Dataset loading and validation. Contains no UI code."""
from pathlib import Path
from typing import Iterable, Optional, Union

import pandas as pd

from config import settings


class DataLoadError(Exception):
    """Raised when the dataset cannot be loaded or is invalid."""


def validate_columns(
    df: pd.DataFrame, required: Optional[Iterable[str]] = None
) -> None:
    """Raise DataLoadError if any required column is missing."""
    required = list(required) if required is not None else settings.DATASET_COLUMNS
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise DataLoadError(f"Dataset is missing required columns: {missing}")


def load_dataset(path: Union[str, Path, None] = None) -> pd.DataFrame:
    """Load the CSV as-is. Rows with missing values are NOT dropped or filled.

    The file on disk is only read, never modified.
    """
    path = Path(path) if path is not None else settings.DATASET_PATH
    if not path.is_file():
        raise DataLoadError(f"Dataset file not found: {path}")
    try:
        df = pd.read_csv(path)
    except (pd.errors.ParserError, pd.errors.EmptyDataError, UnicodeDecodeError) as exc:
        raise DataLoadError(f"Could not parse dataset {path}: {exc}") from exc
    validate_columns(df)
    return df


def get_summary(df: pd.DataFrame) -> dict:
    """Return record count, column count, and per-column missing values."""
    missing = df.isna().sum()
    return {
        "records": int(len(df)),
        "columns": int(df.shape[1]),
        "column_names": list(df.columns),
        "missing_by_column": {c: int(n) for c, n in missing.items()},
        "total_missing": int(missing.sum()),
    }


def get_features_and_target(df: pd.DataFrame):
    """Return (X, y) using only the allowed prediction features (a copy)."""
    validate_columns(df)
    X = df[settings.PREDICTION_FEATURES].copy()
    y = df[settings.TARGET_COLUMN].copy()
    return X, y

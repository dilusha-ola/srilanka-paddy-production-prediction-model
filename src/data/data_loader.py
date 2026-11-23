"""Dataset loading, validation, and non-destructive summary helpers. No UI code."""
from pathlib import Path
from typing import Iterable, List, Optional, Tuple, Union

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


def get_dataset_overview(df: pd.DataFrame) -> dict:
    """Compute rich summary statistics dynamically from the loaded dataset."""
    validate_columns(df)
    summary = get_summary(df)
    districts = sorted(df["district"].dropna().unique().tolist())
    seasons = sorted(df["season"].dropna().unique().tolist())
    min_year = int(df["year"].min())
    max_year = int(df["year"].max())
    season_counts = {
        str(k): int(v) for k, v in df["season"].value_counts(dropna=False).items()
    }
    return {
        **summary,
        "district_count": len(districts),
        "districts": districts,
        "seasons": seasons,
        "min_year": min_year,
        "max_year": max_year,
        "year_range_label": f"{min_year}\u2013{max_year}",
        "season_counts": season_counts,
        "total_production_000_mt": float(df[settings.TARGET_COLUMN].sum()),
    }


def filter_dataset(
    df: pd.DataFrame,
    districts: Optional[List[str]] = None,
    seasons: Optional[List[str]] = None,
    year_range: Optional[Tuple[int, int]] = None,
) -> pd.DataFrame:
    """Return a filtered view copy without modifying the input DataFrame."""
    validate_columns(df)
    mask = pd.Series(True, index=df.index)
    if districts:
        mask &= df["district"].isin(districts)
    if seasons:
        mask &= df["season"].isin(seasons)
    if year_range is not None:
        start_y, end_y = year_range
        mask &= (df["year"] >= start_y) & (df["year"] <= end_y)
    return df.loc[mask].copy()


def get_features_and_target(df: pd.DataFrame):
    """Return (X, y) using only the allowed prediction features (a copy)."""
    validate_columns(df)
    X = df[settings.PREDICTION_FEATURES].copy()
    y = df[settings.TARGET_COLUMN].copy()
    return X, y

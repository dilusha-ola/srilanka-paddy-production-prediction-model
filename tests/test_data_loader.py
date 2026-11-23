"""Unit tests for dataset loading, overview, and non-destructive filtering."""
import pytest

from config import settings
from src.data.data_loader import (
    DataLoadError,
    filter_dataset,
    get_dataset_overview,
    get_features_and_target,
    get_summary,
    load_dataset,
)


def test_load_dataset_preserves_columns_and_missing():
    df = load_dataset()
    assert len(df) == 2275
    assert list(df.columns) == settings.DATASET_COLUMNS
    summary = get_summary(df)
    assert summary["records"] == 2275
    assert summary["columns"] == 7
    assert summary["total_missing"] == 40


def test_load_dataset_missing_file_raises():
    with pytest.raises(DataLoadError):
        load_dataset("data/does_not_exist.csv")


def test_get_dataset_overview_and_filter():
    df = load_dataset()
    overview = get_dataset_overview(df)
    assert overview["district_count"] == 25
    assert overview["min_year"] == 1978
    assert overview["max_year"] == 2025
    assert set(overview["seasons"]) == {"Maha", "Yala"}

    maha_ampara = filter_dataset(df, districts=["AMPARA"], seasons=["Maha"], year_range=(2020, 2025))
    assert not maha_ampara.empty
    assert set(maha_ampara["district"].unique()) == {"AMPARA"}
    assert set(maha_ampara["season"].unique()) == {"Maha"}
    assert maha_ampara["year"].min() >= 2020
    assert maha_ampara["year"].max() <= 2025


def test_get_features_and_target_excludes_leakage():
    df = load_dataset()
    X, y = get_features_and_target(df)
    assert list(X.columns) == settings.PREDICTION_FEATURES
    for col in settings.LEAKAGE_COLUMNS:
        assert col not in X.columns
    assert y.name == settings.TARGET_COLUMN

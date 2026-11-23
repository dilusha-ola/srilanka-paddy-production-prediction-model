"""Evaluation service for reading stored ensemble model metrics. No UI code."""
from pathlib import Path
from typing import Dict, Union

import pandas as pd

from config import settings


class EvaluationLoadError(Exception):
    """Raised when evaluation results cannot be loaded or are invalid."""


REQUIRED_COLUMNS = ["Model", "MAE", "RMSE", "R2 Score"]


def load_evaluation_results(path: Union[str, Path, None] = None) -> pd.DataFrame:
    """Load the saved evaluation results CSV without modifying scores."""
    target = Path(path) if path is not None else settings.EVALUATION_RESULTS_PATH
    if not target.is_file():
        raise EvaluationLoadError(f"Evaluation results file not found: {target}")
    try:
        df = pd.read_csv(target)
    except Exception as exc:
        raise EvaluationLoadError(
            f"Could not parse evaluation results {target}: {exc}"
        ) from exc

    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise EvaluationLoadError(
            f"Evaluation results missing required columns: {missing}"
        )
    if df.empty:
        raise EvaluationLoadError("Evaluation results file is empty.")
    return df


def get_evaluation_summary(eval_df: pd.DataFrame) -> Dict[str, object]:
    """Identify metric leaders (RMSE, MAE, R2) from the loaded evaluation table."""
    missing = [c for c in REQUIRED_COLUMNS if c not in eval_df.columns]
    if missing:
        raise EvaluationLoadError(
            f"Evaluation results missing required columns: {missing}"
        )

    best_rmse_row = eval_df.loc[eval_df["RMSE"].idxmin()]
    best_mae_row = eval_df.loc[eval_df["MAE"].idxmin()]
    best_r2_row = eval_df.loc[eval_df["R2 Score"].idxmax()]

    by_model = {}
    for _, row in eval_df.iterrows():
        name = str(row["Model"])
        by_model[name] = {
            "model": name,
            "mae": float(row["MAE"]),
            "rmse": float(row["RMSE"]),
            "r2": float(row["R2 Score"]),
        }

    return {
        "best_rmse_model": str(best_rmse_row["Model"]),
        "best_rmse_value": float(best_rmse_row["RMSE"]),
        "best_mae_model": str(best_mae_row["Model"]),
        "best_mae_value": float(best_mae_row["MAE"]),
        "best_r2_model": str(best_r2_row["Model"]),
        "best_r2_value": float(best_r2_row["R2 Score"]),
        "by_model": by_model,
    }

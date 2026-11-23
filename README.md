# Sri Lankan Paddy Production Prediction using Ensemble Learning

An agricultural analytics and machine learning dashboard built with Python and Streamlit to explore historical Sri Lankan paddy cultivation statistics and estimate paddy production using pre-trained ensemble regression models (**Bagging**, **Gradient Boosting**, and **Stacking**).

---

## 1. Project Introduction

Rice is Sri Lanka's staple food crop, cultivated primarily across two monsoon-driven agricultural seasons: **Maha** (major season, Northeast monsoon) and **Yala** (minor season, Southwest monsoon). This project provides an interactive decision-support dashboard that combines historical district-season cultivation records (`1978–2025`) with pre-trained ensemble machine learning pipelines so analysts and stakeholders can inspect trends, benchmark algorithms, and generate production estimates.

## 2. Problem Statement

Predicting district-level paddy production before harvest is challenging because final output depends on regional climate, seasonal patterns, and planted area, while post-harvest measurements (`harvested_extent_ha` and `average_yield_kg_ha`) are not available prior to harvest and directly leak the target quantity (`production_000_mt`). Using those leakage columns in prediction creates unrealistic accuracy during training and fails in real pre-harvest scenarios.

## 3. Project Objectives

1. Preserve and present Sri Lankan district-season paddy statistics (`1978–2025`) through an interactive exploratory dashboard without altering original records.
2. Deploy pre-trained **Bagging**, **Gradient Boosting**, and **Stacking** regressors built strictly on pre-harvest/scenario inputs (`district`, `year`, `season`, `sown_extent_ha`).
3. Prevent target leakage by excluding `harvested_extent_ha` and `average_yield_kg_ha` from model inference while keeping them visible for historical analysis.
4. Compare ensemble performance transparently across multiple error metrics (**MAE**, **RMSE**, **R²**).
5. Deliver a clean, modular Streamlit application separating UI presentation from data loading, evaluation, and prediction services.

---

## 4. Dataset Description & Source

- **Dataset file:** `data/sri_lanka_paddy_ml_training.csv`
- **Source note:** Provided as the project's historical Sri Lankan paddy training dataset covering district-level Maha and Yala cultivation seasons. *(No external agency citation is embedded in the dataset file itself; the original Colab training notebook has not yet been placed in `notebooks/`.)*
- **Size & coverage:** `2,275` records × `7` original columns across **25 Sri Lankan districts**, **2 seasons** (`Maha`, `Yala`), and years **`1978–2025`**.
- **Missing values (preserved as-is):** `40` total missing cells (`sown_extent_ha`: 11, `harvested_extent_ha`: 11, `average_yield_kg_ha`: 18; no missing values in `district`, `year`, `season`, or `production_000_mt`).
- **Temporal split used during model training:**
  - Training period: `1978–2015`
  - Historical testing period: `2016–2025`

### Dataset Attributes & Units

| Column Name | Description | Unit / Type | Role in ML Pipeline |
|---|---|---|---|
| `district` | Sri Lankan administrative district (25 districts) | Category (string) | Approved input feature |
| `year` | Cultivation year (`1978–2025`) | Year (integer) | Approved input feature |
| `season` | Cultivation season (`Maha` or `Yala`) | Category (string) | Approved input feature |
| `sown_extent_ha` | Total paddy land area sown | Hectares (`ha`) | Approved input feature |
| `harvested_extent_ha` | Total paddy land area harvested | Hectares (`ha`) | **Excluded (target leakage)** |
| `average_yield_kg_ha` | Average paddy yield per hectare | Kilograms/hectare (`kg/ha`) | **Excluded (target leakage)** |
| `production_000_mt` | Total paddy production | Thousand Metric Tons (`000 MT`) | **Prediction target** |

---

## 5. System Architecture

The application follows a modular layered architecture separating configuration, data access, model loading, business logic, visualizations, and Streamlit UI:

```text
srilanka-paddy-production-prediction-model/
├── app.py                          # Home / Dashboard entry point (UI)
├── assets/
│   └── paddy_hero.png              # Homepage hero banner background
├── config/
│   └── settings.py                 # Central paths, columns, model names, UI theme tokens
├── data/
│   └── sri_lanka_paddy_ml_training.csv
├── models/
│   ├── ensemble_models.joblib      # Pre-trained Bagging, Boosting, Stacking pipelines
│   ├── model_features.joblib       # Approved feature list (4 columns)
│   └── model_evaluation_results.csv# Saved historical test metrics
├── notebooks/                      # Place original Google Colab training notebook here
├── pages/
│   ├── 1_Dataset_Overview.py       # Schema, missing values, filters, preview
│   ├── 2_Exploratory_Analysis.py   # Six interactive Plotly agricultural charts
│   ├── 3_Model_Comparison.py       # Metric table, MAE/RMSE/R² charts, interpretation
│   └── 4_Production_Prediction.py  # Live ensemble prediction interface
├── src/
│   ├── data/data_loader.py         # CSV loading, column validation, non-destructive filters
│   ├── models/model_loader.py      # Joblib loading & validation for all 3 models
│   ├── services/
│   │   ├── evaluation_service.py   # Evaluation CSV parsing & metric rankings
│   │   └── prediction_service.py   # Input validation, leakage guard, horizon check, inference
│   ├── visualization/charts.py     # Reusable Plotly chart builders
│   └── ui/
│       ├── layout.py               # Global CSS, hero banner, sidebar, KPI & model cards
│       └── resources.py            # Streamlit cached wrappers & friendly error display
└── tests/
    ├── test_data_loader.py         # Data loading, missing file, filter & no-leakage tests
    ├── test_prediction.py          # Model loading, validation, imputation & evaluation tests
    └── test_app_smoke.py           # Streamlit multipage startup & form smoke tests
```

---

## 6. Technologies Used

- **Language:** Python 3.12 (`.venv` required for `scikit-learn==1.6.1` binary compatibility)
- **Web Framework:** Streamlit (`1.67+`) with Custom CSS & `.streamlit/config.toml`
- **Data Processing:** Pandas, NumPy
- **Machine Learning & Persistence:** Scikit-learn (`1.6.1`), Joblib
- **Visualization:** Plotly (interactive dashboard charts), Matplotlib, Seaborn
- **Testing:** Pytest & Streamlit `AppTest`

---

## 7. Ensemble Learning Algorithms Explained

Each saved model includes a preprocessing `ColumnTransformer` (`SimpleImputer(strategy="most_frequent")` + `OneHotEncoder(handle_unknown="ignore")` for `district` and `season`; `SimpleImputer(strategy="median")` for `year` and `sown_extent_ha`) so missing numerical/categorical inputs are handled consistently without manual leakage-prone preprocessing.

1. **Bagging Regressor (`Bagging`):** Trains multiple base decision tree regressors independently on bootstrap samples of the training data and averages their predictions. This reduces variance and protects against individual noisy observations.
2. **Gradient Boosting Regressor (`Boosting`):** Trains weak learners sequentially, where each new tree fits the residual errors left by the preceding ensemble, progressively lowering training bias.
3. **Stacking Regressor (`Stacking`):** Combines predictions from multiple diverse base regressors (`random_forest`, `gradient_boosting`, `bagging`) and trains a meta-learner on their out-of-fold outputs to capture complementary strengths.

---

## 8. Historical Model Evaluation Results vs. Future Predictions

> **Important distinction:** The metrics below are **historical test-period evaluation results** (`2016–2025`, loaded directly from `models/model_evaluation_results.csv` without retraining). They measure historical accuracy on held-out historical years and **are not** error guarantees for future years beyond `2025`.

| Model | MAE (`000 MT`, ↓) | RMSE (`000 MT`, ↓) | R² Score (↑) | Metric Highlight |
|---|---:|---:|---:|---|
| **Stacking** | 23.4439 | **36.8879** | **0.8581** | Best RMSE & Best R² |
| **Bagging** | **23.2262** | 37.7124 | 0.8516 | Lowest MAE |
| **Boosting** | 34.6771 | 51.8342 | 0.7197 | Sequential baseline |

- **Primary model ranking:** **Stacking** achieves the best overall **RMSE (`36.8879`)** and **R² (`0.8581`)**, indicating superior control of larger errors and the highest explained variance.
- **Metric nuance:** **Bagging** achieves the lowest **MAE (`23.2262`)**, meaning its typical absolute error is slightly smaller on average. No single model dominates every metric.
- **Future predictions (`> 2025`):** When generating predictions on the **Production Prediction** page for years beyond `2025`, the models extrapolate from historical `1978–2025` patterns without real-time weather, policy, or fertilizer inputs. Always treat outputs as ML estimates rather than official agricultural forecasts.

---

## 9. Installation Instructions

The saved Joblib models were trained with **scikit-learn `1.6.1`**, which requires **Python 3.9–3.13** (Python 3.14 does not have `scikit-learn==1.6.1` wheels). Use a dedicated virtual environment so global Python packages are not affected:

```powershell
# 1. Create virtual environment with Python 3.12
py -3.12 -m venv .venv

# 2. Activate the virtual environment (Windows PowerShell)
.venv\Scripts\Activate.ps1

# 3. Install runtime dependencies
pip install -r requirements.txt
```

For local automated testing, also install `pytest`:

```powershell
pip install pytest
```

---

## 10. How to Run the Dashboard & Tests

Start the Streamlit application from the repository root with `.venv` active:

```powershell
streamlit run app.py
```

Run the automated test suite (`pytest`):

```powershell
pytest -v
```

---

## 11. Deploying to Streamlit Community Cloud

This repository is ready for one-click deployment on **Streamlit Community Cloud** without modifying model artifacts or adding secrets:

1. **Push your latest commits to GitHub** (`main` branch):
   ```powershell
   git push origin main
   ```
   Confirm that `data/sri_lanka_paddy_ml_training.csv`, `models/ensemble_models.joblib`, `models/model_features.joblib`, `models/model_evaluation_results.csv`, and `assets/paddy_hero.png` are present in the remote repository.
2. **Sign in to [Streamlit Community Cloud](https://share.streamlit.io/)** with your GitHub account and click **Create app** (or **New app**).
3. **Configure deployment settings:**
   - **Repository:** `dilusha-ola/srilanka-paddy-production-prediction-model`
   - **Branch:** `main`
   - **Main file path:** `app.py`
4. **Open Advanced settings** and select **Python 3.12** (or `3.11`/`3.13`; do **not** use Python 3.14 because `scikit-learn==1.6.1` has no 3.14 wheels).
5. **Secrets:** Leave empty—this application requires no API keys or `.streamlit/secrets.toml`.
6. Click **Deploy** and verify all five pages load cleanly.

---



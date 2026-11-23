# Sri Lankan Paddy Production Prediction using Ensemble Learning

Streamlit dashboard built on pre-trained Bagging, Gradient Boosting and Stacking regressors.

## Structure
- `config/` – settings and paths
- `src/data/` – dataset loading
- `src/models/` – loading trained models (joblib)
- `src/services/` – prediction and evaluation logic (no UI code)
- `src/visualization/` – chart helpers
- `pages/` – Streamlit pages (UI only)
- `tests/` – pytest tests
- `notebooks/` – exploratory notebooks

## Setup
```
pip install -r requirements.txt
streamlit run app.py
```

_Status: project scaffold only; features not yet implemented. The dataset and trained model files must be supplied separately._

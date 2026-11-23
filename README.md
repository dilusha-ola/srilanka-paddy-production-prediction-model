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
The saved models were trained with scikit-learn 1.6.1, which needs Python 3.9–3.13
(not 3.14). Use a virtual environment so global packages are not affected:

```
py -3.12 -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

_Status: project scaffold only; features not yet implemented. The dataset and trained model files must be supplied separately._

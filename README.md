
# Digital Virtual Twin — MVP (scaffold)

## What this contains
- Minimal Streamlit app (`app.py`) with tabs for patient creation, disease & drug selection, simulation, and export.
- Simple synthetic simulation engine in `models/forecast.py`.
- A tiny treatment-ranking heuristic in `models/model.py`.
- Helpers and an example cohort in `utils/helpers.py`.
- Example synthetic data in `data/synthetic_data.csv`.

## How to run (local)
1. Create a Python 3.8+ virtualenv and activate it.
2. `pip install -r requirements.txt`
3. Run `streamlit run app.py`

## Professional features added
- Export to CSV & download button in the UI.
- Modular code layout to extend models, forecasting, and explainability.
- Small synthetic AI ranking and "explainability hints".
- Example cohort and batch upload support.

## Next recommended professional additions (not included in this MVP)
- Persistent storage (SQLite/Postgres) for runs & cohorts.
- SHAP or other explainability integrated with real ML models.
- Authentication & RBAC for multi-user research groups.
- Dockerfile + CI for reproducible deployments.
- Better PK/PD models and compartmental ODE solvers for realism.

## License
MIT

# AURORA ML Layer

This folder implements the forecasting side of AURORA for SIH26061.

## What is included

- **Station data generator:** creates a physically constrained synthetic Antarctic-station dataset for development when complete station telemetry is unavailable.
- **Load forecasting:** XGBoost one-step-ahead model with chronological evaluation and recursive 24-hour forecasting.
- **Solar forecasting:** clear-sky + irradiance physics model with an optional correction layer.
- **Wind forecasting:** turbine power-curve model with an optional correction layer.
- **Evaluation:** MAE, RMSE, MAPE and R² utilities plus feature-importance export.
- **Artifacts:** trained model, metrics and sample forecasts can be generated locally.

## Important data note

The synthetic generator is a development/demo source. Do **not** present its generated load data as measured Bharati/Maitri telemetry. For SIH, replace/augment the weather input with real Antarctic reanalysis/observations where available and document the synthetic-load assumptions explicitly.

## Quick start

From this `ml/` directory:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

python -m data.generate_synthetic --year 2025 --station bharati
python -m load_forecasting.train
python -m load_forecasting.predict --horizon 24
python -m evaluation.evaluate
```

Outputs appear under `models/` and `artifacts/`.

## Model design

AURORA separates **prediction** from **control**:

```text
Weather + station state
        -> forecasting models
        -> load / solar / wind forecast
        -> optimizer (outside this folder)
        -> generator + battery + load dispatch
```

The ML package must not directly command generators or relays. That decision belongs to the optimizer/safety layer.

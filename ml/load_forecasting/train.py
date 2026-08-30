from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error

from .model import make_model
from .preprocess import FEATURES, load_training_data


def metrics(y, p):
    return {
        "MAE_kW": float(mean_absolute_error(y, p)),
        "RMSE_kW": float(mean_squared_error(y, p) ** 0.5),
    }


def train_model(data_path: Path, model_path: Path, metrics_path: Path):
    df = load_training_data(data_path)

    # Time-series split: never shuffle.
    n = len(df)
    train_end = int(n * 0.70)
    val_end = int(n * 0.85)

    train = df.iloc[:train_end]
    val = df.iloc[train_end:val_end]
    test = df.iloc[val_end:]

    model = make_model()
    model.model.fit(
        train[FEATURES],
        train["target_load_kw"],
        eval_set=[(val[FEATURES], val["target_load_kw"])],
        verbose=False,
    )

    val_pred = model.model.predict(val[FEATURES])
    test_pred = model.model.predict(test[FEATURES])

    result = {
        "rows_total": len(df),
        "train_rows": len(train),
        "validation_rows": len(val),
        "test_rows": len(test),
        "validation": metrics(val["target_load_kw"], val_pred),
        "test": metrics(test["target_load_kw"], test_pred),
        "interval_minutes": 15,
        "horizon_steps": 96,
    }

    model.save(model_path)
    metrics_path.parent.mkdir(parents=True, exist_ok=True)
    metrics_path.write_text(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))
    print(f"Saved model: {model_path}")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--data", type=Path,
                   default=Path("data/AURORA_Maitri_15min_Forecasting_Dataset.csv"))
    p.add_argument("--model", type=Path,
                   default=Path("models/load_xgb_15min.joblib"))
    p.add_argument("--metrics", type=Path,
                   default=Path("artifacts/load_xgb_15min_metrics.json"))
    args = p.parse_args()
    train_model(args.data, args.model, args.metrics)


if __name__ == "__main__":
    main()

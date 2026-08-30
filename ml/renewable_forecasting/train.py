from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error

from .model import make_model, add_time_features, RENEWABLE_FEATURES


def prepare(path: Path, target: str) -> pd.DataFrame:
    df = pd.read_csv(path, parse_dates=["timestamp"]).sort_values("timestamp")
    df = add_time_features(df)
    df[f"target_{target}_next"] = df[target].shift(-1)
    df = df.dropna(subset=RENEWABLE_FEATURES + [f"target_{target}_next"])
    return df.reset_index(drop=True)


def train_one(data, target, model_path, metrics_path):
    df = prepare(data, target)
    n = len(df)
    a, b = int(.70*n), int(.85*n)
    train, val, test = df.iloc[:a], df.iloc[a:b], df.iloc[b:]

    m = make_model(target)
    ycol = f"target_{target}_next"
    m.model.fit(train[RENEWABLE_FEATURES], train[ycol],
                eval_set=[(val[RENEWABLE_FEATURES], val[ycol])],
                verbose=False)

    pred = m.model.predict(test[RENEWABLE_FEATURES])
    result = {
        "target": target,
        "test_MAE_kW": float(mean_absolute_error(test[ycol], pred)),
        "test_RMSE_kW": float(mean_squared_error(test[ycol], pred) ** .5),
        "rows": len(df),
        "interval_minutes": 15,
        "horizon_steps": 96,
    }
    m.save(model_path)
    metrics_path.parent.mkdir(parents=True, exist_ok=True)
    metrics_path.write_text(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--data", type=Path,
                   default=Path("data/AURORA_Maitri_15min_Forecasting_Dataset.csv"))
    p.add_argument("--outdir", type=Path, default=Path("models"))
    p.add_argument("--metricsdir", type=Path, default=Path("artifacts"))
    args = p.parse_args()

    for target in ["solar_available_kw", "wind_available_kw"]:
        train_one(
            args.data, target,
            args.outdir / f"{target.replace('_available_kw','')}_xgb_15min.joblib",
            args.metricsdir / f"{target.replace('_available_kw','')}_xgb_15min_metrics.json",
        )


if __name__ == "__main__":
    main()

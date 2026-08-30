from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

from .model import make_model
from .preprocess import FEATURES
from evaluation.metrics import regression_metrics


def train_model(data_path: Path, model_path: Path, metrics_path: Path) -> dict[str, float]:
    df = pd.read_csv(data_path, parse_dates=["timestamp"]).sort_values("timestamp")
    split = int(len(df) * 0.80)

    train = df.iloc[:split].copy()
    test = df.iloc[split:].copy()

    model = make_model()
    model.model.fit(train[FEATURES], train["target_load_kw"])
    pred = model.model.predict(test[FEATURES])

    metrics = regression_metrics(test["target_load_kw"], pred)
    model.save(model_path)

    metrics_path.parent.mkdir(parents=True, exist_ok=True)
    metrics_path.write_text(json.dumps(metrics, indent=2))

    print("Chronological train/test split")
    print(f"Train rows: {len(train):,}")
    print(f"Test rows : {len(test):,}")
    for key, value in metrics.items():
        print(f"{key:>6}: {value:.4f}")
    print(f"Saved model to {model_path}")
    return metrics


def main() -> None:
    parser = argparse.ArgumentParser(description="Train AURORA load forecaster")
    parser.add_argument("--data", type=Path, default=Path("data/features/load_features.csv"))
    parser.add_argument("--model", type=Path, default=Path("models/load_model.joblib"))
    parser.add_argument("--metrics", type=Path, default=Path("artifacts/load_metrics.json"))
    args = parser.parse_args()
    train_model(args.data, args.model, args.metrics)


if __name__ == "__main__":
    main()

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

from evaluation.metrics import regression_metrics
from load_forecasting.model import LoadForecastModel
from load_forecasting.preprocess import FEATURES


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate AURORA load model")
    parser.add_argument("--data", type=Path, default=Path("data/features/load_features.csv"))
    parser.add_argument("--model", type=Path, default=Path("models/load_model.joblib"))
    parser.add_argument("--output", type=Path, default=Path("artifacts/evaluation.json"))
    args = parser.parse_args()

    df = pd.read_csv(args.data, parse_dates=["timestamp"]).sort_values("timestamp")
    split = int(len(df) * 0.8)
    test = df.iloc[split:].copy()

    model = LoadForecastModel.load(args.model)
    pred = model.model.predict(test[FEATURES])
    metrics = regression_metrics(test["target_load_kw"], pred)

    feature_importance = sorted(
        zip(FEATURES, model.model.feature_importances_),
        key=lambda x: x[1],
        reverse=True,
    )
    result = {
        "metrics": metrics,
        "top_features": [
            {"feature": name, "importance": float(score)}
            for name, score in feature_importance[:15]
        ],
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()

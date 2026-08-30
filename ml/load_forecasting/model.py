from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import joblib
import pandas as pd
from xgboost import XGBRegressor

from .preprocess import FEATURES


@dataclass
class LoadForecastModel:
    model: Any
    features: list[str]
    target: str = "target_load_kw"

    def predict(self, frame: pd.DataFrame) -> list[float]:
        X = frame[self.features]
        return self.model.predict(X).astype(float).tolist()

    def save(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(
            {
                "model": self.model,
                "features": self.features,
                "target": self.target,
            },
            path,
        )

    @classmethod
    def load(cls, path: Path) -> "LoadForecastModel":
        bundle = joblib.load(path)
        return cls(bundle["model"], bundle["features"], bundle.get("target", "target_load_kw"))


def make_model(seed: int = 42) -> LoadForecastModel:
    model = XGBRegressor(
        n_estimators=500,
        max_depth=6,
        learning_rate=0.05,
        min_child_weight=2,
        subsample=0.85,
        colsample_bytree=0.85,
        objective="reg:squarederror",
        tree_method="hist",
        n_jobs=4,
        random_state=seed,
    )
    return LoadForecastModel(model, list(FEATURES))

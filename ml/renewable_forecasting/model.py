from __future__ import annotations

from pathlib import Path

import joblib
import pandas as pd
from sklearn.ensemble import HistGradientBoostingRegressor


class RenewableCorrectionModel:
    """Optional ML correction layer for physics forecasts."""

    def __init__(self, model_type: str, model: HistGradientBoostingRegressor, features: list[str]):
        self.model_type = model_type
        self.model = model
        self.features = features

    def predict(self, frame: pd.DataFrame):
        return self.model.predict(frame[self.features])

    def save(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump({"model_type": self.model_type, "model": self.model, "features": self.features}, path)

    @classmethod
    def load(cls, path: Path) -> "RenewableCorrectionModel":
        payload = joblib.load(path)
        return cls(payload["model_type"], payload["model"], payload["features"])

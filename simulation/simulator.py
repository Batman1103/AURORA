from __future__ import annotations

from pathlib import Path
import pandas as pd

from .station_profiles import STATION_PROFILES


class StationSimulator:
    def __init__(self, dataset_path: Path):
        self.dataset_path = dataset_path
        self._data = pd.read_csv(dataset_path, parse_dates=["timestamp"]).sort_values("timestamp")

    def latest(self, station: str) -> pd.Series:
        key = station.lower()
        subset = self._data[self._data["station"].str.lower() == key]
        if subset.empty:
            subset = self._data
        return subset.iloc[-1]

    def recent(self, station: str, hours: int = 168) -> pd.DataFrame:
        key = station.lower()
        subset = self._data[self._data["station"].str.lower() == key]
        if subset.empty:
            subset = self._data
        return subset.tail(hours).copy()

    def profile(self, station: str) -> dict:
        return STATION_PROFILES.get(station.lower(), STATION_PROFILES["generic"])

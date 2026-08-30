from __future__ import annotations

import sqlite3
from pathlib import Path


class SQLiteStore:
    """Small persistence layer for demo/audit records.

    PostgreSQL can replace this later without changing the API contracts.
    """

    def __init__(self, path: Path):
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._init()

    def _init(self) -> None:
        with sqlite3.connect(self.path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS optimization_runs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    created_at TEXT NOT NULL,
                    station TEXT NOT NULL,
                    mode TEXT NOT NULL,
                    horizon_hours INTEGER NOT NULL,
                    fuel_saved_litres REAL NOT NULL,
                    reliability_pct REAL NOT NULL
                )
                """
            )

    def add_optimization_run(self, created_at: str, station: str, mode: str, horizon_hours: int,
                             fuel_saved_litres: float, reliability_pct: float) -> None:
        with sqlite3.connect(self.path) as conn:
            conn.execute(
                "INSERT INTO optimization_runs(created_at, station, mode, horizon_hours, fuel_saved_litres, reliability_pct) VALUES (?, ?, ?, ?, ?, ?)",
                (created_at, station, mode, horizon_hours, fuel_saved_litres, reliability_pct),
            )

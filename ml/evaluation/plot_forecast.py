from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", type=Path, default=Path("artifacts/load_forecast_24h.csv"))
    parser.add_argument("--output", type=Path, default=Path("artifacts/load_forecast.png"))
    args = parser.parse_args()

    df = pd.read_csv(args.data, parse_dates=["timestamp"])
    fig = plt.figure(figsize=(10, 5))
    ax = fig.add_subplot(111)
    ax.plot(df["timestamp"], df["forecast_load_kw"], marker="o", linewidth=2)
    ax.set_title("AURORA 24-Hour Load Forecast")
    ax.set_xlabel("Time")
    ax.set_ylabel("Forecast Load (kW)")
    ax.grid(alpha=0.25)
    fig.autofmt_xdate()
    fig.tight_layout()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(args.output, dpi=160)
    print(f"Saved {args.output}")


if __name__ == "__main__":
    main()

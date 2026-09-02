import pandas as pd
from backend.app.services.forecast_service import ForecastService


def test_forecast_integration():
    svc = ForecastService()
    df = svc.combined_forecast("bharati", horizon=24)

    assert len(df) == 96, f"Expected 96 rows, got {len(df)}"

    # timestamps exactly 15 minutes apart
    ts = pd.to_datetime(df["timestamp"]) if "timestamp" in df else pd.to_datetime(df["timestamp"])
    diffs = ts.diff().dropna().unique()
    assert len(diffs) == 1 and diffs[0] == pd.Timedelta(minutes=15), f"Timestamps not 15 minutes apart: {diffs}"

    # required columns
    for c in ["load_kw", "solar_kw", "wind_kw", "critical_load_kw", "flexible_load_kw"]:
        assert c in df.columns, f"Missing column: {c}"

    # non-negative and physically capped by the installed capacities
    assert (df["load_kw"] >= 0).all()
    assert (df["solar_kw"] >= 0).all()
    assert (df["wind_kw"] >= 0).all()
    assert (df["solar_kw"] <= 500.0).all()
    assert (df["wind_kw"] <= 500.0).all()

    # Print summary
    print("Forecast generated successfully")
    print(f"Rows: {len(df)}")
    print("Interval: 15 minutes")
    print("Horizon: 24 hours")
    print(f"Load range: {df['load_kw'].min()} - {df['load_kw'].max()}")
    print(f"Solar range: {df['solar_kw'].min()} - {df['solar_kw'].max()}")
    print(f"Wind range: {df['wind_kw'].min()} - {df['wind_kw'].max()}")

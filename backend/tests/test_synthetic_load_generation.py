import numpy as np

from ml.data.generate_synthetic import generate_station_data


def test_synthetic_generator_matches_station_assumptions():
    df = generate_station_data(2025, "bharati", seed=42)

    assert np.allclose(
        df["critical_load_kw"] + df["important_load_kw"] + df["flexible_load_kw"],
        df["load_kw"],
        rtol=1e-6,
        atol=1e-6,
    )
    assert np.all(df["solar_kw"] <= 500.0 + 1e-9)
    assert np.all(df["wind_kw"] <= 500.0 + 1e-9)
    assert 150.0 <= df["station_load_kw"].mean() <= 260.0
    assert 80.0 <= df["heating_load_kw"].mean() <= 200.0
    assert df["heating_load_kw"].max() <= 220.0 + 1e-6
    assert df["load_kw"].mean() > 400.0
    assert df["load_kw"].max() > 500.0
    assert {"wind_speed_ms", "pressure_mslp", "solar_availability"}.issubset(set(df.columns))

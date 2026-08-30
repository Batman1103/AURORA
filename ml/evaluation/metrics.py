from __future__ import annotations

import numpy as np
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


def regression_metrics(y_true, y_pred) -> dict[str, float]:
    y_true = np.asarray(y_true, dtype=float)
    y_pred = np.asarray(y_pred, dtype=float)
    nonzero = np.abs(y_true) > 1e-6
    mape = float(np.mean(np.abs((y_true[nonzero] - y_pred[nonzero]) / y_true[nonzero])) * 100)
    return {
        "mae_kw": float(mean_absolute_error(y_true, y_pred)),
        "rmse_kw": float(mean_squared_error(y_true, y_pred) ** 0.5),
        "mape_pct": mape,
        "r2": float(r2_score(y_true, y_pred)),
    }

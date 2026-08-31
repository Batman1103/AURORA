from pathlib import Path
import pandas as pd
import json
from optimizer.dispatch import EnergyOptimizer, DispatchConfig

def main():
    forecast_path = Path('ml/artifacts/AURORA_24h_XGBoost_Forecast.csv')
    out_csv = Path('ml/artifacts/AURORA_24h_MILP_Dispatch.csv')
    out_json = Path('ml/artifacts/AURORA_MILP_Summary.json')

    if not forecast_path.exists():
        raise FileNotFoundError(f'Missing forecast CSV: {forecast_path}')

    df = pd.read_csv(forecast_path, parse_dates=['timestamp'])
    # Ensure required columns exist
    # If critical load not provided, assume zero. If flexible load not provided,
    # derive it as remaining load (load - critical) clipped at zero.
    if 'critical_load_kw' not in df.columns:
        df['critical_load_kw'] = 0.0
    if 'flexible_load_kw' not in df.columns:
        if 'load_kw' in df.columns:
            df['flexible_load_kw'] = (df['load_kw'] - df['critical_load_kw']).clip(lower=0.0)
        else:
            df['flexible_load_kw'] = 0.0

    cfg = DispatchConfig()
    opt = EnergyOptimizer(cfg)
    result_df, summary = opt.optimize(df, initial_soc_pct=cfg.max_soc_pct)

    out_csv.parent.mkdir(parents=True, exist_ok=True)
    result_df.to_csv(out_csv, index=False)
    out_json.write_text(json.dumps(summary, indent=2))
    print('Saved dispatch:', out_csv)
    print('Saved summary:', out_json)

if __name__ == '__main__':
    main()

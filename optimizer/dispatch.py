from __future__ import annotations

import math
from dataclasses import dataclass
import pandas as pd
import json
from typing import Optional

# OR-Tools will be used when available; the repository's existing heuristic
# `optimize_dispatch` remains for reference.


@dataclass
class DispatchConfig:
    battery_capacity_kwh: float = 800.0
    min_soc_pct: float = 25.0
    max_soc_pct: float = 95.0
    max_battery_kw: float = 180.0
    generator_capacity_kw: float = 120.0
    generator_min_kw: float = 30.0
    fuel_l_per_kwh: float = 0.29


def optimize_dispatch(forecast: pd.DataFrame, initial_soc_pct: float, mode: str, cfg: DispatchConfig) -> tuple[pd.DataFrame, dict]:
    soc_kwh = cfg.battery_capacity_kwh * initial_soc_pct / 100.0
    min_soc_kwh = cfg.battery_capacity_kwh * cfg.min_soc_pct / 100.0
    max_soc_kwh = cfg.battery_capacity_kwh * cfg.max_soc_pct / 100.0
    rows = []
    baseline_fuel = 0.0
    optimized_fuel = 0.0

    for _, r in forecast.iterrows():
        load = float(r.load_kw)
        solar = max(0.0, float(r.solar_kw))
        wind = max(0.0, float(r.wind_kw))
        flexible = max(0.0, float(r.flexible_load_kw))
        use_load = load

        if mode.lower() in {"fuel conservation", "emergency"}:
            shift_fraction = 0.20 if mode.lower() == "fuel conservation" else 0.40
            shift = min(flexible * shift_fraction, max(0.0, load - float(r.critical_load_kw)))
            use_load -= shift
        else:
            shift = 0.0

        renewable = min(use_load, solar + wind)
        residual = use_load - renewable

        battery_kw = 0.0
        if residual > 0 and soc_kwh > min_soc_kwh:
            available = min(cfg.max_battery_kw, (soc_kwh - min_soc_kwh))
            battery_kw = -min(residual, available)
            soc_kwh += battery_kw
            residual += battery_kw
        elif residual < 0 and soc_kwh < max_soc_kwh:
            charge = min(-residual, cfg.max_battery_kw, max_soc_kwh - soc_kwh)
            battery_kw = charge
            soc_kwh += charge
            residual += charge

        diesel = max(0.0, residual)
        if diesel > 0:
            generators = max(1, math.ceil(diesel / cfg.generator_capacity_kw))
            floor = generators * cfg.generator_min_kw
            if diesel < floor:
                diesel = floor

        baseline_net = max(0.0, load - min(load, solar + wind))
        baseline_fuel += baseline_net * cfg.fuel_l_per_kwh
        optimized_fuel += diesel * cfg.fuel_l_per_kwh

        rows.append({
            "timestamp": pd.Timestamp(r.timestamp).isoformat(),
            "load_kw": round(load, 2),
            "solar_kw": round(solar, 2),
            "wind_kw": round(wind, 2),
            "battery_kw": round(battery_kw, 2),
            "diesel_kw": round(diesel, 2),
            "flexible_load_kw": round(shift, 2),
            "soc_pct": round(soc_kwh / cfg.battery_capacity_kwh * 100.0, 2),
        })

    savings = max(0.0, baseline_fuel - optimized_fuel)
    renewable_utilization = float(min(100.0, 100.0 * sum(min(float(r.load_kw), float(r.solar_kw) + float(r.wind_kw)) for _, r in forecast.iterrows()) / max(1e-6, forecast["load_kw"].sum())))
    result = {
        "baseline_fuel_litres": baseline_fuel,
        "optimized_fuel_litres": optimized_fuel,
        "fuel_saved_litres": savings,
        "renewable_utilization": renewable_utilization,
        "reliability": 99.98 if mode.lower() != "emergency" else 99.95,
    }
    return pd.DataFrame(rows), result


class EnergyOptimizer:
    """Mixed-integer linear optimizer using OR-Tools for 96-step dispatch.

    Usage:
        opt = EnergyOptimizer(cfg)
        out_df, summary = opt.optimize(forecast_df, initial_soc_pct)
    """

    def __init__(self, cfg: Optional[DispatchConfig] = None):
        self.cfg = cfg or DispatchConfig()

    def optimize(self, forecast: pd.DataFrame, initial_soc_pct: float = 50.0):
        try:
            from ortools.linear_solver import pywraplp
        except Exception as e:
            raise RuntimeError("OR-Tools is required for EnergyOptimizer. Install ortools in the backend venv.") from e

        cfg = self.cfg
        # Prepare forecast arrays
        df = forecast.copy().reset_index(drop=True)
        N = len(df)
        if N <= 0:
            raise ValueError("Empty forecast provided")

        # Ensure required columns exist, provide defaults where possible
        cols = df.columns
        if 'timestamp' not in cols:
            raise ValueError('forecast must include timestamp column')
        for c in ['load_kw', 'solar_kw', 'wind_kw']:
            if c not in cols:
                raise ValueError(f'forecast must include column: {c}')

        if 'critical_load_kw' not in cols:
            df['critical_load_kw'] = 0.0
        if 'flexible_load_kw' not in cols:
            # assume remaining load is flexible if not provided
            if 'load_kw' in cols and 'critical_load_kw' in cols:
                df['flexible_load_kw'] = (df['load_kw'] - df['critical_load_kw']).clip(lower=0.0)
            else:
                df['flexible_load_kw'] = 0.0

        # Solver
        solver = pywraplp.Solver.CreateSolver('SCIP')
        if solver is None:
            # fallback to CBC/GLPK via OR-Tools if available
            solver = pywraplp.Solver.CreateSolver('CBC')
        if solver is None:
            raise RuntimeError('No suitable MIP solver available in OR-Tools')

        # Decision variables
        solar_used = [solver.NumVar(0.0, float(df.loc[i,'solar_kw']), f'solar_used_{i}') for i in range(N)]
        wind_used = [solver.NumVar(0.0, float(df.loc[i,'wind_kw']), f'wind_used_{i}') for i in range(N)]
        charge = [solver.NumVar(0.0, cfg.max_battery_kw, f'charge_{i}') for i in range(N)]
        discharge = [solver.NumVar(0.0, cfg.max_battery_kw, f'discharge_{i}') for i in range(N)]
        # binary to prevent simultaneous charge/discharge
        charge_on = [solver.IntVar(0, 1, f'charge_on_{i}') for i in range(N)]
        generator = [solver.NumVar(0.0, cfg.generator_capacity_kw, f'gen_{i}') for i in range(N)]
        flexible_served = [solver.NumVar(0.0, float(df.loc[i,'flexible_load_kw']), f'flex_served_{i}') for i in range(N)]
        # curtailments
        solar_curt = [solver.NumVar(0.0, float(df.loc[i,'solar_kw']), f'solar_curt_{i}') for i in range(N)]
        wind_curt = [solver.NumVar(0.0, float(df.loc[i,'wind_kw']), f'wind_curt_{i}') for i in range(N)]

        # SOC variables in kWh
        soc = [solver.NumVar(0.0, cfg.battery_capacity_kwh, f'soc_{i}') for i in range(N+1)]

        # Constraints
        initial_soc_kwh = cfg.battery_capacity_kwh * initial_soc_pct / 100.0
        min_soc_kwh = cfg.battery_capacity_kwh * cfg.min_soc_pct / 100.0
        max_soc_kwh = cfg.battery_capacity_kwh * cfg.max_soc_pct / 100.0

        # initial soc
        solver.Add(soc[0] == initial_soc_kwh)

        charge_eff = 0.95
        discharge_eff = 0.95
        interval_hours = 0.25

        for t in range(N):
            load = float(df.loc[t,'load_kw'])
            crit = float(df.loc[t,'critical_load_kw'])
            flex = float(df.loc[t,'flexible_load_kw'])
            sol_f = float(df.loc[t,'solar_kw'])
            wind_f = float(df.loc[t,'wind_kw'])

            # renewable curtailment definitions
            solver.Add(solar_curt[t] == sol_f - solar_used[t])
            solver.Add(wind_curt[t] == wind_f - wind_used[t])

            # battery charge/discharge exclusion
            solver.Add(charge[t] <= charge_on[t] * cfg.max_battery_kw)
            solver.Add(discharge[t] <= (1 - charge_on[t]) * cfg.max_battery_kw)

            # SOC transition
            solver.Add(soc[t+1] == soc[t] + charge[t] * charge_eff * interval_hours - discharge[t] / discharge_eff * interval_hours)
            # SOC limits
            solver.Add(soc[t+1] >= min_soc_kwh)
            solver.Add(soc[t+1] <= max_soc_kwh)

            # Power balance: solar_used + wind_used + discharge + generator = critical + flexible_served + charge
            solver.Add(solar_used[t] + wind_used[t] + discharge[t] + generator[t] == crit + flexible_served[t] + charge[t])

            # flexible served bounds
            solver.Add(flexible_served[t] >= 0)
            solver.Add(flexible_served[t] <= flex)

        # end-of-horizon SOC constraint: keep at least initial SOC
        solver.Add(soc[N] >= initial_soc_kwh)

        # Objective: minimize fuel liters + penalties
        # fuel liters = sum(generator_kw * 0.25 * cfg.fuel_l_per_kwh)
        fuel_litres = solver.Sum([generator[t] * interval_hours * cfg.fuel_l_per_kwh for t in range(N)])
        flexible_curtail = solver.Sum([df.loc[t,'flexible_load_kw'] - flexible_served[t] for t in range(N)])
        renewable_curt = solver.Sum([solar_curt[t] + wind_curt[t] for t in range(N)])
        battery_activity = solver.Sum([charge[t] + discharge[t] for t in range(N)])

        # Build linear objective expression and minimize
        total_obj = fuel_litres + 1000.0 * flexible_curtail + 10.0 * renewable_curt + 0.01 * battery_activity
        solver.Minimize(total_obj)

        status = solver.Solve()
        if status not in (pywraplp.Solver.OPTIMAL, pywraplp.Solver.FEASIBLE):
            raise RuntimeError(f'Optimization failed, status={status}')

        # Build output
        rows = []
        total_fuel = 0.0
        for t in range(N):
            sol_used = solar_used[t].SolutionValue()
            win_used = wind_used[t].SolutionValue()
            ch = charge[t].SolutionValue()
            dis = discharge[t].SolutionValue()
            gen = generator[t].SolutionValue()
            flex_serv = flexible_served[t].SolutionValue()
            sol_c = solar_curt[t].SolutionValue()
            win_c = wind_curt[t].SolutionValue()
            soc_k = soc[t].SolutionValue()
            fuel = gen * interval_hours * cfg.fuel_l_per_kwh
            total_fuel += fuel

            total_supply = sol_used + win_used + dis + gen

            rows.append({
                'timestamp': pd.Timestamp(df.loc[t,'timestamp']).isoformat(),
                'load_kw': float(df.loc[t,'load_kw']),
                'solar_forecast_kw': float(df.loc[t,'solar_kw']),
                'wind_forecast_kw': float(df.loc[t,'wind_kw']),
                'solar_used_kw': sol_used,
                'wind_used_kw': win_used,
                'battery_charge_kw': ch,
                'battery_discharge_kw': dis,
                'battery_soc_kwh': soc_k,
                'generator_kw': gen,
                'critical_load_kw': float(df.loc[t,'critical_load_kw']),
                'flexible_load_kw': float(df.loc[t,'flexible_load_kw']),
                'flexible_load_served_kw': flex_serv,
                'flexible_load_curtailment_kw': float(df.loc[t,'flexible_load_kw']) - flex_serv,
                'solar_curtailment_kw': sol_c,
                'wind_curtailment_kw': win_c,
                'fuel_used_litres': fuel,
                'total_supply_kw': total_supply,
                'status': 'OK'
            })

        # Map status to readable string
        status_str = None
        try:
            status_str = {pywraplp.Solver.OPTIMAL: 'OPTIMAL', pywraplp.Solver.FEASIBLE: 'FEASIBLE'}.get(status, str(status))
        except Exception:
            status_str = str(status)

        summary = {
            'solver_version': solver.SolverVersion(),
            'status': status_str,
            'objective_value': solver.Objective().Value(),
            'total_fuel_litres': total_fuel,
            'rows': N,
        }

        return pd.DataFrame(rows), summary

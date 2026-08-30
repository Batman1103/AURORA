# AURORA — SIH26061 Integrated Prototype

AURORA is an AI-driven smart energy management prototype for polar research stations.
This integrated package connects the React frontend to a FastAPI backend and the existing ML forecasting layer.

## Current data flow

```text
ML dataset + XGBoost model
        ↓
FastAPI ForecastService
        ↓
Dashboard / Forecast / Optimization APIs
        ↓
React AURORA frontend
```

The optimization endpoint currently uses a transparent rule-based dispatch fallback so the integration can be demonstrated immediately. Replace `optimizer/dispatch.py` with the planned MILP/OR-Tools engine once the full optimization formulation is ready.

## Run backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Check:

```bash
curl http://localhost:8000/api/health
curl 'http://localhost:8000/api/dashboard?station=bharati'
curl 'http://localhost:8000/api/forecast/load?station=bharati&horizon=24'
```

## Run frontend

```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

Open `http://localhost:5173`.

## ML

The `ml/` folder is the previously implemented AURORA forecasting package. It contains the XGBoost load model and renewable physics models plus their development artifacts.

## Important limitation

The ML package uses physically constrained synthetic station load data for development. Do not present it as measured Bharati/Maitri telemetry. Replace/augment the weather and load inputs with authoritative station data when available.

# AURORA — SIH26061 Frontend

AURORA is the frontend command center for **AI-Driven Smart Energy Management System for Polar Research Stations**.

## Frontend architecture

```text
src/
├── components/
│   ├── charts/       # Recharts-based forecast, dispatch, battery and analytics visuals
│   ├── common/       # Reusable cards, headers, alerts, status pills and toast
│   ├── energy/       # Energy-flow, battery, fuel and system-health widgets
│   └── layout/       # Topbar, sidebar and application shell
├── data/             # Demo station telemetry and UI configuration
├── hooks/            # React hooks used by the UI
├── pages/            # Product modules / screens
├── services/         # Backend API integration layer with mock fallback
├── App.jsx           # Route-like module switcher and global state
├── main.jsx          # React entry point
└── styles.css        # AURORA visual system
```

## Product screens

- Overview / Energy Command Center
- Live Monitor
- Energy Flow
- Forecasting
- Optimization
- Fuel Management
- Battery Management
- Reports & Analytics
- Alerts & Events
- Settings
- Help & Documentation

## Run locally

```bash
npm install
npm run dev
```

The UI starts in simulation mode by default. To connect the FastAPI backend later, copy `.env.example` to `.env` and set:

```text
VITE_API_BASE_URL=http://localhost:8000
VITE_USE_MOCK=false
```

Expected backend endpoints already referenced by the frontend:

```text
GET  /api/dashboard
POST /api/optimization/run
GET  /api/forecast/load
```

## Design direction

Dark polar-tech command center, cyan/green energy signals, high-contrast operational metrics, dense analytical cards, and operator-first controls. The interface is intentionally designed around the AURORA system architecture: prediction → optimization → simulation → operator decision.

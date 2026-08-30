# AURORA Frontend + FastAPI Integration

The frontend now uses `src/services/api.js` to communicate with the backend.

Default development settings:

```env
VITE_API_BASE_URL=http://localhost:8000
VITE_USE_MOCK=false
```

The dashboard refreshes every 15 seconds and the forecasting workspace consumes the ML-backed endpoints.

const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL || '').replace(/\/$/, '');
const USE_MOCK = String(import.meta.env.VITE_USE_MOCK ?? 'true').toLowerCase() === 'true';

async function request(path, options = {}) {
  if (USE_MOCK || !API_BASE_URL) return null;
  const response = await fetch(`${API_BASE_URL}${path}`, { headers: { 'Content-Type': 'application/json', ...(options.headers || {}) }, ...options });
  if (!response.ok) throw new Error(`AURORA API error: ${response.status}`);
  return response.json();
}

export const api = {
  async getDashboard() {
    const live = await request('/api/dashboard');
    return live || { loadKw: 187, batterySoc: 72, fuelLitres: 218400, renewablePct: 41, daysToExhaustion: 174 };
  },
  async runOptimization({ station, mode, horizon }) {
    const live = await request('/api/optimization/run', { method: 'POST', body: JSON.stringify({ station, mode, horizon }) });
    if (live) return live;
    await new Promise((resolve) => setTimeout(resolve, 900));
    return { station, mode, horizon, fuelSavedLitres: 184, reliability: 99.98, renewableUtilization: 41 };
  },
  async getForecasts() {
    const live = await request('/api/forecast/load');
    return live || {};
  },
};

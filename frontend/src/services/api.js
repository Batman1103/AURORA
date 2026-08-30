const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000').replace(/\/$/, '');
const USE_MOCK = String(import.meta.env.VITE_USE_MOCK ?? 'false').toLowerCase() === 'true';

const mockDashboard = {station:'bharati',loadKw:187,batterySoc:72,fuelLitres:218400,renewablePct:41,daysToExhaustion:174,solarKw:42,windKw:61,thermalKw:112,mode:'Normal',model:'XGBoost',metrics:{mae_kw:16.12,rmse_kw:20.08,mape_pct:5.81,r2:0.713}};

async function request(path, options = {}) {
  if (USE_MOCK) return null;
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers: {'Content-Type':'application/json', ...(options.headers || {})},
  });
  if (!response.ok) throw new Error(`AURORA API error ${response.status}`);
  return response.json();
}

export const api = {
  async getDashboard(station = 'bharati') {
    const data = await request(`/api/dashboard?station=${encodeURIComponent(station)}`);
    return data || mockDashboard;
  },
  async getForecasts(station = 'bharati', horizon = 24) {
    const [load, renewable] = await Promise.all([
      request(`/api/forecast/load?station=${encodeURIComponent(station)}&horizon=${horizon}`),
      request(`/api/forecast/renewable?station=${encodeURIComponent(station)}&horizon=${horizon}`),
    ]);
    if (load && renewable) return {load, renewable};
    return {load:null, renewable:null};
  },
  async getEnergyLive(station = 'bharati') {
    return request(`/api/energy/live?station=${encodeURIComponent(station)}`);
  },
  async getFuelStatus(station = 'bharati') {
    return request(`/api/fuel/status?station=${encodeURIComponent(station)}`);
  },
  async getBatteryStatus(station = 'bharati') {
    return request(`/api/battery/status?station=${encodeURIComponent(station)}`);
  },
  async getAlerts(station = 'bharati') {
    return request(`/api/alerts?station=${encodeURIComponent(station)}`);
  },
  async runOptimization({station, mode, horizon}) {
    const data = await request('/api/optimization/run', {method:'POST', body:JSON.stringify({station: station.toLowerCase().split(' ')[0], mode, horizon})});
    if (data) return {
      ...data,
      fuelSavedLitres: data.fuel_saved_litres,
      renewableUtilization: data.renewable_utilization,
    };
    await new Promise(resolve => setTimeout(resolve, 700));
    return {station,mode,horizon,fuelSavedLitres:184,reliability:99.98,renewableUtilization:41};
  },
  async runScenario({station, scenario, batterySoc, fuelLitres}) {
    return request('/api/simulation/scenario', {method:'POST', body:JSON.stringify({station: station.toLowerCase().split(' ')[0], scenario, battery_soc:batterySoc, fuel_litres:fuelLitres})});
  }
};

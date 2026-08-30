export const COLORS = {
  cyan: '#68dcff', cyan2: '#00b7ff', green: '#66e6a5', lime: '#c9ff73', orange: '#ffad5c', red: '#ff6e87', purple: '#b48cff', white: '#edf7ff', muted: '#7995ac',
};

export const hourly = [
  { t: '00', actual: 172, forecast: 178, solar: 0, wind: 54 },
  { t: '03', actual: 165, forecast: 171, solar: 0, wind: 61 },
  { t: '06', actual: 181, forecast: 186, solar: 22, wind: 57 },
  { t: '09', actual: 209, forecast: 214, solar: 48, wind: 60 },
  { t: '12', actual: 223, forecast: 228, solar: 66, wind: 73 },
  { t: '15', actual: 217, forecast: 221, solar: 58, wind: 69 },
  { t: '18', actual: 234, forecast: 228, solar: 31, wind: 67 },
  { t: '21', actual: 191, forecast: 197, solar: 0, wind: 62 },
  { t: '00', actual: null, forecast: 205, solar: 0, wind: 58 },
  { t: '03', actual: null, forecast: 188, solar: 0, wind: 52 },
  { t: '06', actual: null, forecast: 198, solar: 18, wind: 59 },
  { t: '09', actual: null, forecast: 217, solar: 42, wind: 71 },
  { t: '12', actual: null, forecast: 231, solar: 72, wind: 79 },
  { t: '15', actual: null, forecast: 238, solar: 64, wind: 76 },
  { t: '18', actual: null, forecast: 225, solar: 36, wind: 68 },
  { t: '21', actual: null, forecast: 204, solar: 0, wind: 59 },
];

export const optimizationData = [
  { label: 'Renewables', value: 41, fill: COLORS.green },
  { label: 'Battery', value: 24, fill: COLORS.cyan },
  { label: 'Diesel/CHP', value: 29, fill: COLORS.orange },
  { label: 'Load shift', value: 6, fill: COLORS.purple },
];

export const navItems = [
  ['Overview', 'Grid2X2'], ['Live Monitor', 'Activity'], ['Energy Flow', 'GitBranch'], ['Forecasting', 'LineChart'], ['Optimization', 'BrainCircuit'], ['Fuel Management', 'Gauge'], ['Battery Management', 'BatteryCharging'], ['Reports & Analytics', 'Database'], ['Alerts & Events', 'Bell'], ['Settings', 'Settings'], ['Help & Documentation', 'CircleHelp'],
];

export const statusItems = [
  ['Generators', '1 / 3 running', 'ok', 'Server'], ['Solar system', 'Operational', 'ok', 'Sun'], ['Wind system', 'Operational', 'ok', 'Wind'], ['Battery system', 'Operational', 'ok', 'BatteryCharging'], ['Thermal / CHP', 'Operational', 'ok', 'ThermometerSnowflake'], ['Weather station', 'Operational', 'ok', 'CloudSun'],
];

export const pageSubtitles = {
  'Live Monitor': 'Real-time telemetry and component status.',
  'Energy Flow': 'Trace power generation, storage, and consumption.',
  'Forecasting': 'AI demand and renewable prediction workspace.',
  'Optimization': 'Constraint-aware dispatch and fuel minimization.',
  'Fuel Management': 'Strategic fuel reserve and risk forecasting.',
  'Battery Management': 'State-of-charge, health, and dispatch trajectory.',
  'Reports & Analytics': 'Historical KPIs and baseline comparisons.',
  'Alerts & Events': 'Warnings, events, maintenance, and audit trail.',
  Settings: 'Station policy and model behavior controls.',
  'Help & Documentation': 'Architecture, workflows, and operator guidance.',
};

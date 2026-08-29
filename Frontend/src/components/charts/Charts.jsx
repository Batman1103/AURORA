import React from 'react';
import { Area, AreaChart, Bar, BarChart, CartesianGrid, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';
import { COLORS, hourly } from '../../data/mockData';

export function ChartTooltip({ active, payload, label, unit }) {
  if (!active || !payload?.length) return null;
  return <div className="chart-tooltip"><strong>{label}:00</strong>{payload.map((p) => <div key={p.dataKey}><span>{p.dataKey}</span><b>{p.value}{unit}</b></div>)}</div>;
}

export function LoadForecastChart() {
  return <div className="chart-box large"><ResponsiveContainer width="100%" height="100%"><AreaChart data={hourly} margin={{ top: 6, right: 4, left: -20, bottom: 0 }}>
    <defs><linearGradient id="forecastFill" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stopColor={COLORS.cyan} stopOpacity={0.25}/><stop offset="100%" stopColor={COLORS.cyan} stopOpacity={0}/></linearGradient></defs>
    <CartesianGrid stroke="#173148" strokeDasharray="3 4" vertical={false} /><XAxis dataKey="t" tick={{ fill: '#64839d', fontSize: 10 }} axisLine={false} tickLine={false} /><YAxis domain={[100, 300]} ticks={[100, 200, 300]} tick={{ fill: '#64839d', fontSize: 10 }} axisLine={false} tickLine={false} unit=" kW" />
    <Tooltip content={<ChartTooltip unit="kW" />} /><Area type="monotone" dataKey="forecast" stroke={COLORS.cyan} strokeWidth={2.2} fill="url(#forecastFill)" dot={false} /><Line type="monotone" dataKey="actual" stroke="#d7e9f5" strokeWidth={1.2} dot={false} connectNulls={false} />
  </AreaChart></ResponsiveContainer><div className="chart-footer"><span><i className="legend-line cyan" /> Forecast</span><span><i className="legend-line white" /> Actual</span><span className="chart-note">MAE 8.6 kW · 96.1% confidence</span></div></div>;
}

export function RenewableChart({ mode = 'Solar', data }) {
  const points = data || hourly.map(d => ({ t: d.t, value: mode === 'Solar' ? d.solar : d.wind }));
  const stroke = mode === 'Solar' ? '#ffd469' : COLORS.cyan;
  return <div className="chart-box"><ResponsiveContainer width="100%" height="100%"><LineChart data={points} margin={{ top: 12, right: 4, left: -20, bottom: 0 }}>
    <defs><linearGradient id={`renewFill-${mode}`} x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stopColor={stroke} stopOpacity={0.22}/><stop offset="100%" stopColor={stroke} stopOpacity={0}/></linearGradient></defs>
    <CartesianGrid stroke="#173148" strokeDasharray="3 4" vertical={false} /><XAxis dataKey="t" tick={{ fill: '#64839d', fontSize: 10 }} axisLine={false} tickLine={false} /><YAxis ticks={[0, 40, 80]} tick={{ fill: '#64839d', fontSize: 10 }} axisLine={false} tickLine={false} unit=" kW" /><Tooltip content={<ChartTooltip unit="kW" />} /><Area type="monotone" dataKey="value" stroke={stroke} fill={`url(#renewFill-${mode})`} strokeWidth={2.2} dot={false} />
  </LineChart></ResponsiveContainer><div className="chart-footer"><span>{mode === 'Solar' ? <><i className="legend-line solar" /> Solar forecast</> : <><i className="legend-line cyan" /> Wind forecast</>}</span><span className="chart-note">Weather model · ERA5 + station telemetry</span></div></div>;
}

export function BatteryChart() {
  const d = hourly.map((v,i)=>({t:v.t, soc: Math.max(28,72 + Math.sin(i*.7)*11 - i*.9)}));
  return <div className="chart-box"><ResponsiveContainer width="100%" height="100%"><AreaChart data={d} margin={{left:-20,right:5}}><defs><linearGradient id="socFill" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stopColor={COLORS.cyan} stopOpacity={0.25}/><stop offset="100%" stopColor={COLORS.cyan} stopOpacity={0}/></linearGradient></defs><CartesianGrid stroke="#173148" strokeDasharray="3 4" vertical={false}/><XAxis dataKey="t" tick={{fill:'#69879c',fontSize:10}} axisLine={false} tickLine={false}/><YAxis domain={[20,100]} ticks={[20,50,80]} tick={{fill:'#69879c',fontSize:10}} axisLine={false} tickLine={false}/><Tooltip content={<ChartTooltip unit="%"/>}/><Area dataKey="soc" stroke={COLORS.cyan} fill="url(#socFill)" strokeWidth={2.2} dot={false}/></AreaChart></ResponsiveContainer></div>;
}

export function DispatchBars() {
  const data = [
    { h: '11:00', wind: 58, solar: 49, battery: 31, diesel: 49 }, { h: '12:00', wind: 62, solar: 66, battery: 18, diesel: 34 }, { h: '13:00', wind: 66, solar: 72, battery: 0, diesel: 28 }, { h: '14:00', wind: 63, solar: 67, battery: 0, diesel: 35 }, { h: '15:00', wind: 59, solar: 56, battery: 12, diesel: 37 }, { h: '16:00', wind: 57, solar: 38, battery: 28, diesel: 46 },
  ];
  return <div className="dispatch-wrap"><div className="dispatch-legend"><span><i className="legend-dot cyan"/>Wind</span><span><i className="legend-dot green"/>Solar</span><span><i className="legend-dot purple"/>Battery</span><span><i className="legend-dot orange"/>Diesel</span></div><ResponsiveContainer width="100%" height={290}><BarChart data={data} margin={{ left: -20, right: 8 }}><CartesianGrid stroke="#173148" strokeDasharray="3 4" vertical={false}/><XAxis dataKey="h" tick={{fill:'#69879c',fontSize:10}} axisLine={false} tickLine={false}/><YAxis tick={{fill:'#69879c',fontSize:10}} axisLine={false} tickLine={false}/><Tooltip content={<ChartTooltip unit=" kW"/>}/><Bar dataKey="wind" stackId="a" fill={COLORS.cyan}/><Bar dataKey="solar" stackId="a" fill={COLORS.green}/><Bar dataKey="battery" stackId="a" fill={COLORS.purple}/><Bar dataKey="diesel" stackId="a" fill={COLORS.orange} radius={[4,4,0,0]}/></BarChart></ResponsiveContainer></div>;
}

export function FuelRiskChart() {
  const d = Array.from({ length: 13 }, (_, i) => ({ day: `${i * 15}`, normal: 218 - i * 15.4 + (i > 8 ? i * 0.7 : 0), conserved: 218 - i * 12.1 + (i > 8 ? i * 0.25 : 0) }));
  return <div className="chart-box"><ResponsiveContainer width="100%" height="100%"><LineChart data={d} margin={{left:-20,right:5}}><CartesianGrid stroke="#173148" strokeDasharray="3 4" vertical={false}/><XAxis dataKey="day" tick={{fill:'#69879c',fontSize:10}} axisLine={false} tickLine={false}/><YAxis tick={{fill:'#69879c',fontSize:10}} axisLine={false} unit="kL"/><Tooltip content={<ChartTooltip unit=" kL"/>}/><Line dataKey="normal" stroke={COLORS.orange} strokeWidth={2} dot={false}/><Line dataKey="conserved" stroke={COLORS.green} strokeWidth={2.2} strokeDasharray="5 5" dot={false}/></LineChart></ResponsiveContainer><div className="chart-footer"><span><i className="legend-line orange"/> Baseline</span><span><i className="legend-line green"/> AURORA conservative</span></div></div>;
}

export function EnergyMixChart() {
  const d=[{m:'Mar',baseline:31,aurora:42},{m:'Apr',baseline:30,aurora:39},{m:'May',baseline:29,aurora:44},{m:'Jun',baseline:27,aurora:41},{m:'Jul',baseline:26,aurora:43},{m:'Aug',baseline:24,aurora:41}];
  return <div className="chart-box"><ResponsiveContainer width="100%" height="100%"><BarChart data={d} margin={{left:-20,right:5}}><CartesianGrid stroke="#173148" strokeDasharray="3 4" vertical={false}/><XAxis dataKey="m" tick={{fill:'#69879c',fontSize:10}} axisLine={false} tickLine={false}/><YAxis tick={{fill:'#69879c',fontSize:10}} axisLine={false} tickLine={false} unit="%"/><Tooltip content={<ChartTooltip unit="%"/>}/><Bar dataKey="baseline" fill="#37516a" radius={[4,4,0,0]}/><Bar dataKey="aurora" fill={COLORS.green} radius={[4,4,0,0]}/></BarChart></ResponsiveContainer><div className="chart-footer"><span><i className="legend-dot" style={{background:'#37516a'}}/>Baseline</span><span><i className="legend-dot green"/>AURORA optimized</span></div></div>;
}

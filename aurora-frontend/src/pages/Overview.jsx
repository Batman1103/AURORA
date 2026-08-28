import React, { useMemo, useState } from 'react';
import { Activity, AlertTriangle, BatteryCharging, Bell, BrainCircuit, CalendarClock, CloudSun, Gauge, GitBranch, Leaf, LineChart, Power, Server, ShieldCheck, Sparkles, TrendingUp, Zap, ThermometerSnowflake } from 'lucide-react';
import PanelHeader from '../components/common/PanelHeader';
import MetricCard from '../components/common/MetricCard';
import MiniStat from '../components/common/MiniStat';
import AlertCard from '../components/common/AlertCard';
import EnergyFlow from '../components/energy/EnergyFlow';
import StatusList from '../components/energy/StatusList';
import FuelGauge from '../components/energy/FuelGauge';
import OptimizationDonut from '../components/energy/OptimizationDonut';
import { LoadForecastChart, RenewableChart } from '../components/charts/Charts';
import { hourly } from '../data/mockData';

export default function Overview({ systemMode, setSystemMode, horizon, setHorizon, onRunOptimization, running, lastOptimization, setToast }) {
  const [forecastMode, setForecastMode] = useState('Solar');
  const forecastSeries = useMemo(() => hourly.map(d=>({t:d.t,value:forecastMode === 'Solar' ? d.solar : d.wind})), [forecastMode]);
  const exportReport = () => setToast({type:'info', text:'Report queued: dispatch, fuel risk, and KPI summary.'});
  return <>
    <section className="kpi-grid">
      <MetricCard title="DAYS UNTIL FUEL EXHAUSTION" value="174" unit="days" hint="Projected 18 Feb 2027" delta="+12 days" icon={<Gauge size={18}/>} tone="green" />
      <MetricCard title="FUEL REMAINING" value="218,400" unit="L" hint="62% of tank capacity" delta="−1,250 L today" icon={<Power size={18}/>} tone="orange" progress={62} />
      <MetricCard title="RENEWABLE CONTRIBUTION" value="41" unit="%" hint="Today's blended share" delta="+8.2 pp vs baseline" icon={<Leaf size={18}/>} tone="green" />
      <MetricCard title="BATTERY STATE OF CHARGE" value="72" unit="%" hint="Discharging at 48 kW" delta="+3% / 6h" icon={<BatteryCharging size={18}/>} tone="cyan" progress={72} />
      <MetricCard title="CURRENT LOAD" value="187" unit="kW" hint="Total station consumption" delta="−4.8% vs forecast" icon={<Activity size={18}/>} tone="purple" />
    </section>
    <section className="main-grid">
      <div className="panel energy-panel span-7"><PanelHeader title="LIVE ENERGY FLOW" subtitle="Station power balance · 10:24 AM" icon={<GitBranch size={16}/>}/><EnergyFlow/></div>
      <div className="panel span-5 forecast-panel"><PanelHeader title="LOAD FORECAST" subtitle="Next 48 hours · AI prediction" icon={<LineChart size={16}/>} action={<span className="ai-badge"><Sparkles size={12}/> XGBoost</span>}/><LoadForecastChart/></div>
      <div className="panel span-5"><PanelHeader title="RENEWABLE FORECAST" subtitle="Weather-aware generation" icon={<CloudSun size={16}/>} action={<div className="segmented mini"><button className={forecastMode==='Solar'?'selected':''} onClick={()=>setForecastMode('Solar')}>Solar</button><button className={forecastMode==='Wind'?'selected':''} onClick={()=>setForecastMode('Wind')}>Wind</button></div>}/><RenewableChart data={forecastSeries} mode={forecastMode}/></div>
      <div className="panel span-7 optimization-panel"><PanelHeader title="ENERGY OPTIMIZATION · TODAY" subtitle="Dispatch strategy vs baseline" icon={<BrainCircuit size={16}/>} action={<div className="live-label"><span className="live-dot"/> SIMULATION</div>}/><div className="optimization-layout"><OptimizationDonut/><div className="optimization-metrics"><div className="opt-row"><span><i className="legend-dot green"/>Renewables used</span><strong>41%</strong></div><div className="opt-row"><span><i className="legend-dot cyan"/>Battery discharge</span><strong>24%</strong></div><div className="opt-row"><span><i className="legend-dot orange"/>Diesel / CHP</span><strong>29%</strong></div><div className="opt-row"><span><i className="legend-dot purple"/>Load shifted</span><strong>6%</strong></div><div className="divider"/><div className="compare-grid"><MiniStat label="Fuel saved" value="184 L" trend="+12.4%" good/><MiniStat label="CO₂ avoided" value="483 kg" trend="+9.1%" good/><MiniStat label="Cost saved" value="₹23.6k" trend="Today"/><MiniStat label="Reliability" value="99.98%" trend="Critical load" good/></div></div></div></div>
      <div className="panel span-4 fuel-panel"><PanelHeader title="FUEL RESILIENCE" subtitle="Strategic reserve outlook" icon={<Gauge size={16}/>}/><FuelGauge/><div className="fuel-cells"><div><span>Avg/day</span><strong>1,250 L</strong></div><div><span>Projected need</span><strong>245k L</strong></div></div><div className="risk-banner"><AlertTriangle size={15}/><div><strong>Reserve watch active</strong><span>Conservation mode at &lt; 30k L buffer.</span></div></div></div>
      <div className="panel span-4 status-panel"><PanelHeader title="SYSTEM STATUS" subtitle="Component health" icon={<Server size={16}/>}/><StatusList/></div>
      <div className="panel span-4 alerts-panel"><PanelHeader title="ACTIVE ALERTS" subtitle="2 events need attention" icon={<Bell size={16}/>} action={<button className="text-btn">View all</button>}/><AlertCard severity="warning" title="High fuel consumption" body="12% above optimal operating range." time="10:15 AM" onClick={()=>setToast({type:'warning',text:'Generator 1 is 14% above optimal; AURORA recommends a load shift.'})}/><AlertCard severity="info" title="Polar night approaching" body="Solar generation expected to drop 31% over 35 days." time="09:40 AM" onClick={()=>setToast({type:'info',text:'AURORA recommends increasing wind utilization and battery reserve.'})}/><div className="maintenance-strip"><CalendarClock size={14}/><span>Generator 2 service</span><b>in 2 days</b></div></div>
    </section>
    <section className="control-bar"><div className="mode-control"><span className="control-label">SYSTEM MODE</span><div className="segmented"><button className={systemMode==='Normal'?'selected':''} onClick={()=>setSystemMode('Normal')}>Normal</button><button className={systemMode==='Fuel Conservation'?'selected warning':''} onClick={()=>setSystemMode('Fuel Conservation')}>Fuel Conservation</button><button className={systemMode==='Emergency'?'selected danger':''} onClick={()=>setSystemMode('Emergency')}>Emergency</button></div></div><div className="horizon-control"><span className="control-label">OPTIMIZATION HORIZON</span><div className="segmented"><button className={horizon==='24 Hours'?'selected':''} onClick={()=>setHorizon('24 Hours')}>24 Hours</button><button className={horizon==='7 Days'?'selected':''} onClick={()=>setHorizon('7 Days')}>7 Days</button><button className={horizon==='30 Days'?'selected':''} onClick={()=>setHorizon('30 Days')}>30 Days</button><button className={horizon==='180 Days'?'selected':''} onClick={()=>setHorizon('180 Days')}>180 Days</button></div></div><div className="run-control"><div className="last-run">LAST OPTIMIZATION <b>{lastOptimization}</b></div><button className={`primary-btn ${running?'busy':''}`} onClick={onRunOptimization}>{running?<><Sparkles className="spin" size={15}/> Optimizing…</>:<><Sparkles size={15}/> Run optimization</>}</button><button className="ghost-btn" onClick={exportReport}>Export snapshot</button></div></section>
    <div className="footer-note"><span><ShieldCheck size={13}/> Control actions are simulation-safe</span><span>Model confidence 96.4% · Data quality 99.1%</span></div>
  </>;
}

import React from 'react';
import { ArrowDown, BatteryCharging, GitBranch, Server, Sun, ThermometerSnowflake, Wind, Zap } from 'lucide-react';

export function EnergyNode({ label, value, sub, icon, tone }) { return <div className={`energy-node ${tone}`}><div className="node-icon">{icon}</div><div><div className="node-label">{label}</div><strong>{value}</strong><span>{sub}</span></div></div>; }
export function ArrowFlow({ tone }) { return <div className={`arrow-flow ${tone}`}><span /><ArrowDown size={15} /></div>; }
export default function EnergyFlow({ dashboard }) {
  const solar = dashboard?.solarKw ?? 42;
  const wind = dashboard?.windKw ?? 61;
  const load = dashboard?.loadKw ?? 187;
  const battery = dashboard?.batterySoc ?? 72;
  const diesel = Math.max(0, load - solar - wind);
  const thermal = dashboard?.thermalKw ?? 112;
  return <div className="energy-flow-wrap"><div className="flow-map">
    <EnergyNode label="SOLAR ARRAY" value={`${solar.toFixed(0)} kW`} sub="48 panels active" icon={<Sun size={21}/>} tone="green"/><ArrowFlow tone="green"/>
    <EnergyNode label="WIND FARM" value={`${wind.toFixed(0)} kW`} sub="9 turbines · 64%" icon={<Wind size={21}/>} tone="green"/><ArrowFlow tone="green"/>
    <EnergyNode label="DIESEL / CHP" value={`${diesel.toFixed(0)} kW`} sub="GEN 1 · 87% load" icon={<Server size={21}/>} tone="orange"/>
    <div className="flow-core"><div className="core-ring"/><div className="core-inner"><Zap size={19}/><strong>187</strong><span>kW LOAD</span></div></div>
    <div className="side-flow battery"><EnergyNode label="BATTERY" value={`${battery.toFixed(0)}%`} sub="−48 kW discharge" icon={<BatteryCharging size={21}/>} tone="cyan"/></div>
    <div className="side-flow thermal"><EnergyNode label="THERMAL / CHP" value={`${thermal.toFixed(0)} kWth`} sub="Heating demand" icon={<ThermometerSnowflake size={21}/>} tone="orange"/></div>
  </div><div className="flow-legend"><span><i className="legend-line green"/> Generation</span><span><i className="legend-line cyan"/> Battery</span><span><i className="legend-line orange"/> Thermal</span><span><i className="legend-line purple"/> Forecasted</span></div></div>;
}

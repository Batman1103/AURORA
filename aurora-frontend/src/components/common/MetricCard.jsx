import React from 'react';
export default function MetricCard({ title, value, unit, hint, delta, icon, tone, progress }) {
  return <div className={`metric-card tone-${tone}`}>
    <div className="metric-top"><span>{title}</span><div className="metric-icon">{icon}</div></div>
    <div className="metric-value">{value}<small>{unit}</small></div>
    <div className="metric-bottom"><span>{hint}</span><b>{delta}</b></div>
    {progress != null && <div className="progress"><span style={{ width: `${progress}%` }} /></div>}
  </div>;
}

import React from 'react';
export default function PanelHeader({ title, subtitle, icon, action }) {
  return <div className="panel-head"><div className="panel-title"><span className="section-icon">{icon}</span><div><h2>{title}</h2><p>{subtitle}</p></div></div>{action}</div>;
}

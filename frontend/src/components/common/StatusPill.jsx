import React from 'react';
export default function StatusPill({ icon, label, value, tone }) { return <div className={`status-pill ${tone}`}><span>{icon}</span><div><small>{label}</small><b>{value}</b></div></div>; }

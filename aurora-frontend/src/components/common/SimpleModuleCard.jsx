import React from 'react';
export default function SimpleModuleCard({ icon, title, value, note }) { return <div className="module-mini-card"><div className="module-mini-icon">{icon}</div><div><span>{title}</span><strong>{value}</strong><small>{note}</small></div></div>; }

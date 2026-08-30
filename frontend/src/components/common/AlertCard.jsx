import React from 'react';
import { AlertTriangle, ArrowUpRight, Moon } from 'lucide-react';
export default function AlertCard({ severity, title, body, time, onClick }) {
  return <button className={`alert-card ${severity}`} onClick={onClick}><div className="alert-icon">{severity === 'warning' ? <AlertTriangle size={15} /> : <Moon size={15} />}</div><div className="alert-copy"><div><strong>{title}</strong><span>{time}</span></div><p>{body}</p><span className="view-detail">View details <ArrowUpRight size={11} /></span></div></button>;
}

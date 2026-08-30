import React from 'react';
import * as Icons from 'lucide-react';
import { navItems } from '../../data/mockData';

export default function Sidebar({ active, onNavigate }) {
  return <aside className="sidebar"><div className="side-scroll"><div className="nav-caption">COMMAND CENTER</div>{navItems.map(([label, iconName]) => {
    const Icon = Icons[iconName] || Icons.Circle;
    return <button key={label} className={`nav-item ${active === label ? 'active' : ''}`} onClick={() => onNavigate(label)}><Icon size={17} strokeWidth={1.8} /><span>{label}</span></button>;
  })}</div><div className="side-footer"><div className="ai-card"><div className="ai-head"><span className="ai-pulse" /><span>AURORA AI</span><Icons.Bot size={16} /></div><div className="ai-status">Models online · 4/4</div><div className="ai-bars"><span /><span /><span /><span /><span /><span /><span /><span /></div></div><div className="station-footer"><Icons.ShieldCheck size={14} /> Secure control layer enabled</div></div></aside>;
}

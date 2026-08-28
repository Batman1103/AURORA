import React from 'react';
import { Bell, ChevronDown, Globe2, Menu, Radio, Sun } from 'lucide-react';
import StatusPill from '../common/StatusPill';

export default function Topbar({ station, setStation, menuOpen, setMenuOpen }) {
  return <header className="topbar">
    <div className="brand-block"><button className="mobile-menu" onClick={() => setMenuOpen(!menuOpen)}><Menu size={19} /></button><div className="brand-mark"><span className="brand-glyph">A</span></div><div><div className="brand-name">AURORA</div><div className="brand-sub">AI ENERGY INTELLIGENCE</div></div></div>
    <div className="station-selector"><div className="station-icon"><Globe2 size={17} /></div><select value={station} onChange={(e) => setStation(e.target.value)} aria-label="Research station"><option>Bharati Station</option><option>Maitri Station</option><option>Maitri-II Simulation</option></select><ChevronDown size={15} className="select-chevron" /></div>
    <div className="top-actions"><StatusPill icon={<Radio size={15} />} label="SYSTEM" value="NORMAL" tone="success" /><div className="weather-pill"><div className="weather-icon"><Sun size={18} /></div><div><div className="weather-temp">−18.6°C</div><div className="weather-copy">Clear sky · 12 m/s</div></div></div><div className="top-time"><div>10:24 AM</div><span>28 AUG 2026</span></div><button className="icon-btn notification"><Bell size={18} /><span className="dot" /></button><button className="avatar">AR</button></div>
  </header>;
}

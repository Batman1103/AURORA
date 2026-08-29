import React from 'react';
import { Download, RefreshCw } from 'lucide-react';
import { pageSubtitles } from '../../data/mockData';
import Sidebar from './Sidebar';
import Topbar from './Topbar';
import Toast from '../common/Toast';

export default function AppShell({ active, onNavigate, station, setStation, menuOpen, setMenuOpen, toast, children, onExport }) {
  return <div className="app-shell"><div className="ambient ambient-a" /><div className="ambient ambient-b" /><div className="grid-overlay" />
    <Topbar station={station} setStation={setStation} menuOpen={menuOpen} setMenuOpen={setMenuOpen} />
    <div className={`workspace ${menuOpen ? 'menu-active' : ''}`}><Sidebar active={active} onNavigate={(label) => { onNavigate(label); setMenuOpen(false); }} />
      <main className="content"><div className="page-head"><div><div className="eyebrow">{active === 'Overview' ? 'STATION OVERVIEW' : 'AURORA MODULE'}</div><h1>{active === 'Overview' ? 'Energy Command Center' : active}</h1><p>{active === 'Overview' ? 'AI-guided dispatch, fuel resilience, and renewable coordination.' : pageSubtitles[active]}</p></div><div className="head-actions"><div className="sync-chip"><RefreshCw size={13} /> Data synced 58s ago</div><button className="ghost-btn" onClick={onExport}><Download size={15} /> Export</button></div></div>{children}</main>
    </div><Toast toast={toast} />
  </div>;
}

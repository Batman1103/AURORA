import React, { useState } from 'react';
import { api } from './services/api';
import { pageSubtitles } from './data/mockData';
import AppShell from './components/layout/AppShell';
import EnergyFlow from './components/energy/EnergyFlow';
import Overview from './pages/Overview';
import { LiveMonitor, EnergyFlowPage, Forecasting, Optimization, FuelManagement, BatteryManagement, Reports, Alerts, SettingsPage, HelpPage } from './pages/ModulePages';

export default function App(){
  const [active,setActive]=useState('Overview');
  const [station,setStation]=useState('Bharati Station');
  const [systemMode,setSystemMode]=useState('Normal');
  const [horizon,setHorizon]=useState('24 Hours');
  const [running,setRunning]=useState(false);
  const [lastOptimization,setLastOptimization]=useState('Today, 09:45 AM');
  const [toast,setToast]=useState(null);
  const [menuOpen,setMenuOpen]=useState(false);

  const runOptimization=async()=>{
    if(running) return;
    setRunning(true);
    setToast({type:'info',text:`AURORA is optimizing ${horizon.toLowerCase()} in ${systemMode.toLowerCase()} mode…`});
    const result=await api.runOptimization({station,mode:systemMode,horizon});
    setRunning(false); setLastOptimization('Just now');
    setToast({type:'success',text:`Optimization complete · ${result.fuelSavedLitres} L fuel saving opportunity identified.`});
  };
  const content={
    Overview:<Overview systemMode={systemMode} setSystemMode={setSystemMode} horizon={horizon} setHorizon={setHorizon} onRunOptimization={runOptimization} running={running} lastOptimization={lastOptimization} setToast={setToast}/>,
    'Live Monitor':<LiveMonitor/>,
    'Energy Flow':<EnergyFlowPage EnergyFlow={EnergyFlow}/>,
    Forecasting:<Forecasting/>,
    Optimization:<Optimization runOptimization={runOptimization}/>,
    'Fuel Management':<FuelManagement/>,
    'Battery Management':<BatteryManagement/>,
    'Reports & Analytics':<Reports/>,
    'Alerts & Events':<Alerts setToast={setToast}/>,
    Settings:<SettingsPage setToast={setToast}/>,
    'Help & Documentation':<HelpPage setToast={setToast}/>,
  };
  return <AppShell active={active} onNavigate={setActive} station={station} setStation={setStation} menuOpen={menuOpen} setMenuOpen={setMenuOpen} toast={toast} onExport={()=>setToast({type:'info',text:'AURORA export package prepared.'})}>{content[active] || content.Overview}</AppShell>;
}

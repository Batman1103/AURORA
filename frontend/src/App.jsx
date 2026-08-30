import React, { useCallback, useEffect, useState } from 'react';
import { api } from './services/api';
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
  const [dashboard,setDashboard]=useState(null);
  const [forecasts,setForecasts]=useState({load:null, renewable:null});
  const [apiError,setApiError]=useState(null);
  const [optimizationResult,setOptimizationResult]=useState(null);

  const stationKey = station.toLowerCase().startsWith('maitri') ? 'maitri' : 'bharati';

  const refreshData = useCallback(async()=>{
    try {
      const [dash, fc] = await Promise.all([api.getDashboard(stationKey), api.getForecasts(stationKey, 24)]);
      setDashboard(dash);
      setForecasts(fc);
      setApiError(null);
    } catch (error) {
      setApiError(error.message);
    }
  }, [stationKey]);

  useEffect(()=>{ refreshData(); const id=setInterval(refreshData,15000); return ()=>clearInterval(id); },[refreshData]);

  const runOptimization=async()=>{
    if(running) return;
    setRunning(true);
    setToast({type:'info',text:`AURORA is optimizing ${horizon.toLowerCase()} in ${systemMode.toLowerCase()} mode…`});
    try {
      const result=await api.runOptimization({station,mode:systemMode,horizon});
      setLastOptimization('Just now');
      setOptimizationResult(result);
      setToast({type:'success',text:`Optimization complete · ${Number(result.fuelSavedLitres || 0).toFixed(1)} L fuel saving opportunity identified.`});
      await refreshData();
    } catch (error) {
      setToast({type:'error',text:`Optimization failed · ${error.message}`});
    } finally { setRunning(false); }
  };

  const content={
    Overview:<Overview dashboard={dashboard} forecasts={forecasts} optimizationResult={optimizationResult} systemMode={systemMode} setSystemMode={setSystemMode} horizon={horizon} setHorizon={setHorizon} onRunOptimization={runOptimization} running={running} lastOptimization={lastOptimization} setToast={setToast} apiError={apiError}/>,
    'Live Monitor':<LiveMonitor dashboard={dashboard}/>,
    'Energy Flow':<EnergyFlowPage EnergyFlow={EnergyFlow} dashboard={dashboard}/>,
    Forecasting:<Forecasting forecasts={forecasts} dashboard={dashboard}/>,
    Optimization:<Optimization runOptimization={runOptimization}/>,
    'Fuel Management':<FuelManagement dashboard={dashboard}/>,
    'Battery Management':<BatteryManagement dashboard={dashboard}/>,
    'Reports & Analytics':<Reports dashboard={dashboard}/>,
    'Alerts & Events':<Alerts setToast={setToast}/>,
    Settings:<SettingsPage setToast={setToast}/>,
    'Help & Documentation':<HelpPage setToast={setToast}/>,
  };

  return <AppShell active={active} onNavigate={setActive} station={station} setStation={setStation} menuOpen={menuOpen} setMenuOpen={setMenuOpen} toast={toast} onExport={()=>setToast({type:'info',text:'AURORA export package prepared.'})}>{content[active] || content.Overview}</AppShell>;
}

import React from 'react';
import { optimizationData } from '../../data/mockData';
export default function OptimizationDonut(){let cursor=0;const conic=optimizationData.map(item=>{const start=cursor;cursor+=item.value;return `${item.fill} ${start}% ${cursor}%`;}).join(', ');return <div className="donut-wrap"><div className="donut" style={{background:`conic-gradient(${conic})`}}><div className="donut-inner"><strong>4,487</strong><span>kWh optimized</span></div></div><div className="donut-caption">Dispatch mix</div></div>}

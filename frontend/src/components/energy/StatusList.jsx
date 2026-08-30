import React from 'react';
import * as Icons from 'lucide-react';
import { statusItems } from '../../data/mockData';
export default function StatusList() { return <div className="status-list">{statusItems.map(([name, value, state, iconName])=>{const Icon=Icons[iconName] || Icons.Circle; return <div className="status-row" key={name}><Icon size={15}/><span>{name}</span><strong>{value}</strong><i className={state}/></div>;})}</div>; }

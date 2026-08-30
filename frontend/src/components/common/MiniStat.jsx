import React from 'react';
import { ArrowUpRight, TrendingUp } from 'lucide-react';
export default function MiniStat({ label, value, trend, good }) { return <div className="mini-stat"><span>{label}</span><strong>{value}</strong><em className={good ? 'positive' : ''}>{good ? <TrendingUp size={11} /> : <ArrowUpRight size={11} />}{trend}</em></div>; }

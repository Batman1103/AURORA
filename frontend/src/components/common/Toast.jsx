import React from 'react';
import { CheckCircle2, Sparkles, TriangleAlert } from 'lucide-react';
export default function Toast({ toast }) {
  if (!toast) return null;
  const icon = toast.type === 'success' ? <CheckCircle2 size={18} /> : toast.type === 'info' ? <Sparkles size={18} /> : <TriangleAlert size={18} />;
  return <div className={`toast ${toast.type}`}><div className="toast-icon">{icon}</div><span>{toast.text}</span></div>;
}

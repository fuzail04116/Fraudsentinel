import { NavLink } from 'react-router-dom';
import { LayoutDashboard, Activity, AlertTriangle, Heart, RotateCcw } from 'lucide-react';
import { useModelMetrics } from '../hooks/useModelMetrics';

export default function Sidebar() {
  const { modelInfo } = useModelMetrics();
  
  const versionStr = modelInfo?.model_version || 'v2.4.1';
  const cleanVersion = versionStr.startsWith('v') ? versionStr : `v${versionStr}`;

  return (
    <aside className="sidebar">
      <div className="sidebar-logo">
        <div className="sidebar-logo-text">FraudSentinel</div>
        <div className="sidebar-logo-sub">MLOps Dashboard</div>
      </div>
      <nav className="sidebar-nav">
        <NavLink to="/" className={({isActive}) => isActive ? "nav-item active" : "nav-item"} end>
          <LayoutDashboard size={16} /> Overview
        </NavLink>
        <NavLink to="/live" className={({isActive}) => isActive ? "nav-item active" : "nav-item"}>
          <Activity size={16} /> Live Feed
        </NavLink>
        <NavLink to="/alerts" className={({isActive}) => isActive ? "nav-item active" : "nav-item"}>
          <AlertTriangle size={16} /> Alerts
        </NavLink>
        <NavLink to="/model" className={({isActive}) => isActive ? "nav-item active" : "nav-item"}>
          <Heart size={16} /> Model Health
        </NavLink>
        <NavLink to="/retrain" className={({isActive}) => isActive ? "nav-item active" : "nav-item"}>
          <RotateCcw size={16} /> Retrain
        </NavLink>
      </nav>
      <div className="sidebar-footer">
        <div>Model {cleanVersion} · XGBoost</div>
        <div>Last trained 2h ago</div>
      </div>
    </aside>
  );
}

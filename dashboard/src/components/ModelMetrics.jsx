export default function ModelMetrics({ auc, f1, precision, driftPsi }) {
  const isDriftHealthy = driftPsi < 0.2;
  
  return (
    <div className="panel">
      <h3 className="panel-title">Model Health</h3>
      
      <div className="metric-row">
        <div className="metric-header">
          <span className="metric-name">AUC-ROC</span>
          <span className="metric-val">{((auc || 0) * 100).toFixed(1)}%</span>
        </div>
        <div className="metric-bar-bg">
          <div className="metric-bar-fill" style={{ width: `${(auc || 0) * 100}%` }}></div>
        </div>
      </div>

      <div className="metric-row">
        <div className="metric-header">
          <span className="metric-name">F1 Score</span>
          <span className="metric-val">{((f1 || 0) * 100).toFixed(1)}%</span>
        </div>
        <div className="metric-bar-bg">
          <div className="metric-bar-fill" style={{ width: `${(f1 || 0) * 100}%` }}></div>
        </div>
      </div>
      
      <div className="metric-row">
        <div className="metric-header">
          <span className="metric-name">Precision</span>
          <span className="metric-val">{((precision || 0) * 100).toFixed(1)}%</span>
        </div>
        <div className="metric-bar-bg">
          <div className="metric-bar-fill" style={{ width: `${(precision || 0) * 100}%` }}></div>
        </div>
      </div>

      <div className="metric-row">
        <div className="metric-header">
          <span className="metric-name">Data Drift PSI</span>
          <span className="metric-val" style={{ color: isDriftHealthy ? 'var(--accent-green)' : 'var(--accent-red)' }}>
            {driftPsi?.toFixed(3) || '0.000'}
          </span>
        </div>
        <div className="metric-bar-bg">
          <div className="metric-bar-fill" style={{ 
            width: `${Math.min(((driftPsi || 0) / 0.5) * 100, 100)}%`,
            backgroundColor: isDriftHealthy ? 'var(--accent-green)' : 'var(--accent-red)'
          }}></div>
        </div>
      </div>
    </div>
  );
}

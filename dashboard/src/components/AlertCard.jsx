export default function AlertCard({ alert }) {
  if (!alert) return (
    <div className="alert-card" style={{ opacity: 0.5 }}>
      <div className="alert-title">⚠️ No recent alerts</div>
    </div>
  );

  return (
    <div className="alert-card">
      <div className="alert-title">⚠️ Last Fraud Alert</div>
      <div className="alert-row">
        <span className="alert-label">Transaction ID</span>
        <span className="alert-value">{alert.transaction_id?.slice(0, 12)}...</span>
      </div>
      <div className="alert-row">
        <span className="alert-label">Amount</span>
        <span className="alert-value">€{Number(alert.amount || 0).toFixed(2)}</span>
      </div>
      <div className="alert-row">
        <span className="alert-label">Confidence</span>
        <span className="alert-value">{((alert.confidence || 0) * 100).toFixed(1)}%</span>
      </div>
      <div className="alert-row">
        <span className="alert-label">Top Feature</span>
        <span className="alert-value">{alert.shap_top_feature || 'N/A'}</span>
      </div>
      <div className="alert-row">
        <span className="alert-label">Flagged At</span>
        <span className="alert-value">{new Date(alert.created_at).toLocaleTimeString()}</span>
      </div>
    </div>
  );
}

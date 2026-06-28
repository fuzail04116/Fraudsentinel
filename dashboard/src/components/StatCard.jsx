export default function StatCard({ label, value, sub, colorVariant = 'blue' }) {
  const colors = {
    blue: '#1A1A2E',
    red: '#C0392B',
    green: '#27AE60',
    amber: '#E8A87C'
  };
  
  return (
    <div className="stat-card" style={{ borderTop: `3px solid ${colors[colorVariant]}` }}>
      <div className="stat-card-label">{label}</div>
      <div className="stat-card-value">{value}</div>
      <div className="stat-card-sub">{sub}</div>
    </div>
  );
}

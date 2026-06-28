export default function FraudGauge({ fraudRate, fraudCount }) {
  const radius = 36;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (fraudRate / 100) * circumference;

  return (
    <div className="panel" style={{ textAlign: 'center' }}>
      <h3 className="panel-title">Current Fraud Rate</h3>
      <div style={{ position: 'relative', width: 120, height: 120, margin: '0 auto 16px' }}>
        <svg width="120" height="120" viewBox="0 0 80 80">
          <circle 
            cx="40" cy="40" r={radius} 
            fill="none" 
            stroke="#F0EBE0" 
            strokeWidth="8" 
          />
          <circle 
            cx="40" cy="40" r={radius} 
            fill="none" 
            stroke="#C0392B" 
            strokeWidth="8" 
            strokeDasharray={circumference} 
            strokeDashoffset={offset} 
            strokeLinecap="round"
            transform="rotate(-90 40 40)"
            style={{ transition: 'stroke-dashoffset 1s ease-out' }}
          />
        </svg>
        <div style={{ position: 'absolute', top: 0, left: 0, width: '100%', height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center', flexDirection: 'column' }}>
          <div style={{ fontFamily: 'var(--font-display)', fontSize: '20px', fontWeight: 700 }}>{fraudRate}%</div>
        </div>
      </div>
      
      <div style={{ fontFamily: 'var(--font-display)', fontSize: '32px', fontWeight: 700, color: '#C0392B' }}>{fraudCount}</div>
      <div style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>Flags Today</div>
      
      <div style={{ marginTop: '24px', textAlign: 'left' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px', fontSize: '12px' }}>
          <div style={{ width: '8px', height: '8px', backgroundColor: '#C0392B' }}></div> High-Value Target
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px', fontSize: '12px' }}>
          <div style={{ width: '8px', height: '8px', backgroundColor: '#E8A87C' }}></div> International
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '12px' }}>
          <div style={{ width: '8px', height: '8px', backgroundColor: '#F0EBE0' }}></div> Repeat Card
        </div>
      </div>
    </div>
  );
}

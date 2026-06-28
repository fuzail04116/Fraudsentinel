import { useState } from 'react';
import TopBar from '../components/TopBar';
import ShapChart from '../components/ShapChart';
import { useRealtimeTransactions } from '../hooks/useRealtimeTransactions';

export default function Alerts() {
  const { transactions } = useRealtimeTransactions();
  const [selectedTx, setSelectedTx] = useState(null);
  const [minConfidence, setMinConfidence] = useState(0.5);
  const [minAmount, setMinAmount] = useState(0);

  const alerts = transactions
    .filter(t => t.label === 1)
    .filter(t => t.confidence >= minConfidence)
    .filter(t => parseFloat(t.amount) >= minAmount);

  return (
    <div>
      <TopBar title="Fraud Alerts" />
      
      <div className="panel" style={{ padding: 0 }}>
        <div className="filters-bar" style={{ padding: '24px', display: 'flex', gap: '24px', alignItems: 'center' }}>
          <div>
            <label style={{ fontSize: '12px', fontWeight: 600, display: 'block', marginBottom: '8px' }}>Min Confidence: {(minConfidence*100).toFixed(0)}%</label>
            <input type="range" min="0.5" max="1" step="0.05" value={minConfidence} onChange={e => setMinConfidence(parseFloat(e.target.value))} />
          </div>
          <div>
            <label style={{ fontSize: '12px', fontWeight: 600, display: 'block', marginBottom: '8px' }}>Min Amount: €{minAmount}</label>
            <input type="range" min="0" max="2000" step="50" value={minAmount} onChange={e => setMinAmount(parseFloat(e.target.value))} />
          </div>
        </div>

        <table className="data-table">
          <thead>
            <tr>
              <th>Time</th>
              <th>Card</th>
              <th>Amount</th>
              <th>Confidence</th>
              <th>Top SHAP Feature</th>
              <th>SHAP Value</th>
            </tr>
          </thead>
          <tbody>
            {alerts.length === 0 && (
              <tr><td colSpan="6" style={{ textAlign: 'center', padding: '32px' }}>No alerts found matching filters.</td></tr>
            )}
            {alerts.map(tx => (
              <tr key={tx.id || tx.transaction_id} onClick={() => setSelectedTx(tx)}>
                <td>{new Date(tx.created_at).toLocaleString()}</td>
                <td>{tx.card_no || 'XXXX'}</td>
                <td style={{ color: 'var(--accent-red)', fontWeight: 600 }}>€{parseFloat(tx.amount).toFixed(2)}</td>
                <td>{(tx.confidence * 100).toFixed(1)}%</td>
                <td>{tx.shap_top_feature || 'N/A'}</td>
                <td style={{ color: tx.shap_top_value > 0 ? 'var(--accent-red)' : 'var(--accent-green)' }}>
                  {tx.shap_top_value ? tx.shap_top_value.toFixed(4) : 'N/A'}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {selectedTx && (
        <div style={{ position: 'fixed', top: 0, right: 0, width: 400, height: '100vh', backgroundColor: '#FFF', boxShadow: '-4px 0 24px rgba(0,0,0,0.1)', padding: 32, zIndex: 100, display: 'flex', flexDirection: 'column', animation: 'slideIn 300ms ease-out' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 24 }}>
            <h2 className="playfair">Fraud Analysis</h2>
            <button className="btn" onClick={() => setSelectedTx(null)}>Close</button>
          </div>
          <div style={{ marginBottom: 24 }}>
            <div style={{ fontSize: 13, color: '#888', marginBottom: 4 }}>Transaction ID</div>
            <div style={{ fontWeight: 600 }}>{selectedTx.transaction_id}</div>
          </div>
          <div style={{ display: 'flex', gap: '32px', marginBottom: 24 }}>
             <div>
                <div style={{ fontSize: 13, color: '#888', marginBottom: 4 }}>Card</div>
                <div style={{ fontWeight: 600 }}>{selectedTx.card_no || 'XXXX'}</div>
             </div>
             <div>
                <div style={{ fontSize: 13, color: '#888', marginBottom: 4 }}>Amount</div>
                <div style={{ fontWeight: 600 }}>€{parseFloat(selectedTx.amount).toFixed(2)}</div>
             </div>
          </div>
          <div style={{ marginBottom: 24 }}>
            <div style={{ fontSize: 13, color: '#888', marginBottom: 4 }}>Confidence Score</div>
            <div style={{ fontWeight: 700, color: 'var(--accent-red)', fontSize: 24 }}>{(selectedTx.confidence * 100).toFixed(1)}%</div>
          </div>
          <div>
            <h3 className="playfair" style={{ marginBottom: 16 }}>Top SHAP Features</h3>
            {selectedTx.shap_values ? (
              <ShapChart shapData={selectedTx.shap_values} />
            ) : selectedTx.shap_top_feature ? (
              <ShapChart shapData={{ [selectedTx.shap_top_feature]: selectedTx.shap_top_value }} />
            ) : (
               <div style={{color: '#888'}}>No SHAP data available</div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

import { useState } from 'react';
import TopBar from '../components/TopBar';
import TransactionRow from '../components/TransactionRow';
import ShapChart from '../components/ShapChart';
import { useRealtimeTransactions } from '../hooks/useRealtimeTransactions';

export default function LiveFeed() {
  const { transactions } = useRealtimeTransactions();
  const [selectedTx, setSelectedTx] = useState(null);

  return (
    <div>
      <TopBar title="Live Transaction Feed" />
      <div className="panel" style={{ padding: 0 }}>
        <div className="tx-list">
          {transactions.slice(0, 50).map(tx => (
            <TransactionRow 
              key={tx.id || tx.transaction_id}
              merchant={tx.merchant || "Kafka Stream Merchant"}
              cardNo={tx.card_no || "9999"}
              time={tx.created_at}
              amount={tx.amount}
              confidence={tx.confidence}
              isFraud={tx.label === 1}
              onClick={() => tx.label === 1 && setSelectedTx(tx)}
            />
          ))}
        </div>
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

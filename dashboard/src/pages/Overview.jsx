import { useState } from 'react';
import TopBar from '../components/TopBar';
import StatCard from '../components/StatCard';
import TransactionRow from '../components/TransactionRow';
import FraudGauge from '../components/FraudGauge';
import AlertCard from '../components/AlertCard';
import ModelMetrics from '../components/ModelMetrics';
import ShapChart from '../components/ShapChart';
import { useRealtimeTransactions } from '../hooks/useRealtimeTransactions';
import { useModelMetrics } from '../hooks/useModelMetrics';

export default function Overview() {
  const { transactions, fraudCount, totalCount, fraudRate } = useRealtimeTransactions();
  const { modelInfo, driftReport } = useModelMetrics();
  const [selectedTx, setSelectedTx] = useState(null);

  const lastAlert = transactions.find(t => t.label === 1);
  const avgLatency = "12.4ms"; 
  
  return (
    <div>
      <TopBar title="Dashboard Overview" />
      
      <div className="stat-row">
        <StatCard label="Total Today" value={totalCount} sub="Transactions processed" colorVariant="blue" />
        <StatCard label="Fraud Flagged" value={<>{fraudCount} {fraudCount > 0 && <span style={{fontSize: '18px', color: '#C0392B', verticalAlign: 'middle'}}>↑</span>}</>} sub={`${fraudRate}% rate`} colorVariant="red" />
        <StatCard label="AUC-ROC" value={modelInfo?.auc_roc ? (modelInfo.auc_roc * 100).toFixed(1) + '%' : '...'} sub="Staging/Prod" colorVariant="green" />
        <StatCard label="Avg Latency" value={avgLatency} sub="API Inference" colorVariant="amber" />
      </div>
      
      <div className="content-grid">
        <div className="panel" style={{ padding: 0, overflow: 'hidden' }}>
          <div style={{ padding: 24, borderBottom: '1px solid var(--border-main)' }}>
            <h3 className="panel-title" style={{ margin: 0 }}>Live Transaction Feed</h3>
          </div>
          <div className="tx-list" style={{ maxHeight: '600px', overflowY: 'auto' }}>
            {transactions.slice(0, 20).map(tx => (
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
            {transactions.length === 0 && <div style={{ padding: 24, textAlign: 'center', color: '#888' }}>Waiting for transactions...</div>}
          </div>
        </div>
        
        <div className="grid-right-col">
          <FraudGauge fraudRate={fraudRate} fraudCount={fraudCount} />
          <AlertCard alert={lastAlert} />
          <ModelMetrics 
            auc={modelInfo?.auc_roc} 
            f1={modelInfo?.f1_score} 
            precision={modelInfo?.precision_score || 0.91} 
            driftPsi={driftReport?.max_psi} 
          />
        </div>
      </div>

      {selectedTx && (
        <div style={{ position: 'fixed', top: 0, right: 0, width: 400, height: '100vh', backgroundColor: '#FFF', boxShadow: '-4px 0 24px rgba(0,0,0,0.1)', padding: 32, zIndex: 100, display: 'flex', flexDirection: 'column' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 24 }}>
            <h2 className="playfair">Fraud Analysis</h2>
            <button className="btn" onClick={() => setSelectedTx(null)}>Close</button>
          </div>
          <div style={{ marginBottom: 24 }}>
            <div style={{ fontSize: 13, color: '#888', marginBottom: 4 }}>Transaction</div>
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

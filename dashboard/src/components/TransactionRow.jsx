export default function TransactionRow({ merchant, cardNo, time, amount, confidence, isFraud, onClick }) {
  const formattedAmount = `€${Number(amount).toFixed(2)}`;
  
  return (
    <div className={`tx-row ${isFraud ? 'fraud' : 'clear'}`} onClick={onClick}>
      <div className={`tx-icon ${isFraud ? 'fraud' : 'clear'}`}>
        {isFraud ? '🚨' : '✅'}
      </div>
      <div className="tx-info">
        <div className="tx-merchant">{merchant || "Unknown Merchant"}</div>
        <div className="tx-meta">Card ••{cardNo?.slice(-4) || 'XXXX'} · {new Date(time).toLocaleTimeString()} · Confidence {(confidence*100).toFixed(0)}%</div>
      </div>
      <div className="tx-right">
        <div className={`tx-amount ${isFraud ? 'fraud' : 'clear'}`}>{formattedAmount}</div>
        <div className={`badge ${isFraud ? 'fraud' : 'clear'}`}>{isFraud ? 'FRAUD' : 'CLEAR'}</div>
      </div>
    </div>
  );
}

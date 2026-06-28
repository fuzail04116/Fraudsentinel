import { Routes, Route } from 'react-router-dom';
import { useState, useEffect } from 'react';
import Sidebar from './components/Sidebar';
import Overview from './pages/Overview';
import LiveFeed from './pages/LiveFeed';
import Alerts from './pages/Alerts';
import ModelHealth from './pages/ModelHealth';
import Retrain from './pages/Retrain';
import { useRealtimeTransactions } from './hooks/useRealtimeTransactions';

function App() {
  const { fraudCount } = useRealtimeTransactions();
  const [showToast, setShowToast] = useState(false);

  useEffect(() => {
    if (fraudCount > 0) {
      setShowToast(true);
      const timer = setTimeout(() => setShowToast(false), 3000);
      return () => clearTimeout(timer);
    }
  }, [fraudCount]);

  return (
    <div className="app-container">
      <Sidebar />
      <main className="main-content">
        <Routes>
          <Route path="/" element={<Overview />} />
          <Route path="/live" element={<LiveFeed />} />
          <Route path="/alerts" element={<Alerts />} />
          <Route path="/model" element={<ModelHealth />} />
          <Route path="/retrain" element={<Retrain />} />
        </Routes>
      </main>
      
      {showToast && (
        <div style={{ position: 'fixed', bottom: '24px', right: '24px', backgroundColor: '#C0392B', color: 'white', padding: '16px 24px', borderRadius: '8px', boxShadow: '0 4px 12px rgba(0,0,0,0.15)', display: 'flex', alignItems: 'center', gap: '12px', zIndex: 9999, animation: 'slideIn 300ms ease-out' }}>
          <span style={{ fontSize: '20px' }}>🚨</span>
          <div>
            <div style={{ fontWeight: 700, fontSize: '14px' }}>New Fraud Detected!</div>
            <div style={{ fontSize: '12px', opacity: 0.9 }}>A high-risk transaction was just flagged.</div>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;

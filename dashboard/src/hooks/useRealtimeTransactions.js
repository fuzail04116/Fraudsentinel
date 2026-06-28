import { useState, useEffect } from 'react';
import { supabase } from '../lib/supabaseClient';

export function useRealtimeTransactions() {
  const [transactions, setTransactions] = useState([]);
  const [fraudCount, setFraudCount] = useState(0);
  const [totalCount, setTotalCount] = useState(0);
  const [isConnected, setIsConnected] = useState(false);

  useEffect(() => {
    // Fetch initial state instantly
    fetch('/api/transactions?limit=50')
      .then(res => res.json())
      .then(data => {
        if (data && data.transactions) {
          setTransactions(data.transactions);
          setTotalCount(data.transactions.length);
          setFraudCount(data.transactions.filter(t => t.label === 1).length);
        }
      })
      .catch(err => console.error('Failed to fetch initial transactions', err));

    if (import.meta.env.VITE_SUPABASE_URL) {
      setIsConnected(true);
      const channelName = 'public:predictions:' + Math.random().toString(36).substring(7);
      const channel = supabase
        .channel(channelName)
        .on('postgres_changes', { event: 'INSERT', schema: 'public', table: 'predictions' }, payload => {
          const newTx = payload.new;
          setTransactions(prev => {
            const next = [newTx, ...prev];
            return next.slice(0, 500); 
          });
          setTotalCount(c => c + 1);
          if (newTx.label === 1) setFraudCount(c => c + 1);
        })
        .subscribe();

      return () => {
        supabase.removeChannel(channel);
      };
    } else {
      console.log('No Supabase config found, using mock data generator.');
      let interval = setInterval(() => {
        const isFraud = Math.random() < 0.05;
        const mockTx = {
          id: crypto.randomUUID(),
          transaction_id: 'txn_mock_' + Math.floor(Math.random() * 10000),
          amount: (Math.random() * 500).toFixed(2),
          confidence: isFraud ? 0.95 : 0.99,
          label: isFraud ? 1 : 0,
          created_at: new Date().toISOString(),
          shap_top_feature: isFraud ? 'V14' : 'V4',
          shap_top_value: isFraud ? -0.45 : 0.12
        };
        
        setTransactions(prev => {
            const next = [mockTx, ...prev];
            return next.slice(0, 500);
        });
        setTotalCount(c => c + 1);
        if (isFraud) setFraudCount(c => c + 1);
      }, 3000); 
      
      return () => clearInterval(interval);
    }
  }, []);

  const fraudRate = totalCount > 0 ? ((fraudCount / totalCount) * 100).toFixed(2) : 0;

  return { transactions, fraudCount, totalCount, fraudRate, isConnected };
}

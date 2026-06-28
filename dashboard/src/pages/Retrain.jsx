import { useState, useEffect } from 'react';
import TopBar from '../components/TopBar';
import PipelineStatus from '../components/PipelineStatus';
import StatCard from '../components/StatCard';
import { RotateCcw } from 'lucide-react';

export default function Retrain() {
  const [status, setStatus] = useState('idle'); 
  const [errorMsg, setErrorMsg] = useState('');
  const [progress, setProgress] = useState(0);

  useEffect(() => {
    let timer;
    if (status === 'running') {
      timer = setInterval(() => {
        setProgress(p => Math.min(p + 10, 90));
      }, 1000);
    } else if (status === 'done') {
      setProgress(100);
    }
    return () => clearInterval(timer);
  }, [status]);

  const handleRetrain = async () => {
    setStatus('running');
    setErrorMsg('');
    setProgress(0);
    try {
      const resp = await fetch('http://localhost:8000/retrain', { method: 'POST' });
      if (!resp.ok) {
        throw new Error(`Server returned ${resp.status}`);
      }
      setTimeout(() => setStatus('done'), 8000);
    } catch (err) {
      console.error(err);
      setStatus('error');
      setErrorMsg(err.message || 'Failed to trigger Airflow pipeline.');
    }
  };

  return (
    <div>
      <TopBar title="MLOps Retraining Pipeline" />
      
      <div className="stat-row">
        <StatCard label="Pipeline Trigger" value="Manual" sub="Override drift checks" colorVariant="blue" />
        <StatCard label="Data Source" value="creditcard.csv" sub="284k records" colorVariant="amber" />
        <StatCard label="Est. Duration" value="4m 20s" sub="Cloud Runners" colorVariant="green" />
      </div>

      <div className="content-grid">
        <div className="panel">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 24 }}>
            <div>
              <h3 className="panel-title" style={{ marginBottom: 8 }}>Manual Pipeline Trigger</h3>
              <p style={{ fontSize: 13, color: 'var(--text-secondary)' }}>Launch the full Airflow DAG to validate data, engineer features, retrain the ensemble, and deploy to staging.</p>
            </div>
            <button 
              className="btn" 
              onClick={handleRetrain} 
              disabled={status === 'running'}
            >
              <RotateCcw size={16} className={status === 'running' ? 'animate-spin' : ''} />
              <span style={{ marginLeft: 8 }}>{status === 'running' ? 'Pipeline Running...' : 'Run Pipeline'}</span>
            </button>
          </div>
          
          {errorMsg && (
             <div style={{ padding: '16px', backgroundColor: '#FDECEA', color: '#C0392B', border: '1px solid #F5C6C2', borderRadius: '8px', marginBottom: '24px', fontSize: '13px' }}>
                <strong>Error triggering pipeline:</strong> {errorMsg}
             </div>
          )}

          {status === 'done' && (
             <div style={{ padding: '16px', backgroundColor: '#E8F5E9', color: '#27AE60', border: '1px solid #C3E6CB', borderRadius: '8px', marginBottom: '24px', fontSize: '13px' }}>
                <strong>Success!</strong> Pipeline executed and new model version was deployed to staging.
             </div>
          )}
          
          <div style={{ backgroundColor: '#FAF7F2', padding: 16, borderRadius: 8, fontFamily: 'monospace', fontSize: 12, color: '#333' }}>
            &gt; DAG fraud_pipeline state: {status}<br/>
            {(status === 'running' || status === 'done') && <>&gt; Fetching latest data from Supabase... {progress > 10 ? '[OK]' : '...'}<br/></>}
            {(status === 'running' || status === 'done') && progress > 20 && <>&gt; Running Great Expectations suite... {progress > 40 ? '[OK]' : '...'}<br/></>}
            {(status === 'running' || status === 'done') && progress > 40 && <>&gt; Training XGBoost &amp; Isolation Forest... {progress > 80 ? '[OK]' : '...'}<br/></>}
            {status === 'done' && <>&gt; Model registered to MLflow. [OK]<br/>&gt; CD triggered via GitHub Actions. [OK]</>}
          </div>
        </div>
        
        <div className="grid-right-col">
          <PipelineStatus status={status} progress={progress} />
        </div>
      </div>
    </div>
  );
}

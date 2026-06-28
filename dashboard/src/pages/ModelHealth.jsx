import TopBar from '../components/TopBar';
import DriftChart from '../components/DriftChart';
import ModelMetrics from '../components/ModelMetrics';
import { useModelMetrics } from '../hooks/useModelMetrics';
import StatCard from '../components/StatCard';

export default function ModelHealth() {
  const { modelInfo, driftReport } = useModelMetrics();

  const mockDriftData = [
    { date: 'Mon', psi: 0.05 },
    { date: 'Tue', psi: 0.08 },
    { date: 'Wed', psi: 0.06 },
    { date: 'Thu', psi: 0.12 },
    { date: 'Fri', psi: 0.15 },
    { date: 'Sat', psi: driftReport?.max_psi || 0.18 },
  ];

  return (
    <div>
      <TopBar title="Model Health & Drift" />
      
      <div className="stat-row">
        <StatCard label="Model Version" value={modelInfo?.model_version || '2.4.1'} sub="XGBoost + IsoForest" colorVariant="blue" />
        <StatCard label="Max PSI" value={driftReport?.max_psi?.toFixed(3) || '0.120'} sub="Data Drift Score" colorVariant={driftReport?.max_psi > 0.2 ? 'red' : 'green'} />
        <StatCard label="Status" value={driftReport?.drift_detected ? 'DRIFTED' : 'HEALTHY'} sub="Retraining recommended" colorVariant={driftReport?.drift_detected ? 'red' : 'green'} />
        <StatCard label="Last Retrain" value="2 Days Ago" sub="Automated Pipeline" colorVariant="amber" />
      </div>

      <div className="content-grid">
        <div className="panel">
          <h3 className="panel-title">Data Drift Over Time (PSI)</h3>
          <DriftChart data={mockDriftData} />
        </div>
        
        <div className="grid-right-col">
          <ModelMetrics 
            auc={modelInfo?.auc_roc} 
            f1={modelInfo?.f1_score} 
            precision={modelInfo?.precision_score || 0.91} 
            driftPsi={driftReport?.max_psi} 
          />
        </div>
      </div>
    </div>
  );
}

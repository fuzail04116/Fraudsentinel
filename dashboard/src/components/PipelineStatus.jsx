import { CheckCircle2, Loader2, Circle } from 'lucide-react';

export default function PipelineStatus({ status = 'running' }) {
  const tasks = [
    { name: 'ingest_data', state: 'done' },
    { name: 'validate_data', state: 'done' },
    { name: 'engineer_features', state: 'done' },
    { name: 'check_drift', state: 'done' },
    { name: 'retrain_model', state: status === 'running' ? 'running' : (status === 'done' ? 'done' : 'idle') },
    { name: 'evaluate_model', state: status === 'done' ? 'done' : 'idle' },
    { name: 'register_model', state: status === 'done' ? 'done' : 'idle' },
    { name: 'deploy_model', state: status === 'done' ? 'done' : 'idle' },
    { name: 'notify_slack', state: status === 'done' ? 'done' : 'idle' }
  ];

  const getIcon = (state) => {
    if (state === 'done') return <CheckCircle2 size={16} color="#27AE60" />;
    if (state === 'running') return <Loader2 size={16} color="#E8A87C" className="animate-spin" />;
    return <Circle size={16} color="#E5DDD0" />;
  };

  return (
    <div className="panel">
      <h3 className="panel-title">Airflow DAG Status: fraud_pipeline</h3>
      <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
        {tasks.map((task, idx) => (
          <div key={task.name} style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
            <div style={{ position: 'relative', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              {getIcon(task.state)}
              {idx < tasks.length - 1 && (
                <div style={{ position: 'absolute', top: 20, width: 2, height: 16, backgroundColor: task.state === 'done' ? '#27AE60' : '#E5DDD0' }}></div>
              )}
            </div>
            <div style={{ fontSize: 13, fontWeight: task.state === 'running' ? 600 : 400, color: task.state === 'idle' ? '#888' : '#1A1A2E' }}>
              {task.name}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

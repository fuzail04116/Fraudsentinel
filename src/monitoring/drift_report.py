import pandas as pd
import json
from pathlib import Path
from evidently.report import Report
from evidently.metric_preset import DataDriftPreset, DataQualityPreset, ClassificationPreset
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

def generate_drift_report(current_data_path: str, reference_data_path: str, reports_dir: str):
    logger.info("Generating Evidently AI drift report")
    
    if not Path(reference_data_path).exists() or not Path(current_data_path).exists():
        logger.warning("Reference or current data missing. Cannot generate drift report.")
        return None
        
    ref_df = pd.read_csv(reference_data_path)
    curr_df = pd.read_csv(current_data_path)
    
    report = Report(metrics=[
        DataDriftPreset(),
        DataQualityPreset()
    ])
    
    report.run(reference_data=ref_df, current_data=curr_df)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = Path(reports_dir) / f"drift_report_{timestamp}.html"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report.save_html(str(report_path))
    
    report_json = report.as_dict()
    try:
        drift_metrics = report_json['metrics'][0]['result']
        
        feature_psi = {}
        mean_psi = 0
        max_psi = 0
        drift_detected = False
        
        if 'drift_by_columns' in drift_metrics:
            columns_data = drift_metrics['drift_by_columns']
            psis = []
            for col, data in columns_data.items():
                if 'drift_score' in data:
                    psi = data['drift_score']
                    feature_psi[col] = psi
                    psis.append(psi)
                    if psi > 0.2:
                        drift_detected = True
            
            if psis:
                mean_psi = sum(psis) / len(psis)
                max_psi = max(psis)
    except Exception as e:
        logger.error(f"Error parsing drift report: {e}")
        feature_psi = {}
        mean_psi, max_psi, drift_detected = 0, 0, False
                
    summary = {
        'report_timestamp': timestamp,
        'mean_psi': mean_psi,
        'max_psi': max_psi,
        'drift_detected': drift_detected,
        'feature_psi': feature_psi,
        'retrain_triggered': drift_detected or (max_psi > 0.2)
    }
    
    summary_path = Path(reports_dir) / "latest_drift_summary.json"
    with open(summary_path, 'w') as f:
        json.dump(summary, f)
        
    return summary

if __name__ == "__main__":
    project_root = Path(__file__).parent.parent.parent
    ref = str(project_root / "data" / "reference" / "reference.csv")
    generate_drift_report(ref, ref, str(project_root / "reports"))

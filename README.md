# FraudSentinel 🛡️

FraudSentinel is a full-stack, real-time Machine Learning Operations (MLOps) platform for credit card fraud detection. It ingests simulated live transactions, performs anomaly detection using a powerful ensemble model (XGBoost + Isolation Forest), and streams the predictions to a beautiful, real-time React dashboard.

## Architecture & Tech Stack
- **Frontend (Dashboard)**: React, Vite, Supabase Realtime, Recharts. Features dynamic visualizations, SHAP feature importance graphs, and a real-time Live Feed.
- **Backend (API)**: FastAPI. Handles model inference, logs predictions to Supabase, and exposes endpoints for model metrics and retraining.
- **Machine Learning**: Scikit-Learn, XGBoost, Isolation Forest, SHAP. Includes a full SMOTE-balanced training pipeline.
- **Data Ingestion**: Python-based data simulator (or Kafka producer) that streams real rows from the Kaggle Credit Card Fraud dataset.
- **Database**: Supabase (PostgreSQL) for storing transaction history and real-time pub/sub.

## Setup & Installation

### 1. Environment Setup
Create a virtual environment and install dependencies:
```bash
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 2. Configure Environment Variables
Ensure you have a `.env` file in the root directory and another inside the `dashboard/` directory containing your Supabase credentials:
```env
SUPABASE_URL=your-supabase-url
SUPABASE_ANON_KEY=your-supabase-anon-key
SUPABASE_SERVICE_KEY=your-supabase-service-key
```
Also copy `VITE_SUPABASE_URL` and `VITE_SUPABASE_ANON_KEY` to `dashboard/.env`.

### 3. Run the Full Application
We have provided a convenient `start_demo.bat` file to spin up all 3 services at once:
1. The FastAPI Backend (Port 8000)
2. The React Dashboard (Port 3000)
3. The Real-time Data Simulator

Simply double-click **`start_demo.bat`**, or run the components manually:

**Backend:**
```bash
uvicorn src.serving.main:app --host 0.0.0.0 --port 8000
```
**Frontend:**
```bash
cd dashboard
npm run dev
```
**Data Simulator:**
```bash
python src/ingestion/run_demo.py
```

## Features
- **Real-Time Streaming**: Watch transactions appear instantly on the Live Feed as they are processed by the ML model.
- **Explainable AI**: Click any fraudulent transaction to open the SHAP Drawer, showing exactly which features triggered the alert.
- **Robust Filtering**: Filter alerts by confidence threshold or transaction amount.
- **Model Health Monitoring**: Track the live AUC-ROC, F1 Score, and Precision metrics.

## License
MIT License

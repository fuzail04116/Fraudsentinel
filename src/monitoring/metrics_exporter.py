from prometheus_client import Histogram, Counter

REQUEST_LATENCY = Histogram(
    'request_latency_seconds',
    'Latency of prediction requests in seconds'
)

FRAUD_PREDICTIONS = Counter(
    'fraud_predictions_total',
    'Total number of fraud predictions'
)

TRANSACTION_COUNT = Counter(
    'transaction_count_total',
    'Total number of transactions processed'
)

MODEL_PREDICTION_SCORE = Histogram(
    'model_prediction_score',
    'Distribution of model prediction scores',
    buckets=(0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0)
)

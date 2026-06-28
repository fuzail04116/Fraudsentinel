import os
import json
import time
from kafka import KafkaConsumer
import requests
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def consume_transactions():
    bootstrap_servers = os.environ.get("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
    topic = os.environ.get("KAFKA_TOPIC", "fraud-transactions")
    api_url = os.environ.get("API_PREDICT_URL", "http://localhost:8000/predict")
    
    logger.info(f"Connecting to Kafka at {bootstrap_servers}, topic {topic}")
    
    consumer = KafkaConsumer(
        topic,
        bootstrap_servers=bootstrap_servers,
        auto_offset_reset='latest',
        enable_auto_commit=True,
        group_id='fraud-inference-group',
        value_deserializer=lambda x: json.loads(x.decode('utf-8'))
    )
    
    logger.info("Started consuming messages and sending to API...")
    
    try:
        for message in consumer:
            transaction = message.value
            try:
                response = requests.post(api_url, json=transaction)
                if response.status_code == 200:
                    pred = response.json()
                    is_fraud = pred.get('label', 0) == 1
                    if is_fraud:
                        logger.warning(f"🚨 FRAUD DETECTED: {pred['transaction_id']} (prob: {pred['fraud_probability']:.4f})")
                    else:
                        logger.debug(f"✅ CLEAR: {pred['transaction_id']}")
                else:
                    logger.error(f"API Error {response.status_code}: {response.text}")
            except Exception as e:
                logger.error(f"Failed to post to API: {e}")
                
    except KeyboardInterrupt:
        logger.info("Stopping consumer...")
    finally:
        consumer.close()

if __name__ == "__main__":
    time.sleep(5)
    consume_transactions()

import os
import json
import time
import random
import pandas as pd
from kafka import KafkaProducer
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_merchant(amount, idx):
    if amount < 50: return "Grocery Store · Local Mart"
    elif amount <= 200: return "Restaurant · Café Europa"
    elif amount <= 500: return "ATM Withdrawal · City Bank"
    elif amount <= 2000: return f"Online Purchase · Merchant #{idx}"
    else:
        city = random.choice(["London", "Tokyo", "Dubai", "Singapore", "New York"])
        return f"International Wire · {city}"

def produce_transactions():
    bootstrap_servers = os.environ.get("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
    topic = os.environ.get("KAFKA_TOPIC", "fraud-transactions")
    rate = float(os.environ.get("KAFKA_RATE", "1.0"))
    
    logger.info(f"Connecting to Kafka at {bootstrap_servers}")
    producer = KafkaProducer(
        bootstrap_servers=bootstrap_servers,
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )
    
    project_root = Path(__file__).parent.parent.parent
    data_path = project_root / "data" / "raw" / "creditcard.csv"
    
    logger.info(f"Loading dataset from {data_path}")
    df = pd.read_csv(data_path)
    fraud_df = df[df['Class'] == 1].reset_index(drop=True)
    clear_df = df[df['Class'] == 0].reset_index(drop=True)
    
    logger.info(f"Starting to produce at {rate} tx/sec to topic '{topic}'")
    
    fraud_idx = 0
    clear_idx = 0
    total_idx = 0
    
    try:
        while True:
            if total_idx > 0 and total_idx % 10 == 0 and fraud_idx < len(fraud_df):
                row = fraud_df.iloc[fraud_idx]
                fraud_idx += 1
            else:
                if clear_idx >= len(clear_df): break
                row = clear_df.iloc[clear_idx]
                clear_idx += 1
                
            record = row.to_dict()
            record['row_index'] = total_idx
            record['transaction_id'] = f"txn_{total_idx}_{int(time.time())}"
            
            amt = record.get('Amount', 0.0)
            record['merchant'] = get_merchant(amt, total_idx)
            record['card_no'] = f"••{str(total_idx).zfill(4)[-4:]}"
            
            if 'Class' in record:
                del record['Class']
                
            producer.send(topic, value=record)
            
            if total_idx > 0 and total_idx % 100 == 0:
                logger.info(f"Produced {total_idx} messages")
                
            total_idx += 1
            time.sleep(1.0 / rate)
            
    except KeyboardInterrupt:
        logger.info("Stopping producer...")
    finally:
        producer.flush()
        producer.close()

if __name__ == "__main__":
    produce_transactions()

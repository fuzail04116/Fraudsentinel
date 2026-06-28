import time
import requests
import pandas as pd
import random
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

def run():
    project_root = Path(__file__).parent.parent.parent
    data_path = project_root / "data" / "raw" / "creditcard.csv"
    
    logger.info(f"Loading dataset from {data_path}")
    df = pd.read_csv(data_path)
    fraud_df = df[df['Class'] == 1].reset_index(drop=True)
    clear_df = df[df['Class'] == 0].reset_index(drop=True)
    
    rate = 1.0
    fraud_idx = 0
    clear_idx = 0
    total_idx = 0
    
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
            
        try:
            requests.post("http://localhost:8000/predict", json=record)
            logger.info(f"Sent tx {total_idx}")
        except Exception as e:
            logger.error(f"Failed to send: {e}")
            
        total_idx += 1
        time.sleep(1.0 / rate)

if __name__ == "__main__":
    run()

import pandas as pd
import great_expectations as ge
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

def validate_data(data_path: str, dead_letter_path: str = "data/dead_letter/"):
    logger.info(f"Starting Great Expectations validation for {data_path}")
    df = pd.read_csv(data_path)
    ge_df = ge.from_pandas(df)
    
    expected_cols = [f"V{i}" for i in range(1, 29)] + ["Time", "Amount", "Class"]
    ge_df.expect_table_columns_to_match_ordered_list(expected_cols)
    
    for col in expected_cols:
        ge_df.expect_column_values_to_not_be_null(col)
        
    ge_df.expect_column_values_to_be_between("Amount", min_value=0)
    ge_df.expect_column_values_to_be_in_set("Class", [0, 1])
    ge_df.expect_column_mean_to_be_between("Amount", min_value=0, max_value=2000)
    ge_df.expect_column_stdev_to_be_between("Amount", min_value=0, max_value=1000)
    
    results = ge_df.validate()
    
    success = results["success"]
    pass_count = sum(1 for res in results["results"] if res["success"])
    total_count = len(results["results"])
    score = pass_count / total_count if total_count > 0 else 0
    
    if not success:
        logger.warning("Data validation failed! Routing bad records to dead letter queue.")
        Path(dead_letter_path).mkdir(parents=True, exist_ok=True)
        dead_file = Path(dead_letter_path) / f"failed_batch_{pd.Timestamp.now().strftime('%Y%m%d%H%M%S')}.csv"
        df.to_csv(dead_file, index=False)
        
    return score, success

if __name__ == "__main__":
    project_root = Path(__file__).parent.parent.parent
    data_path = project_root / "data" / "raw" / "creditcard.csv"
    validate_data(str(data_path))

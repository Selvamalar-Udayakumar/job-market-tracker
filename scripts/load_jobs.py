import pandas as pd
import glob
import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

def load_latest_processed_file(processed_folder="data/processed"):
    """
    Find and load the most recent cleaned CSV file.
    """
    files = glob.glob(os.path.join(processed_folder, "jobs_clean_*.csv"))
    if not files:
        raise FileNotFoundError("No processed files found. Run transform_jobs.py first.")

    latest_file = max(files, key=os.path.getctime)
    print(f"Loading: {latest_file}")

    df = pd.read_csv(latest_file)
    return df


def load_to_postgres(df, table_name="job_listings"):
    """
    Load the DataFrame into PostgreSQL (Neon).
    Uses 'append' so repeated runs add new data over time,
    building up historical job market data.
    """
    engine = create_engine(DATABASE_URL)

    df.to_sql(
        table_name,
        engine,
        if_exists="append",  # append new data each run, don't overwrite
        index=False
    )

    print(f"Loaded {len(df)} rows into '{table_name}' table")

    # Quick sanity check: count total rows now in the table
    with engine.connect() as conn:
        result = conn.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
        total_rows = result.scalar()
        print(f"Total rows now in '{table_name}': {total_rows}")


if __name__ == "__main__":
    df = load_latest_processed_file()
    load_to_postgres(df)
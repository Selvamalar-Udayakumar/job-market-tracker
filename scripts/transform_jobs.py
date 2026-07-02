import pandas as pd
import json
import glob
import os
from datetime import datetime

def load_latest_raw_file(raw_folder="data/raw"):
    """
    Find and load the most recently saved raw JSON file.
    """
    files = glob.glob(os.path.join(raw_folder, "jobs_*.json"))
    if not files:
        raise FileNotFoundError("No raw job files found. Run extract_jobs.py first.")

    latest_file = max(files, key=os.path.getctime)
    print(f"Loading: {latest_file}")

    with open(latest_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    return data


def flatten_job(job):
    """
    Take one raw job dict (with nested fields) and flatten it
    into a simple flat dictionary.
    """
    return {
        "id": job.get("id"),
        "title": job.get("title"),
        "company": job.get("company", {}).get("display_name"),
        "location": job.get("location", {}).get("display_name"),
        "state": job.get("location", {}).get("area", [None, None])[1] if len(job.get("location", {}).get("area", [])) > 1 else None,
        "category": job.get("category", {}).get("label"),
        "contract_type": job.get("contract_type"),
        "contract_time": job.get("contract_time"),
        "salary_min": job.get("salary_min"),
        "salary_max": job.get("salary_max"),
        "created": job.get("created"),
        "description": job.get("description"),
        "redirect_url": job.get("redirect_url"),
    }


def is_relevant(title, keywords=None):
    """
    Basic filter to drop clearly irrelevant listings.
    Keeps title if it contains any of the target keywords.
    """
    if keywords is None:
        keywords = ["data engineer", "data engineering", "etl", "big data", "data pipeline"]

    if not title:
        return False

    title_lower = title.lower()
    return any(keyword in title_lower for keyword in keywords)


def transform_jobs(raw_data):
    """
    Full transform pipeline: flatten, clean, filter, add derived columns.
    """
    # Step 1: Flatten all jobs
    flattened = [flatten_job(job) for job in raw_data]
    df = pd.DataFrame(flattened)

    print(f"Total jobs before filtering: {len(df)}")

    # Step 2: Filter to relevant titles only
    df = df[df["title"].apply(is_relevant)]
    print(f"Total jobs after relevance filtering: {len(df)}")

    # Step 3: Handle salary fields
    df["salary_available"] = df["salary_min"].notna() | df["salary_max"].notna()
    df["salary_min"] = pd.to_numeric(df["salary_min"], errors="coerce")
    df["salary_max"] = pd.to_numeric(df["salary_max"], errors="coerce")

    # Step 4: Compute average salary where both min and max are available
    df["salary_avg"] = df[["salary_min", "salary_max"]].mean(axis=1)

    # Step 5: Clean date field
    df["created"] = pd.to_datetime(df["created"], errors="coerce")

    # Step 6: Drop exact duplicate listings (same id)
    df = df.drop_duplicates(subset="id")

    # Step 7: Reset index
    df = df.reset_index(drop=True)

    return df


def save_processed_data(df, filename=None):
    """
    Save the cleaned DataFrame as a CSV in data/processed.
    """
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"data/processed/jobs_clean_{timestamp}.csv"

    df.to_csv(filename, index=False)
    print(f"Saved {len(df)} cleaned jobs to {filename}")


if __name__ == "__main__":
    raw_data = load_latest_raw_file()
    df = transform_jobs(raw_data)
    print(df[["title", "company", "location", "salary_min", "salary_max", "salary_available"]])
    save_processed_data(df)
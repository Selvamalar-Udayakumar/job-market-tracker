import requests
import os
from dotenv import load_dotenv
import json
from datetime import datetime

# Load environment variables from .env file
load_dotenv()

APP_ID = os.getenv("ADZUNA_APP_ID")
APP_KEY = os.getenv("ADZUNA_APP_KEY")

def fetch_jobs(job_title="data engineer", country="in", results_per_page=20, pages=1):
    """
    Fetch job listings from Adzuna API for a given job title.
    """
    all_jobs = []

    for page in range(1, pages + 1):
        url = f"https://api.adzuna.com/v1/api/jobs/{country}/search/{page}"
        params = {
            "app_id": APP_ID,
            "app_key": APP_KEY,
            "results_per_page": results_per_page,
            "what": job_title,
            "content-type": "application/json"
        }

        response = requests.get(url, params=params)

        if response.status_code == 200:
            data = response.json()
            jobs = data.get("results", [])
            all_jobs.extend(jobs)
            print(f"Page {page}: fetched {len(jobs)} jobs")
        else:
            print(f"Error on page {page}: {response.status_code} - {response.text}")

    return all_jobs


def save_raw_data(jobs, filename=None):
    """
    Save raw job data as JSON in data/raw folder.
    """
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"data/raw/jobs_{timestamp}.json"

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(jobs, f, indent=2, ensure_ascii=False)

    print(f"Saved {len(jobs)} jobs to {filename}")


if __name__ == "__main__":
    jobs = fetch_jobs(job_title="data engineer", country="in", results_per_page=20, pages=1)
    save_raw_data(jobs)
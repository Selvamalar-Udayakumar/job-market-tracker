Job Market Tracker

An automated data pipeline that tracks live "Data Engineer" job postings in India, storing them daily to build a historical dataset for trend analysis — instead of relying on a single point-in-time snapshot.

Why I built this

I was researching the data engineering job market for my own career planning and decided to build a tool to track it properly: what roles are being posted, where, by whom, and what fraction disclose salary. This project doubles as a hands-on introduction to core data engineering concepts — building a pipeline end-to-end rather than just analyzing a static dataset.

Dashboard

Show Image

Built in Power BI, connected directly to the Neon PostgreSQL database. Key metrics include total listings, salary disclosure rate, average disclosed salary, top hiring locations, top companies, job posting age distribution, and a daily pipeline ingestion trend that grows automatically as the pipeline runs.

Architecture

Adzuna API (live job listings)
        │
        ▼
   EXTRACT  (Python)
   Pulls raw job listings, saves as timestamped JSON
        │
        ▼
   TRANSFORM  (Python + Pandas)
   Flattens nested fields, filters irrelevant listings,
   cleans salary data, removes duplicates
        │
        ▼
   LOAD  (Python + SQLAlchemy)
   Appends clean data into a PostgreSQL table (Neon, cloud-hosted)
        │
        ▼
   ORCHESTRATION  (GitHub Actions)
   Runs the full pipeline daily on a schedule, commits
   new data files back to the repo automatically
        │
        ▼
   Historical dataset → Power BI dashboard

Tech stack


Python — extraction, transformation, and load logic
Pandas — data cleaning and structuring
SQLAlchemy — database connection and writes
PostgreSQL (Neon) — cloud-hosted data warehouse
Adzuna API — live job listings source
GitHub Actions — scheduled orchestration (daily runs, no local infrastructure required)
Power BI — dashboard and visualization


What the pipeline does


Extract (scripts/extract_jobs.py) — calls the Adzuna API for "data engineer" roles in India, saves the raw response as JSON with a timestamp.
Transform (scripts/transform_jobs.py) — flattens nested JSON (location, company, category), filters out irrelevant listings using keyword matching, converts salary fields to numeric, flags whether salary data is available, and drops duplicates.
Load (scripts/load_jobs.py) — appends the cleaned data into a job_listings table in a Neon PostgreSQL database, building up a historical record over time.
Orchestrate (.github/workflows/daily_pipeline.yml) — runs all three steps automatically every day via GitHub Actions, using repository secrets for API keys and database credentials, and commits the new data files back to the repo.


A design decision worth noting

I originally set up Apache Airflow via Docker for orchestration, since it's the industry-standard tool for this kind of pipeline. I got it fully working locally — DAGs, scheduling, the works — but ran into memory limits on my machine (7.7GB RAM total), which made the multi-container Airflow stack unreliable alongside everyday use.

Rather than fight the hardware, I switched to GitHub Actions: it achieves the same goal — automated, scheduled pipeline runs — but executes entirely on GitHub's infrastructure, at no cost and no local resource usage. For a project at this scale, it's a legitimate and arguably more practical choice.

Findings so far


Only a minority of job listings on Adzuna India disclose salary information — most postings omit salary_min/salary_max entirely.
Listings for "data engineer" often include noisy, tangentially related titles (e.g., unrelated engineering roles), which the transform step filters out via keyword matching.


Running it yourself

Prerequisites: Python 3.11+, an Adzuna API key, and a PostgreSQL database (e.g., a free Neon project).

bash# Clone the repo
git clone https://github.com/Selvamalar-Udayakumar/job-market-tracker.git
cd job-market-tracker

# Set up virtual environment
python -m venv venv
venv\Scripts\activate      # Windows
source venv/bin/activate   # Mac/Linux

# Install dependencies
pip install requests pandas python-dotenv sqlalchemy psycopg2-binary

# Add your credentials to a .env file
# ADZUNA_APP_ID=your_id
# ADZUNA_APP_KEY=your_key
# DATABASE_URL=your_postgres_connection_string

# Run the pipeline manually
python scripts/extract_jobs.py
python scripts/transform_jobs.py
python scripts/load_jobs.py

The pipeline also runs automatically every day via GitHub Actions — see .github/workflows/daily_pipeline.yml.

Roadmap


 Extract — Adzuna API integration
 Transform — cleaning, filtering, deduplication
 Load — PostgreSQL (Neon)
 Orchestration — GitHub Actions (daily schedule)
 Power BI dashboard on top of the accumulated dataset
 Expand to additional job titles / roles for broader market coverage

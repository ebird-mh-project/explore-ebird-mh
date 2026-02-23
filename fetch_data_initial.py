import requests
import pandas as pd
from pathlib import Path
from datetime import datetime
import calendar
import time
import os


# ---------------------------------------
# CONFIG
# ---------------------------------------

EBIRD_API_KEY = os.getenv("EBIRD_API_KEY")

BASE_URL = "https://api.ebird.org/v2/data/obs/IN-MH/historic"


# ---------------------------------------
# FETCH FUNCTION
# ---------------------------------------

def fetch_month_data(year, month):

    if not EBIRD_API_KEY:
        raise ValueError("EBIRD_API_KEY not set as environment variable")

    start_date = datetime(year, month, 1)
    end_day = calendar.monthrange(year, month)[1]
    end_date = datetime(year, month, end_day)

    print(f"Fetching data from {start_date.date()} to {end_date.date()}")

    all_records = []

    current_date = start_date

    while current_date <= end_date:

        date_str = current_date.strftime("%Y/%m/%d")

        url = f"{BASE_URL}/{date_str}"

        headers = {
            "X-eBirdApiToken": EBIRD_API_KEY
        }

        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            print(f"Failed on {date_str}")
            current_date += pd.Timedelta(days=1)
            continue

        daily_data = response.json()

        all_records.extend(daily_data)

        print(f"{date_str} → {len(daily_data)} records", flush=True)

        time.sleep(0.4)  # Avoid rate limits

        current_date += pd.Timedelta(days=1)

    if not all_records:
        print("No records found for month.")
        return

    df = pd.DataFrame(all_records)
    df = df.rename(columns={
    "comName": "commonName",
    "sciName": "scientificName",
    "obsDt": "observationDate",
    "howMany": "observationCount",
    "lat": "latitude",
    "lng": "longitude"})

    month_name = calendar.month_name[month]

    output_dir = Path("months")
    output_dir.mkdir(exist_ok=True)

    output_path = output_dir / f"{month_name}_{year}.csv"

    df.to_csv(output_path, index=False)

    print(f"Saved: {output_path}")

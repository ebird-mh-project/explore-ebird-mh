# EXECUTED MONTHLy

import requests
import pandas as pd
import calendar
from datetime import datetime
from pathlib import Path
import os
import time


EBIRD_API_KEY = os.getenv("EBIRD_API_KEY")
REGION_CODE = "IN-MH"
BASE_URL = "https://api.ebird.org/v2/data/obs"


def fetch_full_month(year, month):

    if not EBIRD_API_KEY:
        raise ValueError("EBIRD_API_KEY not set")

    month_name = calendar.month_name[month]
    end_day = calendar.monthrange(year, month)[1]

    all_records = []

    for day in range(1, end_day + 1):

        date_str = f"{year}/{month:02d}/{day:02d}"
        url = f"{BASE_URL}/{REGION_CODE}/historic/{date_str}?detail=full"

        headers = {"X-eBirdApiToken": EBIRD_API_KEY}

        retry_count = 0
        max_retries = 5

        while retry_count < max_retries:

            response = requests.get(url, headers=headers)

            if response.status_code == 200:
                daily_data = response.json()
                all_records.extend(daily_data)
                print(f"{date_str} → {len(daily_data)} records")
                break

            elif response.status_code == 429:
                wait_time = 2 ** retry_count
                print(f"Rate limit hit ({date_str}). Waiting {wait_time}s...")
                time.sleep(wait_time)
                retry_count += 1

            else:
                print(f"Failed {date_str} → {response.status_code}")
                break

        time.sleep(0.3)

    if not all_records:
        print("No data found.")
        return

    df = pd.DataFrame(all_records)

    df = df.rename(columns={
        "comName": "commonName",
        "sciName": "scientificName",
        "obsDt": "observationDate",
        "howMany": "observationCount",
        "lat": "latitude",
        "lng": "longitude",
        "obsType": "observationType",
        "protocolName": "protocolName"
    })

    output_dir = Path("months")
    output_dir.mkdir(exist_ok=True)

    output_path = output_dir / f"{month_name}_{year}.csv"
    df.to_csv(output_path, index=False)

    print(f"✓ Saved: {output_path}")


if __name__ == "__main__":
    today = datetime.today()
    fetch_full_month(today.year, today.month)

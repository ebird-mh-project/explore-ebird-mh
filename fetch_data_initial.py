import requests
import pandas as pd
from pathlib import Path
from datetime import datetime
import calendar
import time
import os


EBIRD_API_KEY = os.getenv("EBIRD_API_KEY")
BASE_URL = "https://api.ebird.org/v2/data/obs/IN-MH/historic"


def fetch_month_data(year, month):

    if not EBIRD_API_KEY:
        raise ValueError("EBIRD_API_KEY not set")

    start_date = datetime(year, month, 1)
    end_day = calendar.monthrange(year, month)[1]
    end_date = datetime(year, month, end_day)

    print(f"Fetching {start_date.date()} → {end_date.date()}")

    all_records = []
    current_date = start_date

    while current_date <= end_date:

        date_str = current_date.strftime("%Y/%m/%d")
        url = f"{BASE_URL}/{date_str}?detail=full"

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
                print(f"Rate limit hit. Waiting {wait_time}s...")
                time.sleep(wait_time)
                retry_count += 1

            else:
                print(f"Failed {date_str} → {response.status_code}")
                break

        time.sleep(0.3)
        current_date += pd.Timedelta(days=1)

    if not all_records:
        print("No data.")
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

    month_name = calendar.month_name[month]
    output_dir = Path("months")
    output_dir.mkdir(exist_ok=True)

    output_path = output_dir / f"{month_name}_{year}.csv"
    df.to_csv(output_path, index=False)

    print(f"Saved: {output_path}")

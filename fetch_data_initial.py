import requests
import pandas as pd
from pathlib import Path
import os
import calendar

API_KEY = os.getenv("EBIRD_API_KEY")
REGION_CODE = "IN-MH"
BASE_URL = "https://api.ebird.org/v2/data/obs"

HEADERS = {"X-eBirdApiToken": API_KEY}

# Target months
TARGET_MONTHS = [
    (2025, 1), (2025, 2), (2025, 3), (2025, 4),
    (2025, 5), (2025, 6), (2025, 7), (2025, 8),
    (2025, 9), (2025,10), (2025,11), (2025,12),
    (2026, 1), (2026, 2)
]

def fetch_month(year, month):

    month_name = calendar.month_name[month]
    month_year = f"{month_name}_{year}"

    print(f"Fetching {month_year}")

    # Use start + end date for full month
    start_date = f"{year}/{month:02d}/01"
    last_day = calendar.monthrange(year, month)[1]
    end_date = f"{year}/{month:02d}/{last_day}"

    url = f"{BASE_URL}/{REGION_CODE}/historical/{start_date}"

    params = {
        "end": end_date
    }

    response = requests.get(url, headers=HEADERS, params=params)

    if response.status_code != 200:
        print(f"Failed {month_year}")
        print(response.text)
        return

    data = response.json()

    if not data:
        print(f"No data for {month_year}")
        return

    df = pd.DataFrame(data)

    df = df.rename(columns={
        "comName": "commonName",
        "sciName": "scientificName",
        "obsDt": "observationDate",
        "howMany": "observationCount",
        "lat": "latitude",
        "lng": "longitude"
    })

    output_folder = Path(f"months/{month_year}")
    output_folder.mkdir(parents=True, exist_ok=True)

    df.to_csv(output_folder / f"{month_year}.csv", index=False)

    print(f"Saved {month_year}")


if __name__ == "__main__":

    for year, month in TARGET_MONTHS:
        fetch_month(year, month)

    print("Initial bootstrap complete.")

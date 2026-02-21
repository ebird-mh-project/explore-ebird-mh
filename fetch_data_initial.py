import requests
import pandas as pd
from pathlib import Path
from datetime import datetime
import os

from generate_map import generate_map
from generate_summary import generate_summary

API_KEY = os.getenv("EBIRD_API_KEY")
REGION_CODE = "IN-MH"
BASE_URL = "https://api.ebird.org/v2/data/obs"

HEADERS = {
    "X-eBirdApiToken": API_KEY
}

TARGET_MONTHS = [
    "2025-01", "2025-02", "2025-03", "2025-04",
    "2025-05", "2025-06", "2025-07", "2025-08",
    "2025-09", "2025-10", "2025-11", "2025-12",
    "2026-01", "2026-02"
]

def month_name(year_month):
    dt = datetime.strptime(year_month, "%Y-%m")
    return dt.strftime("%B_%Y")

for ym in TARGET_MONTHS:

    year, month = ym.split("-")
    month_folder_name = month_name(ym)

    print(f"Fetching {month_folder_name}")

    # Start & End dates
    start_date = f"{year}{month}01"
    end_date = f"{year}{month}31"

    url = f"{BASE_URL}/{REGION_CODE}/historical/{start_date}"

    params = {
        "endDate": end_date,
        "maxResults": 20000
    }

    response = requests.get(url, headers=HEADERS, params=params)

    if response.status_code != 200:
        print(f"Failed for {month_folder_name}")
        continue

    data = response.json()

    if not data:
        print(f"No data for {month_folder_name}")
        continue

    df = pd.DataFrame(data)

    df = df.rename(columns={
        "comName": "commonName",
        "sciName": "scientificName",
        "obsDt": "observationDate",
        "howMany": "observationCount",
        "lat": "latitude",
        "lng": "longitude"
    })

    # Create folder
    output_folder = Path(f"months/{month_folder_name}")
    output_folder.mkdir(parents=True, exist_ok=True)

    csv_path = output_folder / f"{month_folder_name}.csv"
    df.to_csv(csv_path, index=False)

    print(f"Saved CSV for {month_folder_name}")

    # Generate map
    generate_map(month_folder_name)

    # Generate summary
    generate_summary(month_folder_name)

    print(f"Generated map + summary for {month_folder_name}")

print("Initial bootstrap complete.")

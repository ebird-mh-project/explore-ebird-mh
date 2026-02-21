import requests
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta
import calendar
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

def month_name(year, month):
    dt = datetime(year, month, 1)
    return dt.strftime("%B_%Y")

for ym in TARGET_MONTHS:

    year, month = map(int, ym.split("-"))
    folder_name = month_name(year, month)

    print(f"Processing {folder_name}")

    days_in_month = calendar.monthrange(year, month)[1]

    monthly_data = []

    for day in range(1, days_in_month + 1):

        date_str = f"{year}{month:02d}{day:02d}"
        url = f"{BASE_URL}/{REGION_CODE}/historical/{date_str}"

        response = requests.get(url, headers=HEADERS)

        if response.status_code != 200:
            continue

        data = response.json()

        if data:
            monthly_data.extend(data)

    if not monthly_data:
        print(f"No data for {folder_name}")
        continue

    df = pd.DataFrame(monthly_data)

    df = df.rename(columns={
        "comName": "commonName",
        "sciName": "scientificName",
        "obsDt": "observationDate",
        "howMany": "observationCount",
        "lat": "latitude",
        "lng": "longitude"
    })

    # Remove duplicates
    df = df.drop_duplicates()

    output_folder = Path(f"months/{folder_name}")
    output_folder.mkdir(parents=True, exist_ok=True)

    csv_path = output_folder / f"{folder_name}.csv"
    df.to_csv(csv_path, index=False)

    print(f"Saved CSV for {folder_name}")

    generate_map(folder_name)
    generate_summary(folder_name)

    print(f"Generated map + summary for {folder_name}")

print("Initial bootstrap complete.")

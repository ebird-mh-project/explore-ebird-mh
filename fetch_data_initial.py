import requests
import pandas as pd
import time
from pathlib import Path

API_KEY = "YOUR_API_KEY"
BASE_URL = "https://api.ebird.org/v2/data/obs/geo/recent"

HEADERS = {
    "X-eBirdApiToken": API_KEY
}

OUTPUT_DIR = Path("months")
OUTPUT_DIR.mkdir(exist_ok=True)


def make_request(url, params, retries=5):
    for attempt in range(retries):
        response = requests.get(url, headers=HEADERS, params=params)

        if response.status_code == 200:
            return response.json()

        # Rate limit handling
        if response.status_code == 429:
            wait_time = int(response.headers.get("Retry-After", 60))
            print(f"Rate limit hit. Waiting {wait_time} seconds...")
            time.sleep(wait_time)
            continue

        print(f"Error {response.status_code}: {response.text}")
        time.sleep(5)

    raise Exception("Max retries exceeded.")


def fetch_month(lat, lng, radius_km, month, year):
    params = {
        "lat": lat,
        "lng": lng,
        "dist": radius_km,
        "back": 30,
        "fmt": "json"
    }

    data = make_request(BASE_URL, params)

    if not data:
        print(f"No data for {month}-{year}")
        return

    df = pd.DataFrame(data)
    df["month"] = month
    df["year"] = year

    output_file = OUTPUT_DIR / f"{year}_{month}.csv"
    df.to_csv(output_file, index=False)
    print(f"Saved {output_file}")


if __name__ == "__main__":
    fetch_month(
        lat=19.5,
        lng=75.3,
        radius_km=100,
        month=1,
        year=2025
    )

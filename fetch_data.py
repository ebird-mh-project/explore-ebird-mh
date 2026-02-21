import requests
from datetime import datetime
import pandas as pd
import os
from pathlib import Path

API_KEY = os.getenv("EBIRD_API_KEY")
REGION_CODE = "IN-MH"
BACK_DAYS = 30
BASE_URL = "https://api.ebird.org/v2/data/obs"

today = datetime.today()
month_year = today.strftime("%B_%Y")

url = f"{BASE_URL}/{REGION_CODE}/recent"
params = {"back": BACK_DAYS}
headers = {"X-eBirdApiToken": API_KEY}

response = requests.get(url, headers=headers, params=params)

if response.status_code != 200:
    raise Exception(response.text)

data = response.json()
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

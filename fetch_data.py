import requests
from datetime import datetime, timedelta
import pandas as pd


API_KEY = "jfircrke4rck"   
REGION_CODE = "IN-MH"    
BACK_DAYS = 30        
BASE_URL = "https://api.ebird.org/v2/data/obs"


url = f"{BASE_URL}/{REGION_CODE}/recent"
params = {
    "back": BACK_DAYS, 
}
headers = {
    "X-eBirdApiToken": API_KEY
}


response = requests.get(url, headers=headers, params=params)

if response.status_code == 200:
    data = response.json()
    #print(f"Total records fetched: {len(data)}\n")
    
    # Print a few examples
    #for i, obs in enumerate(data[:10]):
        #print(f"{i+1}. Species: {obs.get('comName')} | Date: {obs.get('obsDt')}")
    #else:
        #print("Error:", response.status_code, response.text)


data = pd.DataFrame(data)

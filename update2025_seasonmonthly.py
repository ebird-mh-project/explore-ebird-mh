'''
21/02/2026
This will fetch data + generate monthly map & summary (generate_map.py & generate_summary.py) + generate seasonal map & summary (generate_summary_seasonal.py)
for all of 2025 + for January 2026......... then, an 'initial.yml' will be ran , in order to run THIS just once + to see if there's any issues which arise
(like with labelling, for example will it be labelled 'February' if it's executed on 1 February? It takes the 'last 30 days', too... maybe make that a
regular interval of 30 days instead of once every month? And also, it only lasts till the end of 2026. Change that in the YAML file.)
But yeah. This will be the 'test run'. Populate with the data based on the new process. Old version will be off to the side.

After this: update About page very briefly

^^^ This stuff will pretty much finish up this dashboard for the most part. Tweaks needed, but it'll be overall presentable.

then get to the SDM project, with this dashboard as the foundation for the presentation (but more DYNAMIC; have more interesting UI elements to select new variables)
'''

import calendar
from pathlib import Path
import pandas as pd

from fetch_data_initial import fetch_month_data
from generate_map import generate_map
from generate_summary import generate_summary
from generate_summary_seasonal import generate_seasonal_summary


MONTHS_2025 = list(range(1, 13))
MONTHS_2026 = [1]

YEAR_MONTHS = {
    2025: MONTHS_2025,
    2026: MONTHS_2026
}


# MONTHLY FETCH + GENERATE

def run_monthly():

    for year, months in YEAR_MONTHS.items():

        for month in months:

            month_name = calendar.month_name[month]

            print(f"\nProcessing {month_name} {year}")

            # 1. Fetch CSV
            fetch_month_data(year, month)

            # 2. Generate map
            generate_map(month_name, year)

            # 3. Generate summary
            generate_summary(month_name, year)


# BUILD SEASONAL DATA

def season_from_month(month):
    if month in [3, 4, 5]:
        return "Summer"
    elif month in [6, 7, 8, 9]:
        return "Monsoon"
    else:
        return "Winter"


def build_seasonal():

    seasonal_data = {}

    for year, months in YEAR_MONTHS.items():

        for month in months:

            season = season_from_month(month)

            if season == "Winter" and month in [1, 2]:
                season_year = year - 1
            else:
                season_year = year

            key = f"{season} {season_year}"

            csv_path = Path(f"months/{calendar.month_name[month]}_{year}.csv")

            if not csv_path.exists():
                continue

            df = pd.read_csv(csv_path)

            if key not in seasonal_data:
                seasonal_data[key] = []

            seasonal_data[key].append(df)

    # Save seasonal CSVs
    for key, dfs in seasonal_data.items():

        season_df = pd.concat(dfs, ignore_index=True)

        out_dir = Path("new seasons")
        out_dir.mkdir(exist_ok=True)

        season_df.to_csv(out_dir / f"{key}.csv", index=False)

        print(f"Season built: {key}")

# GENERATE SEASONAL MAP + SUMMARY

def run_seasonal_outputs():

    season_dir = Path("new seasons")

    for file in season_dir.glob("*.csv"):

        season_year = file.stem

        print(f"Generating seasonal outputs for {season_year}")

        generate_map(season_year)
        generate_seasonal_summary(season_year)

# MAIN
if __name__ == "__main__":
    run_monthly()
    build_seasonal()
    run_seasonal_outputs()

    print("=== BOOTSTRAP COMPLETE ===")

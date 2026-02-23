import calendar
from pathlib import Path
import pandas as pd

from fetch_data_initial import fetch_month
from generate_map import generate_map
from generate_summary import generate_summary
from generate_summary_seasonal import generate_seasonal_summary


# ===============================
# CONFIG
# ===============================

LAT = 19.5
LNG = 75.3
RADIUS_KM = 100

#MONTHS_2025 = list(range(1, 13))
MONTHS_2026 = [1]

YEAR_MONTHS = {
    #2025: MONTHS_2025,
    2026: MONTHS_2026
}


# ===============================
# MONTHLY FETCH + GENERATE
# ===============================

def run_monthly():

    for year, months in YEAR_MONTHS.items():

        for month in months:

            month_name = calendar.month_name[month]
            time_period = f"{month_name}_{year}"

            print(f"\nProcessing {time_period}")

            # 1️⃣ Fetch CSV (CORRECT CALL)
            fetch_month(
                lat=LAT,
                lng=LNG,
                radius_km=RADIUS_KM,
                month=month,
                year=year
            )

            csv_path = Path(f"months/{year}_{month}.csv")

            # Rename to Month_Year format for rest of pipeline
            if csv_path.exists():
                renamed_path = Path(f"months/{time_period}.csv")
                csv_path.rename(renamed_path)
                csv_path = renamed_path

            # 2️⃣ VERIFY FILE EXISTS BEFORE CONTINUING
            if not csv_path.exists():
                print(f"⚠ CSV not created for {time_period}. Skipping.")
                continue

            print(f"✓ CSV confirmed: {csv_path}")

            # 3️⃣ Generate monthly map
            generate_map(time_period, mode="monthly")

            # 4️⃣ Generate monthly summary
            generate_summary(time_period)


# ===============================
# BUILD SEASONAL DATA
# ===============================

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

            month_name = calendar.month_name[month]
            season = season_from_month(month)

            # Handle Jan/Feb winter belonging to previous year
            if season == "Winter" and month in [1, 2]:
                season_year = year - 1
            else:
                season_year = year

            key = f"{season} {season_year}"

            csv_path = Path(f"months/{month_name}_{year}.csv")

            if not csv_path.exists():
                continue

            df = pd.read_csv(csv_path)

            if key not in seasonal_data:
                seasonal_data[key] = []

            seasonal_data[key].append(df)

    # Save seasonal CSVs
    out_dir = Path("new seasons")
    out_dir.mkdir(exist_ok=True)

    for key, dfs in seasonal_data.items():

        season_csv_path = out_dir / f"{key}.csv"

        # Skip if already exists
        if season_csv_path.exists():
            print(f"✓ {key} already built. Skipping.")
            continue

        season_df = pd.concat(dfs, ignore_index=True)
        season_df.to_csv(season_csv_path, index=False)

        print(f"✓ Season built: {key}")


# ===============================
# GENERATE SEASONAL MAP + SUMMARY
# ===============================

def run_seasonal_outputs():

    season_dir = Path("new seasons")

    for file in season_dir.glob("*.csv"):

        season_name = file.stem  # e.g. "Monsoon 2025"

        print(f"Generating seasonal outputs for {season_name}")

        generate_map(season_name, mode="seasonal")
        generate_seasonal_summary(season_name)


# ===============================
# MAIN
# ===============================

if __name__ == "__main__":

    run_monthly()
    build_seasonal()
    run_seasonal_outputs()

    print("=== BOOTSTRAP COMPLETE ===")

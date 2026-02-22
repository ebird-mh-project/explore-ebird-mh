import pandas as pd
from pathlib import Path
from datetime import datetime


MONTHS_DIR = Path("months")
SEASONS_DIR = Path("new seasons")
SEASONS_DIR.mkdir(exist_ok=True)


def get_season(month):
    if month in [3, 4, 5]:
        return "Summer"
    elif month in [6, 7, 8, 9]:
        return "Monsoon"
    else:
        return "Winter"


def get_season_year(year, month):
    if month in [1, 2]:
        return year - 1
    return year


def build_season(season, year):

    season_name = f"{season}_{year}"
    output_file = SEASONS_DIR / f"{season_name}.csv"

    if output_file.exists():
        print(f"✓ {season_name} already exists. Skipping.")
        return

    monthly_files = list(MONTHS_DIR.glob("*.csv"))

    dfs = []

    for file in monthly_files:
        name = file.stem  # e.g. February_2026
        month_str, year_str = name.split("_")
        month = datetime.strptime(month_str, "%B").month
        year_file = int(year_str)

        if get_season(month) == season and \
           get_season_year(year_file, month) == year:

            dfs.append(pd.read_csv(file))

    if not dfs:
        print(f"No data for {season_name}")
        return

    combined = pd.concat(dfs, ignore_index=True)
    combined.to_csv(output_file, index=False)

    print(f"✓ Created seasonal file: {season_name}")


if __name__ == "__main__":

    today = datetime.utcnow()
    month = today.month
    year = today.year

    previous_month = month - 1 or 12
    previous_year = year if month != 1 else year - 1

    season = get_season(previous_month)
    season_year = get_season_year(previous_year, previous_month)

    build_season(season, season_year)

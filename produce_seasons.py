from pathlib import Path
from datetime import datetime

from seasons_data import get_season, get_season_year, build_season
from generate_map import generate_map
from generate_summary_seasonal import generate_seasonal_summary


MONTHS_DIR = Path("months")
SEASONS_DIR = Path("new seasons")


# Required month counts per season
REQUIRED_MONTHS = {
    "Summer": 3,      # Mar, Apr, May
    "Monsoon": 4,     # Jun, Jul, Aug, Sep
    "Winter": 5       # Oct, Nov, Dec, Jan, Feb
}


def parse_month_file(file):
    """
    Convert 'March_2025.csv' → (season, season_year, month_number)
    """
    month_str, year_str = file.stem.split("_")
    month = datetime.strptime(month_str, "%B").month
    year = int(year_str)

    season = get_season(month)
    season_year = get_season_year(year, month)

    return season, season_year, month


def main():

    print("🔹 Scanning monthly files...")

    if not MONTHS_DIR.exists():
        print("⚠ months directory missing.")
        return

    month_files = list(MONTHS_DIR.glob("*.csv"))

    if not month_files:
        print("⚠ No monthly files found.")
        return

    # Group months by (season, season_year)
    season_groups = {}

    for file in month_files:
        season, season_year, month = parse_month_file(file)

        key = (season, season_year)

        if key not in season_groups:
            season_groups[key] = []

        season_groups[key].append(month)

    # Determine which seasons are complete
    for (season, season_year), months in season_groups.items():

        unique_months = set(months)
        required_count = REQUIRED_MONTHS[season]

        if len(unique_months) == required_count:

            season_name = f"{season}_{season_year}"
            print(f"✓ Full season detected: {season_name}")

            # Build CSV (safe: skips if exists)
            build_season(season, season_year)

            # Generate map
            generate_map(season_name, mode="seasonal")

            # Generate summary
            generate_seasonal_summary(season_name)

        else:
            print(
                f"Skipping {season}_{season_year} "
                f"({len(unique_months)}/{required_count} months present)"
            )

    print("Seasonal pipeline complete.")


if __name__ == "__main__":
    main()

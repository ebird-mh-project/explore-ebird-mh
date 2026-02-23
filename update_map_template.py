from pathlib import Path
from generate_map import generate_map 

MONTHS_FOLDER = Path("months")


def main():
    if not MONTHS_FOLDER.exists():
        print("⚠ 'months' folder not found.")
        return

    csv_files = sorted(MONTHS_FOLDER.glob("*.csv"))

    if not csv_files:
        print("⚠ No CSV files found in 'months' folder.")
        return

    for csv_file in csv_files:
        time_period = csv_file.stem  # e.g. January_2025
        print(f"Generating map for {time_period}...")
        generate_map(time_period, mode="monthly")

    print("✓ All monthly maps generated.")


if __name__ == "__main__":
    main()

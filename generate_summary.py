import pandas as pd
from pathlib import Path


def generate_summary(month_year):

    csv_path = Path(f"months/{month_year}.csv")

    if not csv_path.exists():
        print(f"⚠ Monthly CSV not found for {month_year}. Skipping summary.")
        return

    df = pd.read_csv(csv_path)

    # Standardize column names in case of raw API format
    df = df.rename(columns={
        "comName": "commonName",
        "sciName": "scientificName",
        "obsDt": "observationDate",
        "howMany": "observationCount",
        "lat": "latitude",
        "lng": "longitude"
    })

    if df.empty:
        print(f"⚠ {month_year} CSV empty. Skipping summary.")
        return

    total_observations = len(df)

    species_richness = (
        df["scientificName"].nunique()
        if "scientificName" in df.columns
        else 0
    )

    if "commonName" in df.columns:
        top_species = (
            df["commonName"]
            .dropna()
            .value_counts()
            .head(3)
            .reset_index()
        )
        top_species.columns = ["Species", "Observations"]
    else:
        top_species = pd.DataFrame(columns=["Species", "Observations"])

    html_content = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8"/>
<title>{month_year} Summary</title>
<style>
body {{
    font-family: Arial;
    padding: 30px;
}}
.card {{
    background:#f2f2f2;
    padding:15px;
    border-radius:8px;
    margin-bottom:20px;
}}
</style>
</head>
<body>

<h1>{month_year} Summary</h1>

<div class="card">
<b>Total Observations:</b> {total_observations}
</div>

<div class="card">
<b>Species Richness:</b> {species_richness}
</div>

<div class="card">
<b>Top 3 Species:</b>
<ul>
"""

    for _, row in top_species.iterrows():
        html_content += f"<li>{row['Species']} ({row['Observations']})</li>"

    html_content += """
</ul>
</div>

</body>
</html>
"""

    output_folder = Path("month summary")
    output_folder.mkdir(exist_ok=True)

    output_path = output_folder / f"{month_year}.html"

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"✓ Summary generated: {month_year}")

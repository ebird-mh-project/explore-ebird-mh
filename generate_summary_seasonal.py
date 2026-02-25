import pandas as pd
from pathlib import Path


def generate_seasonal_summary(season_year):

    csv_path = Path(f"new seasons/{season_year}.csv")

    if not csv_path.exists():
        print(f"⚠ Seasonal CSV not found for {season_year}.")
        return

    df = pd.read_csv(csv_path)

    if df.empty:
        print(f"⚠ {season_year} empty.")
        return

    total_observations = len(df)
    species_richness = df["scientificName"].nunique()

    def top3(col):
        if col not in df.columns:
            return pd.DataFrame(columns=["Name", "Count"])
        t = df[col].dropna().value_counts().head(3).reset_index()
        t.columns = ["Name", "Count"]
        return t

    top_species = top3("commonName")

    html = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8"/>
<title>{season_year} Seasonal Summary</title>
<style>
body {{font-family:Arial; padding:30px;}}
.card {{background:#f2f2f2; padding:20px; border-radius:10px; margin-bottom:20px;}}
img {{max-width:200px; border-radius:8px; margin-top:10px;}}
</style>
</head>
<body>

<h1>{season_year} Seasonal Summary</h1>

<div class="card">
<b>Total Observations:</b> {total_observations}<br>
<b>Total Species:</b> {species_richness}
</div>

<div class="card"><b>Top 3 Species</b><br>
"""

    assets_path = Path("assets")

    for _, row in top_species.iterrows():
        species = row["Name"]
        count = row["Count"]
        img_tag = ""

        found = False
        for ext in ["jpg", "png", "jpeg"]:
            if (assets_path / f"{species}.{ext}").exists():
                img_tag = f'<img src="../assets/{species}.{ext}">'
                found = True
                break

        if not found:
            img_tag = f"<p><i>img not found: {species}</i></p>"

        html += f"<b>{species}</b><br>{img_tag}<br><br>"

    html += "</div>"
    html += "</body></html>"

    output_path = Path("new season summary")
    output_path.mkdir(exist_ok=True)

    with open(output_path / f"{season_year}.html", "w", encoding="utf-8") as f:
        f.write(html)

    print(f"✓ Seasonal summary generated: {season_year}")

import pandas as pd
from pathlib import Path


def generate_summary(month_year):

    csv_path = Path(f"months/{month_year}.csv")

    if not csv_path.exists():
        print("CSV not found")
        return

    df = pd.read_csv(csv_path)

    total_observations = len(df)
    species_richness = df["scientificName"].nunique()

    def top3(col):
        if col not in df.columns:
            return pd.DataFrame(columns=["Name", "Count"])
        t = df[col].dropna().value_counts().head(3).reset_index()
        t.columns = ["Name", "Count"]
        return t

    top_species = top3("commonName")
    top_protocols = top3("protocolName")
    top_obs_types = top3("observationType")

    html = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8"/>
<title>{month_year} Summary</title>
<style>
body {{font-family:Arial; padding:30px;}}
.card {{background:#f2f2f2; padding:20px; border-radius:10px; margin-bottom:20px;}}
img {{max-width:200px; border-radius:8px; margin-top:10px;}}
</style>
</head>
<body>

<h1>{month_year} Summary</h1>

<div class="card">
<b>Total Observations:</b> {total_observations}<br>
<b>Species Richness:</b> {species_richness}
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

        html += f"<b>{species}</b> ({count})<br>{img_tag}<br><br>"

    html += "</div>"

    def add_section(title, df_section):
        section = f'<div class="card"><b>{title}</b><br>'
        for _, row in df_section.iterrows():
            section += f"{row['Name']} ({row['Count']})<br>"
        section += "</div>"
        return section

    html += add_section("Top 3 Protocol Types", top_protocols)
    html += add_section("Top 3 Observation Types", top_obs_types)

    html += "</body></html>"

    out = Path("month summary")
    out.mkdir(exist_ok=True)
    with open(out / f"{month_year}.html", "w", encoding="utf-8") as f:
        f.write(html)

    print(f"✓ Summary generated {month_year}")

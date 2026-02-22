import pandas as pd
import geopandas as gpd
from pathlib import Path


def generate_seasonal_summary(season_year):

    csv_path = Path(f"new seasons/{season_year}.csv")

    if not csv_path.exists():
        print(f"⚠ Seasonal CSV not found for {season_year}. Skipping.")
        return

    df = pd.read_csv(csv_path)

    # Standardize columns
    df = df.rename(columns={
        "lat": "latitude",
        "lng": "longitude",
        "comName": "commonName",
        "sciName": "scientificName",
        "obsDt": "observationDate",
        "howMany": "observationCount"
    })

    if df.empty:
        print(f"⚠ {season_year} empty. Skipping summary.")
        return

    if "longitude" not in df.columns or "latitude" not in df.columns:
        print(f"⚠ Missing coordinates in {season_year}. Skipping.")
        return

    gdf_points = gpd.GeoDataFrame(
        df,
        geometry=gpd.points_from_xy(df.longitude, df.latitude),
        crs="EPSG:4326"
    )

    grid = gpd.read_file("grid.geojson").to_crs("EPSG:4326")

    # Remove leftover join columns
    for col in ["index_left", "index_right"]:
        if col in gdf_points.columns:
            gdf_points = gdf_points.drop(columns=[col])
        if col in grid.columns:
            grid = grid.drop(columns=[col])

    joined = gpd.sjoin(
        gdf_points,
        grid,
        how="inner",
        predicate="within"
    )

    if joined.empty:
        print(f"⚠ No joined data for {season_year}")
        return

    summaries = []

    for grid_id, group in joined.groupby("grid_id"):

        summaries.append({
            "Grid ID": grid_id,
            "Observations": len(group),
            "Top 5 species": group["commonName"].value_counts().head(5).index.tolist()
        })

    summary_df = pd.DataFrame(summaries)

    html_rows = ""

    for _, row in summary_df.iterrows():
        html_rows += f"""
        <div class="grid-block">
            <h3>Grid {row['Grid ID']}</h3>
            <p><b>Observations:</b> {row['Observations']}</p>
            <p><b>Top 5 species:</b><br>
            {", ".join(row['Top 5 species'])}</p>
        </div>
        """

    html_content = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8"/>
<title>{season_year} Summary</title>
<style>
body {{ font-family: Arial; padding:20px; }}
.grid-block {{ border-bottom:1px solid #ccc; margin-bottom:15px; }}
</style>
</head>
<body>
<h2>{season_year} Seasonal Summary</h2>
{html_rows}
</body>
</html>
"""

    output_path = Path(f"new season summary/{season_year}.html")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"✓ Seasonal summary generated: {season_year}")

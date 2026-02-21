import pandas as pd
import geopandas as gpd
from pathlib import Path


def generate_seasonal_summary(season_year):

    # =========================================
    # Load seasonal CSV
    # =========================================
    csv_path = Path(f"new seasons/{season_year}/{season_year}.csv")
    df = pd.read_csv(csv_path)

    # Convert to GeoDataFrame
    gdf_points = gpd.GeoDataFrame(
        df,
        geometry=gpd.points_from_xy(df.longitude, df.latitude),
        crs="EPSG:4326"
    )

    # =========================================
    # Load seasonal grid (smaller grid)
    # =========================================
    grid = gpd.read_file("grid.geojson")
    grid = grid.to_crs("EPSG:4326")

    # =========================================
    # Spatial Join
    # =========================================
    joined = gpd.sjoin(
        gdf_points,
        grid,
        how="inner",
        predicate="within"
    )

    summaries = []

    for grid_id, group in joined.groupby("grid_id"):

        total_obs = len(group)

        top_species = group["commonName"].value_counts().head(5)

        habitat = (
            group["habitatSpecialization"]
            .dropna()
            .value_counts()
            .head(5)
        )

        migratory = (
            group["migratoryPattern"]
            .dropna()
            .value_counts()
            .head(5)
        )

        protocols = (
            group["protocolType"]
            .dropna()
            .value_counts()
            .head(5)
        )

        obs_types = (
            group["observationCount"]
            .dropna()
            .value_counts()
            .head(5)
        )

        summaries.append({
            "Grid ID": grid_id,
            "Observations": total_obs,
            "Top 5 species": top_species.index.tolist(),
            "Counts of top 5 species": top_species.values.tolist(),
            "Most common habitat specializations": habitat.index.tolist(),
            "Most common migratory patterns": migratory.index.tolist(),
            "Most common protocols": protocols.index.tolist(),
            "Most common observation types": obs_types.index.tolist()
        })

    summary_df = pd.DataFrame(summaries)

    # =========================================
    # Build HTML
    # =========================================
    html_rows = ""

    for _, row in summary_df.iterrows():

        html_rows += f"""
        <div class="grid-block">
            <h3>Grid {row['Grid ID']}</h3>
            <p><b>Observations:</b> {row['Observations']}</p>

            <p><b>Top 5 species:</b><br>
            {", ".join(row['Top 5 species'])}</p>

            <p><b>Counts of top 5 species:</b><br>
            {", ".join(map(str, row['Counts of top 5 species']))}</p>

            <p><b>Most common habitat specializations:</b><br>
            {", ".join(row['Most common habitat specializations'])}</p>

            <p><b>Most common migratory patterns:</b><br>
            {", ".join(row['Most common migratory patterns'])}</p>

            <p><b>Most common protocols:</b><br>
            {", ".join(row['Most common protocols'])}</p>

            <p><b>Most common observation types:</b><br>
            {", ".join(row['Most common observation types'])}</p>
        </div>
        """

    html_content = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8"/>
<title>{season_year} Summary</title>

<style>
body {{
    font-family: Arial, sans-serif;
    padding: 20px;
}}

.grid-block {{
    border-bottom: 1px solid #ccc;
    padding-bottom: 15px;
    margin-bottom: 15px;
}}
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

    print(f"Seasonal summary generated: {season_year}")

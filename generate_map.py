import pandas as pd
import geopandas as gpd
from pathlib import Path


def generate_map(time_period, mode="monthly"):

    if mode == "monthly":
        csv_path = Path(f"months/{time_period}.csv")
        output_path = Path(f"months/{time_period}.html")
        grid_file = "grid.geojson"

    elif mode == "seasonal":
        csv_path = Path(f"new seasons/{time_period}.csv")
        output_path = Path(f"new seasons/{time_period}.html")
        grid_file = "grid.geojson"

    else:
        raise ValueError("Mode must be 'monthly' or 'seasonal'")

    if not csv_path.exists():
        print(f"⚠ {csv_path} not found. Skipping.")
        return

    df = pd.read_csv(csv_path)

    # Standardize column names
    df = df.rename(columns={
        "lat": "latitude",
        "lng": "longitude",
        "comName": "commonName",
        "sciName": "scientificName",
        "obsDt": "observationDate",
        "howMany": "observationCount"
    })

    if df.empty or "longitude" not in df.columns:
        print(f"⚠ {time_period} empty or invalid.")
        return

    gdf_points = gpd.GeoDataFrame(
        df,
        geometry=gpd.points_from_xy(df.longitude, df.latitude),
        crs="EPSG:4326"
    )

    grid = gpd.read_file(grid_file).to_crs("EPSG:4326")

    # Remove leftover spatial join columns
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

    summaries = []

    if not joined.empty:

        for grid_id, group in joined.groupby("grid_id"):

            summaries.append({
                "grid_id": grid_id,
                "observations": len(group),
                "top_species": group["commonName"].dropna().value_counts().head(5).index.tolist(),
            })

    summary_df = pd.DataFrame(summaries)

    if not summary_df.empty:
        grid = grid.merge(summary_df, on="grid_id", how="left")

    grid["observations"] = grid.get("observations", 0).fillna(0)

    geojson_grid = grid.to_json()

    html = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8"/>
<title>{time_period}</title>

<link rel="stylesheet"
 href="https://unpkg.com/leaflet/dist/leaflet.css"/>
<script src="https://unpkg.com/leaflet/dist/leaflet.js"></script>

<style>
html, body {{ margin:0; height:100%; }}
#map {{ height:100%; }}
.leaflet-popup-content {{
    font-size: 14px;
}}
</style>
</head>
<body>

<div id="map"></div>

<script>

var map = L.map('map').setView([19.5, 75.3], 6);

L.tileLayer(
  'https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png',
  {{
    attribution: '© OpenStreetMap contributors'
  }}
).addTo(map);

var gridData = {geojson_grid};

function getColor(d) {{
  return d > 500 ? '#00441b' :
         d > 200 ? '#006d2c' :
         d > 100 ? '#238b45' :
         d > 50  ? '#41ab5d' :
         d > 20  ? '#74c476' :
         d > 0   ? '#a1d99b' :
                   '#f7fcf5';
}}

function style(feature) {{
  return {{
    fillColor: getColor(feature.properties.observations || 0),
    weight: 1,
    color: '#555',
    fillOpacity: 0.7
  }};
}}

function onEachGrid(feature, layer) {{
  var p = feature.properties;

  var content =
    "<b>{time_period}</b><br>" +
    "Grid ID: " + (p.grid_id || "") + "<br>" +
    "Observations: " + (p.observations || 0) + "<br><br>" +

    "<b>Top species:</b><br>" +
    (p.top_species || []).join("<br>") + "<br><br>";

  layer.bindPopup(content);
}}

L.geoJSON(gridData, {{
  style: style,
  onEachFeature: onEachGrid
}}).addTo(map);

</script>
</body>
</html>
"""

    output_path.parent.mkdir(exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"✓ {mode.capitalize()} map generated: {time_period}")

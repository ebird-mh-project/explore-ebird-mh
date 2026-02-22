# generate_map.py

import pandas as pd
import geopandas as gpd
from pathlib import Path


def generate_map(time_period, mode="monthly"):

    if mode == "monthly":
        csv_path = Path(f"months/{time_period}.csv")
        output_path = Path(f"months/{time_period}.html")
        grid_file = "grid_big.geojson"

    elif mode == "seasonal":
        csv_path = Path(f"seasons/{time_period}.csv")
        output_path = Path(f"seasons/{time_period}.html")
        grid_file = "grid.geojson"

    else:
        raise ValueError("Mode must be 'monthly' or 'seasonal'")

    if not csv_path.exists():
        print(f"⚠ {csv_path} not found. Skipping map generation.")
        return

    df = pd.read_csv(csv_path)

    if df.empty:
        print(f"⚠ {time_period} is empty. Generating blank map.")
        df["longitude"] = []
        df["latitude"] = []

    required_cols = ["longitude", "latitude"]
    for col in required_cols:
        if col not in df.columns:
            raise ValueError(f"{col} column missing in {csv_path}")

    # Convert to GeoDataFrame
    gdf_points = gpd.GeoDataFrame(
        df,
        geometry=gpd.points_from_xy(df.longitude, df.latitude),
        crs="EPSG:4326"
    )

    grid = gpd.read_file(grid_file)

    if grid.crs != "EPSG:4326":
        grid = grid.to_crs("EPSG:4326")

    # Remove leftover spatial join columns
    for col in ["index_right", "index_left"]:
        if col in gdf_points.columns:
            gdf_points = gdf_points.drop(columns=[col])
        if col in grid.columns:
            grid = grid.drop(columns=[col])

    # Spatial join
    if not gdf_points.empty:
        joined = gpd.sjoin(
            gdf_points,
            grid,
            how="inner",
            predicate="within",
            lsuffix="pt",
            rsuffix="grid"
        )
    else:
        joined = gpd.GeoDataFrame(columns=gdf_points.columns)

    summaries = []

    if not joined.empty:

        for grid_id, group in joined.groupby("grid_id"):

            total_obs = len(group)

            top_species = (
                group["commonName"]
                .dropna()
                .value_counts()
                .head(5)
            )

            habitat = (
                group.get("habitatSpecialization", pd.Series())
                .dropna()
                .value_counts()
                .head(5)
            )

            migratory = (
                group.get("migratoryPattern", pd.Series())
                .dropna()
                .value_counts()
                .head(5)
            )

            summaries.append({
                "grid_id": grid_id,
                "observations": int(total_obs),
                "top_species": top_species.index.tolist(),
                "habitat": habitat.index.tolist(),
                "migratory": migratory.index.tolist()
            })

    summary_df = pd.DataFrame(summaries)

    if not summary_df.empty:
        grid = grid.merge(summary_df, on="grid_id", how="left")

    grid["observations"] = grid.get("observations", 0).fillna(0)

    geojson_grid = grid.to_json()
    geojson_points = gdf_points.to_json()

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
#controls {{
  position:absolute;
  top:10px;
  left:10px;
  background:white;
  padding:10px;
  border-radius:8px;
  z-index:1000;
}}
button {{
  margin:3px;
  padding:6px 10px;
}}
</style>
</head>
<body>

<div id="controls">
<button onclick="showGrid()">Grid View</button>
<button onclick="showPoints()">Point View</button>
</div>

<div id="map"></div>

<script>

var map = L.map('map').setView([19.5, 75.3], 6);

L.tileLayer(
  'https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}.png',
  {{ attribution: '© OpenStreetMap contributors' }}
).addTo(map);

var gridData = {geojson_grid};
var pointData = {geojson_points};

function getColor(d) {{
  return d > 500 ? '#800026' :
         d > 200 ? '#BD0026' :
         d > 100 ? '#E31A1C' :
         d > 50  ? '#FC4E2A' :
         d > 20  ? '#FD8D3C' :
         d > 0   ? '#FEB24C' :
                   '#FFFFFF';
}}

function style(feature) {{
  return {{
    fillColor: getColor(feature.properties.observations || 0),
    weight: 1,
    color: '#555',
    fillOpacity: 0.6
  }};
}}

function onEachGrid(feature, layer) {{
  var p = feature.properties;

  var content =
    "<b>{time_period}</b><br>" +
    "Grid ID: " + (p.grid_id || "") + "<br>" +
    "Observations: " + (p.observations || 0) + "<br><br>" +
    "<b>Top species</b><br>" +
    (p.top_species || []).join("<br>") + "<br><br>" +
    "<b>Habitat</b><br>" +
    (p.habitat || []).join(", ") + "<br><br>" +
    "<b>Migratory</b><br>" +
    (p.migratory || []).join(", ");

  layer.bindPopup(content);
}}

var gridLayer = L.geoJSON(gridData, {{
  style: style,
  onEachFeature: onEachGrid
}});

var pointLayer = L.geoJSON(pointData, {{
  pointToLayer: function(feature, latlng) {{
    return L.circleMarker(latlng, {{radius:4}});
  }}
}});

gridLayer.addTo(map);

function showGrid() {{
  map.removeLayer(pointLayer);
  gridLayer.addTo(map);
}}

function showPoints() {{
  map.removeLayer(gridLayer);
  pointLayer.addTo(map);
}}

</script>
</body>
</html>
"""

    output_path.parent.mkdir(exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)

import pandas as pd
import geopandas as gpd
import json
from pathlib import Path

def generate_map(time_period, mode="monthly"):

    csv_path = Path(f"{mode}s/{time_period}/{time_period}.csv")
    df = pd.read_csv(csv_path)

    # Convert to GeoDataFrame
    gdf_points = gpd.GeoDataFrame(
        df,
        geometry=gpd.points_from_xy(df.longitude, df.latitude),
        crs="EPSG:4326"
    )

    # Choose grid file
    if mode == "monthly":
        grid = gpd.read_file("grid_big.geojson")
    else:
        grid = gpd.read_file("grid.geojson")

    grid = grid.to_crs("EPSG:4326")

    # Spatial join
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

        habitat = group["habitatSpecialization"].value_counts().head(5)
        migratory = group["migratoryPattern"].value_counts().head(5)

        summaries.append({
            "grid_id": grid_id,
            "observations": int(total_obs),
            "top_species": top_species.index.tolist(),
            "top_counts": top_species.values.tolist(),
            "habitat": habitat.index.tolist(),
            "migratory": migratory.index.tolist()
        })

    summary_df = pd.DataFrame(summaries)

    grid = grid.merge(summary_df, on="grid_id", how="left")
    grid["observations"] = grid["observations"].fillna(0)

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
  'https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png',
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
    fillColor: getColor(feature.properties.observations),
    weight: 1,
    color: '#555',
    fillOpacity: 0.6
  }};
}}

function onEachGrid(feature, layer) {{

  var p = feature.properties;

  var content =
    "<b>{time_period}</b><br>" +
    "Grid ID: " + p.grid_id + "<br>" +
    "Observations: " + p.observations + "<br><br>" +
    "<b>Top 5 species</b><br>" +
    (p.top_species || []).join("<br>") + "<br><br>" +
    "<b>Habitat specializations</b><br>" +
    (p.habitat || []).join(", ") + "<br><br>" +
    "<b>Migratory patterns</b><br>" +
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

    output_path = Path(f"{mode}s/{time_period}.html")

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"{mode.capitalize()} map generated: {time_period}")

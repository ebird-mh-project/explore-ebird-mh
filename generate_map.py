import pandas as pd
import geopandas as gpd
from pathlib import Path


def generate_map(time_period, mode="monthly"):

    if mode == "monthly":
        csv_path = Path(f"months/{time_period}.csv")
        output_path = Path(f"months/{time_period}.html")
    else:
        csv_path = Path(f"new seasons/{time_period}.csv")
        output_path = Path(f"new seasons/{time_period}.html")

    if not csv_path.exists():
        return

    df = pd.read_csv(csv_path)

    gdf_points = gpd.GeoDataFrame(
        df,
        geometry=gpd.points_from_xy(df.longitude, df.latitude),
        crs="EPSG:4326"
    )

    grid = gpd.read_file("grid.geojson").to_crs("EPSG:4326")

    joined = gpd.sjoin(gdf_points, grid, how="inner", predicate="within")

    summaries = []

    for grid_id, group in joined.groupby("grid_id"):

        def top5(col):
            if col not in group.columns:
                return []
            return group[col].dropna().value_counts().head(5).index.tolist()

        summaries.append({
            "grid_id": grid_id,
            "observations": len(group),
            "top_species": top5("commonName"),
            "top_protocols": top5("protocolName"),
            "top_obs_types": top5("observationType")
        })

    summary_df = pd.DataFrame(summaries)

    grid = grid.merge(summary_df, on="grid_id", how="left")
    grid["observations"] = grid["observations"].fillna(0)

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
html, body {{margin:0; height:100%;}}
#map {{height:100%;}}
</style>
</head>
<body>
<div id="map"></div>
<script>

var map = L.map('map').setView([19.5,75.3],6);

L.tileLayer(
  'https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png',
  {{attribution:'© OpenStreetMap contributors'}}
).addTo(map);

var gridData = {geojson_grid};

function onEach(feature, layer){{
    var p = feature.properties;

    var content =
      "<b>{time_period}</b><br>" +
      "Observations: " + (p.observations || 0) + "<br><br>" +
      "<b>Top Species</b><br>" + (p.top_species || []).join("<br>") + "<br><br>" +
      "<b>Top Protocols</b><br>" + (p.top_protocols || []).join("<br>") + "<br><br>" +
      "<b>Top Observation Types</b><br>" + (p.top_obs_types || []).join("<br>");

    layer.bindPopup(content);
}}

L.geoJSON(gridData, {{
  onEachFeature:onEach
}}).addTo(map);

</script>
</body>
</html>
"""

    output_path.parent.mkdir(exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"✓ Map generated {time_period}")

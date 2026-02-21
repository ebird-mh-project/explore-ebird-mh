import pandas as pd
import geopandas as gpd
import json
from pathlib import Path

def generate_map(month_year):

    # =============================
    # Load bird CSV
    # =============================
    csv_path = Path(f"months/{month_year}/{month_year}.csv")
    df = pd.read_csv(csv_path)

    # Convert to GeoDataFrame
    gdf_points = gpd.GeoDataFrame(
        df,
        geometry=gpd.points_from_xy(df.longitude, df.latitude),
        crs="EPSG:4326"
    )

    # =============================
    # Load grid GeoJSON
    # =============================
    grid = gpd.read_file("grid.geojson")
    grid = grid.to_crs("EPSG:4326")

    # =============================
    # Spatial join
    # =============================
    joined = gpd.sjoin(
        gdf_points,
        grid,
        how="inner",
        predicate="within"
    )

    # =============================
    # Aggregate per grid
    # =============================
    summary = []

    for grid_id, group in joined.groupby("grid_id"):

        total_obs = len(group)

        top_species = (
            group["commonName"]
            .value_counts()
            .head(5)
        )

        top_species_list = top_species.index.tolist()
        top_species_counts = top_species.values.tolist()

        popup_data = {
            "Month": month_year,
            "Grid ID": int(grid_id),
            "Observations": int(total_obs),
            "Top 5 species": top_species_list,
            "Counts of top 5 species": top_species_counts
        }

        summary.append((grid_id, popup_data))

    # Merge summary back to grid
    popup_dict = dict(summary)

    grid["popup_data"] = grid["grid_id"].map(popup_dict)

    grid = grid[grid["popup_data"].notnull()]

    # =============================
    # Convert to GeoJSON
    # =============================
    geojson_str = grid.to_json()

    # =============================
    # Generate HTML
    # =============================
    html_content = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8"/>
<title>{month_year}</title>

<link rel="stylesheet"
 href="https://unpkg.com/leaflet/dist/leaflet.css"/>
<script src="https://unpkg.com/leaflet/dist/leaflet.js"></script>

<style>
html, body {{
    margin:0;
    height:100%;
}}

#map {{
    height:100%;
}}

#filterPanel {{
    position:absolute;
    top:10px;
    left:10px;
    background:white;
    padding:10px;
    border-radius:8px;
    z-index:1000;
    box-shadow:0 0 10px rgba(0,0,0,0.2);
}}
</style>
</head>

<body>

<div id="filterPanel">
  <input type="text" id="speciesSearch"
         placeholder="Filter grids by species"/>
</div>

<div id="map"></div>

<script>

var map = L.map('map').setView([19.5, 75.3], 6);

L.tileLayer(
  'https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png',
  {{ attribution: '© OpenStreetMap contributors' }}
).addTo(map);

var geojsonData = {geojson_str};

function style(feature) {{
    return {{
        color: "#444",
        weight: 1,
        fillOpacity: 0
    }};
}}

function onEachFeature(feature, layer) {{

    var props = feature.properties.popup_data;

    if (!props) return;

    var content =
        "<b>" + props["Month"] + "</b><br>" +
        "Grid ID: " + props["Grid ID"] + "<br>" +
        "Observations: " + props["Observations"] + "<br><br>" +
        "<b>Top 5 Species</b><br>" +
        props["Top 5 species"].join("<br>") + "<br><br>" +
        "<b>Counts</b><br>" +
        props["Counts of top 5 species"].join(", ");

    layer.bindPopup(content);

    layer.featureData = props;
}}

var gridLayer = L.geoJSON(geojsonData, {{
    style: style,
    onEachFeature: onEachFeature
}}).addTo(map);

function applyFilter() {{

    var searchText =
        document.getElementById("speciesSearch")
        .value.toLowerCase();

    gridLayer.eachLayer(function(layer) {{

        var props = layer.featureData;

        if (!props) return;

        var speciesList =
            props["Top 5 species"]
            .join(" ")
            .toLowerCase();

        if (speciesList.includes(searchText)) {{
            layer.setStyle({{ color:"#444", weight:1 }});
        }} else {{
            layer.setStyle({{ color:"#ccc", weight:1 }});
        }}
    }});
}}

document.getElementById("speciesSearch")
    .addEventListener("input", applyFilter);

</script>
</body>
</html>
"""

    output_path = Path(f"months/{month_year}.html")

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"Grid map generated: {month_year}")

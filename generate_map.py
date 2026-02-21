import pandas as pd
import json
from pathlib import Path

def generate_map(month_year):

    csv_path = Path(f"months/{month_year}/{month_year}.csv")
    df = pd.read_csv(csv_path)

    features = []

    for _, row in df.iterrows():

        feature = {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [row["longitude"], row["latitude"]]
            },
            "properties": {
                "commonName": row["commonName"],
                "scientificName": row["scientificName"],
                "observationCount": row.get("observationCount", "X")
            }
        }

        features.append(feature)

    geojson = {
        "type": "FeatureCollection",
        "features": features
    }

    geojson_str = json.dumps(geojson)

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
         placeholder="Search species"/>
</div>

<div id="map"></div>

<script>

var map = L.map('map').setView([19.5, 75.3], 6);

L.tileLayer(
  'https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png',
  {{ attribution: '© OpenStreetMap contributors' }}
).addTo(map);

var geojsonData = {geojson_str};

var allMarkers = [];

geojsonData.features.forEach(function(feature) {{

    var coords = feature.geometry.coordinates;
    var props = feature.properties;

    var marker = L.circleMarker(
        [coords[1], coords[0]],
        {{ radius:5 }}
    );

    marker.featureData = props;

    marker.bindPopup(
        "<b>" + props.commonName + "</b><br>" +
        props.scientificName + "<br>" +
        "Count: " + (props.observationCount || "X")
    );

    marker.addTo(map);
    allMarkers.push(marker);
}});

function applyFilter() {{

    var searchText = document
        .getElementById("speciesSearch")
        .value.toLowerCase();

    allMarkers.forEach(function(marker) {{

        var species =
            marker.featureData.commonName.toLowerCase();

        var match =
            species.includes(searchText);

        if (match) {{
            marker.addTo(map);
        }} else {{
            map.removeLayer(marker);
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

    print(f"Map generated: {month_year}")

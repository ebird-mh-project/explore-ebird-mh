# explore-ebird-mh
A page displaying exploratory data from eBird for Maharashtra (Summer 2020 to Monsoon 2025). Prototype for a Species Distribution Modelling app. Will be periodically updated to add more informative details &amp; improve UI/UX. Folium/Leaflet &amp; JavaScript.

# TO-DO LIST as of 2025/12/05
* The HTML for the maps & the data for the geojson files <i>used</i> for the same were generated in Python, in a Jupyter notebook stored on my systems. Need to set up GitHub Actions to automate this process, updating the data each month by making an API call + automate the creation of the maps.
* In the first item I also need to make sure that the POP-UPS are formatted better.
* Add a small window showing what the codes for Behaviour and Observation Types mean (or simply change the codes in the html files)
* Add an About view, and option to alternate between Map view and About view. Explain the project, explain eBird, explain what the various stats mean.
* Add a summary for each season i.e. the WHOLE SEASON, not just grid-by-grid. Make this viewable on the right side. Also, automate the data analysis (+ geojson & map generation) for this (same as the maps). Summary could include a picture of the most common birds from the eBird site, along with any endangered birds observed during the season (plus, a link to learn more about the bird).
* Option to change grid colouration: plain, or based on variables (like number of observations,  IUCN status, number of migrant birds, etc)
* Turn the cursor into a little bird and make it peck when you click things, along with other aesthetic changes.

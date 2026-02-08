# explore-ebird-mh
A page displaying exploratory data from eBird for Maharashtra (Summer 2020 to Monsoon 2025). Prototype for a Species Distribution Modelling app. Will be periodically updated to add more informative details &amp; improve UI/UX. Folium/Leaflet &amp; JavaScript.  https://ebird-mh-project.github.io/explore-ebird-mh/

# TO-DO LIST as of 2026/02/08
* Complete text of About section 
* Complete the summary windows
* Turn the cursor into a little bird and make it peck when you click things, along with other aesthetic changes.
* Add a tab showing the Python notebooks where data cleaning, analysis & visualization were done (note: the notebooks in which I *actually* did this work would seem too messy if shown to the uninitiated; will need to carefully structure the "display" notebook so it is easy to understand!) 

## And what about automating the updates?
This is version 1.0 of the dashboard, as of now. The automation will be in future versions. I am starting to understand stuff like webscraping and API requests in Python, I'm actually learning it by trying to improve the summary window (figuring out how to get images from Wikipedia for each bird; the birds' name is the issue, the name in the data is not always the same as the name in the title of its Wiki page).

There's basically 2 layers of automation, one is what I'm already doing (produce maps + summary windows for each and every season; data analysis done before this), then there's a layer above that which will be in version 2.0 (stuff with GitHub Actions, API calls to get the eBird data for each month (so it'll update every month) & then automate the data cleaning, and THEN maps+summary produced). It's pretty fun to figure out. I need to improve my JavaScript / Leaflet skills a bit more, I used some assistance from ChatGPT because I *tried* on my own & just couldn't figure it out (unlike with Python, where I have more experience), but hopefully I'll "get it" more with time... I would like to have a decent grasp on JS because I want to use it for dynamic & interactive dashboards. 



# TO-DO LIST as of 2026/01/30
* Readability improvements, like formatting of pop-ups, implementing map changes as views instead of iframe, 
* Add a small window showing what the codes for Behaviour and Observation Types mean 
* Add an About view, and option to alternate between Map view and About view. Explain the project, explain eBird, explain what the various stats mean.
* Add a summary for each season i.e. the WHOLE SEASON, not just grid-by-grid. Make this viewable on the right side. Also, automate the data analysis (+ geojson & map generation) for this (same as the maps). Summary could include a picture of the most common birds from the eBird site, along with any endangered birds observed during the season (plus, a link to learn more about the bird).
* Add a summary for each season i.e. the WHOLE SEASON, not just grid-by-grid. Make this viewable on the right side. Summary could include a picture of the most common birds from the eBird site, along with any endangered birds observed during the season (plus, a link to learn more about the bird).
* Option to change grid colouration: plain, or based on variables (like number of observations,  IUCN status, number of migrant birds, etc) *[as it turned out later, this is not possible with the geojson data I currently have for version 1.0, where the point data was basically 'condensed' into the grids... I DO have data where each point is assigned to a grid & a season, and this data could probably be used to create the filter too... this will be best to implement in version 2.0 though, since I'll be making a bunch of changes to the data processing for the sake of automation]*
* Turn the cursor into a little bird and make it peck when you click things, along with other aesthetic changes.

# TO-DO LIST as of 2025/12/05
* The HTML for the maps & the data for the geojson files <i>used</i> for the same were generated in Python, in a Jupyter notebook stored on my systems. Need to set up GitHub Actions to automate this process, updating the data each month by making an API call + automate the creation of the maps.
* In the first item I also need to make sure that the POP-UPS are formatted better.
* Add a small window showing what the codes for Behaviour and Observation Types mean (or simply change the codes in the html files)

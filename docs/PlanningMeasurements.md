# Wireless Channel Measuremnets Planner

This tool provides the user a way of placing candidate coordinates for the air node through the use of markers in a map.

The order in which the markers are placed in the map is assumed to be the order in which the air node will arrive at those marker locations.




## Note on the Wireless Channel Measurements Planner

Thye purpose of this web app is to place the points where both the receiver and the transmitter will be placed on a map.

Ulitmately the placing of the transceivers depends on observing candidate locations in a map source (i.e. Google Maps, OpenStreetMap, etc). Therefore it is easier to have a tool to read the candidate locations input by the user using a map service, for post processing them in whichever task has been thought.

Unfortunately, neither ``Folium``, nor ``Ipyleaflet`` or similar python packages provide support to retrieve the marker coordinates, since they use as the core technology to interact with OpenStreetMaps a ``javascript`` library called ``Leaflet.js``, which handles the user interactions with the map. 


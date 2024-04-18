# Wireless channel measuremnets planner

This web application provides support to place ground and node coordinates, measure distances between them, get yaw anlges for the drone gimbal w.r.t to different reference system, foresee battery consumption, and graphically check PDRA-S01 zones.

## Use of the web application

You can use the web application by entering the following URL in your browser:

[https://jvvtt.github.io/wireless-meas-planner/](Wireless channel measuremnets planner)

## Hosting

The web application is hosted and deployed in Github.

## Note on the Wireless Channel Measurements Planner

Thye purpose of this web app is to place the points where both the receiver and the transmitter will be placed on a map.

Ulitmately the placing of the transceivers depends on observing candidate locations in a map source (i.e. Google Maps, OpenStreetMap, etc). Therefore it is easier to have a tool to read the candidate locations input by the user using a map service, for post processing them in whichever task has been thought.

Unfortunately, neither `Folium`, nor `Ipyleaflet` or similar python packages provide support to retrieve the marker coordinates, since they use as the core technology to interact with OpenStreetMaps a `javascript` library called `Leaflet.js`, which handles the user

interactions with the map.

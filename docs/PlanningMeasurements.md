# Wireless channel measuremnets planner

This web application provides support to place ground and node coordinates, measure distances between them, get yaw anlges for the drone gimbal w.r.t to different reference system, foresee battery consumption, and graphically check PDRA-S01 zones.

# URL for the Wireless channel measurements planner

The web application is hosted and deployed in Github. You can use the web application by entering the following URL in your browser:

[https://jvvtt.github.io/wireless-meas-planner/](Wireless channel measuremnets planner)

!!! success "Python alternatives with Map functionalities"
    Unfortunately, neither `Folium` nor `Ipyleaflet` or similar python packages provide native support to retrieve marker coordinates (i.e. drone locations, ground locations). Both packages use `Leaflet.js` to interact with OpenStreetMaps, which is a javascript library and the workarounds to execute javascript from python are not always successful. Instead of that, we develop a web app that directly uses `Leaflet.js` since it natively supports javascript.

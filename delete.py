import time
import numpy as np
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QTimer, QProcess
import folium
from  folium.plugins import realtime
from folium.utilities import JsCode
import requests

class MapWidget(QWidget):
    """
    Map test for material for mkdocstrings

    Args:
        QWidget (QWidget): Class
    """
    def __init__(self, parent=None):
        super(MapWidget, self).__init__(parent)
                       
        self.cnt = 1
        self.point1 = [60.187372669712566, 24.96109446381862]
        self.point2 = [60.18490587854025, 24.948227873431904]
        json = {"lat": 60.187372669712566, "lon": 24.96109446381862}
        self.init4(json)

        # Create a QWebEngineView object to display the map
        self.webview = QWebEngineView()
        self.webview.setHtml(self.m._repr_html_())

        # Create a layout and add the webview to it
        layout = QVBoxLayout(self)
        layout.addWidget(self.webview)
        
        # Create a QTimer object to update the polyline periodically
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.timerUpdateCoordinates)
        self.timer.start(1000)  # Update every 1000 milliseconds (1 second)
    
    def process_error(self, error):
        print("Error occurred:", error)
    
    def timerUpdateCoordinates(self):
        alfa = np.random.rand()
        self.point = np.array(self.point1)*alfa + (1-alfa)*np.array(self.point2)
        
        self.point = self.point.tolist()
        
        json = {"lat": self.point[0], "lon": self.point[1]}

        response = requests.put("http://127.0.0.1:8000/gps/update/septentrio", json=json)
    
    def init2(self):
        
        self.point1 = [60.187372669712566, 24.96109446381862]
        self.point2 = [60.18490587854025, 24.948227873431904]
        
        kw = {"color": "red", "fill": True, "radius": 5}
        
        # Create a Folium map object
        self.m = folium.Map(location=self.point1, zoom_start=14)

        folium.CircleMarker(self.point1, **kw).add_to(self.m)
        folium.CircleMarker(self.point2, **kw).add_to(self.m)
        
    def init1(self):
        self.m = folium.Map(location=[40.73, -73.94], zoom_start=12)
        self.rt = realtime.Realtime("https://raw.githubusercontent.com/python-visualization/folium-example-data/main/subway_stations.geojson",
                get_feature_id=JsCode("(f) => { return f.properties.objectid; }"),interval=10000,)
        self.rt.add_to(self.m)
    
    def init3(self):
        source = JsCode("""
        function(responseHandler, errorHandler) {
            var url = 'https://api.wheretheiss.at/v1/satellites/25544';

            fetch(url)
            .then((response) => {
                return response.json().then((data) => {
                    var { id, longitude, latitude } = data;

                    return {
                        'type': 'FeatureCollection',
                        'features': [{
                            'type': 'Feature',
                            'geometry': {
                                'type': 'Point',
                                'coordinates': [longitude, latitude]
                            },
                            'properties': {
                                'id': id
                            }
                        }]
                    };
                })
            })
            .then(responseHandler)
            .catch(errorHandler);
        }
    """)
        self.m = folium.Map()
        self.rt = realtime.Realtime(source, interval=10000)
        self.rt.add_to(self.m)
        
    def init4(self, start_point_json):
        response = requests.post("http://127.0.0.1:8000/gps/post/septentrio", json=start_point_json)
        
        time.sleep(0.05)
        url = """'http://127.0.0.1:8000/gps/get'"""
        source = JsCode("""
        function(responseHandler, errorHandler) {
            let url = """+ url+""";
            
            fetch(url)
            .then((response) => {
                    return response.json().then((data) => {
                        var {lat, lon} = data;
                        //The ID does not matter for this map, use any int
                        var id = 45
                        return {"type": "FeatureCollection",
                                "features": [{"type": "Feature",
                                              "geometry": {"type": "Point",
                                                           "coordinates": [lon, lat]
                                                        },
                                "properties": {"id": id}
                                            }]
                                };
                    })
            })
            .then(responseHandler)
            .catch(errorHandler);
        }
        """)
        self.m = folium.Map()
        self.rt = realtime.Realtime(source, interval=2000)
        self.rt.add_to(self.m)        
        
    def add_point_to_polyline(self):
        try:
            # Render again the whole map
            kw = {"color": "blue", "fill": True, "radius": 3}
            alfa = np.random.rand()
            new_point = alfa*np.array(self.point1) + (1-alfa)*np.array(self.point2)
            new_point = new_point.tolist()
            folium.CircleMarker(new_point, **kw).add_to(self.m)
            self.webview.setHtml(self.m._repr_html_())
        except KeyboardInterrupt:
            self.timer.stop()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    widget = MapWidget()
    widget.show()
    sys.exit(app.exec_())

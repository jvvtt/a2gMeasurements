import sys
import folium
from folium.plugins import Draw
from PyQt5.QtWidgets import QVBoxLayout, QApplication, QWidget, QPushButton
from PyQt5.QtWebEngineWidgets import QWebEngineView

class MapWidget(QWidget):
    """
    Map test for material for mkdocstrings

    Args:
        QWidget (QWidget): Class
    """
    def __init__(self, parent=None):
        super(MapWidget, self).__init__(parent)
                       
        self.CreateMap()

        # Create a QWebEngineView object to display the map
        self.webview = QWebEngineView()
        self.webview.setHtml(self.m._repr_html_())

        self.press_button = QPushButton("Press")
        self.press_button.clicked.connect(self.doDummyStuff)
        
        # Create a layout and add the webview to it
        layout = QVBoxLayout(self)        
        layout.addWidget(self.webview)
        layout.addWidget(self.press_button)
        
    def doDummyStuff(self):
        print(dir(self.m._repr_html_()))
        
    def CreateMap(self):
        self.m = folium.Map()
        self.panel = Draw(export=True).add_to(self.m)
    
if __name__ == '__main__':
    app = QApplication(sys.argv)
    widget = MapWidget()
    widget.show()
    sys.exit(app.exec_())
        
        
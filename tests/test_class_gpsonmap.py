from typing import Any
from PyQt5.QtCore import QDateTime, Qt, QTimer, QObject, QThread, QMutex, pyqtSignal
from PyQt5.QtWidgets import (QApplication, QCheckBox, QComboBox, QDateTimeEdit,
        QDial, QDialog, QGridLayout, QGroupBox, QHBoxLayout, QLabel, QLineEdit,
        QProgressBar, QPushButton, QRadioButton, QScrollBar, QSizePolicy,
        QSlider, QSpinBox, QStyleFactory, QTableWidget, QTabWidget, QTextEdit,
        QVBoxLayout, QWidget)

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from a2gmeasurements import RepeatTimer
from a2gUtils import GpsOnMap
import time
import sys
import numpy as np        
        
class WidgetGallery(QDialog):
    def __init__(self, parent=None):
        super(WidgetGallery, self).__init__(parent)

        self.create_GPS_visualization_panel()
        
        self.my_init_coorsd = {'LAT': 60.18592, 'LON': 24.81174 } # hi_q
        
        self.timer_emulate_periodic_fcn_call_from_gps = RepeatTimer(1, self.emulate_periodic_fcn_call_from_gps) 
        
        mainLayout = QGridLayout()
        mainLayout.addWidget(self.gps_vis_panel, 0, 0, 1, 1)
        self.setLayout(mainLayout)

    def stop_timer_emulate(self):
        self.timer_emulate_periodic_fcn_call_from_gps.cancel()
    
    def emulate_periodic_fcn_call_from_gps(self):
        """
        This function emulates each time the serial_receive fcn is called in the gps

        """
        self.my_init_coorsd['LAT'] = self.my_init_coorsd['LAT'] + np.random.randint(-1,1)*np.random.rand()/5000
        self.my_init_coorsd['LON'] = self.my_init_coorsd['LON'] + np.random.randint(-1,1)*np.random.rand()/5000

        self.mygpsonmap.show_air_moving(lat=self.my_init_coorsd['LAT'], lon=self.my_init_coorsd['LON']) 
    
    def create_GPS_visualization_panel(self):
        self.gps_vis_panel = QGroupBox('GPS visualization')
        # Create a Figure object
        fig = Figure()

        # Create a FigureCanvas widget
        canvas = FigureCanvas(fig)

        # Create a QVBoxLayout to hold the canvas
        layout = QVBoxLayout()
        layout.addWidget(canvas)

        # Set the layout of the group box
        self.gps_vis_panel.setLayout(layout)

        # Create a subplot on the Figure
        ax = fig.add_subplot(111)

        hi_q = {'LAT': 60.18592, 'LON': 24.81174 }
        self.mygpsonmap = GpsOnMap('planet_24.81,60.182_24.829,60.189.osm.pbf', canvas=canvas, fig=fig, ax=ax, air_coord=hi_q)

        #self.mygpsonmap.show_air_moving() 

if __name__ == '__main__':
#    appctxt = ApplicationContext()
    app = QApplication([])
    gallery = WidgetGallery()
    gallery.show()
    gallery.timer_emulate_periodic_fcn_call_from_gps.start()
    #gallery.init_external_objs()
    #sys.exit(appctxt.app.exec())
    sys.exit(app.exec())
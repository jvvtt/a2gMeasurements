import uvicorn
import multiprocessing
import requests
import threading
import numpy as np
import csv
import datetime
import platform
import re
import subprocess
import paramiko
import ping3
import time
import can#from fbs_runtime.application_context.PyQt5 import ApplicationContext
from serial.tools.list_ports import comports
from PyQt5.QtCore import Qt, QTimer, QObject, QThread, QMutex, pyqtSignal, QUrl
from PyQt5.QtWidgets import (QApplication, QCheckBox, QComboBox, QDialog, QGridLayout, QGroupBox, QLabel, QLineEdit,
        QPushButton, QRadioButton, QTextEdit, QVBoxLayout, QWidget, QPlainTextEdit, QToolTip, QMenu, QMenuBar, QMainWindow, QAction)
from PyQt5.QtGui import QCursor
from PyQt5.QtWebEngineWidgets import QWebEngineView
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import os
import sys
from a2gmeasurements import HelperA2GMeasurements, RepeatTimer
from a2gUtils import geocentric2geodetic, geodetic2geocentric, azimuth_difference_between_coordinates, elevation_difference_between_coordinates
import folium
from folium.plugins import realtime, Draw
from folium.utilities import JsCode

import pyqtgraph as pg

class TimerThread(QThread):
    update = pyqtSignal()

    def __init__(self, event, updatetime):
        super(TimerThread, self).__init__()
        self.stopped = event
        self.updatetime = updatetime
    
    def run(self):
        while not self.stopped.wait(self.updatetime):
            self.update.emit()

class CustomTextEdit(QTextEdit):
    def write(self, text):
        cursor = self.textCursor()
        cursor.movePosition(cursor.End)
        cursor.insertText(text)
        self.setTextCursor(cursor)
        self.ensureCursorVisible()

class SetupWindow(QDialog):
    """
    Creates a new dialog with configuration options for the user, when is pressed the ``Setup`` > ``Setup devices and more`` menu.
    """
    def __init__(self, parent=None):
        """
        Creates the PyQt5 components of the setup dialog and sets its layout with them.

        Args:
            parent (none, optional): not used. Defaults to None.
        """

        super(SetupWindow, self).__init__(parent)
        self.setWindowTitle("Setup")
        #self.setGeometry(100, 100, 300, 220)
        self.drone_static_coords_list_array = []
        self.gnd_static_coords_list_array = []

        self.droneGimbalChoiceTDMenu = QComboBox()
        self.droneGimbalChoiceTDMenu.addItems(["DJI Ronin RS2", "Gremsy H16"])

        droneGimbalChoiceLabel = QLabel("&Choose drone gimbal:")
        droneGimbalChoiceLabel.setBuddy(self.droneGimbalChoiceTDMenu)
        
        self.fm_droneGimbal_TDMenu = QComboBox()
        self.fm_droneGimbal_TDMenu.addItems(["Only elevation", "Only azimuth", "Elevation and azimuth"])

        fmdroneGimbalChoiceLabel = QLabel("&Choose drone gimbal following mode (if it will be used):")
        fmdroneGimbalChoiceLabel.setBuddy(self.fm_droneGimbal_TDMenu)

        self.fm_gndGimbal_TDMenu = QComboBox()
        self.fm_gndGimbal_TDMenu.addItems(["Only elevation", "Only azimuth", "Elevation and azimuth"])

        fmgndGimbalChoiceLabel = QLabel("&Choose ground gimbal following mode (if it will be used):")
        fmgndGimbalChoiceLabel.setBuddy(self.fm_gndGimbal_TDMenu)

        self.gnd_mobility_TDMenu = QComboBox()
        self.gnd_mobility_TDMenu.addItems(["Moving", "Static"])
        self.gnd_mobility_TDMenu.activated[str].connect(self.enable_gnd_coords_callback)

        gnd_mobility_label = QLabel("&Choose ground node mobility:")
        gnd_mobility_label.setBuddy(self.gnd_mobility_TDMenu)

        self.gnd_lat_textEdit = QLineEdit('')
        gnd_lat_label = QLabel("Enter lat of static (ground) node:")
        self.gnd_lon_textEdit = QLineEdit('')
        gnd_lon_label = QLabel("Enter lon of static (ground) node:")
        self.gnd_alt_textEdit = QLineEdit('')
        gnd_alt_label = QLabel("Enter altitude of static (ground) node:")
        
        gnd_list_coords_label = QLabel("List of static gnd coordinates:")
        self.gnd_list_coords_textEdit = QTextEdit("")
        self.gnd_list_coords_textEdit.setEnabled(False)
        
        self.button_add_gnd_coord = QPushButton("Add coordinate")
        self.button_add_gnd_coord.clicked.connect(self.setup_window_add_gnd_coord_callback)
        
        self.gnd_lat_textEdit.setEnabled(False)
        self.gnd_lon_textEdit.setEnabled(False)
        self.gnd_alt_textEdit.setEnabled(False)

        self.drone_mobility_TDMenu = QComboBox()
        self.drone_mobility_TDMenu.addItems(["Moving", "Static"])
        self.drone_mobility_TDMenu.activated[str].connect(self.enable_drone_coords_callback)

        drone_mobility_label = QLabel("&Choose drone node mobility:")
        drone_mobility_label.setBuddy(self.drone_mobility_TDMenu)

        self.drone_lat_textEdit = QLineEdit('')
        drone_lat_label = QLabel("Enter lat of static (drone) node:")
        self.drone_lon_textEdit = QLineEdit('')
        drone_lon_label = QLabel("Enter lon of static (drone) node:")
        self.drone_alt_textEdit = QLineEdit('')
        drone_alt_label = QLabel("Enter alt of static (drone) node:")
        
        drone_list_coords_label = QLabel("List of static drone coordinates:")
        self.drone_list_coords_textEdit = QTextEdit("")
        self.drone_list_coords_textEdit.setEnabled(False)
        
        self.button_add_drone_coord = QPushButton("Add coordinate")
        self.button_add_drone_coord.clicked.connect(self.setup_window_add_drone_coord_callback)
        
        self.drone_lat_textEdit.setEnabled(False)
        self.drone_lon_textEdit.setEnabled(False)
        self.drone_alt_textEdit.setEnabled(False)

        self.gnd_gps_att_offset_textEdit = QLineEdit('0')
        gnd_gps_att_offset_label = QLabel("Enter the heading offset for the ground gps:")
        
        self.ok_button = QPushButton("OK")
        self.ok_button.clicked.connect(self.accept)

        layout = QGridLayout()
        layout.addWidget(droneGimbalChoiceLabel, 0, 0, 1, 3)
        layout.addWidget(self.droneGimbalChoiceTDMenu, 0, 3, 1, 3)
        layout.addWidget(fmdroneGimbalChoiceLabel, 1, 0, 1, 3)
        layout.addWidget(self.fm_droneGimbal_TDMenu, 1, 3, 1, 3)
        layout.addWidget(fmgndGimbalChoiceLabel, 2, 0, 1, 3)
        layout.addWidget(self.fm_gndGimbal_TDMenu, 2, 3, 1, 3)

        layout.addWidget(gnd_mobility_label, 3, 0, 1, 3)
        layout.addWidget(self.gnd_mobility_TDMenu, 3, 3, 1, 3)
        layout.addWidget(gnd_lat_label, 4, 0, 1, 3)
        layout.addWidget(self.gnd_lat_textEdit, 4, 3, 1, 3)
        layout.addWidget(gnd_lon_label, 5, 0, 1, 3)
        layout.addWidget(self.gnd_lon_textEdit, 5, 3, 1, 3)
        layout.addWidget(gnd_alt_label, 6, 0, 1, 3)
        layout.addWidget(self.gnd_alt_textEdit, 6, 3, 1, 3)
        
        layout.addWidget(gnd_list_coords_label, 7, 0, 1, 3)
        layout.addWidget(self.button_add_gnd_coord, 8, 0, 1, 3)
        layout.addWidget(self.gnd_list_coords_textEdit, 7, 3, 2, 3)   

        layout.addWidget(drone_mobility_label, 9, 0, 1, 3)
        layout.addWidget(self.drone_mobility_TDMenu, 9, 3, 1, 3)
        layout.addWidget(drone_lat_label, 10, 0, 1, 3)
        layout.addWidget(self.drone_lat_textEdit, 10, 3, 1, 3)
        layout.addWidget(drone_lon_label, 11, 0, 1, 3)
        layout.addWidget(self.drone_lon_textEdit, 11, 3, 1, 3)
        layout.addWidget(drone_alt_label, 12, 0, 1, 3)
        layout.addWidget(self.drone_alt_textEdit, 12, 3, 1, 3)
        
        layout.addWidget(drone_list_coords_label, 13, 0, 1, 3)
        layout.addWidget(self.button_add_drone_coord, 14, 0, 1, 3)
        layout.addWidget(self.drone_list_coords_textEdit, 13, 3, 2, 3)        
        
        layout.addWidget(gnd_gps_att_offset_label, 15, 0, 1, 3)
        layout.addWidget(self.gnd_gps_att_offset_textEdit, 15, 3, 1, 3)
                         
        layout.addWidget(self.ok_button, 16, 0, 1, 6)
        self.setLayout(layout)  

    def setup_window_add_drone_coord_callback(self):
        self.drone_static_coords_list_array.append([float(self.drone_lat_textEdit.text()), 
                                                    float(self.drone_lon_textEdit.text()), 
                                                    float(self.drone_alt_textEdit.text())])
        
        if (self.drone_list_coords_textEdit.toPlainText() == ""):
            newText = f"LAT: {self.drone_lat_textEdit.text()}, LON: {self.drone_lon_textEdit.text()}, ALT: {self.drone_alt_textEdit.text()}"
        else:
            newText = self.drone_list_coords_textEdit.toPlainText() + "\n" + f"LAT: {self.drone_lat_textEdit.text()}, LON: {self.drone_lon_textEdit.text()}, ALT: {self.drone_alt_textEdit.text()}"
        self.drone_list_coords_textEdit.setText(newText)
        
    def setup_window_add_gnd_coord_callback(self):
        self.gnd_static_coords_list_array.append([float(self.gnd_lat_textEdit.text()), 
                                                    float(self.gnd_lon_textEdit.text()), 
                                                    float(self.gnd_alt_textEdit.text())])
        
        if (self.gnd_list_coords_textEdit.toPlainText() == ""):
            newText = f"LAT: {self.gnd_lat_textEdit.text()}, LON: {self.gnd_lon_textEdit.text()}, ALT: {self.gnd_alt_textEdit.text()}"
        else:
            newText = self.gnd_list_coords_textEdit.toPlainText() + "\n" + f"LAT: {self.gnd_lat_textEdit.text()}, LON: {self.gnd_lon_textEdit.text()}, ALT: {self.gnd_alt_textEdit.text()}"
        self.gnd_list_coords_textEdit.setText(newText)
    
    def enable_gnd_coords_callback(self, myinput):
        """
        Enables the ground coordinates QLineEdits when the user inputs a ``Static`` mobility for the ground node in the Setup dialog.

        Args:
            myinput (str): ground node mobility. Either ``Static`` or ``Moving``.
        """

        if myinput == "Static":
            self.gnd_lat_textEdit.setEnabled(True)
            self.gnd_lon_textEdit.setEnabled(True)
            self.gnd_alt_textEdit.setEnabled(True)
        elif myinput == "Moving":
            self.gnd_lat_textEdit.setEnabled(False)
            self.gnd_lon_textEdit.setEnabled(False)
            self.gnd_alt_textEdit.setEnabled(False)
    
    def enable_drone_coords_callback(self, myinput):
        """
        Enables the drone coordinates QLineEdits when the user inputs a ``Static`` mobility for the drone node in the Setup dialog.

        Args:
            myinput (str): drone node mobility. Either ``Static`` or ``Moving``.
        """

        if myinput == "Static":
            self.drone_lat_textEdit.setEnabled(True)
            self.drone_lon_textEdit.setEnabled(True)
            self.drone_alt_textEdit.setEnabled(True)
        elif myinput == "Moving":
            self.drone_lat_textEdit.setEnabled(False)
            self.drone_lon_textEdit.setEnabled(False)
            self.drone_alt_textEdit.setEnabled(False)

class WidgetGallery(QMainWindow):
    """
    Python class responsible for creating the main window of the GUI and all the functionality to handle user interaction.
     
    """        
    def __init__(self, parent=None):
        """
        Calls the functions to create some class attributes and the menu bar with its associated callbacks.

        Args:
            parent (none, optional): not used, but required. Defaults to None.
        """

        super(WidgetGallery, self).__init__(parent)
        
        self.uvicorn_server_process = threading.Thread(target=self.start_uvicorn_server)
        self.uvicorn_server_process.start()
    
        self.setWindowTitle("A2G Measurements Center")

        self.init_constants()

        self.createMenu()
         
        self.dummyWidget = QWidget()
        self.setCentralWidget(self.dummyWidget)
        
        #self.setLayout(mainLayout)

        self.showMaximized()
        
    def start_uvicorn_server(self):
        """
        Callback to start the uvicorn server responsible for connecting to the OpenStreetMap interface to plot GPS coordinates.
        """
        uvicorn.run("gpsRESTHandler:app", host="127.0.0.1", port=8000, log_level="info")
    
    def init_constants(self):
        """
        Creates some class attributes. 
         
        The ``STATIC_DRONE_IP_ADDRESS`` is to set a static IP address for the drone. This IP address must be assigned to the drone from the router configuration interface (this IP address was set for the drone on the Archer AX router)
         
        """
        # Parameters of the GUI
        self.debug_cnt_1 = 1
        self.STATIC_DRONE_IP_ADDRESS = '192.168.0.157'
        self.number_lines_log_terminal = 100
        self.log_terminal_txt = ""
        self.remote_drone_conn = None
        
        self.SUCCESS_PING_DRONE = False
        self.SUCCESS_SSH = False
        self.SUCCESS_DRONE_FPGA = False
        self.SUCCESS_DRONE_GPS = False
        self.SUCCES_DRONE_GIMBAL = False
        self.SUCCESS_GND_FPGA = False
        self.SUCCESS_GND_GIMBAL = False
        self.SUCCESS_GND_GPS = False
        
        self.url_get_map = """'http://127.0.0.1:8000/gps/get'"""
        self.url_post_map = "http://127.0.0.1:8000/gps/post/septentrio"
        self.url_put_map = "http://127.0.0.1:8000/gps/update/septentrio"

    def showCentralWidget(self):
        """
        Creates and shows the panels of the main window according to grid layout defined in this function.
        """
        
        #self.original_stdout = sys.stdout
        self.create_check_connections_panel()
        #self.create_log_terminal()
        self.create_Gimbal_GND_panel()
        self.create_Gimbal_AIR_panel()
        self.create_fpga_and_sivers_panel()
        self.create_Planning_Measurements_panel()
        self.create_GPS_visualization_panel()
        self.create_pap_plot_panel()
        
        mainLayout = QGridLayout()
        mainLayout.addWidget(self.checkConnPanel, 0, 0, 1 , 4)
        mainLayout.addWidget(self.gimbalTXPanel, 1, 0, 3, 1)
        mainLayout.addWidget(self.gimbalRXPanel, 1, 1, 3, 1)
        mainLayout.addWidget(self.fpgaAndSiversSettingsPanel, 1, 2, 3, 2)
        mainLayout.addWidget(self.papPlotPanel, 4, 0, 7, 2)
        mainLayout.addWidget(self.gps_vis_panel, 4, 2, 7, 2)
        mainLayout.addWidget(self.planningMeasurementsPanel, 11, 0, 2, 2)
        #mainLayout.addWidget(self.log_widget, 11, 2, 2, 2)
        #self.write_to_log_terminal('Welcome to A2G Measurements Center!')
    
        self.dummyWidget.setLayout(mainLayout)
    
    def showSetupMenu(self):
        """
        Creates an instance of the SetupWindow class (a Setup dialog), and create attributes for this class with the values the user input in the Setup dialog.
        """
        setupWin = SetupWindow()
        result = setupWin.exec_()
        
        self.drone_static_coords_list = setupWin.drone_static_coords_list_array
        self.gnd_static_coords_list = setupWin.gnd_static_coords_list_array
        
        # Save the gps attitude offset for both nodes
        self.gnd_gps_att_offset = setupWin.gnd_gps_att_offset_textEdit
        
        self.droneGimbalChoice = setupWin.droneGimbalChoiceTDMenu.currentText()
        
        if setupWin.fm_droneGimbal_TDMenu.currentText() == "Only elevation":
            self.fm_drone_gimbal = {'FMODE': 0x01}
        elif setupWin.fm_droneGimbal_TDMenu.currentText() == "Only azimuth":
            self.fm_drone_gimbal = {'FMODE': 0x02}
        elif setupWin.fm_droneGimbal_TDMenu.currentText() == "Elevation and azimuth":
            self.fm_drone_gimbal = {'FMODE': 0x00}
        
        if setupWin.fm_gndGimbal_TDMenu.currentText() == "Only elevation":
            self.fm_gnd_gimbal = {'FMODE': 0x01}
        elif setupWin.fm_gndGimbal_TDMenu.currentText() == "Only azimuth":
            self.fm_gnd_gimbal = {'FMODE': 0x02}
        elif setupWin.fm_gndGimbal_TDMenu.currentText() == "Elevation and azimuth":
            self.fm_gnd_gimbal = {'FMODE': 0x00}

        if setupWin.gnd_mobility_TDMenu.currentText() == "Static":
            self.gnd_mobility = "Static"
            try:
                self.static_gnd_coords = [float(setupWin.gnd_lat_textEdit.text()), 
                                          float(setupWin.gnd_lon_textEdit.text()),
                                          float(setupWin.gnd_alt_textEdit.text())] # lat, lon, altitude above sea level
            except Exception as e:
                print("[DEBUG]: Wrong input ground coords OR no input ground coords")
                print("[DEBUG]: Enter again the ground coordinates correctly")
                return
        else: 
            self.gnd_mobility = "Moving"
        if setupWin.drone_mobility_TDMenu.currentText() == "Static":
            self.drone_mobility = "Static"
            try:
                self.static_drone_coords = [float(setupWin.drone_lat_textEdit.text()), 
                                            float(setupWin.drone_lon_textEdit.text()),
                                            float(setupWin.drone_alt_textEdit.text())] # lat, lon
            except Exception as e:
                print("[DEBUG]: Wrong input drone coords OR no input drone coords")
                print("[DEBUG]: Enter again the drone coordinates correctly")
                return
        else:
            self.drone_mobility = "Moving"

        # Remove a previous layout to set it again
        if self.dummyWidget.layout() is not None:
            del self.dummyWidget
            self.setCentralWidget(None)
            self.dummyWidget = QWidget()
            self.setCentralWidget(self.dummyWidget)
            self.init_constants()
        self.showCentralWidget()
        
        self.setupDevicesAndMoreAction.setDisabled(True)
            
    def createMenu(self):
        """
        Creates the menu bar and associates the callback functions for when the user clicks on each of the menu items.          
        """
        
        # Place the menus and actions here
        menuBar = QMenuBar()
        self.setMenuBar(menuBar)
        setupMenu = menuBar.addMenu("&Setup")
        threadsMenu = menuBar.addMenu("&Threads")
        
        self.setupDevicesAndMoreAction = QAction("&Setup devices and more", self)
        setupMenu.addAction(self.setupDevicesAndMoreAction)        
        self.setupDevicesAndMoreAction.triggered.connect(self.showSetupMenu)
        
        self.start_gnd_gimbal_fm_action = QAction("Start GND gimbal following its pair", self)
        threadsMenu.addAction(self.start_gnd_gimbal_fm_action)
        self.start_gnd_gimbal_fm_action.triggered.connect(self.start_thread_gnd_gimbal_fm)
        self.start_gnd_gimbal_fm_action.setDisabled(True)
        
        self.stop_gnd_gimbal_fm_action = QAction("Stop GND gimbal following its pair", self)
        threadsMenu.addAction(self.stop_gnd_gimbal_fm_action)
        self.stop_gnd_gimbal_fm_action.triggered.connect(self.stop_thread_gnd_gimbal_fm)
        self.stop_gnd_gimbal_fm_action.setDisabled(True)
        
        self.start_drone_gimbal_fm_action = QAction("Start DRONE gimbal following its pair", self)
        threadsMenu.addAction(self.start_drone_gimbal_fm_action)
        self.start_drone_gimbal_fm_action.triggered.connect(self.start_thread_drone_gimbal_fm)
        self.start_drone_gimbal_fm_action.setDisabled(True)
        
        self.stop_drone_gimbal_fm_action = QAction("Stop DRONE gimbal following its pair", self)
        threadsMenu.addAction(self.stop_drone_gimbal_fm_action)
        self.stop_drone_gimbal_fm_action.triggered.connect(self.stop_thread_drone_gimbal_fm)
        self.stop_drone_gimbal_fm_action.setDisabled(True)
        
        self.start_gps_visualization_action = QAction("Start GPS visualization", self)
        threadsMenu.addAction(self.start_gps_visualization_action)
        self.start_gps_visualization_action.triggered.connect(self.start_thread_gps_visualization)
        self.start_gps_visualization_action.setDisabled(False)
        
        self.stop_gps_visualization_action = QAction("Stop GPS visualization", self)
        threadsMenu.addAction(self.stop_gps_visualization_action)
        self.stop_gps_visualization_action.triggered.connect(self.stop_thread_gps_visualization)
        self.stop_gps_visualization_action.setDisabled(True)
    
    def start_thread_gnd_gimbal_fm(self):
        """
        Creates and starts a timer thread (periodical callback) to send periodically the ``FOLLOWGIMBAL`` command to the drone node, for (this) ground node gimbal to follow the drone node location. 
        """
        
        if hasattr(self, 'myhelpera2g'):
            self.update_time_gimbal_follow = 1
            self.stop_event_gimbal_follow_thread = threading.Event()
            self.periodical_gimbal_follow_thread = TimerThread(self.stop_event_gimbal_follow_thread, self.update_time_gimbal_follow)

            if self.drone_mobility == "Moving":
                self.periodical_gimbal_follow_thread.update.connect(lambda: self.myhelpera2g.socket_send_cmd(type_cmd='FOLLOWGIMBAL', data=self.fm_gnd_gimbal))
            elif self.drone_mobility == "Static":
                x,y,z = geodetic2geocentric(self.static_drone_coords[0], self.static_drone_coords[1], self.static_drone_coords[2])
                data = {'X': x, 'Y': y, 'Z': z, 'FMODE': self.fm_gnd_gimbal['FMODE']}
                self.periodical_gimbal_follow_thread.update.connect(lambda: self.myhelpera2g.process_answer_get_gps(data=data))
            self.periodical_gimbal_follow_thread.start()
            
        self.start_gnd_gimbal_fm_action.setEnabled(False)
        self.stop_gnd_gimbal_fm_action.setEnabled(True)
        
    def stop_thread_gnd_gimbal_fm(self):
        """
        Stops the timer thread to send periodic ``FOLLOWGIMBAL`` commands to the drone node.
        """

        if hasattr(self, 'periodical_gimbal_follow_thread'):
            if self.periodical_gimbal_follow_thread.isRunning():
                self.stop_event_gimbal_follow_thread.set()
        
        self.start_gnd_gimbal_fm_action.setEnabled(True)
        self.stop_gnd_gimbal_fm_action.setEnabled(False)
        
    def start_thread_drone_gimbal_fm(self):
        """
        Sets the ``drone_fm_flag`` flag in drone's HelperA2GMeasurements class instance, so that the drone periodically send a ``FOLLOWGIMBAL`` command to the ground node, for it (drone) node's gimbal to follow the location of the ground node.
         
        The periodical ``FOLLOWGIMBAL`` command is sent from the drone node main script (``drone_main.py``).
        """

        if hasattr(self, 'myhelpera2g'):
            if self.gnd_mobility == "Moving":
                data = {'X': 0, 'Y': 0, 'Z': 0, 'FMODE': self.fm_drone_gimbal['FMODE'], 'MOBILITY': 0x00}
            elif self.gnd_mobility == "Static":
                x,y,z = geodetic2geocentric(self.static_gnd_coords[0], self.static_gnd_coords[1], self.static_gnd_coords[2])
                data = {'X': x, 'Y': y, 'Z': z, 'FMODE': self.fm_drone_gimbal['FMODE'], 'MOBILITY': 0x01}
            self.myhelpera2g.socket_send_cmd(type_cmd='SETREMOTEFMFLAG', data=data)
        
        self.start_drone_gimbal_fm_action.setEnabled(False)
        self.stop_drone_gimbal_fm_action.setEnabled(True)
        
    def stop_thread_drone_gimbal_fm(self):
        """
        Unsets ``drone_fm_flag`` in drone's HelperA2GMeasurements class instance, so that the drone's gimbal stops following ground node location.
        """
        if hasattr(self, 'myhelpera2g'):
            self.myhelpera2g.socket_send_cmd(type_cmd='SETREMOTESTOPFM')

        self.start_drone_gimbal_fm_action.setEnabled(True)
        self.stop_drone_gimbal_fm_action.setEnabled(False)
        
    def start_thread_gps_visualization(self):
        """
        Creates and starts a timer thread (repeating callback) to display in the GPS panel updated gps coordinates of drone's location.
         
        NOTE: *the callback ``periodical_gps_display_callback`` works as expected with synthetic gps coordinates. However, this function has not been tested with the actual gps and thus, minor bugs might appear*
        """
        #if hasattr(self, 'myhelpera2g'):   
        self.update_vis_time_gps = 1
            
        self.periodical_gps_display_thread = QTimer(self)
        self.periodical_gps_display_thread.timeout.connect(self.periodical_gps_display_callback)
        self.periodical_gps_display_thread.start(1000*self.update_vis_time_gps)  
        
        self.start_gps_visualization_action.setEnabled(False)
        self.stop_gps_visualization_action.setEnabled(True)
        
    def stop_thread_gps_visualization(self):
        """
        Stops the timer thread responsible for display gps coordinates in the GPS panel.
        """
        if self.periodical_gps_display_thread.isActive():
            self.periodical_gps_display_thread.stop()
        
        self.start_gps_visualization_action.setEnabled(True)
        self.stop_gps_visualization_action.setEnabled(False)

    def check_if_ssh_2_drone_reached(self, drone_ip, username, password):
        """
        Checks if it is possible to ping and establish an SSH connection betwwen the host computer of the ground node and the host computer of the drone node.

        Error checking of the input parameters SHOULD BE DONE by the caller function.

        Args:
            drone_ip (str): drone's IP address for the WiFi interface.
            username (str): SSH username
            password (str): SSH password

        Returns:
            success_ping_network (bool): True if drone node is reachable.
            success_air_node_ssh (bool): True if ssh connection can be established.
            success_drone_fpga (bool): True if rfsoc on drone is detected.
        """
        
        try:
            success_ping_network = ping3.ping(drone_ip, timeout=10)
        except Exception as e:
            print("[DEBUG]: Error in ping ", e)
            success_ping_network = False
        
        #if success_ping_network is not None:
        if success_ping_network:
            success_ping_network = True
            print("[DEBUG]: DRONE-AP-GND Network is reachable")
            if self.remote_drone_conn is None:
                try:
                    remote_drone_conn = paramiko.SSHClient()
                    remote_drone_conn.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                    remote_drone_conn.connect(drone_ip, username=username, password=password)
                    print("[DEBUG]: SSH connection to DRONE is successful.")            
                except paramiko.AuthenticationException:
                    print("SSH Authentication failed. Please check your credentials.")
                    success_air_node_ssh = False
                    self.remote_drone_conn = None
                    success_drone_fpga = None
                    return success_ping_network, success_air_node_ssh, success_drone_fpga
                except paramiko.SSHException as ssh_exception:
                    print(f"Unable to establish SSH connection: {ssh_exception}")
                    success_air_node_ssh = False
                    self.remote_drone_conn = None
                    success_drone_fpga = None
                    return success_ping_network, success_air_node_ssh, success_drone_fpga
                except Exception as e:
                    print(f"An error occurred: {e}")
                    success_air_node_ssh = False
                    self.remote_drone_conn = None
                    success_drone_fpga = None
                    return success_ping_network, success_air_node_ssh, success_drone_fpga

                self.remote_drone_conn = remote_drone_conn

            # Will execute either if 'try' statemente success or if self.remote_drone_conn is precisely None
            success_air_node_ssh = True            
            success_drone_fpga = self.check_if_drone_fpga_connected()
        else:
            print("[DEBUG]: DRONE-AP-GND Network is NOT reachable")
            success_ping_network = False
            success_air_node_ssh = None
            success_drone_fpga = None
            self.remote_drone_conn = None
        
        return success_ping_network, success_air_node_ssh, success_drone_fpga
    
    def check_if_drone_fpga_connected(self, drone_fpga_static_ip_addr='10.1.1.40'):
        """
        Checks if the rfsoc is detected on the drone. 
         
        Caller function SHOULD check first if there is an SSH connection.

        Args:
            drone_fpga_static_ip_addr (str, optional): drone's RFSoC IP address for the Ethernet interface. Defaults to '10.1.1.40'.

        Returns:
            success_drone_fpga (bool): True if the ping to the rfsoc IP address (Ethernet interface) is replied.
        """
        
        # Execute the command and obtain the input, output, and error streams
        stdin, stdout, stderr = self.remote_drone_conn.exec_command('ping ' + drone_fpga_static_ip_addr)

        # Read the output from the command
        output = stdout.read().decode('utf-8')
        error = stderr.read().decode('utf-8')

        expected_str_out = "Reply from " + drone_fpga_static_ip_addr
        # Print the output and error, if any
        if expected_str_out in output:
            print("[DEBUG]: RFSoC detected at DRONE node")
            success_drone_fpga = True
        else:
            success_drone_fpga = False
        if error:
            print(f"Command error:\n{error}")
            response_drone_fpga = None
        
        return success_drone_fpga
    
    def check_if_gnd_fpga_connected(self, gnd_fpga_static_ip_addr='10.1.1.30'):
        """
        Check if the rfsoc is detected on the ground node.

        Args:
            gnd_fpga_static_ip_addr (str, optional): ground's RFSoC IP address for the Ethernet interface. Defaults to '10.1.1.30'.

        Returns:
            success_ping_gnd_fpga (bool): True if ping is successful, False otherwise.
        """
        
        try:
            success_ping_gnd_fpga = ping3.ping(gnd_fpga_static_ip_addr, timeout=7)
        except Exception as e:
            print("[DEBUG]: Error in ping ", e)
            print("[DEBUG]: RFSoC is NOT detected at GND node")
            success_ping_gnd_fpga = False
            return
        
        if success_ping_gnd_fpga is not None or success_ping_gnd_fpga:
            print("[DEBUG]: RFSoC is detected at GND node")
            success_ping_gnd_fpga = True
        else:
            print("[DEBUG]: RFSoC is NOT detected at GND node")
            success_ping_gnd_fpga = False
        
        return success_ping_gnd_fpga
    
    def check_if_drone_gimbal_connected(self):
        """
        Checks if a gimbal (Ronin RS2 or Gremsy H16) is connected to the host computer of the drone node.

        Returns:
            success_drone_gimbal (bool): True if the gimbal is detected, False if not. None if an error appeared.
        """
        if self.remote_drone_conn is None:
            success_drone_gimbal = None
            print('[DEBUG]: No SSH connection to drone detected. The drone gps connection check can not be done.')
        else:
            try:
                stdin, stdout, stderr = self.remote_drone_conn.exec_command('PowerShell')
                stdin.channel.send("Get-PnpDevice -PresentOnly | Where-Object { $_.InstanceId -match '^USB' } | Format-List\n")
                stdin.channel.shutdown_write()
                usb_list_str = stdout.read().decode('utf-8')

                # Exit the PowerShell
                stdin, stdout, stderr = self.remote_drone_conn.exec_command('exit')
            except Exception as e:
                print("[DEBUG]: Error encountered executing the Gimbal check commands on drone")
                print("[DEBUG]: ", e)
                success_drone_gimbal = None
            else:
                if self.droneGimbalChoice == "DJI Ronin RS2":
                    if 'PCAN-USB' in usb_list_str:
                        success_drone_gimbal = True
                        print("[DEBUG]: Ronin RS2 is detected at DRONE")
                    else:
                        success_drone_gimbal = False
                        print("[DEBUG]: Ronin RS2 is NOT detected at DRONE")
                elif self.droneGimbalChoice == "Gremsy H16":
                    if 'USB Serial Converter' in usb_list_str:
                        success_drone_gimbal = True
                        print("[DEBUG]: Gremsy Gimbal is detected at DRONE")
                    else:
                        success_drone_gimbal = False
                        print("[DEBUG]: Gremsy Gimbal is NOT detected at DRONE")
                
        return success_drone_gimbal

    def check_if_gnd_gimbal_connected(self):
        """
        Checks if a Ronin RS2 gimbal is connected to the host computer of the ground node.
        
        Returns:
            success_gnd_gimbal (bool): True if a PCAN device is detected, False otherwise.
        """
               
        try:
            # Check if gimbal is connected by looking if connection is established
            bus = can.interface.Bus(interface="pcan", channel="PCAN_USBBUS1", bitrate=1000000)
        except Exception as e:
            success_gnd_gimbal = False
        else:
            bus.shutdown()
            del bus
            success_gnd_gimbal = True
        
        return success_gnd_gimbal
    
    def check_if_server_running_drone_fpga(self):
        """
        Checks if the server.py daemon is running on drone's RFSoC (the PS of the RFSoC). If it is not running, this function starts it.
        
        ASSUMES DRONE RFSOC IP STATIC ADDR FOR ETH INTERFACE IS 10.1.1.40 (THIS IS THE DEFAULT SETUP)

        Returns:
            success_server_drone_fpga (bool): True if the server.py daemon is running. False if not. None if the daemon could not be started.
        """
        
        if self.remote_drone_conn is None:
            print('[DEBUG]: No SSH connection to drone detected. The server-running-on-drone check can not be done.')
            success_server_drone_fpga = False
        else:
            try:
                shell = self.remote_drone_conn.invoke_shell()
                while(shell.recv_ready() == False):
                    time.sleep(0.1)
                out_now = shell.recv(65535).decode('utf-8')
                
                shell.send("ssh xilinx@10.1.1.40\r\n")
                while(shell.recv_ready() == False):
                    time.sleep(0.1)
                out_now = shell.recv(65535).decode('utf-8')

                aux = "Permission denied, please try again"
                cnt=1
                while(("Permission denied, please try again" in aux) and cnt<10):
                    shell.send("xilinx\r\n")
                    while(shell.recv_ready() == False):
                        time.sleep(0.1)
                    out_now = shell.recv(65535).decode('utf-8')
                    aux = out_now
                    cnt = cnt +1
                if cnt == 10:
                    print("[DEBUG]: Unsuccesfull check of drone fpga server. Please CHECK IT MANUALLY on the drone")
                    success_server_drone_fpga = False
                    return success_server_drone_fpga

                aux = "xilinx: command not found"
                cnt=1
                while(("xilinx: command not found" in aux) and cnt<10):
                    shell.send("ps aux | grep mmwsdr\r\n")
                    while(shell.recv_ready() == False):
                        time.sleep(0.1)
                    out_now = shell.recv(65535).decode('utf-8')
                    aux=out_now
                    cnt=cnt+1
                if cnt == 10:
                    print("[DEBUG]: Unsuccesfull check of drone fpga server. Please CHECK IT MANUALLY on the drone")
                    success_server_drone_fpga = False
                    return success_server_drone_fpga
                
                #shell.close()
            except Exception as e:
                print(f"[DEBUG]:Error when trying to check if server is running on drone fpga: {e}")
                success_server_drone_fpga = None
                return success_server_drone_fpga
            
            if 'server.py'in out_now and 'run.sh' in out_now:
                print("[DEBUG]: Server script is running on DRONE fpga")
            else:
                print("[DEBUG]: Server script is not running on DRONE fpga")
                print("[DEBUG]: Starting server daemon on DRONE fpga")
                try:
                    # The shell is not closed                    
                    shell.send("cd jupyter_notebook/mmwsdr\r\n")
                    while(shell.recv_ready() == False):
                        time.sleep(0.1)
                    out_now = shell.recv(65535).decode('utf-8')

                    shell.send("sudo ./run.sh\r\n")
                    while(shell.recv_ready() == False):
                        time.sleep(0.1)
                    out_now = shell.recv(65535).decode('utf-8')

                    shell.send("xilinx\r\n")
                    while(shell.recv_ready() == False):
                        time.sleep(0.1)
                    out_now = shell.recv(65535).decode('utf-8')

                    shell.close()

                    print("[DEBUG]: Server daemon on drone fpga has started")
                    success_server_drone_fpga = True
                except Exception as e:
                    print(f"This error occurred when trying to init daemon server on drone fpga: {e}")
                    success_server_drone_fpga = None
                    return success_server_drone_fpga
        return success_server_drone_fpga

    def check_if_server_running_gnd_fpga(self):
        """
        Checks if the server.py daemon is running on ground's RFSoC (the PS of the RFSoC). If it is not running, this function starts it.
        
        ASSUMES GROUND RFSOC IP STATIC ADDR FOR ETH INTERFACE IS 10.1.1.30 (THIS IS THE DEFAULT SETUP)

        Returns:
            success_server_gnd_fpga (bool): True if the server.py daemon is running on ground's RFSoC. False otherwise.
        """

        try:
            conn_gnd_fpga = paramiko.SSHClient()
            conn_gnd_fpga.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            conn_gnd_fpga.connect('10.1.1.30', username='xilinx', password='xilinx')
        except Exception as e:
            print(f"This error occurred when trying to check if server is running on GND fpga: {e}")
            success_server_gnd_fpga = False
            return success_server_gnd_fpga
        try:
            stdin, stdout, stderr = conn_gnd_fpga.exec_command('ps aux | grep mmwsdr')
            output = stdout.read().decode()

            if stderr.read().decode() == '' and 'server.py' in output and 'run.sh' in output:
                print("[DEBUG]: Server script is running on GND fpga")
            else:
                print("[DEBUG]: Server script is not running on GND fpga")
                conn_gnd_fpga.exec_command('cd jupyter_notebooks/mmwsdr')
                stdin, stdout, stderr = conn_gnd_fpga.exec_command('sudo ./run.sh')
                stdin.channel.send("xilinx\n")
                stdin.channel.shutdown_write()
                print("[DEBUG]: GND node has started the Server Daemon in its FPGA")
        except Exception as e:
            print("[DEBUG]: Could not check if Server script is running in this node FPGA")
            success_server_gnd_fpga = False
            return success_server_gnd_fpga
        
        success_server_gnd_fpga = True

        # Close this connection
        conn_gnd_fpga.close()

        return success_server_gnd_fpga

    def check_if_gnd_gps_connected(self):
        """
        Checks if a Septentrio gps is connected to the host computer of the ground node.

        Returns:
            success_gnd_gps (bool): True if a gps is detected, False otherwise.
        """
        
        tmp = []
        for (_, desc, _) in sorted(comports()):
            tmp.append("Septentrio" in desc)
        if any(tmp):
            success_gnd_gps = True
            print("[DEBUG]: GPS is detected at GND")
        else:
            success_gnd_gps = False
            print("[DEBUG]: GPS is NOT detected at GND")
            
        return success_gnd_gps        

    def check_if_drone_gps_connected(self):
        """
        Checks if a Septentrio gps is connected to the host computer of the drone node.
         
        Requires that there is a SSH connection already established.

        Returns:
            success_drone_gps (bool): True if connected, False if not, None if no SSH connection.
        """
        
        # Double check
        if self.remote_drone_conn is None:
            success_drone_gps = None
            print('[DEBUG]: No SSH connection to drone detected. The drone gps connection check can not be done.')
        else:
            try:
                stdin, stdout, stderr = self.remote_drone_conn.exec_command('PowerShell')
                stdin.channel.send("Get-PnpDevice -PresentOnly | Where-Object { $_.InstanceId -match '^USB' } | Format-List\n")
                stdin.channel.shutdown_write()
                usb_list_str = stdout.read().decode('utf-8')

                # Exit the PowerShell
                stdin, stdout, stderr = self.remote_drone_conn.exec_command('exit')
            except Exception as e:
                print("[DEBUG]: Error encountered executing the GPS check commands on drone")
                print("[DEBUG]: ", e)
                success_drone_gps = None
            else:
                if 'Septentrio' in usb_list_str:
                    success_drone_gps = True
                    print("[DEBUG]: GPS is detected at DRONE")
                else:
                    success_drone_gps = False
                    print("[DEBUG]: GPS is NOT detected at DRONE")                

        return success_drone_gps
    
    def get_gnd_ip_node_address(self):
        """
        Gets the IP address ground's node WiFi interface.
        
        Caller function IS RESPONSIBLE for checking if there is a WiFi operating. 
        """
        
        if platform.system() == "Windows":
            ifconfig_info = subprocess.Popen(["ipconfig"], stdout=subprocess.PIPE)
        else:
            ifconfig_info = subprocess.Popen(["ifconfig"], stdout=subprocess.PIPE)
        out, err = ifconfig_info.communicate()
        stdout_str = out.decode()

        pattern = r'inet\s+\d+.\d+.\d+.\d+'        
        
        try:
            # This is how the IP address should appear, as the GND-DRONE connection is wireless through an AP
            stdout_str_split = stdout_str.split('wlan0: ')
            
            gnd_ip_addr = re.findall(pattern, stdout_str_split[-1])
            gnd_ip_addr = gnd_ip_addr[0].split('inet ')
            gnd_ip_addr = gnd_ip_addr[-1]
        except Exception as e:
            print("[DEBUG]: Error detecting the GND IP address ", e)
        else:
            self.GND_ADDRESS = gnd_ip_addr

    def check_status_all_devices(self):
        """
        Callback for when user presses the "Check" button. Gets the connection status of all devices.
        """
        
        pattern_ip_addresses = r'[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}'
        self.DRONE_ADDRESS = self.air_ip_addr_value_text_edit.text()
        is_ip_addr = bool(re.match(pattern_ip_addresses, self.DRONE_ADDRESS))

        # Input error checking
        if self.DRONE_ADDRESS == '' or not is_ip_addr:
            print('[DEBUG]: No DRONE or incorrect IP address supplied')
            self.network_exists_label_modifiable.setText(str(None))
            self.ssh_conn_gnd_2_drone_label_modifiable.setText(str(None))
            self.drone_rfsoc_conn_label_modifiable.setText(str(None))
        else:
            SUCCESS_PING_DRONE, SUCCESS_SSH, SUCCESS_DRONE_FPGA = self.check_if_ssh_2_drone_reached(self.DRONE_ADDRESS, "manifold-uav-vtt", "mfold2208")
            SUCCESS_DRONE_GPS = self.check_if_drone_gps_connected()
            SUCCES_DRONE_GIMBAL = self.check_if_drone_gimbal_connected()
            self.network_exists_label_modifiable.setText(str(SUCCESS_PING_DRONE))
            self.ssh_conn_gnd_2_drone_label_modifiable.setText(str(SUCCESS_SSH))
            self.drone_rfsoc_conn_label_modifiable.setText(str(SUCCESS_DRONE_FPGA))
            self.drone_gps_conn_label_modifiable.setText(str(SUCCESS_DRONE_GPS))
            self.drone_gimbal_conn_label_modifiable.setText(str(SUCCES_DRONE_GIMBAL))
            self.SUCCESS_PING_DRONE = SUCCESS_PING_DRONE
            self.SUCCESS_SSH = SUCCESS_SSH
            self.SUCCESS_DRONE_FPGA = SUCCESS_DRONE_FPGA
            self.SUCCESS_DRONE_GPS = SUCCESS_DRONE_GPS
            self.SUCCES_DRONE_GIMBAL = SUCCES_DRONE_GIMBAL

        SUCCESS_GND_FPGA = self.check_if_gnd_fpga_connected()
        SUCCESS_GND_GIMBAL = self.check_if_gnd_gimbal_connected()        
        SUCCESS_GND_GPS = self.check_if_gnd_gps_connected()
        #SUCCESS_DRONE_SERVER_FPGA = self.check_if_server_running_drone_fpga()
        #SUCCESS_GND_SERVER_FPGA = self.check_if_server_running_gnd_fpga()
        SUCCESS_DRONE_SERVER_FPGA = None
        SUCCESS_GND_SERVER_FPGA = None
        
        self.get_gnd_ip_node_address()
        self.gnd_gimbal_conn_label_modifiable.setText(str(SUCCESS_GND_GIMBAL))
        self.gnd_gps_conn_label_modifiable.setText(str(SUCCESS_GND_GPS))
        self.gnd_rfsoc_conn_label_modifiable.setText(str(SUCCESS_GND_FPGA))
        self.server_drone_fpga_label_modifiable.setText(str(SUCCESS_DRONE_SERVER_FPGA))
        self.server_gnd_fpga_label_modifiable.setText(str(SUCCESS_GND_SERVER_FPGA))
        
        if hasattr(self, 'GND_ADDRESS'):
            self.gnd_ip_addr_value_label.setText(self.GND_ADDRESS)
        else:
            self.GND_ADDRESS =  ''
        
        self.SUCCESS_GND_FPGA = SUCCESS_GND_FPGA
        self.SUCCESS_GND_GIMBAL = SUCCESS_GND_GIMBAL
        self.SUCCESS_GND_GPS = SUCCESS_GND_GPS
        
        if self.SUCCESS_SSH and self.SUCCESS_PING_DRONE:
            self.connect_to_drone.setEnabled(True)
        
    def create_class_instances(self, IsGPS=False, IsGimbal=False, IsRFSoC=False, GPS_Stream_Interval='sec1'):
        """
        Creates ``HelperA2GMeasurements`` class instance for this (ground) node and starts the WiFi communication thread.

        Args:
            IsGPS (bool, optional): True if there is a Septentrio GPS connected to this (ground) host computer. Defaults to False.
            IsGimbal (bool, optional): True if there is a Ronin RS2 gimbal connected to this (ground) host computer. Defaults to False.
            IsRFSoC (bool, optional): True if there is an RFSoC connected to this (ground) host computer. Defaults to False.
            GPS_Stream_Interval (str, optional): controls the regularity of getting GPS coordinates in this (ground) node. Available options are provided in ``GpsSignaling.start_gps_data_retrieval``. Defaults to 'sec1'.
        """

        # As this app is executed at the ground device...
        self.myhelpera2g = HelperA2GMeasurements('GROUND', self.GND_ADDRESS, IsRFSoC=IsRFSoC, IsGimbal=IsGimbal, IsGPS=IsGPS, rfsoc_static_ip_address='10.1.1.30', GPS_Stream_Interval=GPS_Stream_Interval, DBG_LVL_0=False, DBG_LVL_1=False, heading_offset=self.gnd_gps_att_offset)
        self.myhelpera2g.HelperStartA2GCom()

        print("[DEBUG]: Starting GUI threads")
        time.sleep(1)

        #self.start_GUI_threads()

    def start_GUI_threads(self):
        """
        Start GUI related threads. This threads are related only to the display of information
        on the GUI.
        
        """
        
        print("[DEBUG]: Starting GUI threads...")
        # Although thus function should be called when a HelperA2GMeasurements class instance has been created, better to do a double check
        if hasattr(self, 'myhelpera2g'):
            print("[DEBUG]: Detected helper class at creating GUI threads")
            if self.gps_display_flag:      
                print("[DEBUG]: GPS dispplay flag activated")      
                self.update_vis_time_gps = 1
                #self.periodical_gps_display_thread = RepeatTimer(self.update_vis_time_gps, self.periodical_gps_display_callback)
                self.stop_event_gps_display = threading.Event()
                self.periodical_gps_display_thread = TimerThread(self.stop_event_gps_display, self.update_vis_time_gps)
                self.periodical_gps_display_thread.update.connect(self.periodical_gps_display_callback)
                self.periodical_gps_display_thread.start()
            
            if self.rs2_fm_flag:
                print("[DEBUG]: Gimbal RS2 FM Flag activated")
                self.update_time_gimbal_follow = 1
                self.stop_event_gimbal_follow_thread = threading.Event()
                self.periodical_gimbal_follow_thread = TimerThread(self.stop_event_gimbal_follow_thread, self.update_time_gimbal_follow)
                self.periodical_gimbal_follow_thread.update.connect(lambda: self.myhelpera2g.socket_send_cmd(type_cmd='FOLLOWGIMBAL', data=self.fm_gnd_gimbal))
                self.periodical_gimbal_follow_thread.start()
        
    def periodical_pap_display_callback(self):
        """
        Callback for display the PAP of the measured CIR in the PAP panel of the GUI.
        """
        
        if hasattr(self, 'myhelpera2g'):
            if hasattr(self.myhelpera2g, 'PAP_TO_PLOT'):
                if len(self.myhelpera2g.PAP_TO_PLOT) > 0:
                    self.plot_widget.clear()
                    img = pg.ImageItem()
                    img.setImage(self.myhelpera2g.PAP_TO_PLOT)
                    self.plot_widget.addItem(img)
                    print(f"[DEBUG]: Executed plot command at {self.myhelpera2g.ID}. PAP shape: {self.myhelpera2g.PAP_TO_PLOT.shape}")
        
    def periodical_gps_display_callback(self):
        """
        Displays (periodically) GPS position of the drone node on the GPS panel. 
         
        The period is controlled by the property "update_vis_time_gps" of this class.
         
        Uses the ``show_air_moving`` function of the class ``GpsOnMap``, meaning that such method has to implement the functionality to display gps coordinates on a given input (PyQt5 panel).
        """
        
        # Display coords
        if hasattr(self, 'myhelpera2g'):
            '''
            coords, head_info = self.myhelpera2g.mySeptentrioGPS.get_last_sbf_buffer_info(what='Both')
                
            if coords['X'] == self.ERR_GPS_CODE_BUFF_NULL or self.ERR_GPS_CODE_SMALL_BUFF_SZ:
                print("[DEBUG]: Error in received GPS coordinates from DRONE")
                print("[DEBUG]: Due to this error, DRONE location will not be seen")
            else:
                lat_gnd_node, lon_gnd_node, height_node = geocentric2geodetic(coords['X'], coords['Y'], coords['Z'])
            '''
            if hasattr(self.myhelpera2g, 'last_drone_coords_requested'):
                gps_drone_coords_json = {"lat": self.last_drone_coords_requested['LAT'], "lon": self.last_drone_coords_requested['LON']}
                response = requests.put(self.url_put_map, json=gps_drone_coords_json)
        else:# DEBUG: test showing something updating each self.update_vis_time
            self.debug_cnt_1 = self.debug_cnt_1 + 1
            alfa = np.random.rand()
            point1 = [60.187372669712566, 24.96109446381862]
            point2 = [60.18490587854025, 24.948227873431904]
            point = np.array(point1)*alfa + (1-alfa)*np.array(point2)
            point = point.tolist()
            gps_drone_coords_json = {"lat": point[0], "lon": point[1]}
            response = requests.put(self.url_put_map, json=gps_drone_coords_json)    
            print("Periodical GPS", self.debug_cnt_1)
            
    def write_to_log_terminal(self, newLine):
        '''
        New line to be written into the log terminal. The number of new lines it can handle is controlled
        by the parameter number_lines_log_terminal.
        
        TO BE CHECKED: THE NUMBER OF MAX CHARACTERS FOR A LINE HAS TO BE CHECKED IN THE CODE
        
        '''
        
        log_txt = self.log_terminal_txt.splitlines()
        
        if len(log_txt) < self.number_lines_log_terminal:
            self.log_terminal_txt = self.log_terminal_txt + newLine + "\n"
        else:
            for i in range(len(log_txt)-1, 0, -1):
                log_txt[i] = log_txt[i-1] + "\n"
            log_txt[0] = newLine + "\n"
            
            log_txt = ''.join(log_txt) 
            self.log_terminal_txt = log_txt
            
        self.log_widget.setPlainText(self.log_terminal_txt)

    def create_log_terminal(self):
        """
        Access the widget contents by using ``self.log_widget.setPlainText('')``
        """
        self.log_widget = CustomTextEdit(self)
        
        #self.log_widget = QTextEdit(self)
        self.log_widget.setReadOnly(True) # make it read-only        
        
        # Redirect output of myFunc to the QTextEdit widget
        sys.stdout = self.log_widget
    
    def create_check_connections_panel(self):
        """
        Creates the "Check connections" panel with its widgets and layout.
        """
        self.checkConnPanel = QGroupBox('Connections')

        gnd_gimbal_conn_label = QLabel('Ground gimbal:')
        gnd_gps_conn_label = QLabel('Ground GPS:')
        gnd_rfsoc_conn_label = QLabel('Ground RFSoC:')
        network_exists_label = QLabel('Able to PING drone?:')
        ssh_conn_gnd_2_drone_label = QLabel('SSH to drone:')
        drone_rfsoc_conn_label = QLabel('Drone RFSoC:')
        drone_gps_conn_label = QLabel('Drone GPS:')
        drone_gimbal_conn_label = QLabel('Drone Gimbal:')
        server_gnd_fpga_label = QLabel('Ground FPGA server?:')
        server_drone_fpga_label = QLabel('Drone FPGA server?:')

        gnd_ip_addr_label = QLabel('Ground IP:')
        air_ip_addr_label = QLabel('Drone IP:')
        self.gnd_ip_addr_value_label = QLabel('')
        self.air_ip_addr_value_text_edit = QLineEdit(self.STATIC_DRONE_IP_ADDRESS)

        #self.GndGimbalFollowingCheckBox = QCheckBox("&RS2 FM")
        #self.GndGimbalFollowingCheckBox.setChecked(False)
        #self.GndGimbalFollowingCheckBox.toggled.connect(self.activate_rs2_fm_flag)
        #self.rs2_fm_flag = False

        #self.GpsDisplayCheckBox = QCheckBox("&GPS Display")
        #self.GpsDisplayCheckBox.setChecked(False)
        #self.GpsDisplayCheckBox.toggled.connect(self.activate_gps_display_flag)
        #self.gps_display_flag = False

        self.check_connections_push_button = QPushButton('Check')
        self.connect_to_drone = QPushButton('Connect drone')
        self.disconnect_from_drone = QPushButton('Disconnect drone')
        self.check_connections_push_button.clicked.connect(self.check_status_all_devices)
        self.disconnect_from_drone.setEnabled(False)
        self.connect_to_drone.setEnabled(False)
        self.connect_to_drone.clicked.connect(self.connect_drone_callback)
        self.disconnect_from_drone.clicked.connect(self.disconnect_drone_callback)

        self.gnd_gimbal_conn_label_modifiable = QLabel('--')
        self.gnd_gps_conn_label_modifiable = QLabel('--')
        self.gnd_rfsoc_conn_label_modifiable = QLabel('--')
        self.network_exists_label_modifiable = QLabel('--')
        self.ssh_conn_gnd_2_drone_label_modifiable = QLabel('--')
        self.drone_rfsoc_conn_label_modifiable = QLabel('--')
        self.drone_gps_conn_label_modifiable = QLabel('--')
        self.drone_gimbal_conn_label_modifiable = QLabel('--')
        self.server_gnd_fpga_label_modifiable = QLabel('--')
        self.server_drone_fpga_label_modifiable = QLabel('--')

        layout = QGridLayout()

        layout.addWidget(gnd_ip_addr_label, 0, 0, 1, 1)
        layout.addWidget(self.gnd_ip_addr_value_label, 0, 1, 1, 1)
        layout.addWidget(gnd_gimbal_conn_label, 0, 2, 1, 1)
        layout.addWidget(self.gnd_gimbal_conn_label_modifiable, 0, 3, 1, 1)
        layout.addWidget(gnd_gps_conn_label, 0, 4, 1, 1)
        layout.addWidget(self.gnd_gps_conn_label_modifiable, 0, 5, 1, 1)
        layout.addWidget(gnd_rfsoc_conn_label, 0, 6, 1, 1)
        layout.addWidget(self.gnd_rfsoc_conn_label_modifiable, 0, 7, 1, 1)
        layout.addWidget(network_exists_label, 0, 8, 1, 1)
        layout.addWidget(self.network_exists_label_modifiable, 0, 9, 1, 1)
        layout.addWidget(ssh_conn_gnd_2_drone_label, 0, 10, 1, 1)
        layout.addWidget(self.ssh_conn_gnd_2_drone_label_modifiable, 0, 11, 1, 1)
        layout.addWidget(drone_rfsoc_conn_label, 0, 12, 1, 1)
        layout.addWidget(self.drone_rfsoc_conn_label_modifiable, 0, 13, 1, 1)
        layout.addWidget(drone_gps_conn_label, 0, 14, 1, 1)       
        layout.addWidget(self.drone_gps_conn_label_modifiable, 0, 15, 1, 1)
        layout.addWidget(air_ip_addr_label, 1, 0, 1, 1)
        layout.addWidget(self.air_ip_addr_value_text_edit, 1, 1, 1, 2)
        layout.addWidget(drone_gimbal_conn_label, 1, 3, 1, 1)
        layout.addWidget(self.drone_gimbal_conn_label_modifiable, 1, 4, 1, 1) 
        layout.addWidget(server_gnd_fpga_label, 1, 5, 1, 1)
        layout.addWidget(self.server_gnd_fpga_label_modifiable, 1, 6, 1, 1)
        layout.addWidget(server_drone_fpga_label, 1, 7, 1, 1)
        layout.addWidget(self.server_drone_fpga_label_modifiable, 1, 8, 1, 1)
        layout.addWidget(self.check_connections_push_button, 1, 9, 1, 3)
        layout.addWidget(self.connect_to_drone, 1, 12, 1, 2)
        layout.addWidget(self.disconnect_from_drone, 1, 14, 1, 2)
        
        self.checkConnPanel.setLayout(layout)
    
    def activate_rs2_fm_flag(self):   
        """
        Toggles the ``rs2_fm_flag``
        """     
        
        if self.rs2_fm_flag:
            self.rs2_fm_flag = False
        else:
            self.rs2_fm_flag = True
    
    def activate_gps_display_flag(self):
        """
        Toggles the ``gps_display_flag``
        """
        if self.gps_display_flag:
            self.gps_display_flag = False
        else:
            self.gps_display_flag = True

    def connect_drone_callback(self):
        """
        Callback for when the user presses the "Connect" button.
         
        Calls the ``create_class_instance`` method to create the Helper class in this (ground) node, depending on the availability of ground and drone devices. 
        """
        
        if self.SUCCESS_GND_GIMBAL and self.SUCCESS_GND_FPGA and self.SUCCESS_GND_GPS:
            self.create_class_instances(IsGimbal=True, IsGPS=True, IsRFSoC=True)
            self.start_meas_togglePushButton.setEnabled(True)
            if self.SUCCESS_DRONE_GPS: 
                self.start_gps_visualization_action.setEnabled(True)
                self.stop_gps_visualization_action.setEnabled(False)
                
                # Only activate gnd FM actions if GND GIMBAL and GND GPS and DRONE GPS
                self.start_gnd_gimbal_fm_action.setEnabled(True)
                self.stop_gnd_gimbal_fm_action.setEnabled(False)
            print("[DEBUG]: Class created at GND with Gimbal, GPS and RFSoC")               
        if self.SUCCESS_GND_GIMBAL and self.SUCCESS_GND_FPGA and not self.SUCCESS_GND_GPS:
            self.create_class_instances(IsGimbal=True, IsRFSoC=True)
            print("[DEBUG]: Class created at GND with Gimbal and RFSoC")
            self.start_meas_togglePushButton.setEnabled(True)
        if self.SUCCESS_GND_GIMBAL and not self.SUCCESS_GND_FPGA and not self.SUCCESS_GND_GPS:
            self.create_class_instances(IsGimbal=True)
            self.start_meas_togglePushButton.setEnabled(False)
            print("[DEBUG]: Class created at GND with Gimbal")
        if self.SUCCESS_GND_GIMBAL and not self.SUCCESS_GND_FPGA and self.SUCCESS_GND_GPS:
            self.create_class_instances(IsGimbal=True, IsGPS=True)
            self.start_meas_togglePushButton.setEnabled(False)
            print("[DEBUG]: Class created at GND with Gimbal and GPS")
            if self.SUCCESS_DRONE_GPS:
                self.start_gnd_gimbal_fm_action.setEnabled(True)
                self.stop_gnd_gimbal_fm_action.setEnabled(False)
            if self.SUCCESS_DRONE_GPS:
                self.start_gps_visualization_action.setEnabled(True)
                self.stop_gps_visualization_action.setEnabled(False)
        if not self.SUCCESS_GND_GIMBAL and self.SUCCESS_GND_FPGA and self.SUCCESS_GND_GPS:
            self.create_class_instances(IsGPS=True, IsRFSoC=True)
            self.start_meas_togglePushButton.setEnabled(True)
            print("[DEBUG]: Class created at GND with GPS and RFSoC")
            if self.SUCCESS_DRONE_GPS:
                self.start_gps_visualization_action.setEnabled(True)
                self.stop_gps_visualization_action.setEnabled(False)
        if not self.SUCCESS_GND_GIMBAL and self.SUCCESS_GND_FPGA and not self.SUCCESS_GND_GPS:
            self.create_class_instances(IsRFSoC=True)
            self.start_meas_togglePushButton.setEnabled(True)
            print("[DEBUG]: Class created at GND with RFSoC")
        if not self.SUCCESS_GND_GIMBAL and not self.SUCCESS_GND_FPGA and not self.SUCCESS_GND_GPS:
            self.create_class_instances()
            self.start_meas_togglePushButton.setEnabled(False)
            print("[DEBUG]: Class created at GND with NO devices")
        if not self.SUCCESS_GND_GIMBAL and not self.SUCCESS_GND_FPGA and self.SUCCESS_GND_GPS:
            self.create_class_instances(IsGPS=True)
            self.start_meas_togglePushButton.setEnabled(False)
            print("[DEBUG]: Class created at GND with GPS")
            if self.SUCCESS_DRONE_GPS:
                self.start_gps_visualization_action.setEnabled(True)
                self.stop_gps_visualization_action.setEnabled(False)
        
        if self.SUCCES_DRONE_GIMBAL and self.SUCCESS_DRONE_GPS:
            self.start_drone_gimbal_fm_action.setEnabled(True)
            self.stop_drone_gimbal_fm_action.setEnabled(False)
        
        self.stop_meas_togglePushButton.setEnabled(False)
        self.finish_meas_togglePushButton.setEnabled(False)
        self.connect_to_drone.setEnabled(False)
        self.disconnect_from_drone.setEnabled(True)
        self.setupDevicesAndMoreAction.setDisabled(True)
        
    def disconnect_drone_callback(self):
        """
        Callback for when the user presses the "Disconnect" button.
         
        If there is an ongoing measurement it will be finished.
         
        The WiFi thread will be stopped and its associated socket will be closed in this node. Devices connection to this node will be closed.
        """
        
        if hasattr(self, 'periodical_gimbal_follow_thread'):
            if self.periodical_gimbal_follow_thread.isRunning():
                self.stop_event_gimbal_follow_thread.set()
        
        if hasattr(self, 'periodical_gps_display_thread'):
            if self.periodical_gps_display_thread.isActive():
                self.periodical_gps_display_thread.stop()

        if self.stop_meas_togglePushButton.isChecked():
            print("[DEBUG]: Before disconnecting, the ongoing measurement will be stopped")
            self.stop_meas_button_callback()
        if self.finish_meas_togglePushButton.isChecked():
            print("[DEBUG]: Before disconnecting, the ongoing measurement will be finished")
            self.finish_meas_button_callback()

        self.myhelpera2g.socket_send_cmd(type_cmd='CLOSEDGUI')
        self.myhelpera2g.HelperA2GStopCom(DISC_WHAT='ALL') # shutdowns the devices that where passed by parameters as True, when the class instance is created
        del self.myhelpera2g
        
        self.start_meas_togglePushButton.setEnabled(False)
        self.stop_meas_togglePushButton.setEnabled(False)
        self.finish_meas_togglePushButton.setEnabled(False)
        self.connect_to_drone.setEnabled(True)
        self.disconnect_from_drone.setEnabled(False)

        self.setupDevicesAndMoreAction.setEnabled(True)
        self.start_gnd_gimbal_fm_action.setEnabled(True)
        self.stop_gnd_gimbal_fm_action.setEnabled(False)
        self.start_drone_gimbal_fm_action.setEnabled(True)
        self.stop_drone_gimbal_fm_action.setEnabled(False)        
        self.start_gps_visualization_action.setEnabled(True)
        self.stop_gps_visualization_action.setEnabled(False)
    
    def create_fpga_and_sivers_panel(self):
        """
        Creates the "Sivers settings" panel with its widgets and layout.
        """
        
        self.fpgaAndSiversSettingsPanel = QGroupBox('Sivers settings')

        rf_op_freq_label = QLabel('Freq. Operation [Hz]:')
        tx_bb_gain_label = QLabel('Tx BB Gain [dB]:')
        tx_bb_phase_label = QLabel('Tx BB Phase [dB]:')
        tx_bb_iq_gain_label = QLabel('Tx BB IQ Gain [dB]:')
        tx_bfrf_gain_label = QLabel('Tx BF & RF Gain [dB]:')
        rx_bb_gain_1_label = QLabel('Rx BB Gain 1 [dB]:')
        rx_bb_gain_2_label = QLabel('Rx BB Gain 2 [dB]:')
        rx_bb_gain_3_label = QLabel('Rx BB Gain 3 [dB]:')
        rx_bfrf_gain_label = QLabel('Rx BF & RF Gain [dB]:')
        
        tx_bb_gain_label.leaveEvent = lambda e: QToolTip.hideText()
        tx_bb_gain_label.enterEvent = lambda e: QToolTip.showText(QCursor.pos(), "Not available to the user for the moment")
        
        #tx_bb_phase_label.leaveEvent = lambda e: QToolTip.hideText()
        #tx_bb_phase_label.enterEvent = lambda e: QToolTip.showText(QCursor.pos(), "Defaults to 0.")
        
        # Luckily lambda functions can help us to re implement QLabel methods leaveEvent and enterEvent in one line
        tx_bb_iq_gain_label.leaveEvent = lambda e: QToolTip.hideText()
        tx_bb_iq_gain_label.enterEvent = lambda e: QToolTip.showText(QCursor.pos(), "INPUT A VALUE IN: [0,6] dB\nThis sets the BB gain for the I, Q signals.\nThe actual value in dB is chosen as the closest value in the array linspace(0,6,16)")
        
        tx_bfrf_gain_label.leaveEvent = lambda e: QToolTip.hideText()
        tx_bfrf_gain_label.enterEvent = lambda e: QToolTip.showText(QCursor.pos(), "INPUT A VALUE IN: [0,15] dB\nThis sets the gain after RF mixer for the I, Q signals.\nThe actual value in dB is chosen as the closest value in the array linspace(0,15,16)")
        
        rx_bb_gain_1_label.leaveEvent = lambda e: QToolTip.hideText()
        rx_bb_gain_1_label.enterEvent = lambda e: QToolTip.showText(QCursor.pos(), "INPUT A VALUE IN: [-6,0] dB\nThis sets the rx 1st BB gain for the I, Q signals.\nThe actual value in dB is chosen as the closest value in the array linspace(-6,0,4)")
        
        rx_bb_gain_2_label.leaveEvent = lambda e: QToolTip.hideText()
        rx_bb_gain_2_label.enterEvent = lambda e: QToolTip.showText(QCursor.pos(), "INPUT A VALUE IN: [-6,0] dB\nThis sets the rx 2nd BB gain for the I, Q signals.\nThe actual value in dB is chosen as the closest value in the array linspace(-6,0,4)")
        
        rx_bb_gain_3_label.leaveEvent = lambda e: QToolTip.hideText()
        rx_bb_gain_3_label.enterEvent = lambda e: QToolTip.showText(QCursor.pos(), "INPUT A VALUE IN: [0,6] dB\nThis sets the rx 3rd BB gain for the I, Q signals.\nThe actual value in dB is chosen as the closest value in the array linspace(0,6,16)")
        
        rx_bfrf_gain_label.leaveEvent = lambda e: QToolTip.hideText()
        rx_bfrf_gain_label.enterEvent = lambda e: QToolTip.showText(QCursor.pos(), "INPUT A VALUE IN: [0,15] dB\nThis sets the rx gain before the RF mixer for the I, Q signals.\nThe actual value in dB is chosen as the closest value in the array linspace(0,15,16)")

        self.rf_op_freq_text_edit = QLineEdit('57.51e9')
        self.tx_bb_gain_text_edit = QLineEdit('3')
        self.tx_bb_phase_text_edit = QLineEdit('0')
        self.tx_bb_iq_gain_text_edit = QLineEdit('1.6')
        self.tx_bfrf_gain_text_edit = QLineEdit('3')
        self.rx_bb_gain_1_text_edit = QLineEdit('-1.5')
        self.rx_bb_gain_2_text_edit = QLineEdit('-4.5')
        self.rx_bb_gain_3_text_edit = QLineEdit('1.6')
        self.rx_bfrf_gain_text_edit = QLineEdit('7')
        self.tx_bb_phase_text_edit.setEnabled(False)
        self.tx_bb_gain_text_edit.setEnabled(False)

        layout = QGridLayout()

        layout.addWidget(rf_op_freq_label, 0, 0, 1, 2)
        layout.addWidget(self.rf_op_freq_text_edit, 0, 2, 1, 2)
        layout.addWidget(tx_bb_gain_label, 1, 0, 1, 1)
        layout.addWidget(self.tx_bb_gain_text_edit, 1, 1, 1, 1)
        layout.addWidget(rx_bb_gain_1_label, 1, 2, 1, 1)
        layout.addWidget(self.rx_bb_gain_1_text_edit, 1, 3, 1, 1)

        layout.addWidget(tx_bb_phase_label, 2, 0, 1, 1)
        layout.addWidget(self.tx_bb_phase_text_edit, 2, 1, 1, 1)
        layout.addWidget(rx_bb_gain_2_label, 2, 2, 1, 1)
        layout.addWidget(self.rx_bb_gain_2_text_edit, 2, 3, 1, 1)

        layout.addWidget(tx_bb_iq_gain_label, 3, 0, 1, 1)
        layout.addWidget(self.tx_bb_iq_gain_text_edit, 3, 1, 1, 1)
        layout.addWidget(rx_bb_gain_3_label, 3, 2, 1, 1)
        layout.addWidget(self.rx_bb_gain_3_text_edit, 3, 3, 1, 1)

        layout.addWidget(tx_bfrf_gain_label, 4, 0, 1, 1)
        layout.addWidget(self.tx_bfrf_gain_text_edit, 4, 1, 1, 1)
        layout.addWidget(rx_bfrf_gain_label, 4, 2, 1, 1)
        layout.addWidget(self.rx_bfrf_gain_text_edit, 4, 3, 1, 1)

        self.fpgaAndSiversSettingsPanel.setLayout(layout)

    def checker_gimbal_input_range(self, angle):
        """
        Checks if a given angle is within the allowed range.

        Args:
            angle (float): angle in degrees.

        Returns:
            incorrect_angle_value (bool): True if the angle is within the allowed range, False otherwise.
        """

        incorrect_angle_value = False
        if angle > 180 or angle < -180:
            print("[DEBUG]: Angle value outside of range")
            incorrect_angle_value = True
        
        return incorrect_angle_value

    def move_button_gimbal_gnd_callback(self):
        """
        Callback for when the user presses the "Move" button from the Gimbal GND panel. The yaw and pitch QLineEdits control the amount of movement, and the absolute or relative QRadioButtons if the movement is absolute or relative. BOTH yaw and pitch inputs are required.

        Example:
         
        For a yaw absolute movement to -20 deg and a pitch to 97 deg, the user MUST select the absolute radio button and enter -20 in the yaw text box and enter 97 in the pitch text box.
        """
        
        if hasattr(self, 'myhelpera2g'):
            if hasattr(self.myhelpera2g, 'myGimbal'):
                yaw = self.tx_yaw_value_text_edit.text()
                pitch = self.tx_pitch_value_text_edit.text()

                if yaw == '' or pitch == '':
                    print("[DEBUG]: No YAW or PITCH values provided. No gimbal movement will done.")
                else:
                    if self.tx_abs_radio_button.isChecked():
                        ctrl_byte = 0x01
                    if self.tx_rel_radio_button.isChecked():
                        ctrl_byte = 0x00

                    try:
                        yaw = int(float(yaw))
                        pitch = int(float(pitch))
                        incorrect_angle_value = self.checker_gimbal_input_range(yaw)
                        incorrect_angle_value = self.checker_gimbal_input_range(pitch)
                        self.myhelpera2g.myGimbal.setPosControl(yaw=yaw*10, roll=0, pitch=pitch*10, ctrl_byte=ctrl_byte)
                        print(f"[DEBUG]: gimbal moved {yaw} degs in YAW and {pitch} in PITCH from application")
                    except Exception as e:
                        print("[DEBUG]: Error executing gimbal movement. Most probably wrong angle input, ", e)
            else:
                print("[DEBUG]: No gimbal has been created at GND, so buttons will do nothing")
        else:
            print("[DEBUG]: No HelperA2GMeasurements class instance is available")
    
    def left_button_gimbal_gnd_callback(self):
        """
        Callback for when the user presses the ``Left`` button from the Gimbal GND panel. 
        
        Direction buttons (up, down, left, right) move the gimbal the direction they indicate, by the amount given in the ``Step`` textbox. The movement is relative to the angle before the button was pressed.
        
        If no value is provided in the ``Step`` textbox, the gimbal moves a value of 10 degrees in the direction indicated by this button.
        """
        
        if hasattr(self, 'myhelpera2g'):
            if hasattr(self.myhelpera2g, 'myGimbal'):
                movement_step = self.tx_step_manual_move_gimbal_text_edit.text()

                if movement_step != '':
                    try:
                        tmp = int(float(movement_step))
                        incorrect_angle_value = self.checker_gimbal_input_range(tmp)
                        if tmp < 0:
                            tmp = abs(tmp)
                            print("[DEBUG]: The movement step Textbox in the Gimbal Control Panel is always taken as positive. Direction is given by arrows.")
                        self.myhelpera2g.myGimbal.setPosControl(yaw=-tmp*10, roll=0, pitch=0, ctrl_byte=0x00)
                        print(f"[DEBUG]: gimbal moved -{movement_step} degs from application")
                    except Exception as e:
                        print("[DEBUG]: Error executing gimbal movement. Most probably wrong MOVEMENT STEP format, ", e)
                else:
                    self.myhelpera2g.myGimbal.setPosControl(yaw=-100, roll=0, pitch=0, ctrl_byte=0x00)
                    print("[DEBUG]: gimbal moved from application by a predetermined angle of -10 deg, since no angle was specified")

            else:
                print("[DEBUG]: No gimbal has been created at GND, so buttons will do nothing")
        else:
            print("[DEBUG]: No HelperA2GMeasurements class instance is available")

    def right_button_gimbal_gnd_callback(self):
        """
        Callback for when the user presses the ``Right`` button from the Gimbal GND panel. 
        
        Direction buttons (up, down, left, right) move the gimbal the direction they indicate, by the amount given in the ``Step`` textbox. The movement is relative to the angle before the button was pressed.
        
        If no value is provided in the ``Step`` textbox, the gimbal moves a value of 10 degrees in the direction indicated by this button.
        """        

        if hasattr(self, 'myhelpera2g'):
            if hasattr(self.myhelpera2g, 'myGimbal'):
                movement_step = self.tx_step_manual_move_gimbal_text_edit.text()

                if movement_step != '':
                    try:
                        tmp = int(float(movement_step))
                        incorrect_angle_value = self.checker_gimbal_input_range(tmp)
                        if tmp < 0:
                            tmp = abs(tmp)
                            print("[DEBUG]: The movement step Textbox in the Gimbal Control Panel is always taken as positive. Direction is given by arrows.")
                        self.myhelpera2g.myGimbal.setPosControl(yaw=tmp*10, roll=0, pitch=0, ctrl_byte=0x00)
                        print(f"[DEBUG]: gimbal moved {movement_step} degs from application")
                    except Exception as e:
                        print("[DEBUG]: Error executing gimbal movement. Most probably wrong MOVEMENT STEP format, ", e)
                else:
                    self.myhelpera2g.myGimbal.setPosControl(yaw=100, roll=0, pitch=0, ctrl_byte=0x00)
                    print("[DEBUG]: gimbal moved from application by a predetermined angle of 10 deg, since no angle was specified")

            else:
                print("[DEBUG]: No gimbal has been created at GND, so buttons will do nothing")
        else:
            print("[DEBUG]: No HelperA2GMeasurements class instance is available")
    
    def up_button_gimbal_gnd_callback(self):
        """
        Callback for when the user presses the ``Up`` button from the Gimbal GND panel. 
        
        Direction buttons (up, down, left, right) move the gimbal the direction they indicate, by the amount given in the ``Step`` textbox. The movement is relative to the angle before the button was pressed.
        
        If no value is provided in the ``Step`` textbox, the gimbal moves a value of 10 degrees in the direction indicated by this button.
        """

        if hasattr(self, 'myhelpera2g'):
            if hasattr(self.myhelpera2g, 'myGimbal'):
                movement_step = self.tx_step_manual_move_gimbal_text_edit.text()

                if movement_step != '':
                    try:
                        tmp = int(float(movement_step))
                        incorrect_angle_value = self.checker_gimbal_input_range(tmp)
                        if tmp < 0:
                            tmp = abs(tmp)
                            print("[DEBUG]: The movement step Textbox in the Gimbal Control Panel is always taken as positive. Direction is given by arrows.")
                        self.myhelpera2g.myGimbal.setPosControl(yaw=0, roll=0, pitch=tmp*10, ctrl_byte=0x00)
                        print(f"[DEBUG]: gimbal moved -{movement_step} degs from application")
                    except Exception as e:
                        print("[DEBUG]: Error executing gimbal movement. Most probably wrong MOVEMENT STEP format, ", e)
                else:
                    self.myhelpera2g.myGimbal.setPosControl(yaw=0, roll=0, pitch=100, ctrl_byte=0x00)
                    print("[DEBUG]: gimbal moved from application by a predetermined angle of 10 deg, since no angle was specified")

            else:
                print("[DEBUG]: No gimbal has been created at GND, so buttons will do nothing")
        else:
            print("[DEBUG]: No HelperA2GMeasurements class instance is available")

    def down_button_gimbal_gnd_callback(self):
        """
        Callback for when the user presses the ``Down`` button from the Gimbal GND panel. 
        
        Direction buttons (up, down, left, right) move the gimbal the direction they indicate, by the amount given in the ``Step`` textbox. The movement is relative to the angle before the button was pressed.
        
        If no value is provided in the ``Step`` textbox, the gimbal moves a value of 10 degrees in the direction indicated by this button.
        """

        if hasattr(self, 'myhelpera2g'):
            if hasattr(self.myhelpera2g, 'myGimbal'):
                movement_step = self.tx_step_manual_move_gimbal_text_edit.text()

                if movement_step != '':
                    try:
                        tmp = int(float(movement_step))
                        incorrect_angle_value = self.checker_gimbal_input_range(tmp)
                        if tmp < 0:
                            tmp = abs(tmp)
                            print("[DEBUG]: The movement step Textbox in the Gimbal Control Panel is always taken as positive. Direction is given by arrows.")
                        self.myhelpera2g.myGimbal.setPosControl(yaw=0, roll=0, pitch=-tmp*10, ctrl_byte=0x00)
                        print(f"[DEBUG]: gimbal moved {movement_step} degs from application")
                    except Exception as e:
                        print("[DEBUG]: Error executing gimbal movement. Most probably wrong MOVEMENT STEP format, ", e)
                else:
                    self.myhelpera2g.myGimbal.setPosControl(yaw=0, roll=0, pitch=-100, ctrl_byte=0x00)
                    print("[DEBUG]: gimbal moved from application by a predetermined angle of -10 deg, since no angle was specified")

            else:
                print("[DEBUG]: No gimbal has been created at GND, so buttons will do nothing")
        else:
            print("[DEBUG]: No HelperA2GMeasurements class instance is available")

    def move_button_gimbal_drone_callback(self):
        """
        Callback for when the user presses the "Move" button from the Gimbal Drone panel. The yaw and pitch QLineEdits control the amount of movement, and the absolute or relative QRadioButtons if the movement is absolute or relative. BOTH yaw and pitch inputs are required.

        Example:
         
        For a yaw absolute movement to -20 deg and a pitch to 97 deg, the user MUST select the absolute radio button and enter -20 in the yaw text box and enter 97 in the pitch text box.
        """
        if hasattr(self, 'myhelpera2g'):
            yaw = self.rx_yaw_value_text_edit.text()
            pitch = self.rx_pitch_value_text_edit.text()

            if yaw == '' or pitch == '':
                print("[DEBUG]: No YAW or PITCH values provided. No gimbal movement will done.")
            else:
                if self.rx_abs_radio_button.isChecked():
                    ctrl_byte = 0x01
                if self.rx_rel_radio_button.isChecked():
                    ctrl_byte = 0x00
                try:
                    yaw = int(float(yaw))
                    pitch = int(float(pitch))
                    incorrect_angle_value = self.checker_gimbal_input_range(yaw)
                    incorrect_angle_value = self.checker_gimbal_input_range(pitch)
                    if self.droneGimbalChoice == "DJI Ronin RS2":
                        data = {'YAW': yaw*10, 'PITCH': pitch*10, 'ROLL': 0, 'MODE': ctrl_byte}
                    elif self.droneGimbalChoice == "Gremsy H16":
                        data = {'YAW': yaw, 'PITCH': pitch, 'ROLL': 0, 'MODE': ctrl_byte}
                    self.myhelpera2g.socket_send_cmd(type_cmd='SETGIMBAL', data=data)
                    print(f"[DEBUG]: gimbal moved {yaw} degs in YAW and {pitch} in PITCH from application")
                except Exception as e:
                    print("[DEBUG]: Error executing gimbal movement. Most probably wrong angle input, ", e)
        else:
            print("[DEBUG]: No HelperA2GMeasurements class instance is available")
    
    def left_button_gimbal_drone_callback(self):
        """
        Callback for when the user presses the "Left" button from the Gimbal Drone panel. 
        
        Direction buttons (up, down, left, right) move the gimbal the direction they indicate, by the amount given in the "Step" textbox. The movement is relative to the angle before the button was pressed.
        
        If no value is provided in the "Step" textbox, the gimbal moves a value of 10 degrees in the direction indicated by this button.
        """
        if hasattr(self, 'myhelpera2g'):
            movement_step = self.rx_step_manual_move_gimbal_text_edit.text()
            if movement_step != '':
                try:
                    tmp = int(float(movement_step))
                    incorrect_angle_value = self.checker_gimbal_input_range(tmp)
                    if tmp < 0:
                        tmp = abs(tmp)
                        print("[DEBUG]: The movement step Textbox in the Gimbal Control Panel is always taken as positive. Direction is given by arrows.")
                    
                    if self.droneGimbalChoice == "DJI Ronin RS2":
                        data = {'YAW': -tmp*10, 'PITCH': 0, 'ROLL': 0, 'MODE': 0x00}
                    elif self.droneGimbalChoice == "Gremsy H16":
                        data = {'YAW': -tmp, 'PITCH': 0, 'ROLL': 0, 'MODE': 0x00}
                    self.myhelpera2g.socket_send_cmd(type_cmd='SETGIMBAL', data=data)
                    print(f"[DEBUG]: gimbal moved -{movement_step} degs from application")
                except Exception as e:
                        print("[DEBUG]: Error executing gimbal movement. Most probably wrong MOVEMENT STEP format, ", e)
            else:
                if self.droneGimbalChoice == "DJI Ronin RS2":
                    data = {'YAW': -100, 'PITCH': 0, 'ROLL': 0,'MODE': 0x00}
                elif self.droneGimbalChoice == "Gremsy H16":
                    data = {'YAW': -10, 'PITCH': 0, 'ROLL': 0,'MODE': 0x00}
                self.myhelpera2g.socket_send_cmd(type_cmd='SETGIMBAL', data=data)
                print("[DEBUG]: gimbal moved from application by a predetermined angle of -10 deg, since no angle was specified")
        else:
            print("[DEBUG]: No HelperA2GMeasurements class instance is available")
    
    def right_button_gimbal_drone_callback(self):
        """
        Callback for when the user presses the "Left" button from the Gimbal drone panel. 
        
        Direction buttons (up, down, left, right) move the gimbal the direction they indicate, by the amount given in the "Step" textbox. The movement is relative to the angle before the button was pressed.
        
        If no value is provided in the "Step" textbox, the gimbal moves a value of 10 degrees in the direction indicated by this button.
        """
        if hasattr(self, 'myhelpera2g'):
            movement_step = self.rx_step_manual_move_gimbal_text_edit.text()
            if movement_step != '':
                try:
                    tmp = int(float(movement_step))
                    incorrect_angle_value = self.checker_gimbal_input_range(tmp)
                    if tmp < 0:
                        tmp = abs(tmp)
                        print("[DEBUG]: The movement step Textbox in the Gimbal Control Panel is always taken as positive. Direction is given by arrows.")
                    if self.droneGimbalChoice == "DJI Ronin RS2":
                        data = {'YAW': tmp*10, 'PITCH': 0,'ROLL': 0, 'MODE': 0x00}
                    elif self.droneGimbalChoice == "Gremsy H16":
                        data = {'YAW': tmp, 'PITCH': 0,'ROLL': 0, 'MODE': 0x00}
                    self.myhelpera2g.socket_send_cmd(type_cmd='SETGIMBAL', data=data)
                    print(f"[DEBUG]: gimbal moved {movement_step} degs from application")
                except Exception as e:
                        print("[DEBUG]: Error executing gimbal movement. Most probably wrong MOVEMENT STEP format, ", e)
            else:
                if self.droneGimbalChoice == "DJI Ronin RS2":
                    data = {'YAW': 100, 'PITCH': 0,'ROLL': 0, 'MODE': 0x00}
                elif self.droneGimbalChoice == "Gremsy H16":
                    data = {'YAW': 10, 'PITCH': 0,'ROLL': 0, 'MODE': 0x00}
                self.myhelpera2g.socket_send_cmd(type_cmd='SETGIMBAL', data=data)
                print("[DEBUG]: gimbal moved from application by a predetermined angle of -10 deg, since no angle was specified")
        else:
            print("[DEBUG]: No HelperA2GMeasurements class instance is available")
    
    def up_button_gimbal_drone_callback(self):
        """
        Callback for when the user presses the "Left" button from the Gimbal drone panel. 
        
        Direction buttons (up, down, left, right) move the gimbal the direction they indicate, by the amount given in the "Step" textbox. The movement is relative to the angle before the button was pressed.
        
        If no value is provided in the "Step" textbox, the gimbal moves a value of 10 degrees in the direction indicated by this button.
        """
        if hasattr(self, 'myhelpera2g'):
            movement_step = self.rx_step_manual_move_gimbal_text_edit.text()
            if movement_step != '':
                try:
                    tmp = int(float(movement_step))
                    incorrect_angle_value = self.checker_gimbal_input_range(tmp)
                    if tmp < 0:
                        tmp = abs(tmp)
                        print("[DEBUG]: The movement step Textbox in the Gimbal Control Panel is always taken as positive. Direction is given by arrows.")
                    if self.droneGimbalChoice == "DJI Ronin RS2":
                        data = {'YAW': 0, 'PITCH': tmp*10,'ROLL': 0, 'MODE': 0x00}
                    elif self.droneGimbalChoice == "Gremsy H16":    
                        data = {'YAW': 0, 'PITCH': tmp,'ROLL': 0, 'MODE': 0x00}
                    self.myhelpera2g.socket_send_cmd(type_cmd='SETGIMBAL', data=data)
                    print(f"[DEBUG]: gimbal moved {movement_step} degs from application")
                except Exception as e:
                        print("[DEBUG]: Error executing gimbal movement. Most probably wrong MOVEMENT STEP format, ", e)
            else:
                if self.droneGimbalChoice == "DJI Ronin RS2":
                    data = {'YAW': 0, 'PITCH': 100, 'ROLL': 0,'MODE': 0x00}
                elif self.droneGimbalChoice == "Gremsy H16":
                    data = {'YAW': 0, 'PITCH': 10, 'ROLL': 0,'MODE': 0x00}
                self.myhelpera2g.socket_send_cmd(type_cmd='SETGIMBAL', data=data)
                print("[DEBUG]: gimbal moved from application by a predetermined angle of 10 deg, since no angle was specified")
        else:
            print("[DEBUG]: No HelperA2GMeasurements class instance is available")
    
    def down_button_gimbal_drone_callback(self):
        """
        Callback for when the user presses the "Left" button from the Gimbal drone panel. 
        
        Direction buttons (up, down, left, right) move the gimbal the direction they indicate, by the amount given in the "Step" textbox. The movement is relative to the angle before the button was pressed.
        
        If no value is provided in the "Step" textbox, the gimbal moves a value of 10 degrees in the direction indicated by this button.
        """
        if hasattr(self, 'myhelpera2g'):
            movement_step = self.rx_step_manual_move_gimbal_text_edit.text()
            if movement_step != '':
                try:
                    tmp = int(float(movement_step))
                    incorrect_angle_value = self.checker_gimbal_input_range(tmp)
                    if tmp < 0:
                        tmp = abs(tmp)
                        print("[DEBUG]: The movement step Textbox in the Gimbal Control Panel is always taken as positive. Direction is given by arrows.")
                    if self.droneGimbalChoice == "DJI Ronin RS2":
                        data = {'YAW': 0, 'PITCH': -tmp*10,'ROLL': 0, 'MODE': 0x00}
                    elif self.droneGimbalChoice == "Gremsy H16":
                        data = {'YAW': 0, 'PITCH': -tmp,'ROLL': 0, 'MODE': 0x00}
                    self.myhelpera2g.socket_send_cmd(type_cmd='SETGIMBAL', data=data)
                    print(f"[DEBUG]: gimbal moved -{movement_step} degs from application")
                except Exception as e:
                        print("[DEBUG]: Error executing gimbal movement. Most probably wrong MOVEMENT STEP format, ", e)
            else:
                if self.droneGimbalChoice == "DJI Ronin RS2":
                    data = {'YAW': 0, 'PITCH': -100,'ROLL': 0, 'MODE': 0x00}
                elif self.droneGimbalChoice == "Gremsy H16":
                    data = {'YAW': 0, 'PITCH': -10, 'ROLL': 0,'MODE': 0x00}
                self.myhelpera2g.socket_send_cmd(type_cmd='SETGIMBAL', data=data)
                print("[DEBUG]: gimbal moved from application by a predetermined angle of -10 deg, since no angle was specified")
        else:
            print("[DEBUG]: No HelperA2GMeasurements class instance is available")
    
    def tx_move_according_coords_push_button_callback(self):
        lat_origin, lon_origin, h_origin = self.gnd_static_coords_list[self.gnd_coord_list_ComboBox.currentIndex()]
        lat_dest, lon_dest, h_dest = self.drone_static_coords_list[self.drone_coord_list_ComboBox.currentIndex()]
        
        #yaw_to_set = azimuth_difference_between_coordinates(heading, lat_origin, lon_origin, lat_dest, lon_dest)
        pitch_to_set = elevation_difference_between_coordinates(lat_origin, lon_origin, h_origin, lat_dest, lon_dest, h_dest)
        
        print(f"[DEBUG]: FROM TX: ORIGIN: LAT: {lat_origin}, LON: {lon_origin}, ALT: {h_origin}")
        print(f"[DEBUG]: FROM TX: DESTINATION: LAT: {lat_dest}, LON: {lon_dest}, ALT: {h_dest}")
        print(f"[DEBUG]: PITCH: {pitch_to_set}")
        
    def rx_move_according_coords_push_button_callback(self):
        lat_origin, lon_origin, h_origin = self.drone_static_coords_list[self.drone_coord_list_ComboBox.currentIndex()]
        lat_dest, lon_dest, h_dest = self.gnd_static_coords_list[self.gnd_coord_list_ComboBox.currentIndex()]
        
        #yaw_to_set = azimuth_difference_between_coordinates(heading, lat_origin, lon_origin, lat_dest, lon_dest)
        pitch_to_set = elevation_difference_between_coordinates(lat_origin, lon_origin, h_origin, lat_dest, lon_dest, h_dest)
        
        print(f"[DEBUG]: FROM RX: ORIGIN: LAT: {lat_origin}, LON: {lon_origin}, ALT: {h_origin}")
        print(f"[DEBUG]: FROM RX: DESTINATION: LAT: {lat_dest}, LON: {lon_dest}, ALT: {h_dest}")
        print(f"[DEBUG]: PITCH: {pitch_to_set}")
    
    def create_Gimbal_GND_panel(self):
        """
        Creates the ground gimbal panel with its widgets and layout.
        """
        
        self.gimbalTXPanel = QGroupBox('GND Gimbal')
        
        yaw_label = QLabel('Yaw [D]:')
        pitch_label = QLabel('Pitch [D]:')
        
        self.tx_abs_radio_button = QRadioButton("Absolute")
        self.tx_rel_radio_button = QRadioButton("Relative")        
        self.tx_abs_radio_button.setChecked(True)
        
        self.tx_yaw_value_text_edit = QLineEdit('')
        self.tx_pitch_value_text_edit = QLineEdit('')
        self.tx_step_manual_move_gimbal_text_edit = QLineEdit('')
        
        thisLatLabel = QLabel('This Lat:')
        thisLonLabel = QLabel('This Lon:')
        
        avaialbleGndCoordsLabel = QLabel("Available GND coordinates:")
        self.gnd_coord_list_ComboBox = QComboBox()
        self.gnd_coord_list_ComboBox.addItems([str(i) for i in self.gnd_static_coords_list])
        
        self.tx_this_lat_text_edit = QLineEdit('')
        self.tx_this_lon_text_edit = QLineEdit('')
        
        self.tx_this_lat_text_edit.setEnabled(False)
        self.tx_this_lon_text_edit.setEnabled(False)
        
        self.tx_move_according_coords_push_button = QPushButton('Coords Move')
        self.tx_move_according_coords_push_button.clicked.connect(self.tx_move_according_coords_push_button_callback)
        
        self.tx_gimbal_manual_move_push_button = QPushButton('Move')
        self.tx_gimbal_manual_move_push_button.clicked.connect(self.move_button_gimbal_gnd_callback)
        self.tx_gimbal_move_left_push_button = QPushButton('Left')
        self.tx_gimbal_move_left_push_button.clicked.connect(self.left_button_gimbal_gnd_callback)
        self.tx_gimbal_move_right_push_button = QPushButton('Right')
        self.tx_gimbal_move_right_push_button.clicked.connect(self.right_button_gimbal_gnd_callback)
        self.tx_gimbal_move_up_push_button = QPushButton('Up')
        self.tx_gimbal_move_up_push_button.clicked.connect(self.up_button_gimbal_gnd_callback)
        self.tx_gimbal_move_down_push_button = QPushButton('Down')
        self.tx_gimbal_move_down_push_button.clicked.connect(self.down_button_gimbal_gnd_callback)
        
        layout = QGridLayout()
        layout.addWidget(self.tx_gimbal_move_up_push_button, 0, 0, 1, 3)
        layout.addWidget(self.tx_gimbal_move_left_push_button, 1, 0, 1, 3)
        layout.addWidget(self.tx_step_manual_move_gimbal_text_edit, 2, 0, 1, 3)
        layout.addWidget(self.tx_gimbal_move_right_push_button, 3, 0, 1, 3)
        layout.addWidget(self.tx_gimbal_move_down_push_button, 4, 0, 1, 3)
        
        layout.addWidget(self.tx_abs_radio_button, 0, 3, 1, 3)
        layout.addWidget(self.tx_rel_radio_button, 1, 3, 1, 3)
        layout.addWidget(yaw_label, 2, 3, 1, 1)
        layout.addWidget(self.tx_yaw_value_text_edit, 2, 4, 1, 2)
        layout.addWidget(pitch_label, 3, 3, 1, 1)        
        layout.addWidget(self.tx_pitch_value_text_edit, 3, 4, 1, 2)
        layout.addWidget(self.tx_gimbal_manual_move_push_button, 4, 3, 1, 3)     
        
        layout.addWidget(thisLatLabel, 0, 6, 1, 1)
        layout.addWidget(self.tx_this_lat_text_edit, 0, 7, 1, 2)
        layout.addWidget(thisLonLabel, 1, 6, 1, 1)
        layout.addWidget(self.tx_this_lon_text_edit, 1, 7, 1, 2)
        layout.addWidget(avaialbleGndCoordsLabel, 2, 6, 2, 1)        
        layout.addWidget(self.gnd_coord_list_ComboBox, 2, 7, 2, 2)
        layout.addWidget(self.tx_move_according_coords_push_button, 4, 6, 1, 3)
        
        self.gimbalTXPanel.setLayout(layout)

    def create_Gimbal_AIR_panel(self):
        """
        Creates the drone gimbal panel with its widgets and layout.
        """
        self.gimbalRXPanel = QGroupBox('Drone Gimbal')
        
        yaw_label = QLabel('Yaw [D]:')
        pitch_label = QLabel('Pitch [D]:')
        
        self.drone_gimbal_top_down_menu = QComboBox()
        
        if self.droneGimbalChoice == "DJI Ronin RS2":
            self.rx_abs_radio_button = QRadioButton("Absolute")
            self.rx_rel_radio_button = QRadioButton("Relative")
            self.rx_abs_radio_button.setChecked(True)
        elif self.droneGimbalChoice == "Gremsy H16":
            self.rx_lock_mode_radio_button = QRadioButton("Lock")
            self.rx_follow_mode_radio_button = QRadioButton("Follow")
            self.rx_lock_mode_radio_button.setChecked(True)
        
            self.rx_lock_mode_radio_button.clicked.connect(self.rx_lock_mode_radio_button_callback)
            self.rx_follow_mode_radio_button.clicked.connect(self.rx_follow_mode_radio_button_callback)
            
        self.rx_yaw_value_text_edit = QLineEdit('')
        self.rx_pitch_value_text_edit = QLineEdit('')
        self.rx_step_manual_move_gimbal_text_edit = QLineEdit('')
        
        self.rx_move_according_coords_push_button = QPushButton('Coords Move')
        self.rx_move_according_coords_push_button.clicked.connect(self.rx_move_according_coords_push_button_callback)
        
        self.rx_gimbal_manual_move_push_button = QPushButton('Move')
        self.rx_gimbal_manual_move_push_button.clicked.connect(self.move_button_gimbal_drone_callback)
        self.rx_gimbal_move_left_push_button = QPushButton('Left')
        self.rx_gimbal_move_left_push_button.clicked.connect(self.left_button_gimbal_drone_callback)
        self.rx_gimbal_move_right_push_button = QPushButton('Right')
        self.rx_gimbal_move_right_push_button.clicked.connect(self.right_button_gimbal_drone_callback)
        self.rx_gimbal_move_up_push_button = QPushButton('Up')
        self.rx_gimbal_move_up_push_button.clicked.connect(self.up_button_gimbal_drone_callback)
        self.rx_gimbal_move_down_push_button = QPushButton('Down')
        self.rx_gimbal_move_down_push_button.clicked.connect(self.down_button_gimbal_drone_callback)
        
        thisLatLabel = QLabel('This Lat:')
        thisLonLabel = QLabel('This Lon:')
        
        avaialbleDroneCoordsLabel = QLabel("Available drone coordinates:")
        self.drone_coord_list_ComboBox = QComboBox()
        self.drone_coord_list_ComboBox.addItems([str(i) for i in self.drone_static_coords_list])
        
        self.rx_this_lat_text_edit = QLineEdit('')
        self.rx_this_lon_text_edit = QLineEdit('')
        self.rx_this_lat_text_edit.setEnabled(False)
        self.rx_this_lon_text_edit.setEnabled(False)
        
        layout = QGridLayout()
        layout.addWidget(self.rx_gimbal_move_up_push_button, 0, 0, 1, 3)
        layout.addWidget(self.rx_gimbal_move_left_push_button, 1, 0, 1, 3)
        layout.addWidget(self.rx_step_manual_move_gimbal_text_edit, 2, 0, 1, 3)
        layout.addWidget(self.rx_gimbal_move_right_push_button, 3, 0, 1, 3)
        layout.addWidget(self.rx_gimbal_move_down_push_button, 4, 0, 1, 3)
        
        if self.droneGimbalChoice == "DJI Ronin RS2":
            layout.addWidget(self.rx_abs_radio_button, 0, 3, 1, 3)
            layout.addWidget(self.rx_rel_radio_button, 1, 3, 1, 3)
        elif self.droneGimbalChoice == "Gremsy H16":
            layout.addWidget(self.rx_lock_mode_radio_button, 0, 3, 1, 3)
            layout.addWidget(self.rx_follow_mode_radio_button, 1, 3, 1, 3)
        layout.addWidget(yaw_label, 2, 3, 1, 1)
        layout.addWidget(self.rx_yaw_value_text_edit, 2, 4, 1, 2)
        layout.addWidget(pitch_label, 3, 3, 1, 1)        
        layout.addWidget(self.rx_pitch_value_text_edit, 3, 4, 1, 2)
        layout.addWidget(self.rx_gimbal_manual_move_push_button, 4, 3, 1, 3)     
        
        layout.addWidget(thisLatLabel, 0, 6, 1, 1)
        layout.addWidget(self.rx_this_lat_text_edit, 0, 7, 1, 2)
        layout.addWidget(thisLonLabel, 1, 6, 1, 1)
        layout.addWidget(self.rx_this_lon_text_edit, 1, 7, 1, 2)
        layout.addWidget(avaialbleDroneCoordsLabel, 2, 6, 2, 1)        
        layout.addWidget(self.drone_coord_list_ComboBox, 2, 7, 2, 2)
        layout.addWidget(self.rx_move_according_coords_push_button, 4, 6, 1, 3)
        
        self.gimbalRXPanel.setLayout(layout)

    def rx_lock_mode_radio_button_callback(self):
        """
        Callback for when the user presses the "LOCK" radio button in the drone gimbal panel and when it has selected the "Gremsy H16" gimbal in the Setup dialog.
        """
        
        if hasattr(self, 'myhelpera2g'):
            try:
                data = {'MODE': 'LOCK'}
                self.myhelpera2g.socket_send_cmd(type_cmd='SETGIMBAL', data=data)
                print(f"[DEBUG]: gimbal mode set to {data['MODE']} from application")
            except Exception as e:
                print("[DEBUG]: An error ocurred in the transmission of the Gremsy gimbal mode, ", e)
        else:
            print("[DEBUG]: No HelperA2GMeasurements class instance is available")
    
    def rx_follow_mode_radio_button_callback(self):
        """
        Callback for when the user presses the "FOLLOW" radio button in the drone gimbal panel and when it has selected the "Gremsy H16" gimbal in the Setup dialog.
        """
        
        if hasattr(self, 'myhelpera2g'):
            try:
                data = {'MODE': 'FOLLOW'}
                self.myhelpera2g.socket_send_cmd(type_cmd='SETGIMBAL', data=data)
                print(f"[DEBUG]: gimbal mode set to {data['MODE']} from application")
            except Exception as e:
                print("[DEBUG]: An error ocurred in the transmission of the Gremsy gimbal mode, ", e)
        else:
            print("[DEBUG]: No HelperA2GMeasurements class instance is available")

    def convert_dB_to_valid_hex_sivers_register_values(self):
        """
        Converts the dB gain values (all of them) the user has input in the "Sivers settings" panel to the actual values required for the Sivers EVK registers.

        Returns:
            tx_signal_values (dict): dictionary with the Tx gain values to be set at the Tx Sivers EVK registers.
            rx_signal_values (dict): dictionary with the Rx gain values to be set at the RX Sivers EVK registers.
        """
        
        rxbb1 = float(self.rx_bb_gain_1_text_edit.text())
        rxbb2 = float(self.rx_bb_gain_2_text_edit.text())
        rxbb3 = float(self.rx_bb_gain_3_text_edit.text())
        rxbfrf = float(self.rx_bfrf_gain_text_edit.text())

        txbb = self.tx_bb_gain_text_edit.text()
        txbbiq = float(self.tx_bb_iq_gain_text_edit.text())
        txbbphase = self.tx_bb_phase_text_edit.text()
        txbf = float(self.tx_bfrf_gain_text_edit.text())
        
        valid_values_rx_bb = [0x00, 0x11, 0x33, 0x77, 0xFF]
        valid_values_rx_bb_dB = np.linspace(-6, 0, 5)

        valid_values_rx_bb3_bf = [0x00, 0x11, 0x22, 0x33, 0x44, 0x55, 0x66, 0x77, 0x88, 0x99, 0xAA, 0xBB, 0xCC, 0xDD, 0xEE, 0xFF]
        valid_values_rx_bb3_dB = np.linspace(0,6,16)
        valid_values_rx_bf_dB = np.linspace(0,15,16)

        valid_values_tx_bbiq_bf = [0x00, 0x11, 0x22, 0x33, 0x44, 0x55, 0x66, 0x77, 0x88, 0x99, 0xAA, 0xBB, 0xCC, 0xDD, 0xEE, 0xFF]
        valid_values_tx_bbiq_dB = np.linspace(0,6,16)
        valid_values_tx_bf_dB = np.linspace(0,15,16)        

        tx_signal_values = {'tx_bb_gain':int(txbb,16), 
                            'tx_bb_iq_gain':valid_values_tx_bbiq_bf[np.abs(txbbiq - valid_values_tx_bbiq_dB).argmin()],
                            'tx_bb_phase':int(txbbphase,16), 
                            'tx_bfrf_gain':valid_values_tx_bbiq_bf[np.abs(txbf - valid_values_tx_bf_dB).argmin()]}

        rx_signal_values = {'rx_gain_ctrl_bb1': valid_values_rx_bb[np.abs(rxbb1 - valid_values_rx_bb_dB).argmin()],
                'rx_gain_ctrl_bb2': valid_values_rx_bb[np.abs(rxbb2 - valid_values_rx_bb_dB).argmin()],
                'rx_gain_ctrl_bb3': valid_values_rx_bb3_bf[np.abs(rxbb3 - valid_values_rx_bb3_dB).argmin()],
                'rx_gain_ctrl_bfrf': valid_values_rx_bb3_bf[np.abs(rxbfrf - valid_values_rx_bf_dB).argmin()]}
        
        return tx_signal_values, rx_signal_values
    
    def start_meas_button_callback(self):
        """
        Callback for when the user presses the "START" button. Starts sending pilot signal from the TX Sivers.
         
        Sends the parameters to the RX sivers (RX RFSoC server) for it to be configured and start to listen incoming signals over the air. 
        """

        tx_signal_values, rx_signal_values = self.convert_dB_to_valid_hex_sivers_register_values()

        # Experiment starts
        self.myhelpera2g.myrfsoc.transmit_signal(carrier_freq=float(self.rf_op_freq_text_edit.text()),
                                                tx_bb_gain=tx_signal_values['tx_bb_gain'],
                                                tx_bb_iq_gain=tx_signal_values['tx_bb_iq_gain'],
                                                tx_bb_phase=tx_signal_values['tx_bb_phase'],
                                                tx_bfrf_gain=tx_signal_values['tx_bfrf_gain'])
        
        rx_signal_values['carrier_freq'] = float(self.rf_op_freq_text_edit.text())
        
        self.myhelpera2g.socket_send_cmd(type_cmd='STARTDRONERFSOC', data=rx_signal_values)

        self.start_meas_togglePushButton.setEnabled(False)
        self.stop_meas_togglePushButton.setEnabled(True)
        self.finish_meas_togglePushButton.setEnabled(False)
        self.update_vis_time_pap = 0.5

        #self.periodical_pap_display_thread = RepeatTimer(self.update_vis_time_pap, self.periodical_pap_display_callback)
        
        self.stop_event_pap_display_thread = threading.Event()
        self.periodical_pap_display_thread = TimerThread(self.stop_event_pap_display_thread, self.update_vis_time_pap)
        self.periodical_pap_display_thread.update.connect(self.periodical_pap_display_callback)
        self.periodical_pap_display_thread.start()
        #self.periodical_pap_display_thread = QTimer()
        #self.periodical_pap_display_thread.timeout.connect(self.periodical_pap_display_callback)
        #self.periodical_pap_display_thread.start(1000)
        print(f"[DEBUG]: This {self.myhelpera2g.ID} started thread periodical_pap_display")
    
    def stop_meas_button_callback(self):
        """
        Callback for when the user presses the "STOP" button. Sends a ``STOPDRONERFSOC`` command to the drone, to stop its rfsoc thread.
        """
        
        self.myhelpera2g.socket_send_cmd(type_cmd='STOPDRONERFSOC')
        print("[DEBUG]: SENT REQUEST to STOP measurement")
        self.start_meas_togglePushButton.setEnabled(True)
        self.stop_meas_togglePushButton.setEnabled(False)
        self.finish_meas_togglePushButton.setEnabled(True)
        self.stop_event_pap_display_thread.set()
    
    def finish_meas_button_callback(self):
        """
        Callback for when the user presses the "FINISH" button. Sends a ``FINISHDRONERFSOC`` command to the drone, to stop its rfsoc thread.
        """
        
        self.myhelpera2g.socket_send_cmd(type_cmd='FINISHDRONERFSOC')
        print("[DEBUG]: SENT REQUEST to FINISH measurement")

        datestr = datetime.datetime.now()
        datestr = datestr.strftime('%Y-%m-%d-%H-%M-%S')

        current_text = self.meas_description_text_edit.document().toPlainText()
        if self.myhelpera2g.IsGimbal!=0:
            if hasattr(self.myhelpera2g, 'myGimbal'):
                current_text = current_text + f"\nYaw at pressing FINISH: {self.myhelpera2g.myGimbal.yaw}" + '\n' + f"Pitch at pressing FINISH: {self.myhelpera2g.myGimbal.pitch}"
        with open('description_' + datestr + '.txt', 'a+') as file:
            file.write(current_text)
        
        print("[DEBUG]: Saved description file on GND node")
        
        self.start_meas_togglePushButton.setEnabled(True)
        self.stop_meas_togglePushButton.setEnabled(False)
        self.finish_meas_togglePushButton.setEnabled(False)

        if hasattr(self, 'periodical_gimbal_follow_thread'):
            if self.periodical_gimbal_follow_thread.isRunning():
                self.stop_event_gimbal_follow_thread.set()
        if hasattr(self, 'periodical_gps_display_thread'):
            if self.periodical_gps_display_thread.isActive():
                    self.periodical_gps_display_thread.stop()

    def create_Planning_Measurements_panel(self):
        """
        Creates the "Control measurements" panel with its widgets and layout.
        """
        
        self.planningMeasurementsPanel = QGroupBox('Control measurements')
        
        self.start_meas_togglePushButton = QPushButton("START")
        self.start_meas_togglePushButton.setEnabled(False)
        self.start_meas_togglePushButton.clicked.connect(self.start_meas_button_callback)
        
        self.stop_meas_togglePushButton = QPushButton("STOP")
        self.stop_meas_togglePushButton.setEnabled(False)
        self.stop_meas_togglePushButton.clicked.connect(self.stop_meas_button_callback)
        
        self.finish_meas_togglePushButton = QPushButton("FINISH")
        self.finish_meas_togglePushButton.setEnabled(False)
        self.finish_meas_togglePushButton.clicked.connect(self.finish_meas_button_callback)
        
        self.meas_description_text_edit = QPlainTextEdit('')
        self.meas_description_text_edit.setPlaceholderText("Enter measurement description here")
        
        layout = QGridLayout()
        layout.addWidget(self.meas_description_text_edit, 0, 0, 3, 6)
        
        layout.addWidget(self.start_meas_togglePushButton, 0, 6, 1, 2)
        layout.addWidget(self.stop_meas_togglePushButton, 1, 6, 1, 2)
        layout.addWidget(self.finish_meas_togglePushButton, 2, 6, 1, 2)
        
        self.planningMeasurementsPanel.setLayout(layout)
    
    def create_GPS_visualization_panel(self):
        """
        Creates the GPS visuzliation panel. The ``gps_start_point_in_finland_json`` can be set to any coordinate.

        Requires the ``gpsRESTHandler.py`` file where the REST API for the gps is implemented.
        """

        self.gps_vis_panel = QGroupBox('GPS visualization')
        
        # This starting point can be anything, as it will be updated throught the PUT requests
        gps_start_point_json = {"lat": 60.15301542729288, "lon": 24.316255998379482}
        
        response = requests.post(self.url_post_map, json=gps_start_point_json)
        
        time.sleep(0.05)
        
        js_handler_of_non_geoson = JsCode("""
        function(responseHandler, errorHandler) {
            let url ="""+self.url_get_map+""";

            fetch(url)
            .then((response) => {
                return response.json().then((data) => {
                    var {lat, lon } = data;
                    var id=45;
                    return {
                        "type": "FeatureCollection",
                        "features": [{
                            "type": "Feature",
                            "geometry": {
                                "type": "Point",
                                "coordinates": [lon, lat]
                            },
                            "properties": {
                                "id": id
                            }
                        }]
                    };
                })
            })
            .then(responseHandler)
            .catch(errorHandler);
        }
        """)
        
        self.gps_map = folium.Map()
        self.map_rt_foilum_plugin = realtime.Realtime(js_handler_of_non_geoson, interval=5000)
        self.map_rt_foilum_plugin.add_to(self.gps_map)
        
        self.webview = QWebEngineView()
        self.webview.setHtml(self.gps_map._repr_html_())
        
        tx_info_label = QLabel('TX')
        rx_info_label = QLabel('RX')
        
        tx_info_label.setAlignment(Qt.AlignCenter)
        rx_info_label.setAlignment(Qt.AlignCenter)
        
        tx_x_label = QLabel('X:')
        tx_y_label = QLabel('Y:')
        tx_z_label = QLabel('Z:')
        tx_x_value_label = QLabel('')
        tx_y_value_label = QLabel('')
        tx_z_value_label = QLabel('')
        
        rx_x_label = QLabel('X:')
        rx_y_label = QLabel('Y:')
        rx_z_label = QLabel('Z:')
        rx_x_value_label = QLabel('')
        rx_y_value_label = QLabel('')
        rx_z_value_label = QLabel('')
        
        layout = QGridLayout()
        layout.addWidget(self.webview, 0, 0, 8, 10)
        layout.addWidget(tx_info_label, 8, 0, 1, 5)
        layout.addWidget(rx_info_label, 8, 5, 1, 5)
        layout.addWidget(tx_x_label, 9, 0, 1, 1)
        layout.addWidget(tx_z_label, 10, 0, 1, 1)
        layout.addWidget(tx_y_label, 11, 0, 1, 1)
        layout.addWidget(tx_x_value_label, 9, 1, 1, 4)
        layout.addWidget(tx_y_value_label, 10, 1, 1, 4)
        layout.addWidget(tx_z_value_label, 11, 1, 1, 4)
        layout.addWidget(rx_x_label, 9, 5, 1, 1)
        layout.addWidget(rx_z_label, 10, 5, 1, 1)
        layout.addWidget(rx_y_label, 11, 5, 1, 1)
        layout.addWidget(rx_x_value_label, 9, 6, 1, 4)
        layout.addWidget(rx_y_value_label, 10, 6, 1, 4)
        layout.addWidget(rx_z_value_label, 11, 6, 1, 4)

        # Set the layout of the group box
        self.gps_vis_panel.setLayout(layout)
    
    def create_pap_plot_panel(self):
        """
        Creates the "PAP" panel (responsible for ploting the Power Angular Profile of the measured CIRs).
        """
        
        self.papPlotPanel = QGroupBox('PAP')
        self.time_snaps = 22
        self.plot_widget = pg.PlotWidget() 
        self.plot_widget.setLabel('left', 'Beam steering angle [deg]')
        self.plot_widget.setLabel('bottom', 'Time snapshot number')

        layout = QVBoxLayout()
        layout.addWidget(self.plot_widget)
        self.papPlotPanel.setLayout(layout)

        rx_sivers_beam_index_mapping_file = open('data/rx_sivers_beam_index_mapping.csv')
        csvreader = csv.reader(rx_sivers_beam_index_mapping_file)
        beam_idx_map = [float(i[1]) for cnt,i in enumerate(csvreader) if cnt != 0]
        ticksla = beam_idx_map[::4]
        self.beam_angs = ticksla
        ticks = np.arange(0,16) 
        y_ticks = [(ticks[cnt], f'{tickla:1.2f}°') for cnt, tickla in enumerate(ticksla)]
        self.plot_widget.getAxis('left').setTicks([y_ticks, []])

        x_ticks = [(i, str(i)) for i in np.arange(self.time_snaps)]
        self.plot_widget.getAxis('bottom').setTicks([x_ticks, []])
    
    def closeEvent(self, event):
        if hasattr(self, 'myhelpera2g'):
            self.myhelpera2g.HelperA2GStopCom(DISC_WHAT='ALL')
        #if hasattr(self, 'periodical_pap_display_thread'):
            #self.periodical_pap_display_thread.cancel()
            #self.periodical_pap_display_thread.stop()
        if hasattr(self, 'periodical_gps_display_thread'):
            if self.periodical_gps_display_thread.isActive():
                self.periodical_gps_display_thread.stop()
        if hasattr(self, 'periodical_gimbal_follow_thread'):
            if self.periodical_gimbal_follow_thread.isRunning():
                self.stop_event_gimbal_follow_thread.set()
        
        # Last thing to do is to redirect the stdout
        #sys.stdout = self.original_stdout
            
    def eventFilter(self, source, event):
        if event.type()== event.Close:
            self.closeEvent(event)
            return True
        
        return super().eventFilter(source,event)

if __name__ == '__main__':
    app = QApplication([])
    gallery = WidgetGallery()
    gallery.show()
    sys.exit(app.exec_())

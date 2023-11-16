import threading
import numpy as np
import csv
import json
import datetime
import platform
import re
import subprocess
import paramiko
import ping3
import time
import can#from fbs_runtime.application_context.PyQt5 import ApplicationContext
from serial.tools.list_ports import comports
from PyQt5.QtCore import Qt, QTimer, QObject, QThread, QMutex, pyqtSignal
from PyQt5.QtWidgets import (QApplication, QCheckBox, QComboBox, QDateTimeEdit,
        QDial, QDialog, QGridLayout, QGroupBox, QHBoxLayout, QLabel, QLineEdit,
        QProgressBar, QPushButton, QRadioButton, QScrollBar, QSizePolicy,
        QSlider, QSpinBox, QStyleFactory, QTableWidget, QTabWidget, QTextEdit,
        QVBoxLayout, QWidget)

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

import sys
from a2gmeasurements import HelperA2GMeasurements, RepeatTimer
from a2gUtils import GpsOnMap, geocentric2geodetic, geodetic2geocentric

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

class WidgetGallery(QDialog):
    def __init__(self, parent=None):
        super(WidgetGallery, self).__init__(parent)

        self.setWindowTitle("A2G Measurements Center")

        # Parameters of the GUI
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
                
        self.setLayout(mainLayout)

        self.showMaximized()

    def check_if_ssh_2_drone_reached(self, drone_ip, username, password):
        """
        Checks ssh connection betwwen ground node (running the GUI) and the computer on the drone.

        Error checking of the input parameters SHOULD BE DONE by the caller function.
        
        Args:
            drone_ip (str): drone's IP address. SHOULD BE A PROPER IP ADDRESS.
            username (str): username of the  computer on the drone.
            password (str): password of the computer on the drone.

        Returns:
            success_ping_network (bool): True if drone node reachable.
            success_air_node_ssh (bool): True if ssh connection established.
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
        Caller function SHOULD check first if there is a ssh connection.
        
        Args:
            drone_fpga_static_ip_addr (str, optional): _description_. Defaults to '10.1.1.40'.

        Returns:
            success_drone_fpga (bool): True if the ping to the rfsoc IP address is replied.
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
        Check if ground fpga is connected to its host by pinging.

        Args:
            gnd_fpga_static_ip_addr (str, optional): _description_. Defaults to '10.1.1.30'.

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
                if 'USB Serial Converter' in usb_list_str:
                    success_drone_gimbal = True
                    print("[DEBUG]: Gremsy Gimbal is detected at DRONE")
                else:
                    success_drone_gimbal = False
                    print("[DEBUG]: Gremsy Gimbal is NOT detected at DRONE")                

        return success_drone_gimbal

    def check_if_gnd_gimbal_connected(self):
        """
        Function for checking if gimbal RS2 is connected on ground node.

        Returns:
            success_gnd_gimbal (bool): True if detected, False otherwise.
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
    
    def check_if_gnd_gps_connected(self):
        """
        Function for checking if gps is connected to the ground node.

        Returns:
            success_gnd_gps (bool): True connected, False otherwise
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
        Function for checking if gps is connected to the drone node. Requires that there is a SSH connection established

        Returns:
            success_drone_gps (bool): True if connected, False if not, None if no SSH connection
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
        Gets the IP address of the ground node.
        
        Caller function IS RESPONSIBLE for checking if there is a WIFI operating. 
        
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
        Function callback when user presses the "Check" button.
        
        Gets the connection status of all devices.
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
        
        self.get_gnd_ip_node_address()
        self.gnd_gimbal_conn_label_modifiable.setText(str(SUCCESS_GND_GIMBAL))
        self.gnd_gps_conn_label_modifiable.setText(str(SUCCESS_GND_GPS))
        self.gnd_rfsoc_conn_label_modifiable.setText(str(SUCCESS_GND_FPGA))
        
        if hasattr(self, 'GND_ADDRESS'):
            self.gnd_ip_addr_value_label.setText(self.GND_ADDRESS)
        else:
            self.GND_ADDRESS =  ''
        
        self.SUCCESS_GND_FPGA = SUCCESS_GND_FPGA
        self.SUCCESS_GND_GIMBAL = SUCCESS_GND_GIMBAL
        self.SUCCESS_GND_GPS = SUCCESS_GND_GPS
        
        self.connect_to_drone.setEnabled(True)
        
    def create_class_instances(self, IsGPS=False, IsGimbal=False, IsRFSoC=False, GPS_Stream_Interval='sec1'):
        """
        Responsible for creating any objects (class instances) that will be used to connect to and control the devices,

        Args:
            IsGPS (bool, optional): _description_. Defaults to False.
            IsGimbal (bool, optional): _description_. Defaults to False.
            GPS_Stream_Interval (str, optional): _description_. Defaults to 'sec1'.
        """

        # As this app is executed at the ground device...
        self.myhelpera2g = HelperA2GMeasurements('GROUND', self.GND_ADDRESS, IsRFSoC=IsRFSoC, IsGimbal=IsGimbal, IsGPS=IsGPS, rfsoc_static_ip_address='10.1.1.30', GPS_Stream_Interval=GPS_Stream_Interval, DBG_LVL_0=False, DBG_LVL_1=False)
        self.myhelpera2g.HelperStartA2GCom()

        print("[DEBUG]: Starting GUI threads")
        time.sleep(1)

        self.start_GUI_threads()

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
                self.periodical_gps_display_thread = RepeatTimer(self.update_vis_time_gps, self.periodical_gps_display_callback)
                self.periodical_gps_display_thread.start()
            
            if self.rs2_fm_flag:
                print("[DEBUG]: Gimbal RS2 FM Flag activated")
                self.update_time_gimbal_follow = 1
            #self.periodical_gimbal_follow_thread = RepeatTimer(self.update_time_gimbal_follow, self.myhelpera2g.socket_send_cmd(type_cmd='GETGPS'))
                self.periodical_gimbal_follow_thread = RepeatTimer(self.update_time_gimbal_follow, self.myhelpera2g.socket_send_cmd, args=('FOLLOWGIMBAL',))
                self.periodical_gimbal_follow_thread.start()
        
    def periodical_pap_display_callback(self):
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
        Periodically displays GPS position of both devices on the GPS Visualization panel.
        The period is controlled by the propery "update_vis_time_gps" of this class.

        """        
        # Display GND node coords
        coords, head_info = self.myhelpera2g.mySeptentrioGPS.get_last_sbf_buffer_info(what='Both')
            
        if coords['X'] == self.ERR_GPS_CODE_BUFF_NULL or self.ERR_GPS_CODE_SMALL_BUFF_SZ:
            pass
        else:
            lat_gnd_node, lon_gnd_node, height_node = geocentric2geodetic(coords['X'], coords['Y'], coords['Z'])
            self.mygpsonmap.show_air_moving(lat=lat_gnd_node, lon=lon_gnd_node) 
        
        # Display drone node coords
        # The coordinates shown will be the coordinates of up to self.update_time_fps before
        if hasattr(self.myhelpera2g, 'last_drone_coords_requested'):
            self.mygpsonmap.show_air_moving(lat=self.myhelpera2g.last_drone_coords_requested['LAT'], lon=self.myhelpera2g.last_drone_coords_requested['LON'])
            
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
        Access the widget contents by using self.log_widget.setPlainText('')

        """
        self.log_widget = CustomTextEdit(self)
        
        #self.log_widget = QTextEdit(self)
        self.log_widget.setReadOnly(True) # make it read-only        
        
        # Redirect output of myFunc to the QTextEdit widget
        sys.stdout = self.log_widget
    
    def create_check_connections_panel(self):
        self.checkConnPanel = QGroupBox('Connections')

        gnd_gimbal_conn_label = QLabel('Ground gimbal:')
        gnd_gps_conn_label = QLabel('Ground GPS:')
        gnd_rfsoc_conn_label = QLabel('Ground RFSoC:')
        network_exists_label = QLabel('Able to PING drone?:')
        ssh_conn_gnd_2_drone_label = QLabel('SSH to drone:')
        drone_rfsoc_conn_label = QLabel('Drone RFSoC:')
        drone_gps_conn_label = QLabel('Drone GPS:')
        drone_gimbal_conn_label = QLabel('Drone Gimbal:')

        gnd_ip_addr_label = QLabel('Ground IP:')
        air_ip_addr_label = QLabel('Drone IP:')
        self.gnd_ip_addr_value_label = QLabel('')
        self.air_ip_addr_value_text_edit = QLineEdit(self.STATIC_DRONE_IP_ADDRESS)

        self.GndGimbalFollowingCheckBox = QCheckBox("&RS2 FM")
        self.GndGimbalFollowingCheckBox.setChecked(False)
        self.GndGimbalFollowingCheckBox.toggled.connect(self.activate_rs2_fm_flag)
        self.rs2_fm_flag = False

        self.GpsDisplayCheckBox = QCheckBox("&GPS Display")
        self.GpsDisplayCheckBox.setChecked(False)
        self.GpsDisplayCheckBox.toggled.connect(self.activate_gps_display_flag)
        self.gps_display_flag = False

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
        layout.addWidget(self.check_connections_push_button, 1, 5, 1, 4)
        layout.addWidget(self.GndGimbalFollowingCheckBox, 1, 9, 1, 1)
        layout.addWidget(self.GpsDisplayCheckBox, 1, 10, 1, 1)
        #layout.addWidget(self.connect_to_drone, 1, 9, 1, 4)
        layout.addWidget(self.connect_to_drone, 1, 11, 1, 2)
        layout.addWidget(self.disconnect_from_drone, 1, 13, 1, 3)
        
        self.checkConnPanel.setLayout(layout)
    
    def activate_rs2_fm_flag(self):        
        if self.rs2_fm_flag:
            self.rs2_fm_flag = False
        else:
            self.rs2_fm_flag = True
    
    def activate_gps_display_flag(self):
        if self.gps_display_flag:
            self.gps_display_flag = False
        else:
            self.gps_display_flag = True

    def connect_drone_callback(self):
        if self.SUCCESS_GND_GIMBAL and self.SUCCESS_GND_FPGA and self.SUCCESS_GND_GPS:
            self.create_class_instances(IsGimbal=True, IsGPS=True, IsRFSoC=True)
            self.start_meas_togglePushButton.setEnabled(True)
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
        if not self.SUCCESS_GND_GIMBAL and self.SUCCESS_GND_FPGA and self.SUCCESS_GND_GPS:
            self.create_class_instances(IsGPS=True, IsRFSoC=True)
            self.start_meas_togglePushButton.setEnabled(True)
            print("[DEBUG]: Class created at GND with GPS and RFSoC")
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
        
        self.stop_meas_togglePushButton.setEnabled(False)
        self.finish_meas_togglePushButton.setEnabled(False)
        self.connect_to_drone.setEnabled(False)
        self.disconnect_from_drone.setEnabled(True)
        
    def disconnect_drone_callback(self):
        if hasattr(self, 'periodical_gimbal_follow_thread'):
            self.periodical_gimbal_follow_thread.cancel()

        self.myhelpera2g.socket_send_cmd(type_cmd='CLOSEDGUI')
        self.myhelpera2g.HelperA2GStopCom(DISC_WHAT='ALL') # shutdowns the devices that where passed by parameters as True, when the class instance is created
        del self.myhelpera2g        
        
        self.start_meas_togglePushButton.setEnabled(False)
        self.stop_meas_togglePushButton.setEnabled(False)
        self.finish_meas_togglePushButton.setEnabled(False)
        self.connect_to_drone.setEnabled(True)
        self.disconnect_from_drone.setEnabled(False)     
    
    def create_fpga_and_sivers_panel(self):
        self.fpgaAndSiversSettingsPanel = QGroupBox('RFSoC and Sivers settings')

        rf_op_freq_label = QLabel('Freq. Operation [Hz]:')
        tx_bb_gain_label = QLabel('Tx BB Gain [HEX]:')
        tx_bb_phase_label = QLabel('Tx BB Phase [HEX]:')
        tx_bb_iq_gain_label = QLabel('Tx BB IQ Gain [HEX]:')
        tx_bfrf_gain_label = QLabel('Tx BF & RF Gain [HEX]:')
        rx_bb_gain_1_label = QLabel('Rx BB Gain 1 [HEX]:')
        rx_bb_gain_2_label = QLabel('Rx BB Gain 2 [HEX]:')
        rx_bb_gain_3_label = QLabel('Rx BB Gain 3 [HEX]:')
        rx_bfrf_gain_label = QLabel('Rx BF & RF Gain [HEX]:')

        self.rf_op_freq_text_edit = QLineEdit('57.51e9')
        self.tx_bb_gain_text_edit = QLineEdit('3')
        self.tx_bb_phase_text_edit = QLineEdit('0')
        self.tx_bb_iq_gain_text_edit = QLineEdit('77')
        self.tx_bfrf_gain_text_edit = QLineEdit('40')
        self.rx_bb_gain_1_text_edit = QLineEdit('77')
        self.rx_bb_gain_2_text_edit = QLineEdit('00')
        self.rx_bb_gain_3_text_edit = QLineEdit('99')
        self.rx_bfrf_gain_text_edit = QLineEdit('FF')

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

        incorrect_angle_value = False
        if angle > 180 or angle < -180:
            print("[DEBUG]: Angle value outside of range")
            incorrect_angle_value = True
        
        return incorrect_angle_value

    def move_button_gimbal_gnd_callback(self):
        """
        Move button callback from the Gimbal GND panel. The yaw and pitch QLineEdits control the amount of movement, and the absolute or relative QRadioButtons
        if the movement is absolute or relative.

        VALUES ENTERED IN THE QLineEdits must be the ANGLE DESIRED. For example: for a yaw absolute movement to -20 deg and a pitch to 97, the user MUST select the absolute radio button
        and enter -20 in the yaw text box and enter 97 in the pitch text box.

        BOTH yaw AND pitch are required.

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
        Left button callback from the Gimbal GND panel. 
        Direction buttons (up, down, left, right) move the gimbal the direction they indicate, by the amount
        given in QLineEdit (textbox at the center of the 'software joystick' in the panel) with respect to the ACTUAL angles.

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
        Right button callback from the Gimbal GND panel. 
        Direction buttons (up, down, left, right) move the gimbal the direction they indicate, by the amount
        given in QLineEdit (textbox at the center of the 'software joystick' in the panel) with respect to the ACTUAL angles.

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
        Up button callback from the Gimbal GND panel. 
        Direction buttons (up, down, left, right) move the gimbal the direction they indicate, by the amount
        given in QLineEdit (textbox at the center of the 'software joystick' in the panel) with respect to the ACTUAL angles.

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
        Down button callback from the Gimbal GND panel. 
        Direction buttons (up, down, left, right) move the gimbal the direction they indicate, by the amount
        given in QLineEdit (textbox at the center of the 'software joystick' in the panel) with respect to the ACTUAL angles.

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
        1
    
    def left_button_gimbal_drone_callback(self):
        if hasattr(self, 'myhelpera2g'):
            movement_step = self.rx_step_manual_move_gimbal_text_edit.text()
            if movement_step != '':
                try:
                    tmp = int(float(movement_step))
                    incorrect_angle_value = self.checker_gimbal_input_range(tmp)
                    if tmp < 0:
                        tmp = abs(tmp)
                        print("[DEBUG]: The movement step Textbox in the Gimbal Control Panel is always taken as positive. Direction is given by arrows.")
                        
                    data = {'YAW': -tmp, 'PITCH': 0}
                    self.myhelpera2g.socket_send_cmd(type_cmd='SETGIMBAL', data=data)
                    print(f"[DEBUG]: gimbal moved -{movement_step} degs from application")
                except Exception as e:
                        print("[DEBUG]: Error executing gimbal movement. Most probably wrong MOVEMENT STEP format, ", e)
            else:
                data = {'YAW': -10, 'PITCH': 0}
                self.myhelpera2g.socket_send_cmd(type_cmd='SETGIMBAL', data=data)
                print("[DEBUG]: gimbal moved from application by a predetermined angle of -10 deg, since no angle was specified")
        else:
            print("[DEBUG]: No HelperA2GMeasurements class instance is available")
    
    def right_button_gimbal_drone_callback(self):
        if hasattr(self, 'myhelpera2g'):
            movement_step = self.rx_step_manual_move_gimbal_text_edit.text()
            if movement_step != '':
                try:
                    tmp = int(float(movement_step))
                    incorrect_angle_value = self.checker_gimbal_input_range(tmp)
                    if tmp < 0:
                        tmp = abs(tmp)
                        print("[DEBUG]: The movement step Textbox in the Gimbal Control Panel is always taken as positive. Direction is given by arrows.")
                        
                    data = {'YAW': tmp, 'PITCH': 0}
                    self.myhelpera2g.socket_send_cmd(type_cmd='SETGIMBAL', data=data)
                    print(f"[DEBUG]: gimbal moved {movement_step} degs from application")
                except Exception as e:
                        print("[DEBUG]: Error executing gimbal movement. Most probably wrong MOVEMENT STEP format, ", e)
            else:
                data = {'YAW': 10, 'PITCH': 0}
                self.myhelpera2g.socket_send_cmd(type_cmd='SETGIMBAL', data=data)
                print("[DEBUG]: gimbal moved from application by a predetermined angle of -10 deg, since no angle was specified")
        else:
            print("[DEBUG]: No HelperA2GMeasurements class instance is available")
    
    def up_button_gimbal_drone_callback(self):
        if hasattr(self, 'myhelpera2g'):
            movement_step = self.rx_step_manual_move_gimbal_text_edit.text()
            if movement_step != '':
                try:
                    tmp = int(float(movement_step))
                    incorrect_angle_value = self.checker_gimbal_input_range(tmp)
                    if tmp < 0:
                        tmp = abs(tmp)
                        print("[DEBUG]: The movement step Textbox in the Gimbal Control Panel is always taken as positive. Direction is given by arrows.")
                        
                    data = {'YAW': 0, 'PITCH': tmp}
                    self.myhelpera2g.socket_send_cmd(type_cmd='SETGIMBAL', data=data)
                    print(f"[DEBUG]: gimbal moved {movement_step} degs from application")
                except Exception as e:
                        print("[DEBUG]: Error executing gimbal movement. Most probably wrong MOVEMENT STEP format, ", e)
            else:
                data = {'YAW': 0, 'PITCH': 10}
                self.myhelpera2g.socket_send_cmd(type_cmd='SETGIMBAL', data=data)
                print("[DEBUG]: gimbal moved from application by a predetermined angle of 10 deg, since no angle was specified")
        else:
            print("[DEBUG]: No HelperA2GMeasurements class instance is available")
    
    def down_button_gimbal_drone_callback(self):
        if hasattr(self, 'myhelpera2g'):
            movement_step = self.rx_step_manual_move_gimbal_text_edit.text()
            if movement_step != '':
                try:
                    tmp = int(float(movement_step))
                    incorrect_angle_value = self.checker_gimbal_input_range(tmp)
                    if tmp < 0:
                        tmp = abs(tmp)
                        print("[DEBUG]: The movement step Textbox in the Gimbal Control Panel is always taken as positive. Direction is given by arrows.")
                        
                    data = {'YAW': 0, 'PITCH': -tmp}
                    self.myhelpera2g.socket_send_cmd(type_cmd='SETGIMBAL', data=data)
                    print(f"[DEBUG]: gimbal moved -{movement_step} degs from application")
                except Exception as e:
                        print("[DEBUG]: Error executing gimbal movement. Most probably wrong MOVEMENT STEP format, ", e)
            else:
                data = {'YAW': 0, 'PITCH': -10}
                self.myhelpera2g.socket_send_cmd(type_cmd='SETGIMBAL', data=data)
                print("[DEBUG]: gimbal moved from application by a predetermined angle of -10 deg, since no angle was specified")
        else:
            print("[DEBUG]: No HelperA2GMeasurements class instance is available")
    
    def create_Gimbal_GND_panel(self):
        """
        Creates the panel to control the ground gimbal.
        
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
        
        self.tx_gimbal_manual_move_push_button = QPushButton('Move')
        self.tx_gimbal_manual_move_push_button.clicked.connect(self.move_button_gimbal_gnd_callback)
        self.tx_gimbal_move_left_push_button = QPushButton('<-')
        self.tx_gimbal_move_left_push_button.clicked.connect(self.left_button_gimbal_gnd_callback)
        self.tx_gimbal_move_right_push_button = QPushButton('->')
        self.tx_gimbal_move_right_push_button.clicked.connect(self.right_button_gimbal_gnd_callback)
        self.tx_gimbal_move_up_push_button = QPushButton('^')
        self.tx_gimbal_move_up_push_button.clicked.connect(self.up_button_gimbal_gnd_callback)
        self.tx_gimbal_move_down_push_button = QPushButton('v')
        self.tx_gimbal_move_down_push_button.clicked.connect(self.down_button_gimbal_gnd_callback)
        
        layout = QGridLayout()
        layout.addWidget(self.tx_abs_radio_button, 0, 0, 1, 3)
        layout.addWidget(self.tx_rel_radio_button, 0, 3, 1, 3)
        layout.addWidget(self.tx_gimbal_manual_move_push_button, 0, 6, 1, 4)
        
        layout.addWidget(yaw_label, 1, 0, 1, 1)
        layout.addWidget(self.tx_yaw_value_text_edit, 1, 1, 1, 4)
        layout.addWidget(pitch_label, 1, 5, 1, 1)        
        layout.addWidget(self.tx_pitch_value_text_edit, 1, 6, 1, 4)
        
        layout.addWidget(self.tx_gimbal_move_left_push_button, 3, 2, 1, 2)
        layout.addWidget(self.tx_gimbal_move_right_push_button, 3, 6, 1, 2)
        layout.addWidget(self.tx_gimbal_move_up_push_button, 2, 4, 1, 2)
        layout.addWidget(self.tx_gimbal_move_down_push_button, 4, 4, 1, 2)
        layout.addWidget(self.tx_step_manual_move_gimbal_text_edit, 3, 4, 1, 2)
        
        self.gimbalTXPanel.setLayout(layout)
        
    def create_Gimbal_AIR_panel(self):
        """
        Creates the panel where the air gimbal can be manually controlled.
        
        """
        self.gimbalRXPanel = QGroupBox('Drone Gimbal')
        
        yaw_label = QLabel('Yaw [D]:')
        pitch_label = QLabel('Pitch [D]:')
        
        self.rx_lock_mode_radio_button = QRadioButton("Lock")
        self.rx_follow_mode_radio_button = QRadioButton("Follow")        
        self.rx_lock_mode_radio_button.setChecked(True)
        
        self.rx_lock_mode_radio_button.clicked.connect(self.rx_lock_mode_radio_button_callback)
        self.rx_follow_mode_radio_button.clicked.connect(self.rx_follow_mode_radio_button_callback)

        self.rx_yaw_value_text_edit = QLineEdit('')
        self.rx_pitch_value_text_edit = QLineEdit('')
        
        self.rx_step_manual_move_gimbal_text_edit = QLineEdit('')
        
        self.rx_gimbal_manual_move_push_button = QPushButton('Move')
        self.rx_gimbal_move_left_push_button = QPushButton('<-')
        self.rx_gimbal_move_left_push_button.clicked.connect(self.left_button_gimbal_drone_callback)
        self.rx_gimbal_move_right_push_button = QPushButton('->')
        self.rx_gimbal_move_right_push_button.clicked.connect(self.right_button_gimbal_drone_callback)
        self.rx_gimbal_move_up_push_button = QPushButton('^')
        self.rx_gimbal_move_up_push_button.clicked.connect(self.up_button_gimbal_drone_callback)
        self.rx_gimbal_move_down_push_button = QPushButton('v')
        self.rx_gimbal_move_down_push_button.clicked.connect(self.down_button_gimbal_drone_callback)
        
        layout = QGridLayout()
        layout.addWidget(self.rx_lock_mode_radio_button, 0, 0, 1, 3)
        layout.addWidget(self.rx_follow_mode_radio_button, 0, 3, 1, 3)
        layout.addWidget(self.rx_gimbal_manual_move_push_button, 0, 6, 1, 4)
        
        layout.addWidget(yaw_label, 1, 0, 1, 1)
        layout.addWidget(self.rx_yaw_value_text_edit, 1, 1, 1, 4)
        layout.addWidget(pitch_label, 1, 5, 1, 1)        
        layout.addWidget(self.rx_pitch_value_text_edit, 1, 6, 1, 4)
        
        layout.addWidget(self.rx_gimbal_move_left_push_button, 3, 2, 1, 2)
        layout.addWidget(self.rx_gimbal_move_right_push_button, 3, 6, 1, 2)
        layout.addWidget(self.rx_gimbal_move_up_push_button, 2, 4, 1, 2)
        layout.addWidget(self.rx_gimbal_move_down_push_button, 4, 4, 1, 2)
        layout.addWidget(self.rx_step_manual_move_gimbal_text_edit, 3, 4, 1, 2)
        
        self.gimbalRXPanel.setLayout(layout)

    def rx_lock_mode_radio_button_callback(self):
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
        if hasattr(self, 'myhelpera2g'):
            try:
                data = {'MODE': 'FOLLOW'}
                self.myhelpera2g.socket_send_cmd(type_cmd='SETGIMBAL', data=data)
                print(f"[DEBUG]: gimbal mode set to {data['MODE']} from application")
            except Exception as e:
                print("[DEBUG]: An error ocurred in the transmission of the Gremsy gimbal mode, ", e)
        else:
            print("[DEBUG]: No HelperA2GMeasurements class instance is available")

    def start_meas_button_callback(self):

        # Experiment starts
        self.myhelpera2g.myrfsoc.transmit_signal(carrier_freq=float(self.rf_op_freq_text_edit.text()),
                                                tx_bb_gain=int(self.tx_bb_gain_text_edit.text(), 16),
                                                tx_bb_iq_gain=int(self.tx_bb_iq_gain_text_edit.text(), 16),
                                                tx_bb_phase=int(self.tx_bb_phase_text_edit.text(), 16),
                                                tx_bfrf_gain=int(self.tx_bfrf_gain_text_edit.text(), 16))
        
        data = {'carrier_freq': float(self.rf_op_freq_text_edit.text()),
                'rx_gain_ctrl_bb1': int(self.rx_bb_gain_1_text_edit.text(), 16),
                'rx_gain_ctrl_bb2': int(self.rx_bb_gain_2_text_edit.text(), 16),
                'rx_gain_ctrl_bb3': int(self.rx_bb_gain_3_text_edit.text(), 16),
                'rx_gain_ctrl_bfrf': int(self.rx_bfrf_gain_text_edit.text(), 16)}
        
        self.myhelpera2g.socket_send_cmd(type_cmd='STARTDRONERFSOC', data=data)

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
        self.myhelpera2g.socket_send_cmd(type_cmd='STOPDRONERFSOC')
        print("[DEBUG]: SENT REQUEST to STOP measurement")
        self.start_meas_togglePushButton.setEnabled(True)
        self.stop_meas_togglePushButton.setEnabled(False)
        self.finish_meas_togglePushButton.setEnabled(True)
        self.stop_event_pap_display_thread.set()
        #self.periodical_pap_display_thread.cancel()
    
    def finish_meas_button_callback(self):
        self.myhelpera2g.socket_send_cmd(type_cmd='FINISHDRONERFSOC')
        print("[DEBUG]: SENT REQUEST to FINISH measurement")

        datestr = datetime.datetime.now()
        datestr = datestr.strftime('%Y-%m-%d-%H-%M-%S')
        description = {'H': self.height_from_gnd_text_edit.text(), 'D': self.d_tx_rx_text_edit.text()}
        
        with open('dist_heig_' + datestr + '.txt', 'a+') as file:      
            file.write(json.dumps(description))       
        
        print("[DEBUG]: Saved file with dists between txr and height of drone")
        
        self.start_meas_togglePushButton.setEnabled(True)
        self.stop_meas_togglePushButton.setEnabled(False)
        self.finish_meas_togglePushButton.setEnabled(False)
    
    def manual_meas_radio_button_callback(self):
        self.choose_what_time_is_specified_ComboBox.setEnabled(False)
        self.time_value_text_edit.setEnabled(False)
        
    def auto_meas_radio_button_callback(self):
        self.choose_what_time_is_specified_ComboBox.setEnabled(True)
        self.time_value_text_edit.setEnabled(True)

    def create_Planning_Measurements_panel(self):
        self.planningMeasurementsPanel = QGroupBox('Planning measurements')
        
        self.start_meas_togglePushButton = QPushButton("START")
        #self.start_meas_togglePushButton.setCheckable(True)
        self.start_meas_togglePushButton.setEnabled(False)
        self.start_meas_togglePushButton.clicked.connect(self.start_meas_button_callback)
        
        self.stop_meas_togglePushButton = QPushButton("STOP")
        #self.stop_meas_togglePushButton.setCheckable(True)
        self.stop_meas_togglePushButton.setEnabled(False)
        self.stop_meas_togglePushButton.clicked.connect(self.stop_meas_button_callback)
        
        self.finish_meas_togglePushButton = QPushButton("FINISH")
        #self.finish_meas_togglePushButton.setCheckable(True)
        self.finish_meas_togglePushButton.setEnabled(False)
        self.finish_meas_togglePushButton.clicked.connect(self.finish_meas_button_callback)
        
        self.choose_what_time_is_specified_ComboBox = QComboBox()
        self.choose_what_time_is_specified_ComboBox.addItems(["Time per edge (TPE)", "Time per stop (TPS)", "Total measurement time (TMT)"])

        self.time_value_text_edit = QLineEdit('')
        
        self.height_from_gnd_text_edit = QLineEdit('')
        self.d_tx_rx_text_edit = QLineEdit('')

        self.how_trigger_measurements_radio_button_man = QRadioButton("Manual")
        self.how_trigger_measurements_radio_button_man.clicked.connect(self.manual_meas_radio_button_callback)
        self.how_trigger_measurements_radio_button_auto = QRadioButton("Automatic") 
        self.how_trigger_measurements_radio_button_auto.clicked.connect(self.auto_meas_radio_button_callback)
        self.how_trigger_measurements_radio_button_auto.setChecked(True)
        
        choose_what_type_time_label = QLabel('Choose parameter:')
        value_parameter_label = QLabel('Value:')

        height_from_gndl_label = QLabel('Height [m]:')
        d_tx_rx_label = QLabel('Distance [m]:')
        
        layout = QGridLayout()
        layout.addWidget(self.how_trigger_measurements_radio_button_man, 0, 0, 1, 2)
        layout.addWidget(self.how_trigger_measurements_radio_button_auto, 0, 2, 1, 2)

        layout.addWidget(choose_what_type_time_label, 1, 0, 1, 1)
        layout.addWidget(self.choose_what_time_is_specified_ComboBox, 1, 1, 1, 1)
        layout.addWidget(value_parameter_label, 1, 2, 1, 1)
        layout.addWidget(self.time_value_text_edit, 1, 3, 1, 1)

        layout.addWidget(height_from_gndl_label, 2, 0, 1, 1)
        layout.addWidget(self.height_from_gnd_text_edit, 2, 1, 1, 1)
        layout.addWidget(d_tx_rx_label, 2, 2, 1, 1)
        layout.addWidget(self.d_tx_rx_text_edit, 2, 3, 1, 1)
        
        layout.addWidget(self.start_meas_togglePushButton, 3, 0, 1, 1)
        layout.addWidget(self.stop_meas_togglePushButton, 3, 1, 1, 1)
        layout.addWidget(self.finish_meas_togglePushButton, 3, 2, 1, 2)
        
        self.planningMeasurementsPanel.setLayout(layout)
    
    def create_GPS_visualization_panel(self):
        self.gps_vis_panel = QGroupBox('GPS visualization')
        # Create a Figure object
        fig_gps = Figure()

        # Create a FigureCanvas widget
        canvas = FigureCanvas(fig_gps)

        # Create a QVBoxLayout to hold the canvas
        #layout = QVBoxLayout()
        

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
        layout.addWidget(canvas, 0, 0, 8, 10)
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

        # Create a subplot on the Figure
        ax_gps = fig_gps.add_subplot(111)

        hi_q = {'LAT': 60.18592, 'LON': 24.81174 }
        
        torbacka_point = {'LAT': 60.07850739357558, 'LON': 24.171551864664867}
        #mygpsonmap = GpsOnMap('planet_24.81,60.182_24.829,60.189.osm.pbf', canvas=canvas, fig=fig_gps, ax=ax_gps, air_coord=hi_q)
        mygpsonmap = GpsOnMap('torbacka_planet_24.162,60.076_24.18,60.082.osm.pbf', canvas=canvas, fig=fig_gps, ax=ax_gps, air_coord=torbacka_point)
        
        self.mygpsonmap = mygpsonmap
    
    def create_pap_plot_panel(self):
        self.papPlotPanel = QGroupBox('PAP')
        self.time_snaps = 22
        self.plot_widget = pg.PlotWidget() 
        self.plot_widget.setLabel('left', 'Beam steering angle [deg]')
        self.plot_widget.setLabel('bottom', 'Time snapshot number')

        layout = QVBoxLayout()
        layout.addWidget(self.plot_widget)
        self.papPlotPanel.setLayout(layout)

        rx_sivers_beam_index_mapping_file = open('rx_sivers_beam_index_mapping.csv')
        csvreader = csv.reader(rx_sivers_beam_index_mapping_file)
        beam_idx_map = [float(i[1]) for cnt,i in enumerate(csvreader) if cnt != 0]
        ticksla = beam_idx_map[::4]
        self.beam_angs = ticksla
        ticks = np.arange(0,16) 
        y_ticks = [(ticks[cnt], f'{tickla:1.2f}°') for cnt, tickla in enumerate(ticksla)]
        self.plot_widget.getAxis('left').setTicks([y_ticks, []])

        x_ticks = [(i, str(i)) for i in np.arange(self.time_snaps)]
        self.plot_widget.getAxis('bottom').setTicks([x_ticks, []])

    def create_pdp_plot_panel(self):
        self.pdpPlotPanel = QGroupBox('PDP')
        
        fig_pdp = Figure()

        # Create a FigureCanvas widget
        canvas = FigureCanvas(fig_pdp)

        # Create a QVBoxLayout to hold the canvas
        layout = QVBoxLayout()
        layout.addWidget(canvas)

        # Set the layout of the group box
        self.pdpPlotPanel.setLayout(layout)

        # Create a subplot on the Figure
        ax_pdp = fig_pdp.add_subplot(111)
        
        self.fig_pdp = fig_pdp
        self.ax_pdp = ax_pdp
    
    def closeEvent(self, event):
        if hasattr(self, 'myhelpera2g'):
            self.myhelpera2g.HelperA2GStopCom(DISC_WHAT='ALL')
        #if hasattr(self, 'periodical_pap_display_thread'):
            #self.periodical_pap_display_thread.cancel()
            #self.periodical_pap_display_thread.stop()
        if hasattr(self, 'periodical_gps_display_thread'):
            self.periodical_gps_display_thread.cancel()
        if hasattr(self, 'periodical_gimbal_follow_thread'):
            self.periodical_gimbal_follow_thread.cancel()
        
        # Last thing to do is to redirect the stdout
        #sys.stdout = self.original_stdout
            
    def eventFilter(self, source, event):
        if event.type()== event.Close:
            self.closeEvent(event)
            return True
        
        return super().eventFilter(source,event)

if __name__ == '__main__':
#    appctxt = ApplicationContext()
    app = QApplication([])
    gallery = WidgetGallery()
    gallery.show()

    #gallery.start_GUI_threads()
    
    #sys.exit(appctxt.app.exec())
    #app.exec_()
#    gallery.myhelpera2g.HelperA2GStopCom(DISC_WHAT='GIMBAL')
    sys.exit(app.exec())

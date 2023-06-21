import re
import subprocess
import paramiko
import ping3
import time
import can#from fbs_runtime.application_context.PyQt5 import ApplicationContext
from serial.tools.list_ports import comports
import typing
from PyQt5.QtCore import QDateTime, Qt, QTimer, QObject, QThread, QMutex, pyqtSignal
from PyQt5.QtWidgets import (QApplication, QCheckBox, QComboBox, QDateTimeEdit,
        QDial, QDialog, QGridLayout, QGroupBox, QHBoxLayout, QLabel, QLineEdit,
        QProgressBar, QPushButton, QRadioButton, QScrollBar, QSizePolicy,
        QSlider, QSpinBox, QStyleFactory, QTableWidget, QTabWidget, QTextEdit,
        QVBoxLayout, QWidget)

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

import sys
from a2gmeasurements import GimbalRS2, GpsSignaling, HelperA2GMeasurements, RFSoCRemoteControlFromHost, RepeatTimer
from a2gUtils import GpsOnMap, geocentric2geodetic, geodetic2geocentric

import tkinter as tk
from tkinter import simpledialog, messagebox


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

        # Parameters of the GUI
        self.number_lines_log_terminal = 100
        self.log_terminal_txt = ""

        self.create_check_connections_panel()
        #self.create_GPS_panel()
        self.create_log_terminal()
        self.create_Gimbal_GND_panel()
        self.create_Gimbal_AIR_panel()
        self.create_FPGA_settings_panel()
        self.create_Beamsteering_settings_panel()
        self.create_Planning_Measurements_panel()
        self.create_GPS_visualization_panel()
        self.create_pdp_plot_panel()

        mainLayout = QGridLayout()
        mainLayout.addWidget(self.checkConnPanel, 0, 0, 1 , 4)
        mainLayout.addWidget(self.gimbalTXPanel, 1, 0, 1, 1)
        mainLayout.addWidget(self.gimbalRXPanel, 1, 1, 1, 1)
        mainLayout.addWidget(self.fpgaSettingsPanel, 1, 2, 1, 1)
        mainLayout.addWidget(self.beamsteeringSettingsPanel, 1, 3, 1 , 1)
        #mainLayout.addWidget(self.gpsPanel, 2, 0)
        mainLayout.addWidget(self.gps_vis_panel, 2, 0, 3, 2)
        mainLayout.addWidget(self.pdpPlotPanel, 2, 2, 3, 2)
        mainLayout.addWidget(self.planningMeasurementsPanel, 5, 0, 1, 2)
        mainLayout.addWidget(self.log_widget, 5, 2, 1, 2)
        
        self.write_to_log_terminal('This is an example text')
        self.write_to_log_terminal('This is a new line')
        self.write_to_log_terminal('what ever')
        self.write_to_log_terminal('evasdgf')
        self.write_to_log_terminal('sadgfndsaf')
        self.write_to_log_terminal('dsgfmn')
        self.write_to_log_terminal('what ,mndsfb')
        self.write_to_log_terminal('sdafnb fd')        
                
        self.setLayout(mainLayout)

        #self.init_external_objs()
    
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
        success_ping_network = ping3.ping(drone_ip, timeout=10)
        
        #if success_ping_network is not None:
        if success_ping_network:
            success_ping_network = True
            
            try:
                remote_drone_conn = paramiko.SSHClient()
                remote_drone_conn.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                remote_drone_conn.connect(drone_ip, username=username, password=password)
                self.remote_drone_conn = remote_drone_conn
                print("[DEBUG]: SSH connection successful.")            
            except paramiko.AuthenticationException:
                print("SSH Authentication failed. Please check your credentials.")
                success_air_node_ssh = False
                self.remote_drone_conn = None
                success_drone_fpga = None
            except paramiko.SSHException as ssh_exception:
                print(f"Unable to establish SSH connection: {ssh_exception}")
                success_air_node_ssh = False
                self.remote_drone_conn = None
                success_drone_fpga = None
            except Exception as e:
                print(f"An error occurred: {e}")
                success_air_node_ssh = False
                self.remote_drone_conn = None
                success_drone_fpga = None
            else:
                success_air_node_ssh = True
                success_drone_fpga = self.check_if_drone_fpga_connected()
        else:
            success_ping_network = False
            success_air_node_ssh = None
            success_drone_fpga = None
        
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

        # Print the output and error, if any
        if "Reply" in output:
            print("[DEBUG]: RFSoC detected at drone node")
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
        success_ping_gnd_fpga = ping3.ping(gnd_fpga_static_ip_addr, timeout=7)
        if success_ping_gnd_fpga is not None:
            print("[DEBUG]: GND FPGA is detected in GND node")
            success_ping_gnd_fpga = True
        else:
            print("[DEBUG]: GND FPGA is NOT detected in GND node")
            success_ping_gnd_fpga = False
        
        return success_ping_gnd_fpga
    
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
        else:
            success_gnd_gps = False
            
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
            return
        else:
            1
    
    def get_gnd_ip_node_address(self):
        """
        Gets the IP address of the ground node.
        
        Caller function IS RESPONSIBLE for checking if there is a WIFI operating. 
        
        """
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
            SUCCESS_PING_DRONE, SUCCESS_SSH, SUCCES_DRONE_FPGA = self.check_if_ssh_2_drone_reached(self.DRONE_ADDRESS, "manifold-uav-vtt", "mfold2208")
            self.network_exists_label_modifiable.setText(str(SUCCESS_PING_DRONE))
            self.ssh_conn_gnd_2_drone_label_modifiable.setText(str(SUCCESS_SSH))
            self.drone_rfsoc_conn_label_modifiable.setText(str(SUCCES_DRONE_FPGA))

        SUCCESS_GND_FPGA = self.check_if_gnd_fpga_connected()
        SUCCESS_GND_GIMBAL = self.check_if_gnd_gimbal_connected()        
        SUCCESS_GND_GPS = self.check_if_gnd_gps_connected()
        
        self.get_gnd_ip_node_address()
        self.gnd_gimbal_conn_label_modifiable.setText(str(SUCCESS_GND_GIMBAL))
        self.gnd_gps_conn_label_modifiable.setText(str(SUCCESS_GND_GPS))
        self.gnd_rfsoc_conn_label_modifiable.setText(str(SUCCESS_GND_FPGA))
        self.gnd_ip_addr_value_label.setText(self.GND_ADDRESS)
        #self.drone_gps_conn_label_modifiable.setText()
    
    def create_class_instances(self, IsGPS=False, IsGimbal=False, GPS_Stream_Interval='sec1'):
        """
        Responsible for creating any objects (class instances) that will be used to connect to and control the devices,

        Args:
            IsGPS (bool, optional): _description_. Defaults to False.
            IsGimbal (bool, optional): _description_. Defaults to False.
            GPS_Stream_Interval (str, optional): _description_. Defaults to 'sec1'.
        """
        self.myhelpera2g = HelperA2GMeasurements('GROUND', self.GND_ADDRESS, DBG_LVL_0=False, DBG_LVL_1=False, 
                                                 IsGimbal=IsGimbal, IsGPS=IsGPS, GPS_Stream_Interval=GPS_Stream_Interval, 
                                                 AVG_CALLBACK_TIME_SOCKET_RECEIVE_FCN=0.01)            
    def disconnect_devices(self):
        """
        Wrapper to HelperA2GStopCom.
        
        """
        disc_what = []
        if self.myhelpera2g.myGimbal.GIMBAL_CONN_SUCCES:
            disc_what.append('GIMBAL')
        if self.myhelpera2g.mySeptentrioGPS.GPS_CONN_SUCCESS:
            disc_what.append('GPS')
            
        if len(disc_what) > 0:            
            self.myhelpera2g.HelperA2GStopCom(DISC_WHAT=disc_what)
    
    def start_GUI_threads(self):
        """
        Start GUI related threads. This threads are related only to the display of information
        on the GUI.
        
        """
        self.update_time_gps = 1
        self.periodical_gps_display_thread = RepeatTimer(self.update_time_gps, self.periodical_gps_display_callback) 

    def periodical_gps_display_callback(self):
        
        
        # Display ground node coords
        coords, head_info = self.get_last_sbf_buffer_info(what='Both')
            
        if coords['X'] == self.ERR_GPS_CODE_BUFF_NULL or self.ERR_GPS_CODE_SMALL_BUFF_SZ:
            pass
        else:
            lat_gnd_node, lon_gnd_node, height_node = geocentric2geodetic(coords['X'], coords['Y'], coords['Z'])
            self.mygpsonmap.show_air_moving(lat=lat_gnd_node, lon=lon_gnd_node) 
        
        # Display drone node coords
        # The coordinates shown will be the coordinates of up to self.update_time_fps before
        if hasattr(self.myhelpera2g, 'last_drone_coords_requested'):
            self.mygpsonmap.show_air_moving(lat=self.myhelpera2g.last_drone_coords_requested['LAT'], lon=self.myhelpera2g.last_drone_coords_requested['LON'])
            
        self.myhelpera2g.socket_send_cmd(type_cmd='GETGPS')
            
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
        '''
        Access the widget contents by using self.log_widget.setPlainText('')
        
        '''
        self.log_widget = CustomTextEdit(self)
        
        #self.log_widget = QTextEdit(self)
        self.log_widget.setReadOnly(True) # make it read-only        
        
        # Redirect output of myFunc to the QTextEdit widget
        sys.stdout = self.log_widget
    
    def create_check_connections_panel(self):
        self.checkConnPanel = QGroupBox('Connections checker')

        gnd_gimbal_conn_label = QLabel('Ground gimbal:')
        gnd_gps_conn_label = QLabel('Ground GPS:')
        gnd_rfsoc_conn_label = QLabel('Ground RFSoC:')
        network_exists_label = QLabel('Able to PING drone?:')
        ssh_conn_gnd_2_drone_label = QLabel('SSH to drone:')
        drone_rfsoc_conn_label = QLabel('Drone RFSoC:')
        drone_gps_conn_label = QLabel('Drone GPS:')

        gnd_ip_addr_label = QLabel('Ground IP:')
        air_ip_addr_label = QLabel('Drone IP:')
        self.gnd_ip_addr_value_label = QLabel('')
        self.air_ip_addr_value_text_edit = QLineEdit('')
        self.check_connections_push_button = QPushButton('Check')
        self.check_connections_push_button.clicked.connect(self.check_status_all_devices)

        self.gnd_gimbal_conn_label_modifiable = QLabel('--')
        self.gnd_gps_conn_label_modifiable = QLabel('--')
        self.gnd_rfsoc_conn_label_modifiable = QLabel('--')
        self.network_exists_label_modifiable = QLabel('--')
        self.ssh_conn_gnd_2_drone_label_modifiable = QLabel('--')
        self.drone_rfsoc_conn_label_modifiable = QLabel('--')
        self.drone_gps_conn_label_modifiable = QLabel('--')

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
        layout.addWidget(air_ip_addr_label, 1, 0, 1, 3)
        layout.addWidget(self.air_ip_addr_value_text_edit, 1, 3, 1, 3)
        layout.addWidget(self.check_connections_push_button, 1, 6, 1, 10)
        

        self.checkConnPanel.setLayout(layout)

    def create_FPGA_settings_panel(self):
        self.fpgaSettingsPanel = QGroupBox('FPGA settings')
        
    def create_Beamsteering_settings_panel(self):
        self.beamsteeringSettingsPanel = QGroupBox('Beamsteering settings')

    def left_move_gnd_gimbal(self):
        1
    
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
        #self.tx_gimbal_manual_move_push_button.clicked.connect(self.)
        self.tx_gimbal_move_left_push_button = QPushButton('<-')
        self.tx_gimbal_move_right_push_button = QPushButton('->')
        self.tx_gimbal_move_up_push_button = QPushButton('^')
        self.tx_gimbal_move_down_push_button = QPushButton('v')
        
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
        
        self.rx_abs_radio_button = QRadioButton("Absolute")
        self.rx_rel_radio_button = QRadioButton("Relative")        
        self.rx_abs_radio_button.setChecked(True)
        
        self.rx_yaw_value_text_edit = QLineEdit('')
        self.rx_pitch_value_text_edit = QLineEdit('')
        
        self.rx_step_manual_move_gimbal_text_edit = QLineEdit('')
        
        self.rx_gimbal_manual_move_push_button = QPushButton('Move')
        self.rx_gimbal_move_left_push_button = QPushButton('<-')
        self.rx_gimbal_move_right_push_button = QPushButton('->')
        self.rx_gimbal_move_up_push_button = QPushButton('^')
        self.rx_gimbal_move_down_push_button = QPushButton('v')
        
        layout = QGridLayout()
        layout.addWidget(self.rx_abs_radio_button, 0, 0, 1, 3)
        layout.addWidget(self.rx_rel_radio_button, 0, 3, 1, 3)
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
    
    def create_Planning_Measurements_panel(self):
        self.planningMeasurementsPanel = QGroupBox('Planning measurements')
        
        self.start_meas_togglePushButton = QPushButton("START")
        self.start_meas_togglePushButton.setCheckable(True)
        
        #self.start_meas_togglePushButton.setChecked(True)
        
        self.stop_meas_togglePushButton = QPushButton("STOP")
        self.stop_meas_togglePushButton.setCheckable(True)
        #self.stop_meas_togglePushButton.setChecked(True)
        
        self.finish_meas_togglePushButton = QPushButton("FINISH")
        self.finish_meas_togglePushButton.setCheckable(True)
        #self.finish_meas_togglePushButton.setChecked(True)
        
        self.choose_what_time_is_specified_ComboBox = QComboBox()
        self.choose_what_time_is_specified_ComboBox.addItems(["Time per edge (TPE)", "Time per stop (TPS)", "Total measurement time (TMT)"])

        self.time_value_text_edit = QLineEdit('')
        
        self.how_trigger_measurements_radio_button_man = QRadioButton("Manual")
        self.how_trigger_measurements_radio_button_auto = QRadioButton("Automatic") 
        self.how_trigger_measurements_radio_button_man.setChecked(True)
        
        choose_what_type_time_label = QLabel('Choose parameter:')
        value_parameter_label = QLabel('Value:')
        
        layout = QGridLayout()
        layout.addWidget(self.how_trigger_measurements_radio_button_man, 0, 0, 1, 2)
        layout.addWidget(self.how_trigger_measurements_radio_button_auto, 0, 2, 1, 2)
        layout.addWidget(choose_what_type_time_label, 1, 0, 1, 1)
        layout.addWidget(self.choose_what_time_is_specified_ComboBox, 1, 1, 1, 1)
        layout.addWidget(value_parameter_label, 1, 2, 1, 1)
        layout.addWidget(self.time_value_text_edit, 1, 3, 1, 1)
        
        layout.addWidget(self.start_meas_togglePushButton, 2, 0, 1, 1)
        layout.addWidget(self.stop_meas_togglePushButton, 2, 1, 1, 1)
        layout.addWidget(self.finish_meas_togglePushButton, 2, 2, 1, 2)
        
        self.planningMeasurementsPanel.setLayout(layout)
    
    def create_GPS_visualization_panel(self):
        self.gps_vis_panel = QGroupBox('GPS visualization')
        # Create a Figure object
        fig_gps = Figure()

        # Create a FigureCanvas widget
        canvas = FigureCanvas(fig_gps)

        # Create a QVBoxLayout to hold the canvas
        layout = QVBoxLayout()
        layout.addWidget(canvas)

        # Set the layout of the group box
        self.gps_vis_panel.setLayout(layout)

        # Create a subplot on the Figure
        ax_gps = fig_gps.add_subplot(111)

        hi_q = {'LAT': 60.18592, 'LON': 24.81174 }
        
        torbacka_point = {'LAT': 60.07850739357558, 'LON': 24.171551864664867}
        #mygpsonmap = GpsOnMap('planet_24.81,60.182_24.829,60.189.osm.pbf', canvas=canvas, fig=fig_gps, ax=ax_gps, air_coord=hi_q)
        mygpsonmap = GpsOnMap('torbacka_planet_24.162,60.076_24.18,60.082.osm.pbf', canvas=canvas, fig=fig_gps, ax=ax_gps, air_coord=torbacka_point)
        
        self.mygpsonmap = mygpsonmap
        
    def create_GPS_panel(self):
        self.gpsPanel = QGroupBox('GPS Information')
        
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
        layout.addWidget(tx_info_label, 0, 0, 1, 5)
        layout.addWidget(rx_info_label, 0, 5, 1, 5)
        layout.addWidget(tx_x_label, 1, 0, 1, 1)
        layout.addWidget(tx_z_label, 2, 0, 1, 1)
        layout.addWidget(tx_y_label, 3, 0, 1, 1)
        layout.addWidget(tx_x_value_label, 1, 1, 1, 4)
        layout.addWidget(tx_y_value_label, 2, 1, 1, 4)
        layout.addWidget(tx_z_value_label, 3, 1, 1, 4)
        layout.addWidget(rx_x_label, 1, 5, 1, 1)
        layout.addWidget(rx_z_label, 2, 5, 1, 1)
        layout.addWidget(rx_y_label, 3, 5, 1, 1)
        layout.addWidget(rx_x_value_label, 1, 6, 1, 4)
        layout.addWidget(rx_y_value_label, 2, 6, 1, 4)
        layout.addWidget(rx_z_value_label, 3, 6, 1, 4)
        #layout.setRowStretch(3, 1)
        
        self.gpsPanel.setLayout(layout)
        
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
                
if __name__ == '__main__':
#    appctxt = ApplicationContext()
    app = QApplication([])
    gallery = WidgetGallery()
    gallery.show()
    
    #gallery.get_ip_node_addresses()
    #gallery.check_status_all_devices()
    #gallery.create_class_instances(IsGPS=False, IsGimbal=False, GPS_Stream_Interval='sec1')
    #gallery.start_GUI_threads()
    
    #sys.exit(appctxt.app.exec())
    sys.exit(app.exec())

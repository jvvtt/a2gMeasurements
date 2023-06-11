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
from a2gmeasurements import GimbalRS2, GpsSignaling, HelperA2GMeasurements, RFSoCRemoteControlFromHost
from a2gUtils import GpsOnMap

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

        self.create_GPS_panel()
        self.create_log_terminal()
        self.create_Gimbal_TX_panel()
        self.create_Gimbal_RX_panel()
        self.create_FPGA_settings_panel()
        self.create_Beamsteering_settings_panel()
        self.create_Planning_Measurements_panel()
        self.create_GPS_visualization_panel()
        self.create_pdp_plot_panel()

        mainLayout = QGridLayout()
        mainLayout.addWidget(self.gimbalTXPanel, 0, 0)
        mainLayout.addWidget(self.gimbalRXPanel, 0, 1)
        mainLayout.addWidget(self.gpsPanel, 1, 0)
        mainLayout.addWidget(self.planningMeasurementsPanel, 1, 1)
        mainLayout.addWidget(self.fpgaSettingsPanel, 2, 0)
        mainLayout.addWidget(self.beamsteeringSettingsPanel, 2, 1)
        mainLayout.addWidget(self.pdpPlotPanel, 3, 0, 1, 2)        
        mainLayout.addWidget(self.gps_vis_panel, 4, 0, 1, 2)
        mainLayout.addWidget(self.log_widget, 5, 0, 1, 2)
        
        
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
    
    def check_if_ssh_reached(self, drone_ip, username, password):
        success_ping_network = ping3.ping(drone_ip, timeout=7)
        if success_ping_network is not None:
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
            except paramiko.SSHException as ssh_exception:
                print(f"Unable to establish SSH connection: {ssh_exception}")
                success_air_node_ssh = False
            except Exception as e:
                print(f"An error occurred: {e}")
                success_air_node_ssh = False
            else:
                success_air_node_ssh = True
                success_drone_fpga = self.check_if_drone_fpga_connected()
        else:
            # Try again with a longer timeout
            success_ping_network = ping3.ping(drone_ip, timeout=20)
            
            if success_ping_network is not None:
                success_ping_network = True
            else:
                success_ping_network = False
        
        return success_ping_network, success_air_node_ssh, success_drone_fpga
    
    def check_if_drone_fpga_connected(self, drone_fpga_static_ip_addr='10.1.1.40'):
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
    
    def check_if_gimbal_connected(self):
        """
        Function for checking if gimbal RS2 is connected on ground node.

        Returns:
            MODE_NO_GIMBAL (int): 0 if gimbal RS2 is connected. 
                                  1 if gimbal is NOT connected and USER wants to continue WITHOUT gimbal.
                                  2 if gimbal is NOT connected and USER wants to continue WITH gimbal.
        """
               
        try:
            # Check if gimbal is connected by looking if connection is established
            bus = can.interface.Bus(interface="pcan", channel="PCAN_USBBUS1", bitrate=1000000)
        except Exception as e:
            tmp = messagebox.askyesno(title="NO GIMBAL CONNECTED", message="No ground gimbal was detected. The system can not work without a ground gimbal. You can always control the gimbal manually, but check that the gimbal is powered on and connected to the computer. \n\nIf the gimbal is NOT connected to the computer but powered on, the system can work, but no information about gimbal direction will be obtained, neither control of the gimbal through the GUI will be allowed. \n\nDo you want to continue without a gimbal connection?")
            if tmp:
                MODE_NO_GIMBAL = 1
            else:
                MODE_NO_GIMBAL = 2
        else:
            bus.shutdown()
            del bus
            MODE_NO_GIMBAL = 0
        
        return MODE_NO_GIMBAL
    
    def check_if_gnd_gps_connected(self):
        """
        Function for checking if gps is connected to the ground node.

        Returns:
            MODE_NO_GPS (int): 0 if gps is connected. 
                               1 if gps is NOT connected and USER wants to continue WITHOUT gps.
                               2 if gps is NOT connected and USER wants to continue WITH gps.
        """
        
        tmp = []
        for (_, desc, _) in sorted(comports()):
            tmp.append("Septentrio" in desc)
        if any(tmp):
            MODE_NO_GPS = 0
        else:
            tmp = messagebox.askyesno(title="NO GPS CONNECTED", message="No gps was detected. The system can work without the GPS, but no ground GPS coordinates will be saved and FOLLOWING MODE will not be available. \n\nDo you want to continue without gps?")
            
            if tmp:
                MODE_NO_GPS = 1
            else:
                MODE_NO_GPS = 2
            
        return MODE_NO_GPS
    
    def init_external_objs(self):
        ROOT = tk.Tk()

        ROOT.withdraw()
        
        #GND_ADDRESS = '192.168.0.2' # default address, but needs to be checked
        GND_ADDRESS = simpledialog.askstring(title="SERVER ADDRESS", prompt="After connecting both nodes to the router, check and enter IP address of the ground node:")
        DRONE_ADDRESS = simpledialog.askstring(title="CLIENT ADDRESS", prompt="After connecting both nodes to the router, check and enter IP address of the drone node:")
        
        if GND_ADDRESS is None or DRONE_ADDRESS is None:
            messagebox.showerror(title="MISSING CLIENT OR SERVER ADDRESSES", message="Both nodes IP addresses need to be specified. \nFor controlling the drone gps, for following mode of the ground gimbal and to do measurements in a predefined way, WIFI is required. \nIf no WIFI network is present, measurements have to be started manually at both stations and will be recorded continuously without differentiating if the drone is on ground or on the air. \nFor such case, modify the variable 'ID' in the script 'do_continuous_measurements_no_wifi.py' depending on which node the file will be executed. \nExecute first the script in the ground node and then in the drone node.")
            return
        
        SUCCESS_GND_FPGA = self.check_if_gnd_fpga_connected()
        SUCCESS_PING_DRONE, SUCCESS_SSH, SUCCES_DRONE_FPGA = self.check_if_ssh_reached(DRONE_ADDRESS, "manifold-uav-vtt", "mfold2208")
        
        if SUCCESS_GND_FPGA and SUCCES_DRONE_FPGA:
            1
        elif SUCCESS_GND_FPGA and SUCCESS_SSH:
            1
        elif SUCCESS_GND_FPGA and SUCCESS_PING_DRONE:
            1
        
        MODE_NO_GIMBAL = self.check_if_gimbal_connected()        
        MODE_NO_GPS = self.check_if_gnd_gps_connected()
        
        while(MODE_NO_GIMBAL == 2):
            MODE_NO_GIMBAL = self.check_if_gimbal_connected()
            time.sleep(0.5)
                
        while(MODE_NO_GPS == 2):
            MODE_NO_GPS = self.check_if_gnd_gps_connected()
            time.sleep(0.5)        
        
        if MODE_NO_GIMBAL == 0 and MODE_NO_GPS == 0:        
            self.myhelpera2g = HelperA2GMeasurements('GROUND', GND_ADDRESS, 
                 DBG_LVL_0=False, DBG_LVL_1=False, IsGimbal=True, IsGPS=True, 
                 GPS_Stream_Interval='sec1', AVG_CALLBACK_TIME_SOCKET_RECEIVE_FCN=0.01)
        
            print(self.myhelpera2g.myGimbal.GIMBAL_CONN_SUCCES)
            print(self.myhelpera2g.mySeptentrioGPS.GPS_CONN_SUCCESS)
            
            disc_what = []
            if self.myhelpera2g.myGimbal.GIMBAL_CONN_SUCCES:
                disc_what.append('GIMBAL')
            if self.myhelpera2g.mySeptentrioGPS.GPS_CONN_SUCCESS:
                disc_what.append('GPS')
            
            if len(disc_what) > 0:            
                self.myhelpera2g.HelperA2GStopCom(DISC_WHAT=disc_what)
        
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
    
    def create_FPGA_settings_panel(self):
        self.fpgaSettingsPanel = QGroupBox('FPGA settings')
        
    def create_Beamsteering_settings_panel(self):
        self.beamsteeringSettingsPanel = QGroupBox('Beamsteering settings')
    
    def create_Gimbal_TX_panel(self):
        self.gimbalTXPanel = QGroupBox('Gimbal TX')
        
        yaw_label = QLabel('Yaw [D]:')
        pitch_label = QLabel('Pitch [D]:')
        
        self.tx_abs_radio_button = QRadioButton("Absolute")
        self.tx_rel_radio_button = QRadioButton("Relative")        
        self.tx_abs_radio_button.setChecked(True)
        
        self.tx_yaw_value_text_edit = QLineEdit('')
        self.tx_pitch_value_text_edit = QLineEdit('')
        
        self.tx_step_manual_move_gimbal_text_edit = QLineEdit('')
        
        self.tx_gimbal_manual_move_push_button = QPushButton('Move')
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
        
    def create_Gimbal_RX_panel(self):
        self.gimbalRXPanel = QGroupBox('Gimbal RX')
        
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
        mygpsonmap = GpsOnMap('planet_24.81,60.182_24.829,60.189.osm.pbf', canvas=canvas, fig=fig, ax=ax, air_coord=hi_q)
        
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
                
if __name__ == '__main__':
#    appctxt = ApplicationContext()
    app = QApplication([])
    gallery = WidgetGallery()
    gallery.show()
    #gallery.init_external_objs()
    #sys.exit(appctxt.app.exec())
    sys.exit(app.exec())

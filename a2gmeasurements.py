import logging
from itertools import groupby
from operator import itemgetter
import xmltodict
import datetime
import time
import struct
from ctypes import *
import numpy as np
from check_sum import *
from pynput import keyboard
import can
import socket
import threading
import pynmea2
import serial
import sys
from serial.tools.list_ports import comports
import pyproj as proj
import json
import pyvisa
import pandas as pd
from sys import platform
from crc import Calculator, Configuration, Crc16
from a2gUtils import geocentric2geodetic, geodetic2geocentric

"""
Author: Julian D. Villegas G.
Organization: VTT
Version: 1.1
e-mail: julian.villegas@vtt.fi

Gimbal control adapted and extended from https://github.com/ceinem/dji_rs2_ros_controller, based as well on DJI R SDK demo software.
"""

class GimbalRS2(object):
    def __init__(self, speed=1800/3.47):
        self.header = 0xAA
        self.enc = 0x00
        self.res1 = 0x00
        self.res2 = 0x00
        self.res3 = 0x00
        self.seq = 0x0002

        self.send_id = 0x223
        self.recv_id = 0x222

        self.MAX_CAN_FRAME_LEN = 8

        self.can_recv_msg_buffer = []
        self.can_recv_msg_len_buffer = []
        self.can_recv_buffer_len = 10

        self.roll = 0.0
        self.pitch = 0.0
        self.yaw = 0.0

        self.speed =  speed# deg/s
        self.MAIN_LOOP_STOP = True
        self.keyboard_set_flag = False
        self.keyboard_buff = []

        self.cntBytes = 0
  
    def seq_num(self):
        """
        Updates the sequence number of the gimbal data.

        Returns:
            hex: number in hexadecimal
        """

        if self.seq >= 0xFFFD:
            self.seq = 0x0002
        self.seq += 1
        # Seq_Init_Data = 0x1122
        seq_str = "%04x" % self.seq
        return seq_str[2:] + ":" + seq_str[0:2]

    def can_buffer_to_full_frame(self):
        """
        Saves the full DJI R frame message: its format is explaind in the DJI R SDK Protocol and User Interface
        
        Returns:
            list: full frame 
        """
        full_msg_frames = []
        full_frame_counter = 0
        for i in range(len(self.can_recv_msg_buffer)):
            msg = self.can_recv_msg_buffer[i]
            length = self.can_recv_msg_len_buffer[i]
            msg = msg[:length]
            cmd_data = ':'.join(msg)
            # print("len: " + str(length) + " - " +
            #       str(msg) + " -> " + cmd_data)
            if msg[0] == "AA":
                full_msg_frames.append(msg)
                full_frame_counter += 1
            if msg[0] != "AA" and (full_frame_counter > 0):
                # full_msg_frames[-1] += ":"
                for byte in msg:
                    full_msg_frames[-1].append(byte)
        return full_msg_frames

    def validate_api_call(self, data_frame):
        """
        CRC error check.

        Args:
            data_frame (list): DJI frame message

        Returns:
            boolean: pass the CRC32 check or not
        """
        validated = False
        check_sum = ':'.join(data_frame[-4:])
        data = ':'.join(data_frame[:-4])
        # # print(len(hex_data))
        # # print(data)
        if len(data_frame) >= 8:
            if check_sum == calc_crc32(data):
                #         # print("Approved Message: " + str(hex_data))
                header = ':'.join(data_frame[:10])
                header_check_sum = ':'.join(data_frame[10:12])
                if header_check_sum == calc_crc16(header):
                    validated = True
        return validated

    def parse_position_response(self, data_frame):
        """
        Retrieve the position from the full DJI frame message

        Args:
            data_frame (): DJI frame message
        """
        pos_data = data_frame[16:-4]
        yaw = int(
            '0x' + pos_data[1] + pos_data[0], base=16)
        roll = int(
            '0x' + pos_data[3] + pos_data[2], base=16)
        pitch = int(
            '0x' + pos_data[5] + pos_data[4], base=16)
        if yaw > 1800:
            yaw -= 65538
        if roll > 1800:
            roll -= 65538
        if pitch > 1800:
            pitch -= 65538

        # Radians
        #self.yaw = yaw * 0.1 * np.pi / 180
        #self.roll = roll * 0.1 * np.pi / 180
        #self.pitch = pitch * 0.1 * np.pi / 180

        # Degrees
        self.yaw = yaw * 0.1 
        self.roll = roll * 0.1
        self.pitch = pitch * 0.1
        
        output = "Pitch: " + \
            str(self.pitch) + ", Yaw: " + \
            str(self.yaw) + ", Roll: " + str(self.roll)
        
        print(output + '\n')
        
    def can_callback(self, data):
        """
        Callback for can recv.

        Args:
            data (): DJI frame message
        """
        #if data.id == self.recv_id:
            # print(len(data.data))
            # print(data)
        
        #str_data = ['{:02X}'.format(struct.unpack('<1B', i)[0]) for i in data.data]
        str_data = ['{:02X}'.format(i) for i in data.data]

        # print(str_data)
        
        self.can_recv_msg_buffer.append(str_data)
        self.can_recv_msg_len_buffer.append(data.dlc)

        if len(self.can_recv_msg_buffer) > self.can_recv_buffer_len:
                # print("Pop")
            self.can_recv_msg_buffer.pop(0)
            self.can_recv_msg_len_buffer.pop(0)

        full_msg_frames = self.can_buffer_to_full_frame()

            # print(full_msg_frames)
        for hex_data in full_msg_frames:
            if self.validate_api_call(hex_data):
                # ic(':'.join(hex_data[16:-4]))
                request_data = ":".join(hex_data[12:14])
                # print("Req: " + str(request_data))
                if request_data == "0E:02":
                    # This is response data to a get position request
                    self.parse_position_response(hex_data)

    def setPosControl(self, yaw, roll, pitch, ctrl_byte=0x01, time_for_action=0x14):
        """
        Set the gimbal position by providing the yaw, roll and pitch

        Args:
            yaw (int): yaw value
            roll (int): roll value
            pitch (int): pitch value
            ctrl_byte (hexadecimal, optional): _description_. Defaults to 0x01.
            time_for_action (hexadecimal, optional): _description_. Defaults to 0x14.

        Returns:
            _type_: _description_
        """
        
        # yaw, roll, pitch in 0.1 steps (-1800,1800)
        # ctrl_byte always to 1
        # time_for_action to define speed in 0.1sec
        hex_data = struct.pack('<3h2B', yaw, roll, pitch,
                               ctrl_byte, time_for_action)

        pack_data = ['{:02X}'.format(i) for i in hex_data]
        cmd_data = ':'.join(pack_data)
        # print(cmd_data)
        cmd = self.assemble_can_msg(cmd_type='03', cmd_set='0E',
                                    cmd_id='00', data=cmd_data)

        self.send_cmd(cmd)
        return True    

    def setSpeedControl(self, yaw, roll, pitch, ctrl_byte=0x80):
        """
        
        Sets speed for each axis of the gimbal.

        Args:
            yaw (int): yaw speed in units of 0.1 deg/s
            roll (int): roll speed in units of 0.1 deg/s
            pitch (int): pitch speed in units of 0.1 deg/s
            ctrl_byte (hexadecimal, optional): _description_. Defaults to 0x80.

        Returns:
            _type_: _description_
        """
        
        if -3600 <= yaw <= 3600 and -3600 <= roll <= 3600 and -3600 <= pitch <= 3600:
        
            hex_data = struct.pack('<3hB', yaw, roll, pitch, ctrl_byte)
            pack_data = ['{:02X}'.format(struct.unpack('<1B', i)[
                0]) for i in hex_data]
            cmd_data = ':'.join(pack_data)

            cmd = self.assemble_can_msg(cmd_type='03', cmd_set='0E',
                                        cmd_id='01', data=cmd_data)
            # print('cmd---data {}'.format(cmd))
            self.send_cmd(cmd)
            
            return True
        else:
            return False

    def request_current_position(self):
        """
        Sends command to request the current position of the gimbal
        
        """
        
        hex_data = [0x01]
        pack_data = ['{:02X}'.format(i)
                     for i in hex_data]
        cmd_data = ':'.join(pack_data)
        cmd = self.assemble_can_msg(cmd_type='03', cmd_set='0E',
                                    cmd_id='02', data=cmd_data)
        self.send_cmd(cmd)

    def assemble_can_msg(self, cmd_type, cmd_set, cmd_id, data):
        """
        Builds a DJI message frame based on the command to be sent.

        Args:
            cmd_type (hex): see DJI R SDK Protocol and User Interface document for a description
            cmd_set (hex): see DJI R SDK Protocol and User Interface document for a description
            cmd_id (hex): see DJI R SDK Protocol and User Interface document for a description
            data (hex): see DJI R SDK Protocol and User Interface document for a description

        Returns:
            hex: the dji frame message 
        """
        
        if data == "":
            can_frame_data = "{prefix}" + \
                ":{cmd_set}:{cmd_id}".format(
                    cmd_set=cmd_set, cmd_id=cmd_id)
        else:
            can_frame_data = "{prefix}" + ":{cmd_set}:{cmd_id}:{data}".format(
                cmd_set=cmd_set, cmd_id=cmd_id, data=data)

        cmd_length = len(can_frame_data.split(":")) + 15

        seqnum = self.seq_num()
        # ic(seqnum)
        can_frame_header = "{header:02x}".format(
            header=self.header)  # SOF byte
        can_frame_header += ":" + \
            ("%04x" % (cmd_length))[2:4]  # 1st length byte
        can_frame_header += ":" + \
            ("%04x" % (cmd_length))[0:2]  # 2nd length byte
        can_frame_header += ":" + \
            "{cmd_type}".format(cmd_type=cmd_type)  # Command Type
        can_frame_header += ":" + "{enc:02x}".format(enc=self.enc)  # Encoding
        can_frame_header += ":" + \
            "{res1:02x}".format(res1=self.res1)  # Reserved 1
        can_frame_header += ":" + \
            "{res2:02x}".format(res2=self.res2)  # Reserved 2
        can_frame_header += ":" + \
            "{res3:02x}".format(res3=self.res3)  # Reserved 3
        can_frame_header += ":" + seqnum    # Sequence number
        can_frame_header += ":" + calc_crc16(can_frame_header)

        # hex_seq = [eval("0x" + hex_num) for hex_num in can_frame_header.split(":")]

        whole_can_frame = can_frame_data.format(prefix=can_frame_header)
        whole_can_frame += ":" + calc_crc32(whole_can_frame)
        whole_can_frame = whole_can_frame.upper()
        #
        # print("Header: ", can_frame_header)
        # print("Total: ", whole_can_frame)
        return whole_can_frame

    def send_cmd(self, cmd):
        """
        Wrapper to send a comand 

        Args:
            cmd (str): command fields separated by ':'
        """
        
        data = [int(i, 16) for i in cmd.split(":")]
        self.send_data(self.send_id, data)

    def send_data(self, can_id, data):
        """
        Sends a command through the can bus

        Args:
            can_id (hex): _description_
            data (list): list with the fields of the frame 
        """
        
        data_len = len(data)
        full_frame_num, left_len = divmod(data_len, self.MAX_CAN_FRAME_LEN)

        if left_len == 0:
            frame_num = full_frame_num
        else:
            frame_num = full_frame_num + 1

        data_offset = 0

        full_msg = []
        for i in range(full_frame_num):
            full_msg.append(can.Message(arbitration_id=can_id, dlc=8, data=data[data_offset:data_offset + self.MAX_CAN_FRAME_LEN], 
                                            is_extended_id=False, is_error_frame=False, is_remote_frame=False))
            data_offset += self.MAX_CAN_FRAME_LEN

        # If there is data left over, the last frame isn't 8byte long

        if left_len > 0:
            full_msg.append(can.Message(arbitration_id=can_id, dlc=left_len, data=data[data_offset:data_offset + left_len], 
                                            is_extended_id=False, is_error_frame=False, is_remote_frame=False))        
        
        for m in full_msg:
            try:
                self.actual_bus.send(m)
                print(f"Message sent on {self.actual_bus.channel_info}" + '\n')
            except can.CanError:
                print("Message NOT sent\n")
                return

    def receive(self, bus, stop_event):
        """
        Threading callback function. Defined when the Thread is created. This thread is like a 'listener' 
        for coming (received) can messages. Reads 1 entry of the rx bus buffer at a time.
        
        Args:
            bus (python can object): object pointing to the type of bus (i.e. PCAN)
            stop_event (boolean): flag to stop receiving messages
        """
        
        print("Start receiving messages")
        while not stop_event.is_set():
            rx_msg = bus.recv(1)
            if rx_msg is not None:
                #print(f"rx: {rx_msg}")
                self.cntBytes = self.cntBytes + 1
                self.can_callback(rx_msg)
                #print(' CNT: ', self.cntBytes)
                
        print("Stopped receiving messages")

    def on_press(self, key):
        """Keboard handling. This function is called when the user press a button. Its an early implementation of the GUI to request
        for specific actions on the gimbal. REPLACED BY WEBAPP 

        Args:
            key (char): the pressed key
        """
        '''
        if hasattr(key, 'char'):
            print('Pressed: {}'.format(key.char))
        else:
            print('special key pressed: {0}'.format(key))

        '''

    def on_release(self, key):
        """Keboard handling. This function is called when the user releases a button. Its an early implementation of the GUI to request
        for specific actions on the gimbal. REPLACED BY WEB APP

        Provides gimbal control through keyboard
       
        Args:
            key (char): the released key

        Returns:
            boolean: If 'False' the keyboard thread is stopped
        """

        if self.keyboard_set_flag:
            self.keyboard_buff.append(key.char)

        if hasattr(key, 'char'):
            #print('Released: {}'.format(key.char))

            if key.char == 'r':
                print('REQUEST GIMBAL POSITION')
                self.request_current_position()

            elif key.char == 's':
                print('SETTING GIMBAL POSITION...')
                self.keyboard_set_flag = True

            elif key.char == 'q':
                self.keyboard_set_flag = False
                
                # Delete the 'q' from the buffer (last item)
                self.keyboard_buff.pop()

                lop = ''
                lop_v = []

                for x in self.keyboard_buff:
                    if x == ',':
                        lop_v.append(int(lop))
                        lop = ''
                    else:
                        lop = lop + x

                if lop != '':
                    lop_v.append(int(lop))
                    lop = ''

                print('ENTERED: ', lop_v)
                yaw = lop_v[0]
                roll = lop_v[1]
                pitch = lop_v[2]
                
                self.setPosControl(yaw, roll, pitch, time_for_action=0x1A)

                print('GIMBAL POSITION SET')

                # Flush the keyboard buffer
                self.keyboard_buff = []

            elif key == keyboard.Key.esc:
                self.MAIN_LOOP_STOP = False

                # Returning False Stops the listener
                return False
    
    def start_thread_gimbal(self, bitrate=1000000):
        """
        Starts the thread for 'listening' the incoming data from pcan

        Args:
            bitrate (int, optional): Bitrate used for pcan device. Defaults to 1000000.
        """
        
        bus = can.interface.Bus(interface="pcan", channel="PCAN_USBBUS1", bitrate=bitrate)
        self.actual_bus = bus

        self.event_stop_thread_gimbal = threading.Event()                              
        t_receive = threading.Thread(target=self.receive, args=(self.actual_bus,self.event_stop_thread_gimbal))
        t_receive.start()

    def stop_thread_gimbal(self):
        """
        Stops the gimbal thread

        """
        
        self.event_stop_thread_gimbal.set()        
            
class GpsSignaling(object):
    def __init__(self, DBG_LVL_1=False, DBG_LVL_2=False, DBG_LVL_0=False):
        # Initializations
        # Dummy initialization
        self.SBF_frame_buffer = []
        self.NMEA_buffer = []
        self.stream_info = []

        self.DBG_LVL_1 = DBG_LVL_1
        self.DBG_LVL_2 = DBG_LVL_2
        self.DBG_LVL_0 = DBG_LVL_0

        # Expected SBF sentences to be requested. Add or remove according to planned
        # SBF sentences to be requested.
        self.register_sbf_sentences_by_id = [4006, 5938] # PVTCart, AttEul
        self.n_sbf_sentences = len(self.register_sbf_sentences_by_id)
        
    def socket_connect(self, HOST="192.168.3.1", PORT=28784, time='sec1', ip_port_number='IP11'):
        """
        Creates a socket to connect to the command-line terminal provided by Septentrio receiver. 
        Sends the first command (in Septentrio-defined 'language') to set-up a regular retrieve of gps info

        Args:
            HOST (str, optional): IP address where the server is allocated. Defaults to "192.168.3.1".
            PORT (int, optional): PORT number of the application. Defaults to 28784.
            time (str, optional): How regular get updates of the gps data. Defaults to 'sec1'.
            ip_port_number (str, optional): the number of the IP terminal emulator port. 
        """
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket = s
        
        self.socket.connect((HOST, PORT))
     
    def socket_receive(self, stop_event):
        """
        Callback function to be called when incoming gps data

        Args:
            stop_event (threading): the threading event that stops the TCP/IP com
        """

        while not stop_event.is_set():
            data = self.socket.recv(64)
            self.process_gps_nmea_data(data)
            
    def serial_connect(self, serial_port=None):
        """
        Open a serial connection. The Septentrio mosaic-go provides 2 virtual serial ports.
        
        In Windows the name of the virtual serial ports are typically: 
        -COM15 (Virtual serial port 1)
        -COM14 (Virtual serial port 2)

        In Linux the name of the virtual serial ports (controlled by the standard Linux CDC-ACM driver) are:
        -/dev/ttyACM0 (Virtual serial port 1)
        -/dev/ttyACM1 (Virtual serial port 2)

        For the virtual serial ports the interface name in Septentrio receiver is 'USB' as they
        communication is made through the USB connection with the host computer. 
        
        Additionally there is an actual serial port in the mosaic-go device. Under Linux,
        the name of this port is '/dev/serial0' (or '/dev/serial0') which is the symbolic link
        to either 'dev/ttyS#' or '/dev/ttyAMA#'.
        
        Args:
            serial_port (str, optional): serial port or virtual serial port name. 
        """
        
        # Look for the first Virtual Com in Septentrio receiver. It is assumed that it is available, 
        # meaning that it has been closed by user if was used before.        
        for (this_port, desc, _) in sorted(comports()):
            # Linux CDC-ACM driver
            if 'Septentrio USB Device - CDC Abstract Control Model (ACM)' in desc:
                    self.serial_port = '/dev/ttyACM0'
                    self.interface_number = 1
            # Windows driver
            elif 'Septentrio Virtual USB COM Port 1' in desc:
                    self.serial_port = this_port
                    self.interface_number = 1
        
        serial_instance = None
        while serial_instance is None:
            try:
                serial_instance = serial.serial_for_url(self.serial_port,
                                                        9600,
                                                        parity='N',
                                                        rtscts=False,
                                                        xonxoff=False,
                                                        do_not_open=True)

                serial_instance.timeout = 5
                            
                serial_instance.exclusive = True
                serial_instance.open()
                                
            except serial.SerialException as e:
                sys.stderr.write('could not open port {!r}: {}\n'.format(self.serial_port, e))

            else:
                break
        
        if self.DBG_LVL_0:
            print('CONNECTED TO VIRTUAL SERIAL PORT IN SEPTENTRIO\r\n')
        
        self.serial_instance = serial_instance
        time.sleep(0.1)

    def process_gps_nmea_data(self, data):
        """
        Process the received data of the gps coming from the virtual serial port.
        
        The labels of the items of the returned dictionary are the following ones for the GGA sentence:
        
        'Timestamp', 'Latitude', 'Longitude', 'Latitude Direction', 'Longitude'
        'Longitude Direction', 'GPS Quality Indicator', 'Number of Satellites in use'
        'Horizontal Dilution of Precision', 'Antenna Alt above sea level (mean)'
        'Units of altitude (meters)', 'Geoidal Separation'
        'Units of Geoidal Separation (meters)', 'Age of Differential GPS Data (secs)'
        'Differential Reference Station ID'
        

        Args:
            data (str): line of read data. We assume that the format followed by the data retrieved (the string) is the NMEA.
        """
        
        try:
            if self.DBG_LVL_0:
                print('\nNMEA PARSING')
            
            nmeaobj = pynmea2.parse(data.decode())
            extracted_data = ['%s: %s' % (nmeaobj.fields[i][0], nmeaobj.data[i]) for i in range(len(nmeaobj.fields))]
            gps_data = {}
            for item in extracted_data:
                tmp = item.split(': ')
                gps_data[tmp[0]] = tmp[1]
            
            # GGA type of NMEA sentence
            if 'Antenna Alt above sea level (mean)' in gps_data:
                if int(gps_data['Latitude'][0]) != 0:
                    gps_data['Latitude'] = float(gps_data['Latitude'][0:2]) + float(gps_data['Latitude'][2:])/60
                else:
                    gps_data['Latitude'] = float(gps_data['Latitude'][0:3]) + float(gps_data['Latitude'][3:])/60
                
                if int(gps_data['Longitude'][0]) != 0:
                    gps_data['Longitude'] = float(gps_data['Longitude'][0:2]) + float(gps_data['Longitude'][2:])/60
                else:
                    gps_data['Longitude'] = float(gps_data['Longitude'][0:3]) + float(gps_data['Longitude'][3:])/60
                
                gps_data['Antenna Alt above sea level (mean)'] = float(gps_data['Antenna Alt above sea level (mean)'])
                gps_data['Timestamp'] = float(gps_data['Timestamp'])
                
                '''
                # Save the UNIX timestamp. As the timestamp provides hour/min/sec only, add the date
                today_date = datetime.date.today()
                today_date = [int(i) for i in today_date.strftime("%Y-%m-%d").split('-')]                

                complete_date = datetime.datetime(year=today_date[0], 
                                                month=today_date[1], 
                                                day=today_date[2], 
                                                hour=int(gps_data['Timestamp'][0:2]), 
                                                minute=int(gps_data['Timestamp'][2:4]), 
                                                second=int(gps_data['Timestamp'][4:6]))

                gps_data['Timestamp'] = time.mktime(complete_date.timetuple())
                
                '''
            
            # HDT NMEA sentence
            if 'Heading' in gps_data:
                if gps_data['Heading'] == '':
                    gps_data['Heading'] = -2000
                else:
                    gps_data['Heading'] = float(gps_data['Heading'])
                
                # No need to restrict heading to [-pi, pi] since it will be done 
                # inside 'ground_gimbal_follows_drone' function 
                #if gps_data['Heading'] > 180:
                #    gps_data['Heading'] = gps_data['Heading'] - 360
                
                # Make the timestamp the same format as the GGA sentence
                for stream in self.stream_info:
                    if stream['msg_type'] == 'NMEA':
                        # Need to update faster
                        if 'msec' in stream['interval']:
                            1
                        #elif 'sec' in stream['interval']:                            
                        else:
                            gps_data['Timestamp'] = ''
                            for i in datetime.datetime.utcnow().timetuple()[3:6]:
                                tmp = str(i)
                                if len(tmp) == 1:
                                    tmp = '0' + tmp
                                gps_data['Timestamp'] = gps_data['Timestamp'] + tmp
                            gps_data['Timestamp'] = float(int(gps_data['Timestamp']))
            
            if self.DBG_LVL_2 or len(self.NMEA_buffer):
                if self.DBG_LVL_0:
                    print('\nSAVES NMEA DATA INTO BUFFER')    
                self.NMEA_buffer.append(gps_data)  
             
        except Exception as e:
            # Do not save any other comand line
            if self.DBG_LVL_1:
                print('\nEXCEPTION PROCESSING NMEA')
            if self.DBG_LVL_0:
                print('\nThis is the exception: ', e) 

    def process_pvtcart_sbf_data(self, raw_data):
        """
        Process the PVTCart data type
        
        Args:
            raw_data (bytes): received raw data
        """
        
        format_before_padd = '<1c3H1I1H2B3d5f1d1f4B2H1I2B4H1B' 
        format_after_padd = format_before_padd + str(sys.getsizeof(raw_data)-struct.calcsize(format_before_padd)) + 'B'
        #print('\nFormat: ', format_after_padd, ' Size of format: ', struct.calcsize(format_after_padd))
        
        TOW = struct.unpack('<1I', raw_data[7:11])[0]
        WNc = struct.unpack('<1H', raw_data[11:13])[0]        
        MODE =  struct.unpack('<1B', raw_data[13:14])[0]
        ERR =  struct.unpack('<1B', raw_data[14:15])[0]
        X =  struct.unpack('<1d', raw_data[15:23])[0]
        Y =  struct.unpack('<1d', raw_data[23:31])[0]
        Z = struct.unpack('<1d', raw_data[31:39])[0]
        Undulation =  struct.unpack('<1f', raw_data[39:43])[0]
        Vx =  struct.unpack('<1f', raw_data[43:47])[0]
        Vy = struct.unpack('<1f', raw_data[47:51])[0]
        Vz =  struct.unpack('<1f', raw_data[51:55])[0]
        COG =  struct.unpack('<1f', raw_data[55:59])[0]
        RxClkBias = struct.unpack('<1d', raw_data[59:67])[0]
        RxClkDrift =  struct.unpack('<1f', raw_data[67:71])[0]
        TimeSystem = struct.unpack('<1B', raw_data[71:72])[0]
        Datum =  struct.unpack('<1B', raw_data[72:73])[0]
        NrSV = struct.unpack('<1B', raw_data[73:74])[0]
        WACorrInfo =  struct.unpack('<1B', raw_data[74:75])[0]
        ReferenceID =  struct.unpack('<1H', raw_data[75:77])[0]
        MeanCorrAge = struct.unpack('<1H', raw_data[77:79])[0]
        SignalInfo =  struct.unpack('<1I', raw_data[79:83])[0] 
        AlertFlag = struct.unpack('<1B', raw_data[83:84])[0]
        NrBases =  struct.unpack('<1B', raw_data[84:85])[0]
        PPPInfo =  struct.unpack('<1H', raw_data[85:87])[0]
        Latency =  struct.unpack('<1H', raw_data[87:89])[0]        
        HAccuracy =  struct.unpack('<1H', raw_data[89:91])[0]         
        VAccuracy =  struct.unpack('<1H', raw_data[91:93])[0]  
        
        
        pvt_msg_format = {'TOW': TOW, 'WNc': WNc, 'MODE': MODE, 'ERR': ERR, 'X': X, 'Y': Y, 'Z': Z,
                          'Undulation': Undulation, 'Vx': Vx, 'Vy': Vy, 'Vz': Vz, 'COG': COG,
                          'RxClkBias': RxClkBias, 'RxClkDrift': RxClkDrift, 'TimeSystem': TimeSystem, 'Datum': Datum,
                          'NrSV': NrSV, 'WACorrInfo': WACorrInfo, 'ReferenceID': ReferenceID, 'MeanCorrAge': MeanCorrAge,
                          'SignalInfo': SignalInfo, 'AlertFlag': AlertFlag, 'NrBases': NrBases, 'PPPInfo': PPPInfo,
                          'Latency': Latency, 'HAccuracy': HAccuracy, 'VAccuracy': VAccuracy}        
        
        pvt_data_we_care = {'TOW': TOW, 'WNc': WNc, 'MODE': MODE, 'ERR': ERR, 
                            'X': X, 'Y': Y, 'Z': Z, 'Datum': Datum}

        self.SBF_frame_buffer.append(pvt_data_we_care)
    
    def process_atteuler_sbf_data(self, raw_data):
        """
        Parse the AttEuler SBF sentence.

        Args:
            raw_data (bytes): received raw data
            synch_w_pvt (boolean): this flag tells if the PVTCart and AttEuler are requested
                                   at the same time, so that they can be merged in the same
                                   database or array entry.
        """
        TOW = struct.unpack('<1I', raw_data[7:11])[0]
        WNc = struct.unpack('<1H', raw_data[11:13])[0]        
        NrSV = struct.unpack('<1B', raw_data[13:14])[0]
        ERR =  struct.unpack('<1B', raw_data[14:15])[0]
        MODE =  struct.unpack('<1H', raw_data[15:17])[0]
        Heading =  struct.unpack('<1f', raw_data[19:23])[0]
        Pitch =  struct.unpack('<1f', raw_data[23:27])[0]
        Roll = struct.unpack('<1f', raw_data[27:31])[0]
        PitchDot =  struct.unpack('<1f', raw_data[31:35])[0]
        RollDot =  struct.unpack('<1f', raw_data[35:39])[0]
        HeadingDot = struct.unpack('<1f', raw_data[39:43])[0]
        
        
        atteul_msg_format = {'TOW': TOW, 'WNc': WNc, 'NrSV': NrSV, 'ERR': ERR, 'MODE': MODE, 
                             'Heading': Heading, 'Pitch': Pitch, 'Roll': Roll, 
                             'PitchDot': PitchDot, 'RollDot': RollDot, 'HeadingDot': HeadingDot}        
        
        atteul_msg_useful = {'TOW': TOW, 'WNc': WNc,'ERR': ERR, 'MODE': MODE, 
                             'Heading': Heading, 'Pitch': Pitch, 'Roll': Roll}
        
        self.SBF_frame_buffer.append(atteul_msg_useful)
    
    def parse_septentrio_msg(self, rx_msg):
        """
        Parse the received message and process it depending if it is a SBF or NMEA message
        
        Args:
            rx_msg (bytes or str): received message

        Raises:
            Exception: _description_
        """                
        try:
            if self.DBG_LVL_1:
                print('\nPARSING RX DATA')
            if self.DBG_LVL_0:                
                print('\nRX DATA: ', rx_msg.decode('utf-8', 'ignore'))
            
            # The SBF output follows the $ sync1 byte, with a second sync byte that is the symbol @ or in utf-8 the decimal 64
            # Bytes indexing  works as follows:
            # One integer gives a decimal
            # A slice (i.e. 0:1) gives a bytes object ---> rx_msg[0] != rx_msg[0:1]
            if rx_msg[0] == 64:                
                if self.DBG_LVL_0:
                    print('\nDETECTS SBF')
                    
                # Header detection
                #SYNC = struct.unpack('<1c', rx_msg[0:1]) 
                CRC = struct.unpack('<1H', rx_msg[1:3])                
                ID_SBF_msg = struct.unpack('<1H', rx_msg[3:5])
                LEN_SBF_msg = struct.unpack('<1H', rx_msg[5:7])

                # According to the manual, the LEN should always be a multiple of 4, otherwise 
                # there is an error
                if np.mod(int(LEN_SBF_msg[0]),4) != 0 :
                    if self.DBG_LVL_1:
                        print('\nDiscarded frame as LEN_SBF_msg is not multiple of 4, LEN_SBF_msg: ', LEN_SBF_msg[0])
                    return
                
                '''
                # CRC checker
                crc16_checker = Calculator(Crc16.CCITT)
                idx_bytes_crc_to_read = 7+int(LEN_SBF_msg[0])-8
                crc_data = rx_msg[7:idx_bytes_crc_to_read]
                print(type(crc_data))
                crc16 = crc16_checker.checksum(crc_data)
                print(rx_msg[1:3], type(crc16))
                if CRC[0] != crc16:
                    if self.DBG_LVL_1:
                        print('\nDiscarded frame cause it did not pass the CRC check')
                    return
                '''
                
                # PVTCart SBF sentence identified by ID 4006
                if ID_SBF_msg[0] & 8191 == 4006: # np.sum([np.power(2,i) for i in range(13)]) # --->  bits 0-12 contain the ID                    
                    self.process_pvtcart_sbf_data(rx_msg)
                
                # PosCovCartesian SBF sentence identified by ID 5905
                if ID_SBF_msg[0] & 8191 == 5905: # np.sum([np.power(2,i) for i in range(13)]) # --->  bits 0-12 contain the ID
                    print('\nReceived PosCovCartesian SBF sentence')
                
                if ID_SBF_msg[0] & 8191 == 5907: # np.sum([np.power(2,i) for i in range(13)]) # --->  bits 0-12 contain the ID
                    print('\nReceived VelCovCartesian SBF sentence')
                
                if ID_SBF_msg[0] & 8191 == 4043: # np.sum([np.power(2,i) for i in range(13)]) # --->  bits 0-12 contain the ID
                    print('\nReceived BaseVectorCart SBF sentence')
                
                if ID_SBF_msg[0] & 8191 == 5942: # np.sum([np.power(2,i) for i in range(13)]) # --->  bits 0-12 contain the ID
                    print('\nReceived AuxAntPositions SBF sentence')
                
                if ID_SBF_msg[0] & 8191 == 5938: # np.sum([np.power(2,i) for i in range(13)]) # --->  bits 0-12 contain the ID
                    #print('\nReceived AttEuler SBF sentence')
                    self.process_atteuler_sbf_data(rx_msg)
                
                if ID_SBF_msg[0] & 8191 == 5939: # np.sum([np.power(2,i) for i in range(13)]) # --->  bits 0-12 contain the ID
                    print('\nReceived AttCovEuler SBF sentence')
                               
                if ID_SBF_msg[0] & 8191 == 5943: # np.sum([np.power(2,i) for i in range(13)]) # --->  bits 0-12 contain the ID
                    print('\nReceived EndOfAtt SBF sentence')

                # Sort SBF buffer entries by time (this is double checking, as they are expected to arrive in time order)
                self.SBF_frame_buffer.sort(key=lambda k : k['TOW'])

                # Merge buffer entries corresponding to the same TOW
                #self.util_merge_buffer_entries_by_timetag(type_msg='SBF')

            # NMEA Output starts with the letter G, that in utf-8 is the decimal 71
            elif rx_msg[0] == 71:
                if self.DBG_LVL_0:
                    print('\nDETECTS NMEA')
                self.process_gps_nmea_data(rx_msg[:-1])
                #self.util_merge_buffer_entries_by_timetag(type_msg='NMEA')
                
        except Exception as e:
            if self.DBG_LVL_1:
                print('\nEXCEPTION IN parse_septentrio_msg')
            if self.DBG_LVL_0:
                print('\nThis is the exception: ', e, )
                logging.exception("\nError occurred: ")
    
    def util_merge_buffer_entries_by_timetag(self, type_msg='SBF'):
        """
        Utility function to merge buffer entries that have the same timetag.

        Args:
            type_msg (str, optional): _description_. Defaults to 'SBF'.
        """

        if type_msg == 'SBF':
            tmp_buff = []
            for key, value in groupby(self.SBF_frame_buffer[-2*self.n_sbf_sentences:], key = itemgetter('TOW')):
                tmp_buff.append({'TOW': key})
                for dict_i in value:
                    for key_dict_i, value_dict_i in dict_i.items():
                        if key_dict_i == 'ERR':
                            if 'Heading' in dict_i:
                                tmp_buff[-1]['ERR_ATTEUL'] = value_dict_i
                            elif 'X' in dict_i:
                                tmp_buff[-1]['ERR_PVT'] = value_dict_i
                        elif key_dict_i == 'MODE':
                            if 'Heading' in dict_i:
                                tmp_buff[-1]['MODE_ATTEUL'] = value_dict_i
                            elif 'X' in dict_i:
                                tmp_buff[-1]['MODE_PVT'] = value_dict_i
                        else:
                            tmp_buff[-1][key_dict_i] = value_dict_i
                    
            self.SBF_frame_buffer[-2*self.n_sbf_sentences:] = tmp_buff    

        # NMEA doesn't send GGA and HDT at the same time. They are tipycally spaced by a second.
        # So we consider to groupy by a time bin of 1 second
        elif type_msg == 'NMEA':
            self.NMEA_buffer[-2*2:].sort(key=lambda k : k['Timestamp'])
            
            # Group the buffer entries by timestamps close in time by a max of 'time_bin -1' seconds
            groups = []
            time_bin = 2
            
            if len(self.NMEA_buffer) >= 4 :
                start_time = datetime.datetime.strptime(str(int(self.NMEA_buffer[-2*2]['Timestamp'])), '%H%M%S')
            else:
                start_time = datetime.datetime.strptime(str(int(self.NMEA_buffer[-len(self.NMEA_buffer)]['Timestamp'])), '%H%M%S')
            
            for list_i in self.NMEA_buffer[-2*2:]:
                t_c = datetime.datetime.strptime(str(int(list_i['Timestamp'])), '%H%M%S')
                groups.append(int((t_c - start_time).total_seconds() // time_bin) + 1)
            print(groups)
            tmp_buf = []
            for i in np.unique(groups):
                tmp_buf.append({})
                for cnt, dict_i in enumerate(self.NMEA_buffer[-2*2:]):
                    if groups[cnt] == i:
                        for key, value in dict_i.items():
                            tmp_buf[-1][key] = value

            self.NMEA_buffer[-2*2:] = tmp_buf       
        
    def serial_receive(self, serial_instance_actual, stop_event):
        """
        The callback function invoked by the serial thread.

        Args:
            serial_instance_actual (Serial): serial connection.
            stop_event (threading): stop event for stop reading the serial com port.
        """
        
        while not stop_event.is_set():
            # This is if only NMEA messages are received
            #rx_msg = serial_instance_actual.readline()
            
            # This looks for the start of a sentence in either NMEA or SBF messages
            rx_msg = serial_instance_actual.read_until(expected='$'.encode('utf-8'))
            if len(rx_msg) > 0:
                self.parse_septentrio_msg(rx_msg)
    
    def start_thread_gps(self, interface='USB'):
        """
        Starts the serial read thread.
        
        """
        
        self.event_stop_thread_gps = threading.Event()
        
        if interface == 'USB' or interface == 'COM':
            t_receive = threading.Thread(target=self.serial_receive, args=(self.serial_instance, self.event_stop_thread_gps))
            
        elif interface == 'IP':
            t_receive = threading.Thread(target=self.socket_receive, args=(self.event_stop_thread_gps))

        t_receive.start()
        time.sleep(0.5)
        
    def stop_thread_gps(self, interface='USB'):
        """
        Stops the serial read thread.
        
        """
        
        self.event_stop_thread_gps.set()
        time.sleep(0.1)
        
        if interface =='USB' or interface == 'COM':
            self.serial_instance.close()
            
        elif interface =='IP':
            self.socket.close()
        
    def sendCommandGps(self, cmd, interface='USB'):
        """
        Send a command to the Septentrio gps, following their command format.

        Args:
            cmd (_type_): _description_
        """        
        
        cmd_eof = cmd + '\n'
        
        if interface =='USB':
            self.serial_instance.write(cmd_eof.encode('utf-8'))
        elif interface == 'IP':
            self.socket.sendall(cmd_eof.encode('utf-8'))
            
        time.sleep(0.5)
            
    def start_gps_data_retrieval(self, stream_number=1, interface='USB', interval='sec1', msg_type='NMEA', 
                                 nmea_type='+GGA+HDT', sbf_type='+PVTCartesian+AttEuler'):
        """
        Wrapper to sendCommandGps for a specific command to send.

        Args:
            stream_number(int, optional): stream number. Defaults to 1.
            interface (str, optional): Interface: can be 'USB#', 'COM#' or 'IP#'. Defaults to 'USB1'. 
            interval (str, optional): can be any of: 'msec10', 'msec20', 'msec40', 'msec50', 'msec100', 'msec200', 'msec500',
                                                     'sec1', 'sec2', 'sec5', 'sec10', 'sec15', 'sec30', 'sec60', 
                                                     'min2', 'min5', 'min10', 'min15', 'min30', 'min60'
        """
        
        if interface == 'USB' or interface == 'COM':
            if msg_type == 'SBF':
                cmd1 = 'setDataInOut, ' + interface + str(self.interface_number) + ',, ' + '+SBF'
                cmd2 = 'setSBFOutput, Stream ' + str(stream_number) + ', ' + interface + str(self.interface_number) + ', ' +  sbf_type + ', ' + interval
            elif msg_type == 'NMEA':
                cmd1 = 'setDataInOut, ' + interface + str(self.interface_number) + ',, ' + '+NMEA'
                cmd2 = 'sno, Stream ' + str(stream_number) + ', ' + interface + str(self.interface_number) + ', ' + nmea_type + ', ' + interval
        
        self.stream_info.append({'interface': interface, 'stream_number': stream_number, 'interval': interval, 'msg_type': msg_type})
        
        self.sendCommandGps(cmd1)
        self.sendCommandGps(cmd2)
        
        if self.DBG_LVL_1:
            print('\n'+ cmd1)
            print('\n'+ cmd2)
     
    def stop_gps_data_retrieval(self, stream_number=1, interface='USB', msg_type='+NMEA+SBF'):   
        """
        Stop the streaming of data using septentrio commands. 
        
        DEVELOPER NOTE: it seems that if the stream is not stopped by the time the serial connection is closed, then when the
        user opens a new serial connection, Septentrio will start sending all the SBF or NMEA messages that were produced
        between the last time the serial connection was closed and the time it is opened again.

        Args:
            stream_number (int, optional): _description_. Defaults to 1.
            interface (str, optional): _description_. Defaults to 'USB'.
            msg_type (str, optional): _description_. Defaults to 'NMEA'.
        """
        
        if interface == 'USB' or interface == 'COM':
            if msg_type == 'SBF':
                cmd1 = 'setSBFOutput, Stream ' + str(stream_number) + ', ' + interface + str(self.interface_number) + ', none '
                cmd2 = 'sdio, ' + interface + str(self.interface_number) + ',, -SBF'
                
                self.sendCommandGps(cmd1)
                self.sendCommandGps(cmd2)
            elif msg_type == 'NMEA':
                cmd1 = 'sno, Stream ' + str(stream_number) + ', ' + interface + str(self.interface_number) + ', none ' 
                cmd2 = 'sdio, ' + interface + str(self.interface_number) + ',, -NMEA'

                self.sendCommandGps(cmd1)
                self.sendCommandGps(cmd2)
            elif msg_type == '+NMEA+SBF' or msg_type == '+SBF+NMEA':
                cmd1 = 'setSBFOutput, Stream ' + str(stream_number) + ', ' + interface + str(self.interface_number) + ', none '
                cmd2 = 'sdio, ' + interface + str(self.interface_number) + ',, -SBF'
                cmd3 = 'sno, Stream ' + str(stream_number) + ', ' + interface + str(self.interface_number) + ', none ' 
                cmd4 = 'sdio, ' + interface + str(self.interface_number) + ',, -NMEA'

                self.sendCommandGps(cmd1)
                self.sendCommandGps(cmd2)       
                self.sendCommandGps(cmd3)
                self.sendCommandGps(cmd4)
           
class myAnritsuSpectrumAnalyzer(object):
    def __init__(self, is_debug=True, is_config=True):
        self.model = 'MS2760A'
        self.is_debug = is_debug # Print debug messages
        self.is_config = is_config # True if you want to configure the Spectrum Analyzer
        self.XML_file = {'Timestamp': 0, 'Data': [], 'NSamp': []}
        
    def spectrum_analyzer_connect(self, HOST='127.0.0.1', PORT=9001):
        """
        Create a socket and connect to the spectrum analyzer

        Args:
            HOST (str, optional): IP address. Defaults to '127.0.0.1'.
            PORT (int, optional): TCP/IP port. Defaults to 9001.
        """
                
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.anritsu_con_socket = s
        self.anritsu_con_socket.connect((HOST, PORT))
        
    def retrieve_max_pow(self, method=2):
        """
        Obtain the maximum power and its correspondent frequency

        Args:
            method (int, optional): for developer. It is indisctintive for user. Defaults to 2.

        Raises:
            Exception: _description_

        Returns:
            dictionary: magnitude of power, units of magnitude, frequency, units of frequency
        """

        # Read the ID of the Spectrum Analyzer.
        if self.is_debug:
            self.anritsu_con_socket.send(b"*IDN?\n")
            self.anritsu_con_socket.settimeout(20)
            rsp = self.anritsu_con_socket.recv(1024)
            self.model = rsp.decode()

        # Configure the Spectrum Analyzer
        if self.is_config:
            self.anritsu_con_socket.send(b"SENS:FREQ:START 59.95 GHz\n")
            self.anritsu_con_socket.send(b"SENS:FREQ:STOP 60.05 GHz\n")
            self.anritsu_con_socket.send(b"BAND:RES 200 KHz\n")
            self.anritsu_con_socket.send(b":DISPLAY:POINTCOUNT 101\n")
            self.anritsu_con_socket.send(b":CALCulate:MARKer1:STATe 1\n")

        # Find the maximum power
        # 1. Pause the measurement collection
        self.anritsu_con_socket.send(b"INIT:CONT OFF\n")
        if method == 1:
            # 2.1 Place Marker 1 at maximum peak
            self.anritsu_con_socket.send(b":CALCulate:MARKer1:MAXimum\n")

            # 2.2 Find the frequency in Hz
            self.anritsu_con_socket.send(b":CALCulate:MARKer1:X?\n")
            freq = self.anritsu_con_socket.recv(1024)

            # 2.3 Find the maximum power in dBm
            self.anritsu_con_socket.send(b":CALCulate:MARKer1:Y?\n")
            pwr = self.anritsu_con_socket.recv(1024)
        elif method == 2:
            # 3.1 Find the maximum peak
            self.anritsu_con_socket.send(b":CALCulate:PEAK:COUNt 1\n")

            # 3.2 Read the frequency and power
            self.anritsu_con_socket.send(b":FETCh:PEAK?\n")
            rsp = self.anritsu_con_socket.recv(4096)
            freq, pwr = rsp.decode().split(',')
        else:
            raise Exception("Error: Method not supported.")
        # 4. Resume the measurement collection
        self.anritsu_con_socket.send(b"INIT:CONT ON\n")

        #print(f"Max power {float(pwr):.2f} dBm at {float(freq)*1e-9:.3f} GHz")
        
        return {'MAG': float(pwr), 'MAG_UNITS': 'dBm', 'FREQ': float(freq), 'FREQ_UNITS': 'Hz'}

    def parse_xml_file(self, filename):
        """
        Wrapper for function 'iterate_xml_file'. This function is the one the user needs to use.
        
        Args:
            filename (string): absolute path
        """
        
        with open(filename, 'r') as fd:
            doc = xmltodict.parse(fd.read(), process_namespaces=True)
            self.iterate_xml_file(doc)
    
    def iterate_xml_file(self, iterable):
        """
        Extracts timestamp, sample number and sample value of the Anritsu MS276XA Spectrum Analyzer, from
        the .rsm file generated by the device. This file is similar in structure to a XML file.

        Args:
            iterable (_type_): _description_
        """
        if isinstance(iterable, dict):
            for key, value in iterable.items():
                if key == 'TimeStamp':
                    if value['@year']:
                            meas_date = datetime.datetime(year=int(value['@year']), 
                                                month=int(value['@month']),
                                                day=int(value['@day']),
                                                hour=int(value['@hour']),
                                                minute=int(value['@minute']),
                                                second=int(value['@second']))
                            self.XML_file['Timestamp'] = datetime.datetime.timestamp(meas_date)
                if not (isinstance(value, dict) or isinstance(value, list)):
                    # We know when the key '@id' is an integer then we are in a data point
                    if key == '@id':
                        try:
                            tmp = int(value)
                            if iterable['@value'] != 'nan':
                                self.XML_file['NSamp'].append(int(value))
                                self.XML_file['Data'].append(float(iterable['@value']))
                        except:
                            1
                else:
                    self.iterate_xml_file(value)

        elif isinstance(iterable, list):
            for i in iterable:
                self.iterate_xml_file(i)

    def spectrum_analyzer_close(self):
        """
        Wrapper to close the spectrum analyzer socket
        
        """
        
        self.anritsu_con_socket.close()

class HelperA2GMeasurements(object):
    def __init__(self, ID, SERVER_ADDRESS, DBG_LVL_0=False, DBG_LVL_1=False, IsGimbal=False, IsGPS=False, IsSignalGenerator=False, F0=None, L0=None):
        """        
        GROUND station is the server and AIR station is the client.

        Args:
            ID (_type_): _description_
            SERVER_ADDRESS (str): the IP address of the server (the ground station)
            DBG_LVL_0 (bool): provides DEBUG support at the lowest level (i.e printing incoming messages)
            DBG_LVL_1 (bool): provides DEBUG support at the medium level (i.e printing exceptions)
            IsGimbal (bool): An RS2 Gimbal is going to be connected.
            IsGPS (bool): A Septentrio GPS is going to be connected.
        """
        
        self.ID = ID
        self.SERVER_ADDRESS = SERVER_ADDRESS  
        self.SOCKET_BUFFER = []
        self.DBG_LVL_0 = DBG_LVL_0
        self.DBG_LVL_1 = DBG_LVL_1
        self.IsGimbal = IsGimbal
        self.IsGPS = IsGPS
        self.IsSignalGenerator = IsSignalGenerator
        
        if IsGimbal:
            self.myGimbal = GimbalRS2()
            self.myGimbal.start_thread_gimbal()
            print('\nGimbal RS2 thread opened')
            time.sleep(0.5)
        if IsGPS:
            self.mySeptentrioGPS = GpsSignaling(DBG_LVL_2=True)
            self.mySeptentrioGPS.serial_connect()
            self.mySeptentrioGPS.serial_instance.reset_input_buffer()
            self.mySeptentrioGPS.start_gps_data_retrieval(stream_number=1,  msg_type='SBF', interval='sec1', sbf_type='+PVTCartesian+AttEuler')
            #self.mySeptentrioGPS.start_gps_data_retrieval(msg_type='NMEA', nmea_type='GGA', interval='sec1')
            self.mySeptentrioGPS.start_thread_gps()
            print('\nSeptentrio GPS thread opened')
            time.sleep(0.5)
        if IsSignalGenerator:
            rm = pyvisa.ResourceManager()
            inst = rm.open_resource('GPIB0::19::INSTR')
            self.inst = inst
            self.inst.write('F0 ' + str(F0) + ' GH\n')
            self.inst.write('L0 ' + str(L0)+ ' DM\n')
            time.sleep(0.5)
        
    def ground_gimbal_follows_drone(self, heading=None, lat_ground=None, lon_ground=None, height_ground=None, 
                                    lat_drone=None, lon_drone=None, height_drone=None, 
                                    coord_type='latlon'):
        """
        Ground gimbal points to the drone. The front part of the RS2 Gimbal should be pointing to the North. (or equivalently, the touchscreen
        should be pointing to the south).
        
        The user must input either the 3 ground coordinates or the 3 drone coordinates, but both of them can't be None. 
        Moreover, the user must input exactly the 3 coordinates, otherwise the computation won't work.

        Finds the yaw and pitch angles to be set at the GROUND gimbal so it points towards the DRONE station.

        Args:
            lat_gimbal (float): Latitude of GROUND station. In DDMMS format: i.e: 62.471541 N
            lon_gimbal (float): Longitude of GROUND station. In DDMMS format: i.e: 21.471541 E
            height_gimbal (float): Height of the GPS Antenna in GROUND station. In meters.
            lat_drone (float): Latitude of DRONE station. In DDMMS format: i.e: 62.471541 N
            lon_drone (float): Longitude of DRONE station. In DDMMS format: i.e: 21.471541 E
            height_drone (float): Height of the GPS Antenna in DRONE station. In meters.

        Returns:
            yaw_to_set, roll_to_set (int): yaw and roll angles (in DEGREES*10) to set in GROUND gimbal.
        """

        # Ground station
        if self.IsGPS and self.ID == 'GROUND' and lat_ground is None  and lon_ground is None and height_ground is None:
            '''
            lat_ground = self.mySeptentrioGPS.NMEA_buffer[-1]['Latitude']
            lon_ground = self.mySeptentrioGPS.NMEA_buffer[-1]['Longitude']
            height_ground = self.mySeptentrioGPS.NMEA_buffer[-1]['Antenna Alt above sea level (mean)']
            heading = self.mySeptentrioGPS.NMEA_buffer[-1]
            '''

            # Get the last heading and coordinates
            # If there is more than one heading_ground,lat_ground,lon_ground or height_ground, th eloop overwrites the variable since is an easy implementation and the buffer is small (<=20 entries)
            for dict_i in self.mySeptentrioGPS.SBF_frame_buffer[-self.mySeptentrioGPS.n_sbf_sentences:]:
                if 'Heading' in dict_i:
                    if dict_i['ERR'] == 0:
                        heading = dict_i['Heading']
                    else:
                        print('\nERROR: No heading information available at THIS terminal')
                        return -10000, -10000, -10000 
                elif 'X' and 'Y' and 'Z' in dict_i:
                    if dict_i['ERR'] == 0:
                        # Coordinates encapsulated in SBF sentences are geocentric (X, Y, Z)
                        lat_ground = dict_i['Y']
                        lon_ground = dict_i['X']
                        datum_coordinates = dict_i['Datum']

                        # Geocentric WGS84
                        if datum_coordinates == 0:
                        # Z coordinate is geocentric and does not correspond to the actual height in meters: we need to transform to geodetic and take only the Z variable
                            _, _, height_ground = geocentric2geodetic(lat_ground, lon_ground, dict_i[-1]['Z'])
                        # Geocentric ETRS89
                        elif datum_coordinates == 30:
                            _, _, height_ground = geocentric2geodetic(lat_ground, lon_ground, dict_i['Z'], EPSG_GEOCENTRIC=4346)
                        else:
                            print('\nERROR: Not known geocentric datum')
                            return -10000, -10000, -10000
                        
                    else:
                        print('\nERROR: No geocentric coordinates are available at THIS terminal')
                        return -10000, -10000, -10000
                else:
                    print('\nERROR: No Heading or Geocentric coordinates entries at the gps buffer in THIS terminal')
                    return -10000, -10000, -10000
            
            # If retrieved coordinates and heading info, we know they are geocentric (SBF buffer)
            coord_type = 'planar'

        # Drone station:
        '''
        We can compute the yaw, pitch angle of drone's gimbal, but HEADING information is not available from
        septentrio GPS for the drone, due to secondary antenna placement
        '''
        if self.IsGPS and self.ID == 'DRONE' and lat_drone is None  and lon_drone is None and height_drone is None:
            lat_drone = self.mySeptentrioGPS.NMEA_buffer[-1]['Latitude']
            lon_drone = self.mySeptentrioGPS.NMEA_buffer[-1]['Longitude']
            height_drone = self.mySeptentrioGPS.NMEA_buffer[-1]['Antenna Alt above sea level (mean)']   
        
        if (lat_ground is None and lat_drone is None) or (lon_ground is None and lon_drone is None) or (height_ground is None and height_drone is None):
            print("\nERROR: Either ground or drone coordinates must be provided")
            return 0, 0

        if coord_type == 'latlon':
            lat_drone_planar, lon_drone_planar = self.convert_DDMMS_to_planar(lon_drone, lat_drone, offset=None, epsg_in=4326, epsg_out=3901)
            lat_ground_planar, lon_ground_planar = self.convert_DDMMS_to_planar(lon_ground, lat_ground, offset=None, epsg_in=4326, epsg_out=3901)

        # Testing purposes
        elif coord_type == 'planar':
            lat_drone_planar = lat_drone
            lon_drone_planar = lon_drone
            lat_ground_planar = lat_ground
            lon_ground_planar = lon_ground
        
        position_drone = np.array([lon_drone_planar, lat_drone_planar, height_drone])
        position_ground = np.array([lon_ground_planar, lat_ground_planar, height_ground])
                    
        d_mobile_drone_2D = np.linalg.norm(position_drone[:-1] - position_ground[:-1])
                        
        pitch_to_set = np.arctan2(height_drone - height_ground, d_mobile_drone_2D)
        pitch_to_set = int(np.rad2deg(pitch_to_set)*10)
                            
        alpha = np.arctan2(lat_drone_planar - lat_ground_planar, lon_drone_planar - lon_ground_planar)

        # Restrict heading to [-pi, pi] interval. No need for < -2*pi check, cause it won't happen
        if heading > np.pi:
            heading = heading - np.pi*2
                    
        yaw_to_set = (alpha - np.pi/2) + heading

        if yaw_to_set > np.pi:
            yaw_to_set = yaw_to_set - np.pi*2
        elif yaw_to_set < -np.pi:
            yaw_to_set = yaw_to_set + np.pi*2
            
        yaw_to_set = int(np.rad2deg(-yaw_to_set)*10)
        
        return yaw_to_set, pitch_to_set, alpha
        
    def convert_DDMMS_to_planar(self, input_lon, input_lat, offset=None, epsg_in=4326, epsg_out=3067):
            """
            Converts from DDMMS coordinates to planar coordinates by using a specified projection.

            Args:
                input_lon (scalar): _description_
                input_lat (scalar): _description_
                offset (dictionary, optional): The coordinates of the (0, 0) coordinate in the planar system with meter units. Defaults to None.
                epsg_in (int, optional): _description_. Defaults to 4326.
                epsg_out (int, optional): _description_. Defaults to 3067. 
                
                Known EPSG codes:
                3067 ---> EUREF-FIN geodetic datum (ETRS-TM35FIN)
                4936 ---> ETRS89 Europe

            Returns:
                lat_planar, lon_planar (float): planar coordinates
            """
            
            # setup your projections, assuming you're using WGS84 geographic
            crs_wgs = proj.Proj(init='epsg:' + str(epsg_in))
            crs_bng = proj.Proj(init='epsg:' + str(epsg_out))  # use the Finnish epsg code

            # then cast your geographic coordinate pair to the projected system
            lon_planar, lat_planar = proj.transform(crs_wgs, crs_bng, input_lon, input_lat)

            # Remove offset
            if offset is not None:
                offset_lon_planar, offset_lat_planar = proj.transform(crs_wgs, crs_bng, offset['lon'], offset['lat'])
                lon_planar = lon_planar - offset_lon_planar
                lat_planar = lat_planar - offset_lat_planar

            return lat_planar, lon_planar
    
    def build_a2g_frame(self, type_frame='cmd', data=None, cmd=None, cmd_source_for_ans=None):
        """
        Builds the frame for the a2g communication messages.
        
        The frame consists of the following fields:
        
        SYNCH1 | SYNCH2 | LENGHT_OF_HEADER | TYPE_FRAME | TERMINATOR_HEADER | DATA(OPTIONAL)
        ------  -------   ----------------  -----------   -----------------   -------------
         '%'      '-'         2-entries       string            ';'              string
                            string array       array                              array

        LENGHT_OF_HEADER comprises all the fields but not the DATA field.

        Args:
            type_frame (str, optional): 'cmd' or 'ans'. Defaults to 'cmd'.
            data (str, optional): data to be set with the 'cmd' (i.e. for the comand 'SETGIMBAL', data contains the gimbal position to be set).
                                  Or data to be sent in 'ans' frame. 
            cmd (str, optional): List of commands includes: 'GETGPS', 'SETGIMBAL'. Defaults to None.
            cmd_source_for_ans (str, optional): always provide which command you are replying to, in the answer frame.
            
        Returns:
            frame (str): this might be a string array containing a json-converted dictionary(i.e. ANS frames) or other type of object (SNDDATA).    
        
        
        """
        synch_1 = '%'
        synch_2 = '*'
        term_header_charac = ';'

        if type_frame == 'cmd':
            header_type_field = cmd
            
            if len(header_type_field) > 4:
                header_length_field = str(2 + 2 + len(header_type_field) + 1)
            else:
                header_length_field = '0' + str(2 + 2 + len(header_type_field) + 1)

            if data:
                frame = synch_1 + synch_2 + header_length_field + header_type_field + term_header_charac + json.dumps(data)
            else:
                frame = synch_1 + synch_2 + header_length_field + header_type_field + term_header_charac
        
        elif type_frame =='ans':
            header_type_field = 'ANS'
            
            if len(header_type_field) > 4:
                header_length_field = str(2 + 2 + header_type_field + 1)
            else:
                header_length_field = '0' + str(2 + 2 + header_type_field + 1)

            if data:
                frame = synch_1 + synch_2 + header_length_field + header_type_field + term_header_charac + json.dumps({'CMD_SOURCE': cmd_source_for_ans, 'DATA': data})
            else:
                frame = synch_1 + synch_2 + header_length_field + header_type_field + term_header_charac
        
        return json.dumps(frame)

    def do_getgps_action(self):
        """
        Function to execute when the received instruction in the a2g comm link is 'GETGPS'.

        """
        if self.DBG_LVL_1:
            print(f"THIS ({self.ID}) receives a GETGPS command")
    
        if self.IsGPS:            
            # Only need to send to the OTHER station our last coordinates, NOT heading.
            # Heading info required by the OTHER station is Heading info from the OTHER station
            coordinates = []

            # The loop overwrites data_to_send, so that the last coordinate is saved
            # We have to loop over last buffer entries, cause we don't know if last entry is heading or coordinates
            # Moreover, heading and coordinate msgs don't arrive alternating between them
            for dict_i in self.mySeptentrioGPS.SBF_frame_buffer[-2*self.n_sbf_sentences:]:
                if dict_i['ERR'] == 0:
                    if 'X' in dict_i and 'Y' in dict_i and 'Z' in dict_i:
                        data_to_send = dict_i
                else:
                    print('\nEither heading or coordinates information not available')
                    return    

            frame_to_send = self.build_a2g_frame(type_frame='ans', data=data_to_send, cmd_source_for_ans='GETGPS')
            
            if self.DBG_LVL_1:
                print('\nReceived the GETGPS and read the SBF buffer')
            if self.ID == 'GROUND':
                self.a2g_conn.sendall(frame_to_send.encode())
            if self.ID == 'DRONE':
                self.socket.sendall(frame_to_send.encode())
        else:
            print('\nASKED for GPS position but no GPS connected: IsGPS is False')
    
    def do_setgimbal_action(self, msg_data):
        """
        Function to execute when the received instruction in the a2g comm link is 'SETGIMBAL'.

        Args:
            msg_data (): string array with the yaw and pitch angle to be moved.                             
        """

        if self.IsGimbal:
            # Unwrap the dictionary containing the yaw and pitch values to be set.
            msg_data = json.loads(msg_data)

            # Error checking
            if 'YAW' not in msg_data or 'PITCH' not in msg_data:
                print('\nError: no YAW or PITCH provided')
                return
            else:
                if float(msg_data['YAW']) > 1800 or float(msg_data['PITCH']) > 1800 or float(msg_data['YAW']) < -1800 or float(msg_data['PITCH']) < -1800:
                    print('\nError: Yaw or pitch angles are outside of range')
                    return
                else:
                    self.myGimbal.setPosControl(yaw=int(msg_data['YAW']), roll=0, pitch=int(msg_data['PITCH']))
        else:
            print('\nAction to SET Gimbal not posible cause there is no gimbal: IsGimbal is False')

    def process_answer(self, msg_data):
        
        if self.DBG_LVL_1:
                print(f'\nTHIS ({self.ID}) receives protocol ANS')
                
        msg_data = json.loads(msg_data)
        cmd_source = msg_data['CMD_SOURCE']
        
        data = msg_data['DATA']
        # THIS IS UNNECESARY and it gives an error
        #data = json.loads(msg_data['DATA'])

        if cmd_source == 'GETGPS':
            if self.DBG_LVL_1:
                print(f'\nTHIS ({self.ID}) receives ANS to GETGPS cmd')
            if self.ID =='DRONE':
                # Invoke c++ function controlling drone's gimbal
                1
            elif self.ID == 'GROUND':

                lat_drone = data['Y']
                lon_drone = data['X']
                datum_coordinates = data['Datum']

                # Z is in geocentric coordinates and does not correspond to the actual height

                # Geocentric WGS84
                if datum_coordinates == 0:
                    _, _, height_drone = geocentric2geodetic(lat_drone, lon_drone, data['Z'])
                # Geocentric ETRS89
                elif datum_coordinates == 30:
                    _, _, heightdrone = geocentric2geodetic(lat_drone, lon_drone, data['Z'], EPSG_GEOCENTRIC=4346)
                else:
                    print('\nERROR: Not known geocentric datum')

                yaw_to_set, pitch_to_set, _ = self.ground_gimbal_follows_drone(heading=None, lat_ground=None, lon_ground=None, height_ground=None, 
                                    lat_drone=lat_drone, lon_drone=lon_drone, height_drone=height_drone, coord_type='planar')
                
                print(f"YAW to set: {yaw_to_set}, PITCH to set: {pitch_to_set}")
                
    def parse_rx_msg(self, rx_msg):
        """
        Handles the received socket data. 

        Args:
            rx_msg (str): received data from socket
        """

        # Check:
        if rx_msg[0] != '%':
            print('\nWrong frame message')
            return
        if rx_msg[1] != '*':
            print('\nWrong frame message')
            return

        len_frame_header = int(rx_msg[2:4])
        msg_data_len = len(rx_msg) - len_frame_header

        if msg_data_len > 0:
            msg_data = rx_msg.split(';')
            header_field = msg_data[0][4:]
            msg_data = msg_data[1]
        else:
            header_field = rx_msg[4:-1]

        if self.DBG_LVL_1:
            print(f'\nTHIS ({self.ID}) parses incoming message')
        if header_field == 'ANS':
            self.process_answer(msg_data)
        elif header_field == 'GETGPS':
            self.do_getgps_action()
        elif header_field == 'SETGIMBAL':
            self.do_setgimbal_action(msg_data)
    
    def socket_receive(self, stop_event):
        """
        Callback for when receiveing an incoming socket message.

        Args:
            stop_event (Event thread): event thread used to stop the callback
        """
        while not stop_event.is_set():
            try:
                # Send everything in a json serialized packet
                if self.ID == 'GROUND':
                    data = json.loads(self.a2g_conn.recv(1024).decode())
                elif self.ID == 'DRONE':
                    data = json.loads(self.socket.recv(1024).decode())
                if data:
                    if self.DBG_LVL_0:
                        print(data)
                    self.parse_rx_msg(data)
            # i.e.  Didn't receive anything
            except Exception as e:
                if self.DBG_LVL_0:
                    print('[SOCKET RECEIVE EXCEPTION]: ', e)
         
    def socket_send_cmd(self, type_cmd=None, data=None):
        """
        Wrapper to send a command through the socket between ground and drone connection (or viceversa).
        
        If 'type_cmd' is 'SETGIMBAL', the 'data' argument SHOULD BE a dictionary as follows:
        
        {'YAW': yaw_value, 'PITCH', pitch_value}
        
        where yaw_value and pitch_value are integers (between -1800, 1800).

        Args:
            type_cmd (_type_, optional): _description_. Defaults to None.
            data (object, optional): _description_. Defaults to None.
        """
        if type_cmd == 'GETGPS':
            frame = self.build_a2g_frame(type_frame='cmd', cmd=type_cmd)
        
        elif type_cmd == 'SETGIMBAL':
            frame = self.build_a2g_frame(type_frame='cmd', cmd=type_cmd, data=data)
        
        if self.ID == 'DRONE':
            self.socket.sendall(frame.encode())
        elif self.ID == 'GROUND':
            self.a2g_conn.sendall(frame.encode())
    
    def send_N_azimuth_angles(self, az_now, pitch_now, Naz, el_now=None, Nel=None, meas_number='1', meas_time=10):
        """
        Divides the azimuth in Naz sections and for each correspondent angle sets the yaw of the gimbal,
        and waits for the user input before moving gimbal to next angle. The angle count starts from az_now
        
        Args:
            az_now (int): angle where to start the count. It lies between -1800 and 1800
            Naz (int): number of sectors in azimuth circle
            el_now (_type_, optional): _description_. Defaults to None.
            Nel (_type_, optional): _description_. Defaults to None.
            meas_number (str, optional): number of measurement according to Flight Plan. Defaults to '1'.
        """

        reset_ang_buffer = []
        to_save_file = []
        if self.IsGimbal:
            for i in range(Naz):
                ang = int((i+1)*3600/Naz)
                ang = az_now + ang
                if ang > 1800:
                    ang = ang - 3600
                if ang < -1800:
                    ang = ang + 3600
                
                reset_ang_buffer.append(ang)
                
                self.myGimbal.setPosControl(yaw=ang, roll=0, pitch=pitch_now)
                
                # Approximate gimbal speed of 56 deg/s:
                # Max angular movement is 1800 which is done in 3.5 at the actual speed 
                time.sleep(1800/self.myGimbal.speed + 1) 

                self.inst.write('RF1\n')
                print('Measuring for ' + str(meas_time) + '  secs\n')
                time.sleep(meas_time)
                self.inst.write('RF0\n')
                
                to_save = self.mySeptentrioGPS.NMEA_buffer[-1]
                self.myGimbal.request_current_position()
                time.sleep(0.0015)
                
                to_save['GROUND_GIMBAL_YAW'] = self.myGimbal.yaw
                to_save['GROUND_GIMBAL_PITCH'] = self.myGimbal.pitch
                to_save_file.append(to_save)
        else:
            print('To call this function, IsGimbal has to be set')
        
        to_save_now = json.dumps(to_save_file)
        filename = 'MEASUREMENT_' + meas_number
        f = open(filename + '.json', 'w')
        f.write(to_save_now)
        f.close()
        
        print(f'File {filename} saved')
        
        reset_buffer = reset_ang_buffer[-2::-1]
        reset_buffer.append(reset_ang_buffer[-1])
        return reset_buffer
        
    def HelperStartA2GCom(self, PORT=10000):
        """
        Starts the socket binding, listening and accepting for server side, or connecting for client side. 
        Starts the thread handling the socket messages.
        
        Args:
            PORT (int, optional): _description_. Defaults to 12000.
        """
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket = s
        
        # This will block, so keep it low
        self.socket.settimeout(10) 
        
        # CLIENT
        if self.ID == 'DRONE':
            self.socket.connect((self.SERVER_ADDRESS, PORT))
            if self.DBG_LVL_1:
                print('CONNECTION ESTABLISHED with SERVER ', self.SERVER_ADDRESS)
        
        # SERVER
        elif self.ID == 'GROUND':            

            # Bind the socket to the port
            self.socket.bind(('', PORT))

            # Listen for incoming connections
            self.socket.listen()

            # BLOCKS UNTIL ESTABLISHING A CONNECTION
            a2g_connection, client_address = self.socket.accept()
            
            if self.DBG_LVL_1:
                print('CONNECTION ESTABLISHED with CLIENT ', client_address)
            
            self.a2g_conn = a2g_connection
            self.CLIENT_ADDRESS = client_address
            
        self.event_stop_thread_helper = threading.Event()
        thread_rx_helper = threading.Thread(target=self.socket_receive, args=(self.event_stop_thread_helper,))
        thread_rx_helper.start()
        
    def HelperA2GStopCom(self, DISC_WHAT='ALL', GPS_STOP='+NMEA+SBF'):
        """
        Stops communications with all the devices or the specified ones in the variable 'DISC_WHAT

        Args:
            DISC_WHAT (str, optional): specifies what to disconnect. Defaults to 'ALL'. Options are: 'SG', 'GIMBAL', 'GPS', 'ALL'
        """
        try:   
            self.event_stop_thread_helper.set()
             
            if self.ID == 'DRONE':
                self.socket.close()
            elif self.ID == 'GROUND':
                self.a2g_conn.close()
        except:
            print('\nERROR closing connection: probably NO SOCKET created')         
        
        if self.IsGimbal and (DISC_WHAT=='ALL' or DISC_WHAT == 'GIMBAL'):  
            self.myGimbal.stop_thread_gimbal()
            print('\nDisconnecting gimbal')
            time.sleep(0.05)
            self.myGimbal.actual_bus.shutdown()
            
        if self.IsGPS and (DISC_WHAT=='ALL' or DISC_WHAT == 'GPS'):  
            self.mySeptentrioGPS.stop_gps_data_retrieval()
            print('\nStoping GPS stream')
            self.mySeptentrioGPS.stop_thread_gps()
        
        if self.IsSignalGenerator and (DISC_WHAT=='ALL' or DISC_WHAT == 'SG'): 
            self.inst.write('RF0\n')   
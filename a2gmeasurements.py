import struct
from ctypes import *
import numpy as np
from check_sum import *
from pynput import keyboard
import can
import socket
import threading
import pynmea2

class GimbalRS2(object):
    def __init__(self):
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

        self.MAIN_LOOP_STOP = True
        self.keyboard_set_flag = False
        self.keyboard_buff = []

        self.cntBytes = 0
    
        #self.actual_bus = busObj
   
    def seq_num(self):
        """_summary_ : updates the sequence number and outputs it in an string array
                    Each array entry is a digit from the 4-digit hex string
        Returns:
            _type_: sequence number string array
        """

        if self.seq >= 0xFFFD:
            self.seq = 0x0002
        self.seq += 1
        # Seq_Init_Data = 0x1122
        seq_str = "%04x" % self.seq
        return seq_str[2:] + ":" + seq_str[0:2]

    def can_buffer_to_full_frame(self):
        '''

        '''
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
        print(output)
        
    def can_callback(self, data):
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

    def send_joint_pos(self, req):
        # print("Returning [%s + %s +%s ]" % (req.pitch, req.yaw, req.roll))

        yaw = 10 * req.yaw
        roll = 10 * req.roll
        pitch = 10 * req.pitch
        success = False
        if -1800 <= yaw <= 1800 and -1800 <= roll <= 1800 and -1800 <= pitch <= 1800:
            success = self.setPosControl(yaw, roll, pitch)
        #return SendJointPosResponse(success)

    def send_joint_speed_cmd(self, req):
        # Angular speeds in 0.1 deg/sec
        yaw = req.yaw * 10
        pitch = req.pitch * 10
        roll = req.roll * 10

        success = False
        if -3600 <= yaw <= 3600 and -3600 <= roll <= 3600 and -3600 <= pitch <= 3600:
            success = self.setSpeedControl(yaw, roll, pitch)
        #return SendJointSpeedResponse(success)

    def setSpeedControl(self, yaw, roll, pitch, ctrl_byte=0x80):
        hex_data = struct.pack('<3hB', yaw, roll, pitch, ctrl_byte)
        pack_data = ['{:02X}'.format(struct.unpack('<1B', i)[
            0]) for i in hex_data]
        cmd_data = ':'.join(pack_data)

        cmd = self.assemble_can_msg(cmd_type='03', cmd_set='0E',
                                    cmd_id='01', data=cmd_data)
        # print('cmd---data {}'.format(cmd))
        self.send_cmd(cmd)
        return True

    def request_current_position(self):
        hex_data = [0x01]
        pack_data = ['{:02X}'.format(i)
                     for i in hex_data]
        cmd_data = ':'.join(pack_data)
        cmd = self.assemble_can_msg(cmd_type='03', cmd_set='0E',
                                    cmd_id='02', data=cmd_data)
        self.send_cmd(cmd)

    def assemble_can_msg(self, cmd_type, cmd_set, cmd_id, data):
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
        data = [int(i, 16) for i in cmd.split(":")]
        #print(data)
        self.send_data(self.send_id, data)

    def send_data(self, can_id, data):
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
                print(f"Message sent on {self.actual_bus.channel_info}")
            except can.CanError:
                print("Message NOT sent")
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
    def __init__(self, gpsID):
        # Initializations
        # Dummy initialization
        self.gpsID = gpsID
        
    def socket_connect(self, HOST="192.168.3.1", PORT=28784, time='sec1'):
        """
        Creates a socket to connect to the command-line terminal provided by Septentrio receiver. 
        Sends the first command (in Septentrio-defined 'language') to set-up a regular retrieve of gps info

        Args:
            HOST (str, optional): IP address where the server is allocated. Defaults to "192.168.3.1".
            PORT (int, optional): PORT number of the application. Defaults to 28784.
            time (str, optional): How regular get updates of the gps data. Defaults to 'sec1'.
        """
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket = s
        
        self.socket.connect((HOST, PORT))
        #data = s.recv(64)

        cmd_set_gps = 'sno, Stream 3, IP11, GGA, ' + time + '\n'
        self.socket.sendall(cmd_set_gps.encode('utf-8'))

        self.event_stop_thread_socket = threading.Event()
        t_receive = threading.Thread(target=self.socket_receive, args=(self.event_stop_thread_socket))
        t_receive.start()

    def socket_receive(self, stop_event):
        """
        Callback function to be called when incoming gps data

        Args:
            stop_event (threading): the threading event that stops the TCP/IP com
        """

        while not stop_event.is_set():
            data = self.socket.recv(64)
            self.process_input_data(data)
            
            
    def process_input_data(self, data):
        """

        Translates gps data in NMEA format into a dictionary

        Args:
            data (list): list of gps data in NMEA format

        Returns:
            dict: dictionary with the gps data
        """

        nmeaobj = pynmea2.parse(data.decode('utf-8'))
        gps_list = ['%s: %s' % (nmeaobj.fields[i][0], nmeaobj.data[i]) for i in range(len(nmeaobj.fields))]
        
        gps_data = {}
        for item in gps_list:
            tmp = item.split(': ')
            gps_data[tmp[0]] = tmp[1]


        return gps_data
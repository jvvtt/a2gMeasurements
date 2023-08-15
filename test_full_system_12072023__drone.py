from a2gmeasurements import HelperA2GMeasurements
from a2gUtils import geodetic2geocentric
import time
import threading
import re

pattern_ip_addresses = r'[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}'
print("Welcome to the DRONE client program! You have 60s to input")

def check_devices():
    GND_ADDRESS = input('Enter the GND node IP address: ')
    is_ip_addr = bool(re.match(pattern_ip_addresses, GND_ADDRESS))

    while(not is_ip_addr):
        print("IP address entered is not an IP address. ")
        GND_ADDRESS = input('Enter GND node IP address: ')
        is_ip_addr = bool(re.match(pattern_ip_addresses, GND_ADDRESS))    

    is_gps_used = input('GPS at DRONE is going to be used? y/n: ')
    if is_gps_used == 'y':
        gps_used = True
    elif is_gps_used == 'n':
        gps_used = False

    is_gimbal_used = input('Gimbal at DRONE is going to be used? y/n: ')
    if is_gimbal_used == 'y':
        gimbal_used = True
    elif is_gimbal_used == 'n' :
        gimbal_used = False
        
    is_rfsoc_used = input('RFSoC at DRONE is going to be used? y/n: ')
    if is_rfsoc_used == 'y':
        rfsoc_used = True
    elif is_rfsoc_used == 'n':
        rfsoc_used = False
        
    return GND_ADDRESS, gps_used, gimbal_used, rfsoc_used

not_created_class_instance = True
not_finish_tcp_connection_attempt = True
unsuccessful_drone2gnd_connection_attempt_cnt = 0

while(not_created_class_instance):
    try:   
        GND_ADDRESS, gps_used, gimbal_used, rfsoc_used = check_devices()
        drone_a2g_helper = HelperA2GMeasurements('DRONE', GND_ADDRESS, DBG_LVL_1=False, IsGPS=gps_used, IsRFSoC=rfsoc_used, rfsoc_static_ip_address='10.1.1.40', IsGimbal=gimbal_used)
    except Exception as e:
        print("[DEBUG]: There is some error creating the a2gmeasurements class instance")
        print("[DEBUG]: ERROR: ", e)
        print("[DEBUG]: Check that device flag values for IsGPS, IsRFSoC, IsGimbal correspond to what is connected to the Manifold")
    else:
        not_created_class_instance = False

while(not_finish_tcp_connection_attempt):
    try:
        drone_a2g_helper.HelperStartA2GCom()
    except Exception as e:
        print("[DEBUG]: There is an error establishing the TCP connection to the server")
        print("[DEBUG]: ERROR: ", e)
        input("Press ENTER to try to establish the connection again")
        unsuccessful_drone2gnd_connection_attempt_cnt = unsuccessful_drone2gnd_connection_attempt_cnt + 1
    else:
        print("[DEBUG]: Connection established with GND")
        not_finish_tcp_connection_attempt = False
    finally:
        if unsuccessful_drone2gnd_connection_attempt_cnt == 100:
            print("[DEBUG]: Number of connection attempts is high (100). Closing the program")
            break        

if not_finish_tcp_connection_attempt == False:
    while(drone_a2g_helper.CONN_MUST_OVER_FLAG == False):
        time.sleep(0.1)
        
        if hasattr(drone_a2g_helper.myrfsock, 'data_to_visualize'):
            if len(drone_a2g_helper.myrfsoc.data_to_visualize) > 0:
                drone_a2g_helper.socket_send_cmd(type_cmd='SETIRF', data=drone_a2g_helper.myrfsoc.data_to_visualize)
                drone_a2g_helper.myrfsoc.data_to_visualize = []  # this is the way we flush the buffer after read it, so that we don't send the same data multiple times
        
drone_a2g_helper.HelperA2GStopCom(DISC_WHAT='ALL')
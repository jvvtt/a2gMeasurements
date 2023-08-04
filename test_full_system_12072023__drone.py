from a2gmeasurements import HelperA2GMeasurements
from a2gUtils import geodetic2geocentric
import time
import threading
import re


pattern_ip_addresses = r'[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}'
print("Welcome to the DRONE client program! You have 60s to input")

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

drone_a2g_helper = HelperA2GMeasurements('DRONE', GND_ADDRESS, DBG_LVL_1=False, IsGPS=gps_used, IsRFSoC=rfsoc_used, rfsoc_static_ip_address='10.1.1.40', IsGimbal=gimbal_used)
drone_a2g_helper.HelperStartA2GCom()

try:    
    while(True):   
        
        time.sleep(1)
        

except Exception as e:        
    print('\nThere is an exception: ', e)
    
    drone_a2g_helper.HelperA2GStopCom(DISC_WHAT='ALL')
from a2gmeasurements import HelperA2GMeasurements
from a2gUtils import geodetic2geocentric
import time
import threading
import re


pattern_ip_addresses = r'[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}'
GND_ADDRESS = input('Enter the GND node IP address: ')
is_ip_addr = bool(re.match(pattern_ip_addresses, GND_ADDRESS))

while(not is_ip_addr):
    print("IP address entered is not an IP address. ")
    GND_ADDRESS = input('Enter GND node IP address: ')
    is_ip_addr = bool(re.match(pattern_ip_addresses, GND_ADDRESS))    

drone_a2g_helper = HelperA2GMeasurements('DRONE', GND_ADDRESS, DBG_LVL_1=True, IsGPS=True, IsRFSoc=True, rfsoc_static_ip_address='10.1.1.40')
drone_a2g_helper.HelperStartA2GCom()

try:    
    while(True):   
        
        time.sleep(1)
        

except Exception as e:        
    print('\nThere is an exception: ', e)
    
    drone_a2g_helper.HelperA2GStopCom(DISC_WHAT='ALL')
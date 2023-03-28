from a2gmeasurements import HelperA2GMeasurements
from a2gUtils import geodetic2geocentric
import time
import threading


SERVER_ADDRESS = '192.168.0.2'
drone_a2g_helper = HelperA2GMeasurements('DRONE', SERVER_ADDRESS, DBG_LVL_1=True, IsGPS=True)

drone_a2g_helper.HelperStartA2GCom()

try:    
    while(True):   
        
        time.sleep(1)
        

except Exception as e:        
    print('\nThere is an exception: ', e)
    
    drone_a2g_helper.HelperA2GStopCom(DISC_WHAT='GPS')
import socket
from a2gmeasurements import HelperA2GMeasurements, GpsSignaling, GimbalRS2
import json
import sys
import time

host = 'localhost'
myHelper = HelperA2GMeasurements('DRONE', host, DBG_LVL_0=False, DBG_LVL_1=True)
myHelper.HelperStartA2GCom()

mySeptentrioGPS = GpsSignaling(DBG_LVL_2=True)
mySeptentrioGPS.serial_connect()
mySeptentrioGPS.start_thread_gps()
mySeptentrioGPS.start_gps_data_retrieval(msg_type='NMEA', nmea_type='GGA', interval='sec1')
print('Setting GPS...')
time.sleep(0.5)

Naz = 4
continue_condition = True
while(continue_condition):    
    try:
        if myHelper.SOCKET_BUFFER:
            if myHelper.SOCKET_BUFFER[-1] == 'GET_GPS':
                if mySeptentrioGPS.NMEA_buffer != []:    
                    # Send last GPS coordinate
                    data = json.dumps(mySeptentrioGPS.NMEA_buffer[-1])
                    myHelper.socket.sendall(data.encode())
                    
        if myHelper.SOCKET_BUFFER:
            if myHelper.SOCKET_BUFFER[-1] == 'END_EXPERIMENT':
                continue_condition = False
    except Exception as e:
        print('Error in CLIENT:', e)
        break
        
    
myHelper.HelperA2GStopCom()

mySeptentrioGPS.stop_gps_data_retrieval(msg_type='NMEA')
mySeptentrioGPS.stop_thread_gps()

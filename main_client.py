import socket
from a2gmeasurements import HelperA2GMeasurements, GpsSignaling, GimbalRS2
import json
import sys
import time

host = 'localhost'
myHelper = HelperA2GMeasurements('DRONE', host, DBG_LVL_0=False, DBG_LVL_1=True)
myHelper.HelperStartA2GCom()

myGimbal = GimbalRS2()
myGimbal.start_thread_gimbal()
print('Setting Gimbal RS2...')
time.sleep(0.5)

mySeptentrioGPS = GpsSignaling(DBG_LVL_2=True)
mySeptentrioGPS.serial_connect()
mySeptentrioGPS.start_thread_gps()
mySeptentrioGPS.start_gps_data_retrieval(msg_type='NMEA', nmea_type='GGA', interval='msec500')
print('Setting GPS...')
time.sleep(0.5)

Naz = 4
continue_condition = True
while(continue_condition):    
    try:
        if mySeptentrioGPS.NMEA_buffer != []:            
            data = json.dumps(mySeptentrioGPS.NMEA_buffer[-1])
            myHelper.socket.sendall(data.encode())
            
            myGimbal.request_current_position()
            #input('[CLIENT]: Press ENTER to continue MAIN THREAD')
            
            az_now = input('[CLIENT]: Input the actual angle\n')
            myGimbal.send_N_azimuth_angles(int(float(az_now)), Naz)
            
            continue_condition = False            
            #Naz = Naz-1            
    except Exception as e:
        print('Error in client side', e)
        break
        
    
myHelper.HelperA2GStopCom()

mySeptentrioGPS.stop_gps_data_retrieval(msg_type='NMEA')
mySeptentrioGPS.stop_thread_gps()

myGimbal.stop_thread_gimbal()
print('Disconnecting gimbal...')
time.sleep(0.05)
myGimbal.actual_bus.shutdown()
import json
import numpy as np
from socket import socket
import time
from a2gmeasurements import HelperA2GMeasurements, GimbalRS2, GpsSignaling

route_1 = {'CLOSE_GRB': [60.159470, 24.911216], 'FAR_GRB': [60.160341, 24.913697]}
drone_pos_sim = [60.158775, 24.911166]
heights_drone = [20, 40, 60, 90]
height_car = 1
simulation = True
DEBUG = True

continue_condition=True
Naz = 4

host = 'localhost'
myHelper = HelperA2GMeasurements('GROUND', host, DBG_LVL_0=False, DBG_LVL_1=True)
myHelper.HelperStartA2GCom()

myGimbal = GimbalRS2()
myGimbal.start_thread_gimbal()
print('Setting Gimbal RS2...\n')
time.sleep(0.5)

mySeptentrioGPS = GpsSignaling(DBG_LVL_2=True)
mySeptentrioGPS.serial_connect()
mySeptentrioGPS.start_thread_gps()
mySeptentrioGPS.start_gps_data_retrieval(msg_type='NMEA', nmea_type='GGA', interval='sec1')
print('Setting GPS...')
time.sleep(0.5)

while(continue_condition):    
    # Always checking if a request of sending coordinates has arrived
    try:
        if myHelper.SOCKET_BUFFER:
            if myHelper.SOCKET_BUFFER[-1] == 'GET_GPS':
                if mySeptentrioGPS.NMEA_buffer != []:    
                    # Send last GPS coordinate
                    data = json.dumps(mySeptentrioGPS.NMEA_buffer[-1])
                    myHelper.a2g_conn.sendall(data.encode())
    except Exception as e:
        print('[DEBUG]: Exception when reading socket or sending gps coordinates: ', e)
        
    #input('Send GPS request?')
    myHelper.a2g_conn.sendall(json.dumps('GET_GPS').encode())
    try:
        if myHelper.SOCKET_BUFFER:
            if myHelper.SOCKET_BUFFER[-1]['Latitude'] != '' or DEBUG==True:
               # When No GPS conn, emulate some random lat, lon and alt for the drone position
                if simulation:
                    print("[SERVER]: Simulating drone and car realistic positions")
                    lat_drone = drone_pos_sim[0]
                    lon_drone = drone_pos_sim[1]
                    lat_car = route_1['CLOSE_GRB'][0] + np.random.rand()*(route_1['FAR_GRB'][0] - route_1['CLOSE_GRB'][0])
                    lon_car = route_1['CLOSE_GRB'][1] + np.random.rand()*(route_1['FAR_GRB'][1] - route_1['CLOSE_GRB'][1])
                    
                    # This angles are respect to the North
                    yaw, roll = myHelper.mobile_gimbal_follows_drone(lat_car, lon_car, height_car, 
                                                    lat_drone, lon_drone, heights_drone[0])
                else:
                    lat_drone = float(myHelper.SOCKET_BUFFER['Latitude'])/10
                    lon_drone = float(myHelper.SOCKET_BUFFER['Longitude'])/10
                    
                    # Septentrio handling of car coordinates
                
                print(f"[SERVER]: Move gimbal towards YAW :{yaw}, ROLL: {roll}, to point to DRONE")
    except Exception as e:
        print('[SERVER]: Exception ', e)
            
    myGimbal.request_current_position()
    print(myGimbal.yaw, myGimbal.roll, '\n')
    
    az_now = input('[SERVER]: Input the actual angle\n')
    myGimbal.send_N_azimuth_angles(int(float(az_now)), Naz)
    
    answer = input('End of measurement?\n')
    
    if answer == 'Yes':
        continue_condition = False            
        myHelper.a2g_conn.sendall(json.dumps('END_EXPERIMENT').encode())

print('Stoping SERVER')
myHelper.HelperA2GStopCom()

myGimbal.stop_thread_gimbal()
print('Disconnecting gimbal...')
time.sleep(0.05)
myGimbal.actual_bus.shutdown()

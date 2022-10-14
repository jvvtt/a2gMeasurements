import json
import numpy as np
from socket import socket
import time
from a2gmeasurements import HelperA2GMeasurements, GimbalRS2, GpsSignaling

input('Start Experiment?')

host = 'localhost'
myHelper = HelperA2GMeasurements('GROUND', host, DBG_LVL_0=False, DBG_LVL_1=True, IsGPS=True, IsGimbal=True)
myHelper.HelperStartA2GCom()
print('Starting SERVER...')
time.sleep(1)

# ---------------------------Pointing GROUND gimbal to DRONE------------------------------------------------
# 1. Send GET_GPS
myHelper.a2g_conn.sendall(json.dumps('GET_GPS').encode())

# 2. Request Gimbal orientation
myHelper.myGimbal.request_current_position()
time.sleep(0.0015)

# Gimbal assumed to be not moving
yaw_now = myHelper.myGimbal.yaw
roll_now = myHelper.myGimbal.roll
print('Compare yaw printed value previously, with yaw_now var: ', yaw_now, '\n')
print('Compare roll printed value previously, with roll_now var: ', roll_now, '\n')

# 3. Wait and block for DRONE position answer
while(myHelper.SOCKET_BUFFER==[]):
    1
# 4. Get DRONE coordinates    
lat_drone = float(myHelper.SOCKET_BUFFER[-1]['Latitude'])/10
lon_drone = float(myHelper.SOCKET_BUFFER[-1]['Longitude'])/10
height_drone = float(myHelper.SOCKET_BUFFER[-1]['Antenna Alt above sea level (mean)'])

# 5. Get GROUND (own) coordinates
while(myHelper.mySeptentrioGPS.NMEA_buffer == []):
    1
    
lat_ground = float(myHelper.mySeptentrioGPS.NMEA_buffer[-1]['Latitude'])/10
lon_ground = float(myHelper.mySeptentrioGPS.NMEA_buffer[-1]['Longitude'])/10
height_ground = float(myHelper.mySeptentrioGPS.NMEA_buffer[-1]['Antenna Alt above sea level (mean)'])

# 6. Point GROUND gimbal towards DRONE
yaw, roll = myHelper.mobile_gimbal_follows_drone(yaw_now, lat_ground, lon_ground, height_ground, 
                                                lat_drone, lon_drone, height_drone)

myHelper.myGimbal.setPosControl(yaw, roll, 0)

# ------------------------------- Angular movement and save experiments --------------------------------
# 7. Wait 
input('Press ENTER when GROUND gimbal finishes its pointing towards DRONE')

# 8. Send START_SA message to DRONE
myHelper.a2g_conn.sendall(json.dumps('START_SA').encode())

# 9. Request Gimbal orientation
myHelper.myGimbal.request_current_position()
time.sleep(0.0015)

# Gimbal assumed to be not moving
yaw_now = myHelper.myGimbal.yaw
roll_now = myHelper.myGimbal.roll
print('Compare yaw printed value previously, with yaw_now var: ', yaw_now, '\n')
print('Compare yaw printed value previously, with roll_now var: ', roll_now, '\n')

# 10. Move GROUND gimbal in 30 deg steps
N_ang_steps = 360/30
reset_yaw_gimbal = myHelper.send_N_azimuth_angles(int(yaw_now*10), int(roll_now*10), int(N_ang_steps), meas_number=meas_number)

# 11. Make the gimbal move in the opposite direction to unfold cables
for i in reset_yaw_gimbal:
    myHelper.myGimbal.setPosControl(i, int(roll_now*10), 0)
    time.sleep(1)

input('Stop test?')
myHelper.HelperA2GStopCom()
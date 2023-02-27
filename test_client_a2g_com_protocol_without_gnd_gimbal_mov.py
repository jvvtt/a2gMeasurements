from a2gmeasurements import HelperA2GMeasurements
from a2gUtils import geodetic2geocentric
import time
import numpy as np
import threading


cnt = 0
emulated_drone_coords = [[60.18592, 24.81174, 50], #'HiQ'
                         [60.18650, 24.81350, 50], # 'FutHub'
                         [60.18555, 24.82041, 60], # 'FatLiz'
                         [60.18495, 24.82302, 70]] # 'AaltoMetro'

SERVER_ADDRESS = '192.168.0.2'
drone_a2g_helper = HelperA2GMeasurements('DRONE', SERVER_ADDRESS, DBG_LVL_1=True, IsGPS=True)

def emulate_drone_sbf_gps_coords(cnt):
    '''
    Emulated drone position at the following known coordinates:

    HiQ Finland Y: 60.18592, 24.81174
    VTT Future Hub: 60.18650, 24.81350
    Ravintola Fat Lizard: 60.18555, 24.82041
    Aalto Yliopisto Metro Google maps mark: 60.18495, 24.82302

    '''

    X,Y,Z = geodetic2geocentric(emulated_drone_coords[int(cnt)][0], 
                                    emulated_drone_coords[int(cnt)][1], 
                                    emulated_drone_coords[int(cnt)][2])
        
    drone_a2g_helper.mySeptentrioGPS.SBF_frame_buffer[-1]['X'] =  X
    drone_a2g_helper.mySeptentrioGPS.SBF_frame_buffer[-1]['Y'] = Y
    drone_a2g_helper.mySeptentrioGPS.SBF_frame_buffer[-1]['Z'] = Z
    drone_a2g_helper.mySeptentrioGPS.SBF_frame_buffer[-1]['Datum'] =  0
    drone_a2g_helper.mySeptentrioGPS.SBF_frame_buffer[-1]['ERR'] =  0


drone_a2g_helper.HelperStartA2GCom()

try:    
    while(True):   
        emulate_drone_sbf_gps_coords(cnt)
        time.sleep(1)
        
        cnt = cnt + 1    

except Exception as e:        
    print('\nThere is an exception: ', e)
    #drone_a2g_helper.mySeptentrioGPS.stop_gps_data_retrieval()
    #drone_a2g_helper.mySeptentrioGPS.stop_thread_gps()
    drone_a2g_helper.HelperA2GStopCom(DISC_WHAT='GPS')
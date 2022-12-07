from a2gmeasurements import HelperA2GMeasurements
from a2gUtils import geodetic2geocentric
import time
import numpy as np
import threading
cnt = 1
emulated_drone_coords = [[60.18592, 24.81174, 50], #'HiQ'
                         [60.18650, 24.81350, 50], # 'FutHub'
                         [60.18555, 24.82041, 60], # 'FatLiz'
                         [60.18495, 24.82302, 70]] # 'AaltoMetro'

SERVER_ADDRESS = '192.168.0.2'
drone_a2g_helper = HelperA2GMeasurements('DRONE', SERVER_ADDRESS, DBG_LVL_0=True, DBG_LVL_1=True, IsGPS=True)

def emulate_drone_sbf_gps_coords():
    '''
    Emulated drone position at the following known coordinates:

    HiQ Finland Y: 60.18592, 24.81174
    VTT Future Hub: 60.18650, 24.81350
    Ravintola Fat Lizard: 60.18555, 24.82041
    Aalto Yliopisto Metro Google maps mark: 60.18495, 24.82302

    '''
    if 'X' in drone_a2g_helper.mySeptentrioGPS.SBF_frame_buffer[-1] and 'Y' in drone_a2g_helper.mySeptentrioGPS.SBF_frame_buffer[-1] and 'Z' in drone_a2g_helper.mySeptentrioGPS.SBF_frame_buffer[-1]:
        mod_len_em_coords = np.mod(cnt, len(emulated_drone_coords))

        X,Y,Z = geodetic2geocentric(emulated_drone_coords[int(mod_len_em_coords)][0], 
                                    emulated_drone_coords[int(mod_len_em_coords)][1], 
                                    emulated_drone_coords[int(mod_len_em_coords)][2])
        drone_a2g_helper.mySeptentrioGPS.SBF_frame_buffer[-1]['X'] =  X
        drone_a2g_helper.mySeptentrioGPS.SBF_frame_buffer[-1]['Y'] = Y
        drone_a2g_helper.mySeptentrioGPS.SBF_frame_buffer[-1]['Z'] = Z
        drone_a2g_helper.mySeptentrioGPS.SBF_frame_buffer[-1]['Datum'] =  0

for i in range(10):    
    emulate_drone_sbf_gps_coords()    
    
    print('\nCNT: ', cnt)
    print(f"\nTHIS ({drone_a2g_helper.ID}) emulated buff length: {len(drone_a2g_helper.mySeptentrioGPS.SBF_frame_buffer)}")
    #print(drone_a2g_helper.mySeptentrioGPS.SBF_frame_buffer[-1])
    
    cnt = cnt + 1    

drone_a2g_helper.mySeptentrioGPS.stop_gps_data_retrieval()
drone_a2g_helper.mySeptentrioGPS.stop_thread_gps()
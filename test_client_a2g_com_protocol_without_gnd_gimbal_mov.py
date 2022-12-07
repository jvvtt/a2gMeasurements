from a2gmeasurements import HelperA2GMeasurements
from a2gUtils import geodetic2geocentric


def emulate_drone_sbf_gps_coords():
    '''
    Emulated drone position at the following known coordinates:

    HiQ Finland Y: 60.18592, 24.81174
    VTT Future Hub: 60.18650, 24.81350
    Ravintola Fat Lizard: 60.18555, 24.82041
    Aalto Yliopisto Metro Google maps mark: 60.18495, 24.82302

    '''

    emulated_drone_coords = {'HiQ': [60.18592, 24.81174, 50], 
                             'FutHub': [60.18650, 24.81350, 50],
                             'FatLiz': [60.18555, 24.82041, 60],
                             'AaltoMetro': [60.18495, 24.82302, 70]}

    for key, val in emulate_drone_sbf_gps_coords.items():
        X,Y,Z = geodetic2geocentric(val[0], val[1], val[2])
        em_drone_gps_msg_data = {'X': X, 'Y': Y, 'Z': Z, 'Datum': 0}

SERVER_ADDRESS = '192.168.0.2'
drone_a2g_helper = HelperA2GMeasurements('DRONE', SERVER_ADDRESS, DBG_LVL_0=True, DBG_LVL_1=True)


drone_a2g_helper.HelperStartA2GCom()

# Update the emulated drone position
#drone_a2g_helper.



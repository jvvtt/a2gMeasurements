from a2gmeasurements import GpsSignaling
import time

def test_get_last_sbf_buffer_info(gpsObject, gps_state='off'):
    
    if gps_state == 'off':
        # 1. Call all the functions with the gps off
        COORD = gpsObject.get_last_sbf_buffer_info(what='Coordinates')
        HEAD = gpsObject.get_last_sbf_buffer_info(what='Heading')
        COORD_1, HEAD_1 = gpsObject.get_last_sbf_buffer_info(what='Both')
        
        if COORD['X'] == gpsObject.ERR_GPS_CODE_BUFF_NULL:
            print('\nTest 1 passed')
        if HEAD['Heading'] == gpsObject.ERR_GPS_CODE_BUFF_NULL:
            print('\nTest 2 passed')
        if COORD_1['X'] == gpsObject.ERR_GPS_CODE_BUFF_NULL and HEAD_1['Heading'] == gpsObject.ERR_GPS_CODE_BUFF_NULL:
            print('\nTest 3 passed')
    
    elif gps_state == 'ON_INDOOR':
        # 2. Call all the functions after GPS on, but indoor (no info available)
        gpsObject.serial_connect()
        #gpsObject.sendCommandGps(cmd='sga, MultiAntenna') # by default this is the command
        
        gpsObject.start_gps_data_retrieval(stream_number=1,  msg_type='SBF', interval='sec1', sbf_type='+PVTCartesian+AttEuler')
        gpsObject.start_thread_gps()
        
        COORD = gpsObject.get_last_sbf_buffer_info(what='Coordinates')
        HEAD = gpsObject.get_last_sbf_buffer_info(what='Heading')
        COORD_1, HEAD_1 = gpsObject.get_last_sbf_buffer_info(what='Both')

        if COORD['X'] == gpsObject.ERR_GPS_CODE_NO_COORD_AVAIL:
            print('\nTest 4 passed')
        if HEAD['Heading'] == gpsObject.ERR_GPS_CODE_NO_HEAD_AVAIL:
            print('\nTest 5 passed')
        if COORD_1['X'] == gpsObject.ERR_GPS_CODE_SMALL_BUFF_SZ and HEAD_1['Heading'] == gpsObject.ERR_GPS_CODE_SMALL_BUFF_SZ:
            print('\nTest 6 passed')

        gpsObject.stop_gps_data_retrieval(stream_number=1, msg_type='SBF')
        gpsObject.stop_thread_gps()

    elif gps_state == 'ON_ENOUGH_BUFF_SZ':
        # 2. Call all the functions after GPS on in outdoor, and buff size has enough entries, and heading is working properly
        gpsObject.serial_connect()
        #gpsObject.sendCommandGps(cmd='sga, MultiAntenna') # by default this is the command
        
        gpsObject.start_gps_data_retrieval(stream_number=1,  msg_type='SBF', interval='msec10', sbf_type='+PVTCartesian+AttEuler')
        gpsObject.start_thread_gps()
        
        time.sleep(1)
                
        COORD = gpsObject.get_last_sbf_buffer_info(what='Coordinates')
        HEAD = gpsObject.get_last_sbf_buffer_info(what='Heading')
        COORD_1, HEAD_1 = gpsObject.get_last_sbf_buffer_info(what='Both')

        if COORD['X'] != gpsObject.ERR_GPS_CODE_NO_COORD_AVAIL:
            print('\nTest 7 passed, ' + str(COORD['X']))
        if HEAD['Heading'] != gpsObject.ERR_GPS_CODE_NO_HEAD_AVAIL:
            print('\nTest 8 passed, ' + str(COORD['X']))
        if COORD_1['X'] != gpsObject.ERR_GPS_CODE_SMALL_BUFF_SZ and HEAD_1['Heading'] != gpsObject.ERR_GPS_CODE_SMALL_BUFF_SZ:
            print('\nTest 9 passed, ' + str(COORD_1['X']) + ' , ' + str(HEAD_1['Heading']))

        gpsObject.stop_gps_data_retrieval(stream_number=1, msg_type='SBF')
        gpsObject.stop_thread_gps()        
    
        
# Turn on all debugging verbose
mySeptentrioGPS = GpsSignaling(DBG_LVL_0=False, DBG_LVL_1=False, DBG_LVL_2=False)

which = 3

if which == 1 or which == 'all':
    input('For Tests 1,2,3: GPS must be OFF')
    test_get_last_sbf_buffer_info(mySeptentrioGPS,gps_state='off')
elif which == 2 or which == 'all':
    input('For Tests 4,5,6: GPS must be ON but indoor')
    test_get_last_sbf_buffer_info(mySeptentrioGPS,gps_state='ON_INDOOR')
elif which == 3 or which == 'all':
    input('For Tests 7,8,9: GPS must be ON and outdoor')
    test_get_last_sbf_buffer_info(mySeptentrioGPS,gps_state='ON_ENOUGH_BUFF_SZ')

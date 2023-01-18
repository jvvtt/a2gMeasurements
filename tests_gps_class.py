from a2gmeasurements import GpsSignaling
import time

def test_get_last_sbf_buffer_info(gpsObject, gps_state='off'):
    
    if gps_state == 'off':
        # 1. Call all the functions with the gps off
        COORD = gpsObject.get_last_sbf_buffer(what='Coordinates')
        HEAD = gpsObject.get_last_sbf_buffer(what='Heading')
        COORD_1, HEAD_1 = gpsObject.get_last_sbf_buffer(what='Both')
        
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
        
        COORD = gpsObject.get_last_sbf_buffer(what='Coordinates')
        HEAD = gpsObject.get_last_sbf_buffer(what='Heading')
        COORD_1, HEAD_1 = gpsObject.get_last_sbf_buffer(what='Both')

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
                
        COORD = gpsObject.get_last_sbf_buffer(what='Coordinates')
        HEAD = gpsObject.get_last_sbf_buffer(what='Heading')
        COORD_1, HEAD_1 = gpsObject.get_last_sbf_buffer(what='Both')

        if COORD['X'] != gpsObject.ERR_GPS_CODE_NO_COORD_AVAIL:
            print('\nTest 7 passed, ' + str(COORD['X']))
        if HEAD['Heading'] != gpsObject.ERR_GPS_CODE_NO_HEAD_AVAIL:
            print('\nTest 8 passed, ' + str(COORD['X']))
        if COORD_1['X'] != gpsObject.ERR_GPS_CODE_SMALL_BUFF_SZ and HEAD_1['Heading'] != gpsObject.ERR_GPS_CODE_SMALL_BUFF_SZ:
            print('\nTest 9 passed, ' + str(COORD_1['X']) + ' , ' + str(HEAD_1['Heading']))

        gpsObject.stop_gps_data_retrieval(stream_number=1, msg_type='SBF')
        gpsObject.stop_thread_gps()        
    
def test_multiple_streams(gpsObject):
    gpsObject.serial_connect()
    gpsObject.serial_instance.reset_input_buffer()
    time.sleep(0.1)

    #mySeptentrioGPS.sendCommandGps('erst, hard, PVTData')

    gpsObject.sendCommandGps(cmd='sga, MultiAntenna') # by default this is the command
    gpsObject.start_gps_data_retrieval(stream_number=1,  msg_type='SBF', interval='sec2', sbf_type='+PVTCartesian+AttEuler')
    gpsObject.start_gps_data_retrieval(stream_number=2,  msg_type='NMEA', interval='sec2', nmea_type='+GGA+HDT')

    gpsObject.start_thread_gps()

    input('\nFinish test? Press ENTER')

    gpsObject.stop_gps_data_retrieval(stream_number=1, msg_type='SBF')
    gpsObject.stop_gps_data_retrieval(stream_number=2, msg_type='NMEA')

    gpsObject.stop_thread_gps()

    print(len(gpsObject.SBF_frame_buffer), len(gpsObject.NMEA_buffer))
    if len(gpsObject.SBF_frame_buffer) > 0:
        print(gpsObject.SBF_frame_buffer[-10:])
    if len(gpsObject.NMEA_buffer) > 0:
        print(gpsObject.NMEA_buffer[-10:])    
        
        
# Turn on all debugging verbose
mySeptentrioGPS = GpsSignaling(DBG_LVL_2=True, DBG_LVL_0=True, DBG_LVL_1=True)

test_get_last_sbf_buffer_info(mySeptentrioGPS,gps_state='off')
test_get_last_sbf_buffer_info(mySeptentrioGPS,gps_state='ON_INDOOR')
test_get_last_sbf_buffer_info(mySeptentrioGPS,gps_state='ON_ENOUGH_BUFF_SZ')

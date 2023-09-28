from a2gmeasurements import GpsSignaling
import time

# Multiple streams
mySeptentrioGPS = GpsSignaling(DBG_LVL_2=True, DBG_LVL_0=True, DBG_LVL_1=True)

mySeptentrioGPS.serial_connect()
mySeptentrioGPS.serial_instance.reset_input_buffer()
time.sleep(0.1)
mySeptentrioGPS.stop_gps_data_retrieval(stream_number=1, msg_type='SBF')
#mySeptentrioGPS.sendCommandGps('erst, hard, PVTData')
time.sleep(1)
mySeptentrioGPS.sendCommandGps(cmd='sga, MultiAntenna') # by default this is the command
mySeptentrioGPS.start_gps_data_retrieval(stream_number=1,  msg_type='SBF', interval='sec2', sbf_type='+PVTCartesian+AttEuler')
mySeptentrioGPS.start_gps_data_retrieval(stream_number=2,  msg_type='NMEA', interval='sec2', nmea_type='+GGA+HDT')

mySeptentrioGPS.start_thread_gps()

input('\nFinish test? Press ENTER')

mySeptentrioGPS.stop_gps_data_retrieval(stream_number=1, msg_type='SBF')
mySeptentrioGPS.stop_gps_data_retrieval(stream_number=2, msg_type='NMEA')

mySeptentrioGPS.stop_thread_gps()

print(len(mySeptentrioGPS.SBF_frame_buffer), len(mySeptentrioGPS.NMEA_buffer))
if len(mySeptentrioGPS.SBF_frame_buffer) > 0:
    print(mySeptentrioGPS.SBF_frame_buffer[-10:])
if len(mySeptentrioGPS.NMEA_buffer) > 0:
    print(mySeptentrioGPS.NMEA_buffer[-10:])
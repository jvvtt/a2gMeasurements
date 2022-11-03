from a2gmeasurements import GpsSignaling
import time

# Multiple streams
str_nm = 2
msg_type = 'SBF'
mySeptentrioGPS = GpsSignaling(DBG_LVL_2=True)

mySeptentrioGPS.serial_connect()
mySeptentrioGPS.serial_instance.reset_input_buffer()
time.sleep(0.1)
#mySeptentrioGPS.sendCommandGps('erst, hard, PVTData')
mySeptentrioGPS.sendCommandGps(cmd='sga, MultiAntenna') # by default this is the command
mySeptentrioGPS.sendCommandGps('sdio, USB1,, -NMEA')
mySeptentrioGPS.start_gps_data_retrieval(stream_number=1,  msg_type=msg_type, interval='sec2')
mySeptentrioGPS.start_gps_data_retrieval(stream_number=2,  msg_type='NMEA', interval='sec5', nmea_type='HDT')
mySeptentrioGPS.start_gps_data_retrieval(stream_number=3,  msg_type='NMEA', interval='sec2', nmea_type='GGA')
mySeptentrioGPS.start_thread_gps()

input('')


mySeptentrioGPS.stop_gps_data_retrieval(stream_number=1, msg_type=msg_type)
mySeptentrioGPS.stop_gps_data_retrieval(stream_number=2, msg_type='NMEA')
mySeptentrioGPS.stop_gps_data_retrieval(stream_number=3, msg_type='NMEA')
mySeptentrioGPS.stop_thread_gps()

print(len(mySeptentrioGPS.SBF_frame_buffer), len(mySeptentrioGPS.NMEA_buffer))
if len(mySeptentrioGPS.SBF_frame_buffer) > 0:
    print(mySeptentrioGPS.SBF_frame_buffer[-5:])
if len(mySeptentrioGPS.NMEA_buffer) > 0:
    print(mySeptentrioGPS.NMEA_buffer[-5:])
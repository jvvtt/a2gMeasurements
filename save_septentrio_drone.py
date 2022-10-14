from a2gmeasurements import GpsSignaling
import json
mySeptentrioGPS = GpsSignaling(DBG_LVL_2=True)

mySeptentrioGPS.serial_connect()
mySeptentrioGPS.start_thread_gps()
mySeptentrioGPS.start_gps_data_retrieval(msg_type='NMEA', nmea_type='GGA', interval='sec1') # HDF instead of GGA for heading info

filename = 'save_septentrio_gps_coords_drone'
f = open(filename + '.json', 'a')
while(1):
    if mySeptentrioGPS.NMEA_buffer: 
        tmp = mySeptentrioGPS.NMEA_buffer[-1]
        to_save = json.dumps(tmp)
        f.write(to_save)    
f.close()
mySeptentrioGPS.stop_gps_data_retrieval(msg_type='NMEA')
mySeptentrioGPS.stop_thread_gps()
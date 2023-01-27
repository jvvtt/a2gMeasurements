from a2gmeasurements import HelperA2GMeasurements
import time

Naz = 6
meas_time = 3
filename = 'test_gps_and_gimbal_classes'

myHelper = HelperA2GMeasurements(ID='GROUND', SERVER_ADDRESS='0.0.0.0', DBG_LVL_0=True, DBG_LVL_1=True, IsGimbal=True, IsGPS=True, IsSignalGenerator=False, F0=None, L0=None, SPEED=None, GPS_Stream_Interval='sec1')

myHelper.az_rot_gnd_gimbal_toggle_sig_generator(Naz=Naz, meas_time=meas_time, filename=filename)

# Shutdown all streams
for stream in myHelper.mySeptentrioGPS.stream_info:
    myHelper.mySeptentrioGPS.stop_gps_data_retrieval(stream_number=stream['stream_number'], msg_type=stream['msg_type'])

# Stop threads
myHelper.mySeptentrioGPS.stop_thread_gps()
myHelper.myGimbal.stop_thread_gimbal()
time.sleep(0.01)
myHelper.myGimbal.actual_bus.shutdown()

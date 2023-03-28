from a2gmeasurements import HelperA2GMeasurements
import time

SERVER_ADDRESS = ''
ground_a2g_helper = HelperA2GMeasurements('GROUND', SERVER_ADDRESS, DBG_LVL_0=True, DBG_LVL_1=True, IsGPS=True, IsGimbal=True)
ground_a2g_helper.HelperStartA2GCom()


try:    
    while(True):
        ground_a2g_helper.socket_send_cmd(type_cmd='GETGPS')
    
        time.sleep(1)

except Exception as e:
  
    
    ground_a2g_helper.HelperA2GStopCom(DISC_WHAT='ALL')
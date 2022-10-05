import json
import numpy as np
from socket import socket
import time
from a2gmeasurements import HelperA2GMeasurements, GimbalRS2, GpsSignaling


continue_cond = True
input('Start test?')

host = 'localhost'
myHelper = HelperA2GMeasurements('DRONE', host, DBG_LVL_0=False, DBG_LVL_1=True)
myHelper.HelperStartA2GCom()
print('Starting CLIENT...')
time.sleep(1)

myHelper.socket.sendall(json.dumps('GET_GPS').encode())


while(continue_cond):
    if myHelper.SOCKET_BUFFER:
        print(myHelper.SOCKET_BUFFER[-1])
        continue_cond=False
    else:
        print('Nothing in Buffer')

input('Stopping test...')
myHelper.HelperA2GStopCom()
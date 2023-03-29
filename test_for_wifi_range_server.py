import json
import numpy as np
from socket import socket
import time
from a2gmeasurements import HelperA2GMeasurements, GimbalRS2, GpsSignaling

def dummy_fcn(sz):
    return np.sum(np.matmul(np.random.rand(sz,sz), np.random.rand(sz,sz)), axis=(0,1))

continue_cond = True
input('Start test?')

server_ip_addr = '0.0.0.0'
myHelper = HelperA2GMeasurements('GROUND', server_ip_addr, DBG_LVL_0=False, DBG_LVL_1=False)
myHelper.HelperStartA2GCom()
print('\nStarting SERVER...')
time.sleep(1)

size_to_compute = 1500
try:
    while(continue_cond):
        tmp = dummy_fcn(size_to_compute)
        data = 'Result of random matmul sum norm is ' + str(tmp)
        
        myHelper.socket_send_cmd(type_cmd='DEBUG_WIFI_RANGE', data=data)

        del tmp
except KeyboardInterrupt:
    pass

myHelper.HelperA2GStopCom()
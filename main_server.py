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
myHelper = HelperA2GMeasurements('GROUND', server_ip_addr, DBG_LVL_0=True, DBG_LVL_1=True)
myHelper.HelperStartA2GCom()
print('\nStarting SERVER...')
time.sleep(1)

size_to_compute = 2000
times_to_send = 0
try:
    while(continue_cond):
            
        # Main thread: calculate something expensive and based on a received parameter update computation
        sz = np.random.randint(size_to_compute, np.round(size_to_compute*(1.5)))
        tmp = dummy_fcn(sz)
        data = 'Result of random matmul sum norm is ' + str(tmp)
        
               
        if times_to_send == 20:
            myHelper.socket_send_cmd(type_cmd='DEBUG_WIFI_RANGE', data=data)
            print('\nPacket just sent')
        if (times_to_send >= 3) or (times_to_send > 30):
            print('Computed data: ', data)
        if times_to_send < 3:
            myHelper.socket_send_cmd(type_cmd='DEBUG_WIFI_RANGE', data=data)
            print('\nPacket just sent')
            
        times_to_send += 1
except KeyboardInterrupt:
    pass

input('Stopping test...')
myHelper.HelperA2GStopCom()
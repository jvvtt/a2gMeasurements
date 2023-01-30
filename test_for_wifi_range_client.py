import json
import numpy as np
from socket import socket
import time
from a2gmeasurements import HelperA2GMeasurements, GimbalRS2, GpsSignaling

def dummy_fcn(sz):
    return np.sum(np.matmul(np.random.rand(sz,sz), np.random.rand(sz,sz)), axis=(0,1))

continue_cond = True
input('Start test?')

server_ip_addr = '192.168.0.2'
myHelper = HelperA2GMeasurements('DRONE', server_ip_addr, DBG_LVL_0=False, DBG_LVL_1=True)
myHelper.HelperStartA2GCom()
print('\nStarting CLIENT...')
time.sleep(1)

size_to_compute = 2000
while(continue_cond):
    # Ask for gps coordinates each certain time
    frame_to_send = myHelper.build_a2g_frame(type_frame='cmd', cmd='GETGPS')
    myHelper.socket.sendall(frame_to_send.encode())
    
    # Main thread: calculate something expensive and based on a received parameter update computation
    sz = np.random.randint(size_to_compute, np.round(size_to_compute*(1.5)))
    tmp = dummy_fcn(sz)
    del tmp


input('Stopping test...')
myHelper.HelperA2GStopCom()
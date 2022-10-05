import json
import numpy as np
from socket import socket
import time
from a2gmeasurements import HelperA2GMeasurements, GimbalRS2, GpsSignaling

input('Start Experiment?')

host = 'localhost'
myHelper = HelperA2GMeasurements('GROUND', host, DBG_LVL_0=False, DBG_LVL_1=True, IsGPS=True, IsGimbal=True)
myHelper.HelperStartA2GCom()
print('Starting SERVER...')
time.sleep(1)

#

input('Stop test?')
myHelper.HelperA2GStopCom()
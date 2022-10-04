from socket import socket
import time
from a2gmeasurements import HelperA2GMeasurements

host = 'localhost'
myHelper = HelperA2GMeasurements('GROUND', host, DBG_LVL_0=False, DBG_LVL_1=True)
myHelper.HelperStartA2GCom()

input('Whenever want to stop, press enter')
myHelper.HelperA2GStopCom()
#print(myHelper.SOCKET_BUFFER, len(myHelper.SOCKET_BUFFER))
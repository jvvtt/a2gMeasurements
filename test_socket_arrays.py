from a2gmeasurements import HelperA2GMeasurements, RepeatTimer, NumpyArrayEncoder
from json import JSONEncoder
import time
import numpy as np

GND_ADDRESS = '192.168.175.234'
myhelpera2g = HelperA2GMeasurements('DRONE', GND_ADDRESS, DBG_LVL_0=False, DBG_LVL_1=False)
myhelpera2g.HelperStartA2GCom()

time.sleep(1)

while(1):
    try:
        data = np.random.rand(10,32)
        myhelpera2g.socket_send_cmd(type_cmd='SETIRF', data=data)
        time.sleep(1)
    except Exception as e:
        myhelpera2g.HelperA2GStopCom()
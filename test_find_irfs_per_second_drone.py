from a2gmeasurements import RFSoCRemoteControlFromHost
import time 
import numpy as np
import datetime

myrfsoc = RFSoCRemoteControlFromHost()
myrfsoc.set_rx_rf()

myrfsoc.hest = []
nbeams = 64
nbytes = 2
nread = 1024
nbytes = nbeams * nbytes * nread * 2 # Beams x SubCarriers(delay taps) x 2Bytes from  INT16 x 2 frpm Real and Imaginary

cnt = 0
while(1):
    start_time = time.time()
    myrfsoc.radio_control.sendall(b"receiveSamples")    
    buf = bytearray()

    while len(buf) < nbytes:
        data = myrfsoc.radio_data.recv(nbytes)
        buf.extend(data)

    data = np.frombuffer(buf, dtype=np.int16)
    rxtd = data[:nread*nbeams] + 1j*data[nread*nbeams:]
    rxtd = rxtd.reshape(nbeams, nread)

    stop_time = time.time()
    
    start_unnecessary = time.time()
    myrfsoc.hest.append(rxtd)
    cnt = cnt + 1
    print("Time: ", stop_time - start_time, ", LOOP CNT: ", cnt)
    stop_unnecessary = time.time()
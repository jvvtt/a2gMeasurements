from a2gmeasurements import RFSoCRemoteControlFromHost
import time 
import numpy as np
import datetime
import threading
class RepeatTimer(threading.Timer):  
    def run(self):  
        while not self.finished.wait(self.interval):  
            self.function(*self.args,**self.kwargs)
            
myrfsoc = RFSoCRemoteControlFromHost()
myrfsoc.set_rx_rf()

myrfsoc.hest = []
nbeams = 64
nbytes = 2
nread = 1024
nbytes = nbeams * nbytes * nread * 2 # Beams x SubCarriers(delay taps) x 2Bytes from  INT16 x 2 frpm Real and Imaginary

txtd = np.load('FPGA/txtd.npy') # self.wideband()
txtd /= np.max([np.abs(txtd.real), np.abs(txtd.imag)])
txfd = np.fft.fft(txtd)
txtd *= 2**13-1

cnt = 0
my_data_buffer = []
hest = []
accum_time = 0
def receive_signal_async():
    global accum_time
    global cnt
    start_time = time.time()
    myrfsoc.radio_control.sendall(b"receiveSamples")    
    buf = bytearray()

    while len(buf) < nbytes:
        data = myrfsoc.radio_data.recv(nbytes)
        buf.extend(data)

    my_data_buffer.append(np.frombuffer(buf, dtype=np.int16))
    accum_time = accum_time + time.time() - start_time
    cnt = cnt + 1

timer_rx_irf = RepeatTimer(0.2, receive_signal_async)
timer_rx_irf.start()

while(1):
    try:
        if len(my_data_buffer) >= 20:  # At 20MB reset the local data buffer and call the function to do expensive computations
            for frame in my_data_buffer:
                rxtd = frame[:nread*nbeams] + 1j*frame[nread*nbeams:]
                rxtd = rxtd.reshape(nbeams, nread)
            
                rxfd = np.fft.fft(rxtd, axis=1)
                Hest = rxfd * np.conj(txfd)
                hest.append(np.fft.ifft(Hest, axis=1))
                    
            hest = np.stack(hest, axis=0)
            
            datestr = "".join([str(i) + '-' for i in datetime.datetime.utcnow().timetuple()[0:6]])
            
            with open('TEST_IRFS_HZ_' + datestr + '.npy', 'wb') as f:
                np.save(f, hest)
            
            print("Saved hest")
                
            my_data_buffer = []
            hest = []
            
            print("Avg time irf: ", accum_time/cnt)
            accum_time = 0
            cnt = 0
            
    except KeyboardInterrupt:
        print("Interrupted by user")
        timer_rx_irf.cancel()
    
import socket
import time
import numpy as np
import threading
from timeit import default_timer as timer


def dummy_fcn(sz):
    return np.sum(np.matmul(np.random.rand(sz,sz), np.random.rand(sz,sz)), axis=(0,1))

def receive(stop_event, sock):
    while not stop_event.is_set():
        data = sock.recv(1024)
        data = data.decode()
        if data:
            print(data)

server_ip = '192.168.0.2' # Server IP address
port = 10000

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((server_ip, port))

print('\nCLIENT connected to server')

time.sleep(1)
event_stop_thread = threading.Event()
myThread = threading.Thread(target=receive, args=(event_stop_thread, sock))
myThread.start()

print('\nEntering main CLIENT thread')

#sock.sendall(HTTP_msg.encode())

try:    
    while(True):
    # Faster task than server side
        sz = np.random.randint(5000, 6000)
        start = timer()
        tmp = dummy_fcn(sz)
        del tmp
        
        msg = 'Computing time of CLIENT task is: ' + str(timer() - start)
                
        sock.sendall(msg.encode())           
        print('\nCLIENT messages sent')
    
except KeyboardInterrupt:
    event_stop_thread.set()
    sock.close()
        
import socket
import time
import numpy as np
import threading
from timeit import default_timer as timer

# Time consuming task
def dummy_fcn(sz):
    return np.sum(np.matmul(np.random.rand(sz,sz), np.random.rand(sz,sz)), axis=(0,1))

def receive(stop_event, sock):
    while not stop_event.is_set():
        data = sock.recv(1024)
        data = data.decode()
        if data:
            print(data)

ip_addr = 'localhost'
port = 10000

serverSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serverSock.bind((ip_addr, port))
print('\nSERVER bound')

serverSock.listen()

(clientConn, clientAddr) = serverSock.accept()
print(f'\nSERVER accepted connection of {clientAddr}')

time.sleep(3)

event_stop_thread = threading.Event()
myThread = threading.Thread(target=receive, args=(event_stop_thread, clientConn))
myThread.start()

print('\nEntering main SERVER thread')

try:    
    # Heavy task with some randomness
    while(True):
        sz = np.random.randint(8000, 9000)
        start = timer()
        tmp = dummy_fcn(sz)
        del tmp
        
        msg = 'Computing time of SERVER task is: ' + str(timer() - start)
                
        clientConn.sendall(msg.encode())           
        print('\nSERVER messages sent')

except KeyboardInterrupt:
    event_stop_thread.set()
    serverSock.close()
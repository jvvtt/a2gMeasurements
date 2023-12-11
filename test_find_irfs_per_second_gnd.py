from a2gmeasurements import RFSoCRemoteControlFromHost
import time 
import numpy


myrfsoc = RFSoCRemoteControlFromHost(rfsoc_static_ip_address='10.1.1.30')
myrfsoc.transmit_signal()
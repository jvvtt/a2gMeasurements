import time
from GimbalRS2 import GimbalRS2
import can
import threading
from pynput import keyboard

gc = GimbalRS2()
gc.cntBytes = 0

with can.interface.Bus(interface="pcan", channel="PCAN_USBBUS1", bitrate=1000000) as bus:
    gc.actual_bus = bus

    stop_event = threading.Event()
    t_receive = threading.Thread(target=gc.receive, args=(bus, stop_event))
    t_receive.start()

    # Starts the keyboard listener
    listener = keyboard.Listener(on_press=gc.on_press, on_release=gc.on_release)
    listener.start()

    # Let's make sure we can stop the loop through CTRL + C, in case there is any bug we don't know
    try:
        while(gc.MAIN_LOOP_STOP):
            time.sleep(0)  # yield
    except KeyboardInterrupt:
        pass  # exit normally

    stop_event.set()
    time.sleep(0.5)
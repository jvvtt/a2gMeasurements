from a2gmeasurements import SBUSEncoder
import numpy as np
import time

list_of_channels = {'MODE': 5, 'TILT': 2, 'ROLL': 4, 'PAN': 1, 'TILT_SPEED': 9, 'PAN_SPEED': 10}


def test_modechannel_sbus(sbus_obj):
    
    # Do three rounds
    for i in range(1):
    
        sbus_obj.update_channel(channel=5, value=-100)
        print('\nChannel MODE in state 1')
        time.sleep(5)
        sbus_obj.update_channel(channel=5, value=0)
        print('\nChannel MODE in state 2')
        time.sleep(5)
        sbus_obj.update_channel(channel=5, value=100)
        print('\nChannel MODE in state 3')
        time.sleep(5)
        
def test_mov_channels(sbus_obj, ch):
    
    print('\nUpdate channel: ', ch)
    sbus_obj.update_channel(channel=ch, value=-50)
    time.sleep(2)
    sbus_obj.update_channel(channel=ch, value=-30)
    time.sleep(2)
    sbus_obj.update_channel(channel=ch, value=-10)
    time.sleep(2)

sbus = SBUSEncoder()

serial_interface = input('Type serial interface:\n')
print(serial_interface)

sbus.start_sbus(serial_interface=serial_interface)

time.sleep(3)

test_modechannel_sbus(sbus_obj=sbus)

test_mov_channels(sbus_obj=sbus, ch=1)
test_mov_channels(sbus_obj=sbus, ch=2)
test_mov_channels(sbus_obj=sbus, ch=4)


print('\nEnd of tests')
sbus.stop_updating()

    
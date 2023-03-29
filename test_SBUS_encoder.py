from a2gmeasurements import SBUSEncoder
import numpy as np
import time

list_of_channels = {'MODE': 5, 'TILT': 2, 'ROLL': 4, 'PAN': 1, 'TILT_SPEED': 9, 'PAN_SPEED': 10}


sbus = SBUSEncoder()

serial_interface = input('\nType serial interface:')
print(serial_interface)

sbus.start_sbus(serial_interface=serial_interface)

time.sleep(3)

# Manual test with oscilloscope
val_ail = -100
sbus.update_channel(channel=1, value=val_ail)
sbus.update_channel(channel=2, value=3)
input('\nCheck A value' + str(val_ail) +  ' in oscilloscope: ')

val_ail = -50
sbus.update_channel(channel=1, value=val_ail)
sbus.update_channel(channel=2, value=3)
input('\nCheck A value' + str(val_ail) +  ' in oscilloscope: ')

val_ail = 50
sbus.update_channel(channel=1, value=val_ail)
sbus.update_channel(channel=2, value=3)
input('\nCheck A value' + str(val_ail) +  ' in oscilloscope: ')

val_ail = 100
sbus.update_channel(channel=1, value=100)
sbus.update_channel(channel=2, value=3)
input('\nCheck A value' + str(val_ail) +  ' in oscilloscope: ')

print('\nEnd of tests')
sbus.stop_updating()

    
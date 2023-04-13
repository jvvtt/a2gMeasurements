from a2gmeasurements import SBUSEncoder
import numpy as np
import time

list_of_channels = {'MODE': 5, 'TILT': 2, 'ROLL': 4, 'PAN': 1, 'TILT_SPEED': 9, 'PAN_SPEED': 10}


def not_move_command(sbus):
    '''
    Update the channel so that it does not continue moving

    '''
    
    sbus.update_channel(channel=1, value=0)
    sbus.update_channel(channel=2, value=0)
    sbus.update_channel(channel=3, value=0)
    sbus.update_channel(channel=4, value=0)
    sbus.update_channel(channel=5, value=0)
    #time.sleep(0.1)

def test_Y_axis(sbus, ail, mov_time):
    '''
    Test the roll axis speed

    '''

    sbus.update_channel(channel=1, value=ail)
    sbus.update_channel(channel=2, value=0)
    sbus.update_channel(channel=3, value=0)
    sbus.update_channel(channel=4, value=0)
    sbus.update_channel(channel=5, value=0)
    time.sleep(mov_time)
    not_move_command(sbus)


def test_Z_axis(sbus, ele, mov_time):
    '''
    Test the pitch axis speed

    '''
    
    sbus.update_channel(channel=1, value=0)
    sbus.update_channel(channel=2, value=ele)
    sbus.update_channel(channel=3, value=0)
    sbus.update_channel(channel=4, value=0)
    sbus.update_channel(channel=5, value=0)
    time.sleep(mov_time)
    not_move_command(sbus)

def test_pan_axis(sbus, rud, mov_time):
    '''
    Test the pan axis speed
    '''
    
    sbus.update_channel(channel=1, value=0)
    sbus.update_channel(channel=2, value=0)
    sbus.update_channel(channel=3, value=0)
    sbus.update_channel(channel=4, value=rud)
    sbus.update_channel(channel=5, value=0)
    time.sleep(mov_time)
    not_move_command(sbus)


sbus = SBUSEncoder()

serial_interface = input('\nType serial interface:')
print(serial_interface)

sbus.start_sbus(serial_interface=serial_interface, period_packet=0.007)

time.sleep(3)

###### CHANGE FROME HERE ########

'''
rud = -20
mov_time_pan_axis = 20
test_pan_axis(sbus, rud, mov_time_pan_axis)
input('\nPress ENTER to continue to the next test')
'''

ele = 20
mov_time_elevation_axis = 5
test_Z_axis(sbus, ele, mov_time_elevation_axis)
#input('\nPress ENTER to continue to the next test')


#### UNTIL HERE YOU CAN CHANGE #######
print('\nEnd of tests')
sbus.stop_updating()

    
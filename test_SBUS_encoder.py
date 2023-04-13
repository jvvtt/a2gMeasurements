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

def test_speed_Y_axis(sbus, ail, mov_time):
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


def test_speed_Z_axis(sbus, ele, mov_time):
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

def test_speed_pan_axis(sbus, rud, mov_time):
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

sbus.start_sbus(serial_interface=serial_interface)

time.sleep(3)

###### CHANGE FROME HERE ########

########
val_ail = -30
val_ele = 0
val_rud = 0
sbus.update_channel(channel=1, value=val_ail)
sbus.update_channel(channel=2, value=val_ele)
sbus.update_channel(channel=3, value=-100)
sbus.update_channel(channel=4, value=val_rud)
sbus.update_channel(channel=5, value=0)
time.sleep(2)
not_move_command(sbus)

input('\nAIL: ' + str(val_ail) + ', ELE: ' + str(val_ele) + ', RUD: ' + str(val_rud) + '... CHECK:')

#########
val_ail = -20
val_ele = 0
val_rud = 0
sbus.update_channel(channel=1, value=val_ail)
sbus.update_channel(channel=2, value=val_ele)
sbus.update_channel(channel=3, value=-100)
sbus.update_channel(channel=4, value=val_rud)
sbus.update_channel(channel=5, value=0)
time.sleep(2)
not_move_command(sbus)

input('\nAIL: ' + str(val_ail) + ', ELE: ' + str(val_ele) + ', RUD: ' + str(val_rud) + '... CHECK:')

###########
val_ail = -10
val_ele = 0
val_rud = 0
sbus.update_channel(channel=1, value=val_ail)
sbus.update_channel(channel=2, value=val_ele)
sbus.update_channel(channel=3, value=-100)
sbus.update_channel(channel=4, value=val_rud)
sbus.update_channel(channel=5, value=0)
time.sleep(2)
not_move_command(sbus)

input('\nAIL: ' + str(val_ail) + ', ELE: ' + str(val_ele) + ', RUD: ' + str(val_rud) + '... CHECK:')


########
val_ail = 10
val_ele = 0
val_rud = 0
sbus.update_channel(channel=1, value=val_ail)
sbus.update_channel(channel=2, value=val_ele)
sbus.update_channel(channel=3, value=-100)
sbus.update_channel(channel=4, value=val_rud)
sbus.update_channel(channel=5, value=0)
time.sleep(2)
not_move_command(sbus)

input('\nAIL: ' + str(val_ail) + ', ELE: ' + str(val_ele) + ', RUD: ' + str(val_rud) + '... CHECK:')

#### COPY AND PASTE CODE SECTION HERE #######



#### UNTIL HERE YOU CAN CHANGE #######
print('\nEnd of tests')
sbus.stop_updating()

    
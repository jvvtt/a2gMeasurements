from a2gmeasurements import SBUSEncoder
import numpy as np
import time

list_of_channels = {'MODE': 5, 'TILT': 2, 'ROLL': 4, 'PAN': 1, 'TILT_SPEED': 9, 'PAN_SPEED': 10}

def ctrl_H16_position(sbus):
    
    condition = True
    
    while(condition):
        ele =  input('ENTER elevation speed: ')
        rud = input('ENTER pan speed: ')
        mov_time = input('ENTER time: ')
            
        ele = float(ele)
        rud = float(rud)
        mov_time = float(mov_time)
        
        sbus.move_gimbal(ele, rud, mov_time)
        
        finish = input('Has it finished?: ')
        
        if finish == 'YES' or finish == 'Yes' or finish == 'yes' or finish == 'Y' or finish == 'y':
            condition = False
    
sbus = SBUSEncoder()

serial_interface = input('\nType serial interface:')
print(serial_interface)

sbus.start_sbus(serial_interface=serial_interface, period_packet=0.007)

time.sleep(3)

ctrl_H16_position(sbus)

experiment_not_finish = True

rud = 0
while(experiment_not_finish):
    ele = input('ENTER elevation speed: ')
    ele = float(ele)
    
    condition = True
    while(condition):       
        print('\nACTUAL ELEVATION: ' + str(ele)) 
        mov_time = input('ENTER time: ')
        mov_time = float(mov_time)
        
        sbus.move_gimbal(ele, rud, mov_time)
        
        finnish = input('Time founded?: ')
        
        if finnish == 'YES' or finnish == 'Yes' or finnish == 'yes' or finnish  == 'Y' or finnish == 'y':
            condition = False
        if finnish == 'NO' or finnish == 'No' or finnish =='no' or finnish == 'N' or finnish == 'n':
            ctrl_H16_position(sbus)
    
    finish_experiment = input('Finish experiment?: ')
    
    if finish_experiment == 'YES' or finish_experiment == 'Yes' or finish_experiment == 'yes' or finish_experiment == 'Y' or finish_experiment == 'y':
        experiment_not_finish = False
                    
print('\nEnd of tests')
sbus.stop_updating()

    
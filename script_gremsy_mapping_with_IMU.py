from a2gmeasurements import GimbalGremsyH16, SBUSEncoder
import numpy as np
import time

gh16 = GimbalGremsyH16()

gh16.start_conn()

speeds = [-5,-4,-3, 10, 11, 12]

speed_time_yaw_table = []
for speed_yaw in speeds:
    for time_yaw_2_move in range(1, 7):
        print(f"SPEED: {speed_yaw}, TIME: {time_yaw_2_move}")
        
        gh16.sbus.move_gimbal(0, speed_yaw, time_yaw_2_move)
        
        start_time = time.time()
        
        yaw_before = 1000 # Set it high for first iteration
        pitch_before = 1000 # Set it high for first iteration
        cnt = gh16.cnt_imu_readings
        DONT_STOP = True        
        
        while(DONT_STOP):
            if cnt != gh16.cnt_imu_readings:
                yaw = gh16.last_imu_reading['YAW']
                pitch = gh16.last_imu_reading['PITCH']
                
                if yaw - yaw_before <= 1:
                    CONDITION_YAW_SATISFIED = True
                else:
                    CONDITION_YAW_SATISFIED = False
                    
                if pitch - pitch_before <= 1:
                    CONDITION_PITCH_SATISFIED = True
                else:
                    CONDITION_PITCH_SATISFIED = False
                
                if CONDITION_YAW_SATISFIED and CONDITION_PITCH_SATISFIED:
                    break        
            
                yaw_before = yaw
                pitch_before = pitch
                cnt = gh16.cnt_imu_readings
        
        print(f"TIME UNTIL GIMBAL STOPS: {time.time() - start_time}")        
        speed_time_yaw_table.append([speed_yaw, time_yaw_2_move, yaw - float(gh16.home_position['YAW'])])
        time.sleep(1)

gh16.stop_conn()

print(speed_time_yaw_table)
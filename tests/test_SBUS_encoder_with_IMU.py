from a2gmeasurements import GimbalGremsyH16
import numpy as np


save_pos_azs_imu = {'MOVED_YAW': [], 'TIME': [], 'SPEED': 0}
save_neg_azs_imu = {'MOVED_YAW': [], 'TIME': [], 'SPEED': 0}
save_pos_eles_imu = {'MOVED_PITCH': [], 'TIME': [], 'SPEED': 0}
save_neg_eles_imu = {'MOVED_PITCH': [], 'TIME': [], 'SPEED': 0}

myGimbal = GimbalGremsyH16()
myGimbal.start_conn()

start_yaw_imu = input("Write starting YAW in IMU: ")
start_el_imu = input("Write starting PTICH in IMU: ")
az_imu = start_yaw_imu
el_imu = start_el_imu

input("Start rotating in NEG RUD / POS YAW")

ele = 0
rud = [-15, 20]
mov_time = [2, 3, 4, 5, 6, 7]

save_pos_azs_imu['SPEED'] = rud[0]
for t in mov_time:
    myGimbal.sbus.move_gimbal(ele, rud[0], t)
    print("ACTUAL TIME of MOV: ", t, ", ACTUAL AZ: ", rud[0])
        
    before_az_imu = az_imu
    az_imu = input("Write YAW value in IMU: ")
    save_pos_azs_imu['MOVED_YAW'].append(float(az_imu) - float(before_az_imu))
    save_pos_azs_imu['TIME'].append(t)
        
input("Start rotating in POS RUD / NEG YAW")
save_neg_azs_imu['SPEED'] = rud[1]
for t in mov_time:
    myGimbal.sbus.move_gimbal(ele, rud[1], t)
    print("ACTUAL TIME of MOV: ", t, ", ACTUAL AZ: ", rud[1])
        
    before_az_imu = az_imu
    az_imu = input("Write YAW value in IMU: ")
    save_neg_azs_imu['MOVED_YAW'].append(float(az_imu) - float(before_az_imu))
    save_neg_azs_imu['TIME'].append(t)

input("Start rotating in NEG ELE")

ele = [-5, 15]
rud = 0
mov_time = [3, 4, 5, 6]
save_neg_eles_imu['SPEED'] = ele[0]
for t in mov_time:
    myGimbal.sbus.move_gimbal(ele[0], rud, t)
    print("ACTUAL TIME of MOV: ", t, ", ACTUAL ELE: ", ele[0])
        
    before_el_imu = el_imu
    el_imu = input("Write ELE value in IMU: ")
    save_pos_eles_imu['MOVED_PITCH'].append(float(el_imu) - float(before_el_imu))
    save_pos_eles_imu['TIME'].append(t)

ele = [-5, 15]
rud = 0
mov_time = [3, 4, 5, 6]
save_pos_eles_imu['SPEED'] = ele[1]
for t in mov_time:
    myGimbal.sbus.move_gimbal(ele[1], rud, t)
    print("ACTUAL TIME of MOV: ", t, ", ACTUAL ELE: ", ele[1])
        
    before_el_imu = el_imu
    el_imu = input("Write ELE value in IMU: ")
    save_neg_eles_imu['MOVED_PITCH'].append(float(el_imu) - float(before_el_imu))
    save_neg_eles_imu['TIME'].append(t)

print(save_pos_azs_imu)
print(save_neg_azs_imu)
print(save_pos_eles_imu)
print(save_neg_eles_imu)

myGimbal.stop_thread_gimbal()
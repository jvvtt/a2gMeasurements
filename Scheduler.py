from datetime import datetime
from a2gmeasurements import RFSoCRemoteControlFromHost, GimbalRS2
import numpy as np

battery_drop_ratio = 4.5 / 50
conservative_speed_drone_gimbal = 30 # in deg/s
speed_drone_gimbal = conservative_speed_drone_gimbal # let's assume a conservative speed for the gimbal
speed_gnd_gimbal = speed_drone_gimbal # both nodes use the same gimbal

drone_node_rfsoc_static_ip_address='10.1.1.40'
gnd_node_rfsoc_static_ip_address='10.1.1.30'

gnd_msg_data = {"carrier_freq": 57.51e9,
                "rx_gain_ctrl_bb1": 0x00,
                "rx_gain_ctrl_bb2": 0x00,
                "rx_gain_ctrl_bb3": 0x00,
                "rx_gain_ctrl_bfrf": 0x00}

rfsoc = RFSoCRemoteControlFromHost(rfsoc_static_ip_address=drone_node_rfsoc_static_ip_address)
gimbal = GimbalRS2()

gimbal.start_thread_gimbal()

# Software operator actions
SOFTWARE_OPERATOR_ACTIONS = {
    "NUMBER_ACTIONS": 4,
    "START_RF": {
      "NAME": "Start RF",
      "SHORT": "RX listening incoming signals",
      "PRESET_DURATION": 5,
      "CALLBACK": lambda kwargs:rfsoc.start_thread_receive_meas_data(**kwargs)},
    "STOP_RF": {
      "NAME": "Stop RF",
      "SHORT": "RX stops listening incoming signals",
      "PRESET_DURATION": 5,
      "CALLBACK": lambda kwargs: rfsoc.stop_thread_receive_meas_data(**kwargs)}, # Passed as kwargs, must passed the correct keywords
    "MOVE_DRONE_GIMBAL": {
      "NAME": "Move drone gimbal",
      "SHORT": "Rotate yaw and pitch of gimbal",
      "SPEED_DRONE_GIMBAL": speed_drone_gimbal,
      "PRESET_DURATION": lambda ang: ang / speed_drone_gimbal,
      "CALLBACK": lambda kwargs: gimbal.setPosControl(**kwargs)},
    "MOVE_GND_GIMBAL": {
      "NAME": "Move gnd gimbal",
      "SHORT": "Rotate yaw and pitch of gimbal",
      "SPEED_GND_GIMBAL": speed_gnd_gimbal,
      "PRESET_DURATION": lambda ang: ang / speed_gnd_gimbal,
      "CALLBACK": lambda kwargs: gimbal.setPosControl(**kwargs)}}

# Each specific schedule is loaded from the file produced by the Scheduler planner at the page "https://jvvtt.github.io/wireless-meas-planner/"

# Define the start time of experiment
print(f"Time now is: {datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}")

start_time = input('ENTER MEASUREMENT START TIME IN FORMAT: HH-MM-SS. i.e.: 9-6-0')
start_time = [int(i) for i in start_time.split('-')]

software_operator_schedule = [{"ACTION": "MOVE_GND_GIMBAL",
                               "START_TIME": [22,54,47], 
                               "CALLBACK_PARAMS": {"yaw": 457, "roll": 0, "pitch": -124 }},
                              {"ACTION": "START_RF", 
                               "START_TIME":[22,55,1], 
                               "CALLBACK_PARAMS": {"msg_data":gnd_msg_data}}]

# Scheduler loop
for action_dict in software_operator_schedule:
    while (True):    
        date_time_now = datetime.now()
        hour = date_time_now.hour
        minute = date_time_now.minute
        second = date_time_now.second
        
        if ((action_dict["START_TIME"][0] == hour) & 
            (action_dict["START_TIME"][1] == minute) & 
            (np.abs(action_dict["START_TIME"][2] - second) < min_action_preset_time)):
          
            # Time to act: MUST provide the correct keyword/value pairs (in action_dict["CALLBACK_PARAMS"]) for the function
            SOFTWARE_OPERATOR_ACTIONS[action_dict["ACTION"]]["CALLBACK"](action_dict["CALLBACK_PARAMS"])
            break

gimbal.stop_thread_gimbal()
rfsoc.finish_measurement()

"""
THIS WORKS
import time
import numpy as np

def print_time(time):
  print(f"I'm printing this at: {time}")

actions_time = [[19,35,00], [19,35,30], [19,36,4], [19,36,44]]

for scheduled_time in actions_time:  
  while(True):
    this_time = datetime.datetime.now()
    hour = this_time.hour
    minute = this_time.minute
    second = this_time.second
    print(f"Check: {int(hour)==scheduled_time[0]}, {int(minute)==scheduled_time[1]}, {np.abs(int(second)-scheduled_time[2])<2}")
    
    if ((int(hour)==scheduled_time[0]) & (int(minute)==scheduled_time[1]) & (np.abs(int(second)-scheduled_time[2])<2)):
      print_time(this_time)
      break
    else:
      time.sleep(0.5)

"""
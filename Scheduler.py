from datetime import datetime
from a2gmeasurements import RFSoCRemoteControlFromHost, GimbalRS2

start_meas_date = ""
start_meas_time = ""
min_action_preset_time = 2

battery_drop_ratio = 4.5 / 50
conservative_speed_drone_gimbal = 30; # in deg/s
speed_drone_gimbal = conservative_speed_drone_gimbal; # let's assume a conservative speed for the gimbal
speed_gnd_gimbal = speed_drone_gimbal; # both nodes use the same gimbal

rfsoc = RFSoCRemoteControlFromHost()
gimbal = GimbalRS2()
gnd_msg_data = []
keep_scheduler_alive = True

# Software operator actions
SOFTWARE_OPERATOR_ACTIONS = {
    "NUMBER_ACTIONS": 4,
    "START_RF": {
      "NAME": "Start RF",
      "SHORT": "RX listening incoming signals",
      "PRESET_DURATION": 5,
      "CALLBACK": lambda config:rfsoc.start_thread_receive_meas_data(config)},
    "STOP_RF": {
      "NAME": "Stop RF",
      "SHORT": "RX stops listening incoming signals",
      "PRESET_DURATION": 5,
      "CALLBACK": lambda x: rfsoc.stop_thread_receive_meas_data()},
    "MOVE_DRONE_GIMBAL": {
      "NAME": "Move drone gimbal",
      "SHORT": "Rotate yaw and pitch of gimbal",
      "SPEED_DRONE_GIMBAL": speed_drone_gimbal,
      "PRESET_DURATION": lambda ang: ang / speed_drone_gimbal,
      "CALLBACK": lambda yaw, pitch: gimbal.setPosControl(yaw, 0, pitch)},
    "MOVE_GND_GIMBAL": {
      "NAME": "Move gnd gimbal",
      "SHORT": "Rotate yaw and pitch of gimbal",
      "SPEED_GND_GIMBAL": speed_gnd_gimbal,
      "PRESET_DURATION": lambda ang: ang / speed_gnd_gimbal,
      "CALLBACK": lambda yaw, pitch: gimbal.setPosControl(yaw, 0, pitch)}}

# Software operator schedule example for ground node
# Actions should be 
software_operator_schedule = [{"ACTION": "MOVE_GND_GIMBAL", "START_TIME": [22,54,47], "STOP_TIME":[22,55,1], "CALLBACK_PARAMS": {}},
                              {"ACTION": "START_RF", "START_TIME":[22,55,1], "STOP_TIME":[22,56,10], "CALLBACK_PARAMS": {}}]

actions_done = [False]*len(software_operator_schedule)

while (keep_scheduler_alive):
    date_time_now = datetime.now()
    
    # All these are ints
    # year = date_time_now.year month = date_time_now.month day = date_time_now.day
    hour = date_time_now.hour
    minute = date_time_now.minute
    second = date_time_now.second

    # Scheduler loop
    for action_dict, cnt in enumerate(software_operator_schedule):
        if ((action_dict["START_TIME"][0] == hour) & 
            (action_dict["START_TIME"][1] == minute) & 
            (abs(action_dict["START_TIME"][2] - second) < min_action_preset_time)):
            # Time to act
            SOFTWARE_OPERATOR_ACTIONS[action_dict["ACTION"]]["CALLBACK"](action_dict["CALLBACK_PARAMS"])

            # Write down actions done
            actions_done[cnt] = True
        
    if (all(actions_done)):
        keep_scheduler_alive = False
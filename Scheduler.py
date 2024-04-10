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

gnd_msg_data = {"carrier_freq": 59.5e9,
                "rx_gain_ctrl_bb1": 2,
                "rx_gain_ctrl_bb2": 1,
                "rx_gain_ctrl_bb3":1,
                "rx_gain_ctrl_bfrf":1}
keep_scheduler_alive = True

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
# If no file is available to load, a preset file will be loaded.
# Software operator schedule example for ground node
# EACH ACTION SHOULD DO A SPECIFIC PROCEDURE (i.e):
# The "STOP_RF" action will stop the action initiated by the "START_RF" action. 
# Until the "START_TIME" of "STOP_RF" action hasn't come yet, the measurement will continue.
software_operator_schedule = [{"ACTION": "MOVE_GND_GIMBAL", "START_TIME": [22,54,47], "CALLBACK_PARAMS": {"yaw": 457, "roll": 0, "pitch": -124 }},
                              {"ACTION": "START_RF", "START_TIME":[22,55,1], "CALLBACK_PARAMS": {"msg_data":gnd_msg_data}}]

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
          
            # Time to act: MUST provide the correct keyword/value pairs (in action_dict["CALLBACK_PARAMS"]) for the function
            SOFTWARE_OPERATOR_ACTIONS[action_dict["ACTION"]]["CALLBACK"](action_dict["CALLBACK_PARAMS"])

            # Write down actions done
            actions_done[cnt] = True
    
    # Finish scheduler loop if all actions where done
    if (all(actions_done)):
        keep_scheduler_alive = False
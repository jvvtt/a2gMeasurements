from a2gmeasurements import GimbalRS2, RFSoCRemoteControlFromHost
import time
import questionary
from a2gUtils import convert_dB_to_valid_hex_sivers_register_values

################################ SLEEP TIMES #################################
# Set a time sleep to allow the drone node to arrive at its location:
dist_from_takeof_to_node = 100
node_speed = 2 # m/s
time_to_reach_point =  dist_from_takeof_to_node/node_speed

# Set a guard time to allow the drone to reach the point for sure
guard_time = 120
time_to_sleep = time_to_reach_point + guard_time

################################ ANGLES #############################################
yaw = 0
pitch = 578 # IT DEPENDS ON THE AVAILABILITY OF PARKING SPOTS

################################ RF SETTINGS #############################################
freq_op = 57.51e9
tx_bb_gain = '3'
tx_bb_phase = '0'
tx_bb_iq_gain = '1.6'
tx_bfrf_gain = '3'
rx_bb_gain_1 = '-1.5'
rx_bb_gain_2 = '-4.5'
rx_bb_gain_3 = '1.6'
rx_bfrf_gain = '7'

_, rx_signal_values = convert_dB_to_valid_hex_sivers_register_values(rx_bb_gain_1, 
                                                                                    rx_bb_gain_2, 
                                                                                    rx_bb_gain_3, 
                                                                                    rx_bfrf_gain, 
                                                                                    tx_bb_gain, 
                                                                                    tx_bb_iq_gain, 
                                                                                    tx_bb_phase, 
                                                                                    tx_bfrf_gain)

myrfsoc_node_ip_addr = '10.1.1.40'

################################ SLEEP #################################

#time.sleep(time_to_sleep)

################################################################ CLI ################################
is_gimbal_used = questionary.select("Is gimbal going to be used?", choices=["Yes", "No"]).ask()

if (is_gimbal_used == "Yes"):
    mygimbal_node = GimbalRS2()
    mygimbal_node.setPosControl(yaw=yaw, pitch=pitch, ctrl_byte=0x01)

print(f"Sleep for 1 sec before wake up RFSoC")
time.sleep(1)

myrfsoc_node = RFSoCRemoteControlFromHost(rfsoc_static_ip_address=myrfsoc_node_ip_addr)    

is_start = questionary.select("Start measurement?", choices=["Yes", "No"]).ask()

if (is_start == "Yes"):
    myrfsoc_node.start_thread_receive_meas_data(rx_signal_values)

myrfsoc_node.stop_thread_receive_meas_data()
myrfsoc_node.finish_measurement()
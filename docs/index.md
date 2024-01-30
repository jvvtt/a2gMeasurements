# A2GMeasurements

a2gMeasurements.py comprises multiple (drivers for gimbal and gps, among others)
GUI_A2G_MEAS.py has all the functionality related with the GUI

## Quick definitions for documentation
There are only two types of nodes in the system: the ground node or the drone node. A node is just an abstraction of a system (either the drone or the ground) having as one of its components a host computer. 

Each node has multiple components (including as mentioned above a host computer). More information about the components is available in "Manual A2GMeasurements".

When we refer to "this node" in the documentation, it means the node where the attribute/method/class is being executed (whether is set, get, call or create an instance).

Equivalently, the "other node" in the documentation, refers to the node where the attribute/method/class is NOT being executed.

## Use
To use this software, execute in a terminal of the host computer of the ground node:

```{code-block}
---
emphasize-lines: 1
---
$ python GUI_A2G_MEAS.py
```

## API
```{eval-rst}
.. autoclass:: a2gmeasurements.GimbalRS2
    :members: __init__, seq_num, can_buffer_to_full_frame, validate_api_call, parse_position_response, can_callback, setPosControl, setSpeedControl, request_current_position, assemble_can_msg, send_cmd, send_data, receive, start_thread_gimbal, stop_thread_gimbal
.. autoclass:: a2gmeasurements.GpsSignaling
    :members: __init__, serial_connect, process_gps_nmea_data, process_pvtcart_sbf_data, process_pvtgeodetic_sbf_data, process_atteuler_sbf_data, parse_septentrio_msg, get_last_sbf_buffer_info, check_coord_closeness, serial_receive, start_thread_gps, stop_thread_gps, sendCommandGps, start_gps_data_retrieval, stop_gps_data_retrieval
.. autoclass:: a2gmeasurements.myAnritsuSpectrumAnalyzer
    :members: __init__, spectrum_analyzer_connect, retrieve_max_pow, spectrum_analyzer_close
.. autoclass:: a2gmeasurements.HelperA2GMeasurements
    :members: __init__, gimbal_follows_drone, do_follow_mode_gimbal, do_getgps_action, do_setgimbal_action, do_start_meas_drone_rfsoc, do_stop_meas_drone_rfsoc, do_finish_meas_drone_rfsoc, do_set_irf_action, do_closed_gui_action, do_set_remote_fm_flag, do_set_remote_stop_fm, process_answer_get_gps, decode_message, encode_message, socket_receive, socket_send_cmd, HelperStartA2GCom, HelperA2GStopCom
.. autoclass:: a2gmeasurements.GimbalGremsyH16
    :members: __init__, define_home_position, start_imu_thread, receive_imu_data, stop_thread_imu, fit_model_to_gimbal_angular_data, setPosControlGPModel, load_measured_drifts, load_measured_data_july_2023, load_measured_data_august_2023, gremsy_angle, plot_linear_reg_on_near_domain, start_thread_gimbal, setPosControl, stop_thread_gimbal, control_power_motors, change_gimbal_mode
.. autoclass:: a2gmeasurements.SBUSEncoder
    :members: __init__, set_channel, start_sbus, stop_updating, send_sbus_msg, update_rest_state_channel, not_move_command, move_gimbal, change_mode
.. autoclass:: a2gmeasurements.RFSoCRemoteControlFromHost
    :members: __init__, send_cmd, transmit_signal, set_rx_rf, receive_signal_async, pipeline_operations_rfsoc_rx_ndarray, save_hest_buffer, start_thread_receive_meas_data, stop_thread_receive_meas_data, finish_measurement
.. autoclass:: GUI_A2G_MEAS.SetupWindow
    :members: __init__, enable_gnd_coords_callback, enable_drone_coords_callback
.. autoclass:: GUI_A2G_MEAS.WidgetGallery
    :members: __init__, init_constants, showCentralWidget, showSetupMenu, createMenu, start_thread_gnd_gimbal_fm, start_thread_drone_gimbal_fm, stop_thread_drone_gimbal_fm, start_thread_gps_visualization, stop_thread_gps_visualization, check_if_ssh_2_drone_reached, check_if_drone_fpga_connected, check_if_gnd_fpga_connected, check_if_drone_gimbal_connected, check_if_gnd_gimbal_connected, check_if_server_running_drone_fpga, check_if_server_running_gnd_fpga, check_if_gnd_gps_connected, get_gnd_ip_node_address, check_status_all_devices, create_class_instances, periodical_pap_display_callback, periodical_gps_display_callback, create_check_connections_panel, activate_rs2_fm_flag, activate_gps_display_flag, connect_drone_callback, disconnect_drone_callback, create_fpga_and_sivers_panel, checker_gimbal_input_range, move_button_gimbal_gnd_callback, left_button_gimbal_gnd_callback, right_button_gimbal_gnd_callback, up_button_gimbal_gnd_callback, down_button_gimbal_gnd_callback, move_button_gimbal_drone_callback, left_button_gimbal_drone_callback, right_button_gimbal_drone_callback, up_button_gimbal_drone_callback, down_button_gimbal_drone_callback, create_Gimbal_GND_panel, create_Gimbal_AIR_panel, rx_lock_mode_radio_button_callback, rx_follow_mode_radio_button_callback, convert_dB_to_valid_hex_sivers_register_values, start_meas_button_callback, stop_meas_button_callback, finish_meas_button_callback, create_Planning_Measurements_panel, create_GPS_visualization_panel, create_pap_plot_panel
```
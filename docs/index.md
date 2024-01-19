# A2GMeasurements

a2gMeasurements.py comprises multiple (drivers for gimbal and gps, among others)
GUI_A2G_MEAS.py has all the functionality related with the GUI

## Use
To use this software, execute in the ground node:

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
    :members: __init__, gimbal_follows_drone
```
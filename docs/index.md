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
```
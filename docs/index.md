# A2GMeasurements
To download the repository of this project, run the following command in a terminal:
```{code-block}
---
emphasize-lines: 0
---
$ git clone https://github.com/jvvtt/a2gMeasurements
```

or manually download the zip file from the same github page.

The password for the github account is provided in the "Manual A2GMeasurements" file.

## Quick definitions for documentation
There are only two types of nodes in the system: the ground node or the drone node. A node is just an abstraction of a system (either the drone or the ground) having as one of its components a host computer. 

Each node has multiple components (including as mentioned above a host computer). More information about the components is available in "Manual A2GMeasurements".

When we refer to "this node" in the documentation, it means the node where the attribute/method/class is being executed (whether is set, get, call or create an instance).

Equivalently, the "other node" in the documentation, refers to the node where the attribute/method/class is NOT being executed.

# Package requirements
To run this software, a list of python packages are required. All the packages required are listed in the ``requirements.txt`` file.

For the GPS visualization, the last available version of Folium in pip or conda might lack of the Realtime plugin. 
To cope for that, go to the Github of Folium, and download the following files:

1-The ``utilities.py`` (https://github.com/python-visualization/folium/blob/main/folium/utilities.py)

2-The ``realtime.py`` (https://github.com/python-visualization/folium/blob/main/folium/plugins/realtime.py)

1-Copy the ``JsCode`` class of the downloaded ``utilities.py`` file and paste it at the end of the Folium ``utilities.py`` file you have under your conda environment. To look for where is your conda environment, type in Windows:

```{code-block}
---
emphasize-lines: 0
---
$ where python
```

or equivalently in Linux:

```{code-block}
---
emphasize-lines: 0
---
$ which python
```

The ``utilities.py`` file you have under your conda environment must be in 
```{code-block}
---
emphasize-lines: 0
---
PATH_TO_YOUR_CONDA_ENV\Lib\site-packages\folium
```
or in

```{code-block}
---
emphasize-lines: 0
---
PATH_TO_YOUR_CONDA_ENV/lib/python[version]/site-packages/folium
```

2-Place the downloaded ``realtime.py`` file from the Folium Github under the following directory:
```{code-block}
---
emphasize-lines: 0
---
PATH_TO_YOUR_CONDA_ENV\Lib\site-packages\folium\plugins\
```
or in

```{code-block}
---
emphasize-lines: 0
---
PATH_TO_YOUR_CONDA_ENV/lib/python[version]/site-packages/folium/plugins/
```

## Installing PyQt5 on RasberryPi
The ``GUI_A2G_MEAS.py`` software requires PyQt5 and PyQtWebEngine to be working.The installation of both packages under RaspbianOS might have difficulties.

Try first to install them by using the pip manager under your activated conda environment:
```{code-block}
---
emphasize-lines: 0
---
(name_of_your_environment) $ pip install PyQt5
(name_of_your_environment) $ pip install PyQtWebEngine
```

Check if the installation went well by executing python (in your conda environment) and then importing the packages:
```{code-block}
---
emphasize-lines: 0
---
(name_of_your_environment) $ python
```

```{code-block}
---
emphasize-lines: 0
---
>>import PyQt5
>>from PyQt5.QtWebEngineWidgets import QWebEngineView
```
If there were no errors in both imports, the packages where succesfully installed under you conda environment.

If there were errors, try to install them as follows.

First execute:
```{code-block}
---
emphasize-lines: 0
---
sudo apt-get install python3-pyqt5
```

This installation should not have any problem. Then go to ``/usr/lib/python3/dist-packages`` and copy the folders containing the name 'PyQt5' (there might be at least 2: 'PyQt5' and 'PyQt5-version.dist-info) to ``site-packages`` of your conda environment (i.e. ``/home/jvvtt64/mambaforge/envs/groundnode/lib/python3.10/site-packages``)

Next, execute:
```{code-block}
---
emphasize-lines: 0
---
sudo apt-get install python3-pyqt5.qtwebengine
```

Look again for the folders named 'PyQtWebEngine' in ``/usr/lib/python3/dist-packages/`` and copy them to the ``site-packages`` folder of your conda environment (i.e. ``/home/jvvtt64/mambaforge/envs/groundnode/lib/python3.10/site-packages``). 

Look also under the ``/usr/lib/python3/dist-packages/PyQt5`` folder any file having the name 'WebEngine' in it and copy all these files to the 'PyQt5' folder of your conda environment (i.e. ``/home/jvvtt64/mambaforge/envs/groundnode/lib/python3.10/site-packages/PyQt5/``). Respect the folder and file hierarchy of the folder 'PyQt5': if there is a file under a given folder, copy the file to the corresponding destination folder with the same name.

## Use
Open a terminal and set ``a2gMeasurements`` as your working directory. 

In the host computer of the **ground** node execute in a terminal:

```{code-block}
---
emphasize-lines: 0
---
$ python GUI_A2G_MEAS.py
```

Equivalently, in the host computer of the **drone** node execute in a terminal:
```{code-block}
---
emphasize-lines: 0
---
$ python drone_main.py
```

# Notes
The gps visualization is updated slower than the speed of the thread used to update the gps coordinates (``GUI_A2G_MEAS.WidgetGallery.periodical_gps_display_thread``). The thread is called regularly at the time it is expected (i.e. 1 sec). The ``put`` and ``get`` requests to the uvicorn server seem to performed also within the same time margin. This means that either the Folium Leaflet or PyQt5WebEngine packages for the Rasperry run slow.

## Extend docs
This documentation is made using Sphinx and the MyST extension.

To modify the documentation for classes and their methods, modify the docstring of the corresponding class and/or method in its corresponding file. 

After doing so, open a terminal and set the ``docs`` directory as your working directory. After that, execute:
```{code-block}
---
emphasize-lines: 0
---
$ make html
```

Sphinx will automatically update the documentation.


## API
```{eval-rst}
.. autoclass:: a2gmeasurements.GimbalRS2
    :members: __init__, seq_num, can_buffer_to_full_frame, validate_api_call, parse_position_response, can_callback, setPosControl, setSpeedControl, request_current_position, assemble_can_msg, send_cmd, send_data, receive, start_thread_gimbal, stop_thread_gimbal
.. autoclass:: a2gmeasurements.GpsSignaling
    :members: __init__, serial_connect, process_gps_nmea_data, process_pvtcart_sbf_data, process_pvtgeodetic_sbf_data, process_atteuler_sbf_data, parse_septentrio_msg, get_last_sbf_buffer_info, check_coord_closeness, serial_receive, start_thread_gps, stop_thread_gps, sendCommandGps, start_gps_data_retrieval, stop_gps_data_retrieval, setHeadingOffset
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
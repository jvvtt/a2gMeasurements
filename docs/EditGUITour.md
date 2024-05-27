# Change the GUI

To modify the layout of the panel modify  the method ``create_check_connections_panel()``.

If any bug encounter (or the developer wants to extend any functionality) in the methods used to check the connections between the devices and each node, modify one of the following functions (the one/s corresponding to the device/s) : ``check_if_ssh_2_drone_reached()``, 
``check_if_drone_fpga_connected()``, ``check_if_gnd_fpga_connected()``, ``check_if_drone_gimbal_connected()``, ``check_if_gnd_gimbal_connected()``, ``check_if_server_running_drone_fpga()``, ``check_if_server_running_gnd_fpga()``, ``check_if_gnd_gps_connected()``, ``check_if_drone_gps_connected()``.

To modify any implemented functionality in the panel (i.e. if the developer wants that the ``Connect`` button is activated only when both RFSoCs are detected, ...) modify the callbacks ``check_status_all_devices()``, ``connect_drone_callback()`` and ``disconnect_drone_callback()`` corresponding to the buttons ``Check``, ``Connect`` and ``Disconnect`` respectively. 

Also might be necessary to modify the method ``create_class_instances()`` called under some conditions after pressing the ``Connect`` button.
# Communication protocol

A TCP communication is established between the ground and drone nodes. This link is bidirectional and is used to retrieve information, send control and configuration instructions.

In the communication link, the ground node works as the server while the drone node works as the client.

Each message between both nodes has the 5 mandatory fields shown in the following Table.

<div class="center-table" markdown>
| Field   | Bytes    | Description | Values   |
| :-----: | :------: | :---------: | :------: |
| ``source_id`` | 1 | Identifier for the message sender | ``0x01``: ground node, ``0x02``: drone node |
| ``destination_id`` | 1 | Identifier for the message received | ``0x01``: ground node, ``0x02``: drone node |
| ``message_type`` | 1 | Distinguish between messages with acknowledgment from the receiver, and no acknowledgment | ``0x01``: short msg with no ack, ``0x02``: long msg with no ack, ``0x03``: short msg with ack |
| ``cmd`` | 1 | Identifier for the command | ``0x01``-``0x09`` when ``message_type``=``0x01``. Otherwise, ``0x01`` |
| ``length`` | 1 | Counts either the number of bytes or the number of keys in a dictionary in the optional ``data`` field. If no ``data`` is provided is 0 | 0 - 255 |
</div>

The list of available commands are shown in the following Table.

<div class="center-table" markdown>
| cmd    | message_type | Command name | Description |
| :----: | :----------: | :----------: | :---------: |
| ``0x01`` | ``0x01`` | ``FOLLOWGIMBAL`` | Asks the msg receiver to send its GPS coordinates to use them for steering the sender's gimbal towards the receiver |
| ``0x02`` | ``0x01`` | ``GETGPS`` | Asks the msg receiver to send its GPS coordinates to use them for visualization or other purposes different from steering sender's gimbal |
| ``0x03`` | ``0x01`` | ``SETGIMBAL`` | Sets the msg receiver's yaw, pitch and roll angles for its connected gimbal |
| ``0x04`` | ``0x01`` | ``STARTDRONERFSOC`` | Unidirectional command sent always from the ground node to the drone node. Starts a measurement in the drone RFSoC |
| ``0x05`` | ``0x01`` | ``STOPDRONERFSOC`` | Unidirectional command sent always from the ground node to the drone node. Stops a measurement in the drone RFSoC |
| ``0x06`` | ``0x01`` | ``FINISHDRONERFSOC`` | Unidirectional command sent always from the ground node to the drone node. Finishes a measurement in the drone RFSoC |
| ``0x07`` | ``0x01`` | ``CLOSEDGUI`` | Unidirectional command sent always from the ground node to the drone node. Tells the drone node that it can stop the execution of its running script |
| ``0x08`` | ``0x01`` | ``SETREMOTEFMFLAG`` | Unidirectional command sent always from the ground node to the drone node. Activates the ``drone_fm_flag`` flag used to initiate the steering of the drone's gimbal towards the ground node. Sends a data field with the sub-fields shown in next Table |
| ``0x09`` | ``0x01`` | ``SETREMOTESTOPFM`` | Unidirectional command sent always from the ground node to the drone node. Deactivates the ``drone_fm_flag flag`` |
| ``0x01`` | ``0x02`` | ``SETIRF`` | Unidirectional command sent always from the ground node to the drone node. Sends a data field containing a measured Power Angular Profile. More info in next Table |
| ``0x01`` | ``0x03`` | ``ANS`` to ``GETGPS`` | Answer to a ``GETGPS`` command. The answer contains a ``data`` field with the sub-fields shown in next Table |
</div>

The data field of the messages sent is used under specific commands. The length of the data field depends specifically on the command. The information sent in the `data` field for the different commands is shown in the following Table:

<div class="center-table" markdown>
| Data field | Command name | Available options |
| :--------: | :----------: | :---------------: |
| ``FMODE`` | ``FOLLOWGIMBAL`` | ``0x00``: steer azimuth and elevation axis of ground node's gimbal.  ``0x01``: steer elevation axis of ground node's gimbal, ``0x02``: steer azimuth axis of ground node's gimbal |
| ``YAW`` | ``SETGIMBAL`` | Sets the yaw at which to set the other (remote) gimbal |
| ``PITCH`` | ``SETGIMBAL`` | Sets the pitch at which to set the other (remote) gimbal |
| ``ROLL`` | ``SETGIMBAL`` | Sets the roll at which to set the other (remote) gimbal |
| ``carrier_freq`` | ``STARTDRONERFSOC`` | Sets the operating frequency on drone's RFSoC |
| ``rx_gain_ctrl_bb1`` | ``STARTDRONERFSOC`` | Sets the first baseband (BB) gain for the Sivers receiver|
| ``rx_gain_ctrl_bb2``| ``STARTDRONERFSOC` | Sets the second BB gain for the Sivers receiver |
| ``rx_gain_ctrl_bb3`` | ``STARTDRONERFSOC`` | Sets the third BB gain for the Sivers receiver |
| ``rx_gain_ctrl_bfrf`` | ``STARTDRONERFSOC`` | Sets the gain for the I, Q signals before the RF mixer |
| ``X`` | ``SETREMOTEFMFLAG`` | If the ground node's mobility has been set as static, this parameter sets the geocentric ``X`` coordinate corresponding to EPSG 4978. The actual value is set by the user in the GUI by setting the latitude, longitude and altitude coordinates of the ground node |
| ``Y`` | ``SETREMOTEFMFLAG`` | If the ground node's mobility has been set as static, this parameter sets the geocentric ``Y`` coordinate corresponding to EPSG 4978. The actual value is set by the user in the GUI by setting the latitude, longitude and altitude coordinates of the ground node |
| ``Z`` | ``SETREMOTEFMFLAG`` | If the ground node's mobility has been set as static, this parameter sets the geocentric ``Z`` coordinate corresponding to EPSG 4978. The actual value is set by the user in the GUI by setting the latitude, longitude and altitude coordinates of the ground node |
| ``FMODE`` | ``SETREMOTEFMFLAG`` | ``0x00``: steer azimuth and elevation axis of drone node's gimbal. ``0x01``: steer elevation axis of drone node's gimbal. ``0x02``: steer azimuth axis of drone node's gimbal |
| ``MOBILITY`` | ``SETREMOTEFMFLAG`` | ``0x00``: ground node is moving,  ``0x01`` ground node is static |
</div>

!!! failure "Maximum MTU on Raspbian"
    ```sh
    It seems that the Raspbian OS (64 bits) restricts TCP messages to have a maximum of 1472 bytes, no matter if the MTU is bigger. This issue has to be solved if it is desired to send a Power Angular Profile (PAP) that contains more than 23 time snapshots and/or more than 16 beams.
    ```

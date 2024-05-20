# Guide for using the GUI

## Initial recommendations
It is recommended to follow the guidelines in this section to start the operation of the air-to-ground channel sounder.

* Connect every component of the system as shown in the Figure of section [Block Diagram](MeasurementSystem.md#block-diagram).

* Turn on both host computers (Manifold and Rasberry Pi).
* Manually check each component connection, by following what is explained in sections [Gimbal to Host Connection](MeasurementSystem.md#gimbalrs2-to-host-connection), [GPS to Host Connection](MeasurementSystem.md#gps-to-host-connection), [RFSoC to Host Connection](MeasurementSystem.md#rfsoc-to-host-connection), [Host Wifi to Router Connection](MeasurementSystem.md#host-wifi-to-router-connection), [RFSoC to Host Ethernet Connection](MeasurementSystem.md#ethernet-rfsoc-to-host-connection). The software will check which devices are physically connected to the host, but is better to do a double check.
* If an error is encountered check some common problems in section [Troubleshooting](Troubleshooting.md).

## Definitions

For the sake of clarity, we redefine some words that are being used in this document.

* **Measurement**: comprises the channel sounding process *from* the moment the user presses the ``START`` button *until* ``STOP`` is pressed.
* **Experiment**: comprises the channel sounding process *from* the moment the user presses the ``START`` button *until*  ``FINISH`` is pressed. 
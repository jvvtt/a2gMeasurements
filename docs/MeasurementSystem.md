# Measurement system

## Block diagram

The system is composed by two nodes (the ground node and the air/drone node) that communicate with each other through IEEE 802.11 ac.

Each node contains a set of devices connected to it, and managed by a host computer. A diagram of the devices connected to each node is shown in the following Figure.

<figure markdown="span">
  ![Image title](assets/a2g_node_components.PNG){ width="400" }
  <figcaption>Host computer and devices connected to it for each node</figcaption>
</figure>

The specific devices used for each of the components in the previous Figure are shown in the next Table.

<div class="center-table" markdown>
| Type device | Device used                          |
| :---------: | :----------------------------------: |
| Host computer (ground)     | Raspberry Pi 4B  |
| Host computer (air)     | DJI Manifold 2-C |
| Gimbal    | DJI Ronin RS2 |
| PCAN "bridge" | DJI Ronin Focus Wheel + PEAK system PCAN-USB |
| GPS | Septentrio mosaic-go heading evaluation kit |
| RFSoC board | Xilinx RFSoC 2 x 2 Kit |
| WiFi Txr (ground) | Raspberry Pi 4B integrated IEEE 802.11ac |
| WiFi Txr (air) | TP Link Archer T4U |
| RF System | Sivers EVK06002 + Sivers TRX BF/01 RFIC |
</div>

In addition to the mentioned devices, we use a TP-Link AX1500 5GHz router as an access point for both nodes. The router is already configured to assign specific static addresses to each node.

## Software

### Files

The main files where most of the system functionality is implemented are:

- `a2gmeasurements.py`: this file has all the functionality related with operating, controlling and collecting information from the devices. It comprises the classes `GimbalRS2`, `GpsSignaling`, `myAnritsuSpectrumAnalyzer`, `HelperA2GMeasurements`, `GimbalGremsyH16`, `SBUSEncoder` and `RFSoCRemoteControlFromHost` among others. See the available API in [API Reference Gimbal](GimbalRS2.md), [API Reference GPS](GpsSignaling.md), [API Reference RFSoC](RFSoCHandler.md), [API Reference Communication](NodesCommunication.md).

- `GUI_A2G_MEAS.py`: this file has all the functionality related with the Graphical User Interface (GUI). It calls methods from `a2gmeasurements.py` to manipulate the devices by using the GUI.

- `drone_main.py`: this is a script that setup the devices and the wireless connection at the air node.

- `a2gUtils.py`: this file contains few auxiliary (general purpose) methods that are used by other files previously mentioned. It is required for both nodes. If the developer wants to follow the file structure already used, they can extend this file by adding any auxiliary or general purpose functionality that is not specifically related to the devices used, i.e. some type of mathematical computation, memory management, etc.

- `docs/`: this folder contains the documentation for this project.

The files `a2gmeasurements.py` and `a2gUtils.py` must be placed in the working directories of each node's host computer.

The file `GUI_A2G_MEAS.py` is only required to be placed in the working directory of the ground node's host computer.

The file `drone_main.py` is only required to be placed in the working directory of the air node's host computer.

## GimbalRS2 to host connection

Connect the CAN port of the gimbal RS2 to any USB port of the host computer, using the DJI Ronin Focus Wheel and the PEAK System PCAN-USB bridge, as indicated in the following Figure.

<figure markdown="span">
  ![Image title](assets/a2g_node_components.PNG){ width="400" }
  <figcaption>Connection between the gimbal RS2 and the host</figcaption>
</figure>

## GPS to host connection

Connect the USB port from the Septentrio gps to any USB port of the host computer, as indicated in Figure.

<figure markdown="span">
  ![Image title](assets/a2g_node_components.PNG){ width="400" }
  <figcaption>Connection between the GPS and the host</figcaption>
</figure>

**DO NOT** use the port named `REC-USB` of the Septentrio gps.

## RFSoC to host connection

Connect any of the RFSoC Ethernet ports to any of th Ethernet ports of the host computer, as indicated in the following Figure.

<figure markdown="span">
  ![Image title](assets/a2g_node_components.PNG){ width="400" }
  <figcaption>Connection between the RFSoC and the host</figcaption>
</figure>

## Host WiFi to router connection

To guarantee that the connection between each of the host computers (Manifold and Raspberry or their replacements) to the router is done through the 5GHz network, we have only enabled the 5GHz band in the router configuration website.

- The website to configure the router is the address: `192.168.0.1`

- The password to login is: jvvtt2937

In order to automatize the connections between both host computers, the TP-Link AX1500 5GHz Router has been configured so that the IP addressing of the DHCP server assigns always the same IP address to the host computers (Manifold and Raspberry) identified by their MAC addresses.

- The IP address of the drone host computer (Manifold) has been set to: `192.168.0.157`

- The IP address of the ground host computer (Raspberry) has been set to: `192.168.0.124`

## Ethernet RFSoC to host connection

Open a terminal or command line in the host computer. Type the following command:

!!! warning "Connect to RFSoC"
ssh xilinx@10.1.1.30 // the address of the node to be checked

When asked for password, type:
!!! warning "Enter password"
xilinx

This will allow you to use the command line of the RFSoC from the host computer.

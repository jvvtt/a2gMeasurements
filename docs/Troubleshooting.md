# Troubleshooting

## Can ssh but can not ping

Possible cause: ICMP problem on Manifold (Windows Firewall).

Solution to try:

Go to `Start` > `Run` > `firewall.cpl` > `Advanced Settings`.

You get Windows Defender Firewall with Advanced Security. Now create Inbound and Outbound rules to allow ICMP requests. Check Inbound Rules and Outbound Rules. In the right pane, find the file and printer sharing rules (Echo Request - ICMPv4-In). Right-click each rule and select Enable Rule.

## Network is unreachable

Possible cause: Bad ethernet cable connected.

Solution to try:

Power off RFSoC disconnect and disconnect Ethernet cable both sides. Connect again and make sure is well connected.

## Sockets error

Possible cause: server not started in the RFSoC.

1. Power off and power on again the RFSoC.
2. Connect to the RFSoC through SSH.
2. On the RFSoC terminal type:

!!! warning "Check if RFSoC server is running"
    ps aux | grep mmwsdr   

3. Within the listed process there should be two running: `run.sh` and `server.py`.

4. If that is not the case, then, type in the terminal the following commands:

!!! warning "Start RFSoC server"
    cd jupyter\notebooks/mmwsdr
    sudo ./run.sh

    // If password is asked, type
    xilinx

# Measurements methodology

## Goal of the methodology

The purpose of this section is to define the main actors involved in a measurement process with their respective actions. The output of the measurement methodology is a detailed **schedule** where each actor performs its actions in a synchronized or orchestatred manner. This means that there will be actions that can be performed simultaneously (by different actors) and others that not. In what follows, these details are explained.

## Actors and actions

In the measurement process the following main actors are identified:

- Drone operator: responsible for controlling the drone
- Software operator: responsible for managing the a2gMeasurements software
- Vehicle operator/Driver: responsible for moving the vehicle close to where the ground node is located

Each actor **can** perform a defined set of actions.

As for the drone operator, the actions he can perform are:

- Move the drone: the drone is moved from one position to another
- Hover the drone: the drone hovers at its current position

Notice that in the "Move the drone" action are included taking off and landing the drone, since they imply a movement from one location (ground to air or last point to ground) to another.

The software operator can perform the following actions:

- Start RF: starts the thread responsible for making the TX start to send power, and the RX to listening for incoming power
- Stop RF: stops the thread of the RX responsible for listening for incoming power
- Rotate the ground gimbal: rotates the ground gimbal by a given attitude (yaw, pitch)
- Rotate the drone gimbal: rotates the drone gimbal by a given attitude (yaw, pitch)

The "vehicle operator"/drinver can perform the following actions:

- Move the vehicle: the vehicle is moved from one position to another
- Stop the vehicle: the vehicle rests at its current position

It is worth noting that some of these actions can be/would be performed automatically (without the intervention of the respective human operator), but in the **schedule** they are still classified as performed by their respective operator (wheter it is human or automated software) for the convenience of seeing who is responsible of each action to be executed in the measurement process.

There are some actions that can be performed simultaneously by different actors (i.e. drone operator "Hover the drone" while the software operator "Start RF"). Also, while an actor is performing only one action (i.e. "Hover the drone") another operator can perform multiple actions in a predefined priority order (i.e. "Move drone gimbal" -> "Move ground gimbal" -> "Start RF").

Therefore, a list of each Group of Ordered and Simulatenous Actions (GOSA) performed by different operators is detailed as follows:

`Group A`

- Action: "Stop the vehicle". Actor: Vehicle operator
- Action: "Hover the drone". Actor: Drone operator
- Action: "Move the drone gimbal". Actor: Software operator
- Action: "Move the gnd gimbal". Actor: Software operator
- Action: "Start RF". Actor: Software operator
- Action: "Stop RF". Actor: Software operator

`Group B`

- Action: "Move the drone". Actor: Drone operator

`Group C`

- Action: "Move the vehicle". Actor: Vehicle operator

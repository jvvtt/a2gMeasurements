
# Open GPS server

1) Open an Anaconda prompt (in Windows) and set the current directory to the `a2gMeasurements` folder.

2) If you haven't activated your conda environment (having all the python packages required to run the software) activate it by running:

!!! warning "Activate conda environment"
    ```sh
    conda activate NameOfYourCondaEnvironment
    ```

In the Raspberry Pi 4B (64bits) the name of the already created conda environment is `groundnode`. 

On the Manifold 2C the name of the already created conda environment is `uavCom`.

3) Start the GPS server:

!!! warning "Start GPS server"
    ```sh
    uvicorn gpsRESTHandler:app
    ```

4) Execute `python GUI_A2G_MEAS.py` on the ground node (Raspberry PI) to run the GUI.

Alternatively, open Visual Studio Code, open the `a2gMeasurements` folder, and run the GUI by pressing `Run` > `Run Without Debugging`.

5) After opening the A2GMeasurements GUI, the first window that will appear is shown in the following Figure:

<figure markdown="span">
  ![Image title](assets/a2gmeas_setup_win_1.png){ width="400" }
  <figcaption>First window after A2GMeasurements GUI is opened</figcaption>
</figure>

6) Press the ``Setup`` menu:

<figure markdown="span">
  ![Image title](assets/a2gmeas_setup_win_2.png){ width="400" }
  <figcaption>Setup menu opened</figcaption>
</figure>

7) Then press ``Setup devices and more``:

<figure markdown="span">
  ![Image title](assets/a2gmeas_setup_win_3.png){ width="400" }
  <figcaption>Setup devices and more</figcaption>
</figure>

8) After that, a Setup window as shown in the following Figure  will appear:

<figure markdown="span">
  ![Image title](assets/a2gmeas_setup_win_4.png){ width="400" }
  <figcaption>Setup window for configuring some parameters</figcaption>
</figure>

9) Choose the drone gimbal from the available options:

<figure markdown="span">
  ![Image title](assets/a2gmeas_setup_win_5.png){ width="400" }
  <figcaption>Drone gimbal selection</figcaption>
</figure>

NOTE: *the Gremsy H16 gimbal option is available but the behaviour of the gimbal is not optimal*.

10) Choose along which of its own axis, drone's gimbal should follow ground node movement:

<figure markdown="span">
  ![Image title](assets/a2gmeas_setup_win_6.png){ width="400" }
  <figcaption>drone's gimbal axis following ground node</figcaption>
</figure>

11) Choose along which of its own axis, ground's gimbal should follow drone node movement:

<figure markdown="span">
  ![Image title](assets/a2gmeas_setup_win_7.png){ width="400" }
  <figcaption>ground's gimbal axis following drone node</figcaption>
</figure>

12) Choose ground node mobility:

<figure markdown="span">
  ![Image title](assets/a2gmeas_setup_win_8.png){ width="400" }
  <figcaption>ground node mobility</figcaption>
</figure>

12) If ground node's mobility was ``Static``, the following text boxes will become active. Enter there the coordinates (in decimal degrees) of the ground node:

<figure markdown="span">
  ![Image title](assets/a2gmeas_setup_win_9.png){ width="400" }
  <figcaption>static coordinates for ground node</figcaption>
</figure>

13) Choose drone node mobility:

<figure markdown="span">
  ![Image title](assets/a2gmeas_setup_win_10.png){ width="400" }
  <figcaption>drone node mobility</figcaption>
</figure>

14) If drone node's mobility was ``Static``, the following text boxes will become active. Enter there, the coordinates (in decimal degrees) of the drone node:

<figure markdown="span">
  ![Image title](assets/a2gmeas_setup_win_10b.png){ width="400" }
  <figcaption>static coordinates for drone node</figcaption>
</figure>

15) If there is mismatch between the front of the ground gimbal and the GPS attitude baseline (see section [Components](MeasurementSystem.md#components)), enter in the following text box the offset (in degrees). The offset angle is measured as described in the API html in ``GpsSignaling()`` and ``GpsSignaling.setHeadingOffset()``:

<figure markdown="span">
  ![Image title](assets/a2gmeas_setup_win_11.png){ width="400" }
  <figcaption>ground node attitude offset for the baseline between gps antennas</figcaption>
</figure>

16) Finally, press ``OK``:

<figure markdown="span">
  ![Image title](assets/a2gmeas_setup_win_12.png){ width="400" }
  <figcaption>press OK</figcaption>
</figure>

17) After pressing ``OK``, the main window of the A2GMeasurements app will appear.

NOTE: the parameters configured in the Setup window (see [Setup Window](assets/a2gmeas_setup_win_4.png)) are not modifiable until the user presses ``Disconnect drone``. After that, the menu ``Setup devices and more`` will be available again.
<h1 style="color:#000;font-family:system-ui">Flight Plan</h1>

Before proceding with the measurement information, enter the start time and date of the measurements:

<div style="display:flex;gap:5rem;align-items:center;justify-content:center;border-radius:5px; border:1px solid #555;height:2rem">
    <label for="start-date-meas">Start date:</label>
    <input type="date" min="2024-04-01" max="2024-12-31" id="start-date-meas"/>
    <label for="start-time-meas">Start time:</label>
    <input type="time" min="07:00" max="22:00" id="start-time-meas"/>
</div>

## Experiments

### Definitions used in this report

* A **measurement** comprises the channel sounding process *from* the moment the receiver RFSoC is listening to incoming signals *until* it stops listening.

* An **experiment** is a collection of **measurements**.

* A **drone operator** is the person responsible for controlling the drone.

* A **software operator** is the person responsible for using Wireless Channels sounder software.

* A **car operator** is the person resposible for driving the car. 

### Node locations
The following table displays the coordinates for both nodes in the order by which each node will move (i.e. the drone will move first to the coordinates having the `Order ID` 1, then it will move to the coordinates having the `Order ID` 2, and so on).

<section style="display:flex;justify-content:center;align-items:center;gap:3rem">
    <table id="drone-route" style="text-align:center">
        <thead>
            <tr id="drone-route-headers">
                <!-- Header cells will be added dynamically -->
            </tr>
        </thead>
        <tbody id="drone-route-body">
            <!-- Table body will be populated dynamically -->
        </tbody>
  </table>
  <table id="ground-route" style="text-align:center">
    <thead>
      <tr id="ground-route-headers">
        <!-- Header cells will be added dynamically -->
      </tr>
    </thead>
    <tbody id="ground-route-body">
      <!-- Table body will be populated dynamically -->
    </tbody>
  </table>
</section>

### Distances

The following table displays the distances:

<section style="display:flex;justify-content:center;align-items:center">
<table id="dists-info">
    <thead>
      <tr id="dists-headers">
        <!-- Header cells will be added dynamically -->
      </tr>
    </thead>
    <tbody id="dists-body">
      <!-- Table body will be populated dynamically -->
    </tbody>
  </table>
</section>

### Measurement procedure

The actions each operator will perform are specified in the following table:

<section style="display:flex;justify-content:center;align-items:center">
<table id="flight-plan-schedule">
    <thead>
      <tr id="fp-schedule-headers">
        <!-- Header cells will be added dynamically -->
      </tr>
    </thead>
    <tbody id="fp-schedule-body">
      <!-- Table body will be populated dynamically -->
    </tbody>
  </table>
</section>

<script src='../javascripts/updateFlightPlanInfo.js'></script>
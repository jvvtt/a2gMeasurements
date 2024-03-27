fetch('../assets/data.json')
    .then((response) => response.json())
    .then((json) => console.log(json));

function updateTableEntries(newData, columnHeaders, tableName, headerName, tableBodyName) {  
    const table = document.getElementById(tableName);
    const headerRow = document.getElementById(headerName);
    const tableBody = document.getElementById(tableBodyName);
  
    // Clear existing table content
    headerRow.innerHTML = ""; // Clear header row
    tableBody.innerHTML = ""; // Clear table body
  
    // Extract column headers from the first data entry
    const columnKeys = Object.keys(newData[0]);
  
    // Add header cells
    columnHeaders.forEach(headerText => {
        const th = document.createElement("th");
        th.textContent = headerText;
        th.style="text-align:center:word-wrap: break-word";
        headerRow.appendChild(th);
    });
  
    // Add rows to the table body
    newData.forEach(entry => {
        const row = document.createElement("tr");
        columnKeys.forEach(headerText => {
        const cell = document.createElement("td");
        cell.textContent = entry[headerText];
        cell.style="text-align:center;word-wrap:break-word";
        row.appendChild(cell);
    });
        tableBody.appendChild(row);
    });
}

// Get start date and time for measurements
const start_date = document.getElementById("start-date-meas")
const start_time = document.getElementById("start-time-meas")

const handleDateChange = () => {
    console.log(start_date.value)
}

const handleTimeChange = () => {
    console.log(start_time.value)
}

// Event listener for date input
start_date.addEventListener('change', ()=>handleDateChange());

// Event listener for time input
start_time.addEventListener('change', ()=>handleTimeChange());


const columnHeaders = ['START TIME', 'DRONE OPERATOR ACTION', 'SOFTWARE OPERATOR ACTION', 'CAR OPERATOR ACTION', 'ACTION DURATION', 'STOP TIME']
// Sample data for updating the scheduler table
const newData = [
    { START_TIME: "2024-04-05-09:00:00", 
      DRONE_OPERATOR_ACTION: 'Move drone to location 1', 
      SOFTWARE_OPERATOR_ACTION: 'No action',
      CAR_OPERATOR_ACTION: 'No action',
      ACTION_DURATION: 30, 
      STOP_TIME: "2024-04-05-09:00:30" },
    { START_TIME: "2024-04-05-09:00:30", 
      DRONE_OPERATOR_ACTION: 'Leave drone hover in location 1', 
      SOFTWARE_OPERATOR_ACTION: 'Start measurement',
      CAR_OPERATOR_ACTION: 'No action',
      ACTION_DURATION: 30, 
      STOP_TIME: "2024-04-05-09:01:00" },
    { START_TIME: "2024-04-05-09:01:00", 
      DRONE_OPERATOR_ACTION: 'Leave drone hover in location 1', 
      SOFTWARE_OPERATOR_ACTION: 'Stop measurement',
      CAR_OPERATOR_ACTION: 'No action',
      ACTION_DURATION: 5, 
      STOP_TIME: "2024-04-05-09:01:35" },
      { START_TIME: "2024-04-05-09:01:35", 
      DRONE_OPERATOR_ACTION: 'Leave drone hover in location 1', 
      SOFTWARE_OPERATOR_ACTION: 'No action',
      CAR_OPERATOR_ACTION: 'Move car to location 1',
      ACTION_DURATION: 120, 
      STOP_TIME: "2024-04-05-09:03:35" }
    // Add more data as needed
];

const tableFGSchedule = "flight-plan-schedule"
const headerFGSchedule = "fp-schedule-headers"
const bodyFGSchedule = "fp-schedule-body"

// Call the function to update table entries
updateTableEntries(newData, columnHeaders, tableFGSchedule, headerFGSchedule, bodyFGSchedule);

// Sample data for updating the scheduler table
const drone_locations = [
    { Order_ID: 1, Latitude: 60.2454, Longitude: 2.4744},
    { Order_ID: 2, Latitude: 60.3548, Longitude: 2.844 },
    { Order_ID: 3, Latitude: 60.31248, Longitude: 2.3244 },
    // Add more data as needed
];

const columnHeadersDroneRoute = ['Order ID', 'Drone latitude', 'Drone longitude']
const tableDroneRoute = "drone-route"
const headerDroneRoute = "drone-route-headers"
const bodyDroneRoute = "drone-route-body"

// Call the function to update table entries
updateTableEntries(drone_locations, columnHeadersDroneRoute, tableDroneRoute, headerDroneRoute, bodyDroneRoute);

// Sample data for updating the scheduler table
const ground_locations = [
    { Order_ID: 1, Latitude: 60.2554, Longitude: 2.4744},
    { Order_ID: 2, Latitude: 60.33448, Longitude: 2.844},
    // Add more data as needed
];

const columnHeadersGroundRoute = ['Order ID', 'Ground latitude', 'Ground longitude']
const tableGndLocations = "ground-route"
const headerGndLocations = "ground-route-headers"
const bodyGndLocations = "ground-route-body"

// Call the function to update table entries
updateTableEntries(ground_locations, columnHeadersGroundRoute, tableGndLocations, headerGndLocations, bodyGndLocations);
import GeometryUtil from "leaflet-geometryutil"

export const DRAW_ACTION_TYPES  = {
    ADD_MARKER: 'ADD_MARKER',
    EDIT_MARKER: 'EDIT_MARKER',
}

const rad2deg = (rad) =>{
    return rad*(180/Math.PI)
}
const deg2rad = (deg) => {
    return deg*(Math.PI/180)
}

export const handleHoverMarker = (event, n_states, id_marker, table_id) => {
    // Show a tooltip with the order at which the marker was created
    
    if (table_id.includes('drone')) {
        event.target.editing._marker.bindTooltip(`DRONE at: ${n_states+1}`)    
    }
    else if (table_id.includes('ground')) {
        event.target.editing._shape.bindTooltip(`GROUND at: ${n_states+1}`)    
    }

    // Highlight the row of the table that corresponds to this marker
    const mymarkers = document.querySelectorAll(`#${table_id} tbody tr`)

    for (const [, rows] of Object.entries(mymarkers)){
        if (rows.children[0].innerText === `${id_marker}` ){
            rows.style.backgroundColor = 'rgb(255, 109, 25)';
            rows.style.color = '#fff';
        }
        else {
            rows.style.backgroundColor = "";
            rows.style.color = '#000'
        }
    }
}

/**
 * 
 * @param {numeric} b - Bearing angle from drone to ground. Lies in [-180, 180] 
 * @param {numeric} a - Bearing angle from drone to its heading direction. Lies in [-180, 180]
 * @returns {numeric} y - Yaw to set in drone gimbal w.r.t. the drone heading direction. 
 */

export function yaw_from_bearings (b, a) {
    let y = 0;
    
    if ((a > 0) && (b > 0) && (a < 90) & (b < 90) && (a > b)) {
        y = a - b
    }
    else if ((a > 0) && (a < 90) && (b < 0) && (b < -90)) {
        y = 360 - (a - b)
    }
    else if ((a > 0) && (a > 90) && (b < 0) && (b < -90)) {
        y = 360 - (a - b)
    }
    else if ((a < 0) && (a < -90) && (b > 0) && (b > 90)) {
        y = b-a-360
    }
    else {
        y = b - a
    }
    
    return y
}

/**
 * 
 * @param {L.latLng} droneCoords  - Drone coordinates in a Leaflet LatLng object
 * @param {L.latLng} groundCoords - Ground coordinates in a Leaflet LatLng object
 * @param {numeric} droneHeading - Bearing angle from drone to its heading direction. Lies in [-180, 180]. This is the usual heading direction of a node: angle between the north and where the noide is pointing.
 * @returns {numeric} - Yaw angle in degrees to set in gimbal drone. Measured w.r.t. drone heading direction, WHICH IS THE 0 ANGLE FOR THE GIMBAL REFERENCE SYSTEM.
 */
export function drone_yaw_to_set(droneCoords, groundCoords, droneHeading) {

    const b = L.GeometryUtil.bearing(droneCoords, groundCoords)
    //const a = L.GeometryUtil.bearing(droneCoords, droneHeading)

    return yaw_from_bearings(b, droneHeading)
}

/**
 * Computes the drone heading in the specific case where the drone heads to next marker on the map.
 * The heading direction of the drone is then point to the next marker on the map.
 * @param {L.latLng} thisCoords - This marker coordinates in a Leaflet LatLng object
 * @param {L.latLng} nextCoords - Next marker coordinates in a Leaflet LatLng object
 * @returns {number} - Bearing angle from this marker to the next marker on the map
 */
export function drone_heading_to_next_marker(thisCoords, nextCoords) {
    return L.GeometryUtil.bearing(thisCoords, nextCoords)
}

/**
 * 
 * @param {numeric} beta  - Bearing angle in degrees for two coordinates
 * @returns Angle in degrees w.r.t North of the direction perpendicular to the line segment between the two coordinates considered for the angle 'beta'
 */
const anglesForMarkersExtendedLimits = (beta) => {
    let ang_clockwise = 0
    let ang_counterclockwise = 0

    // 1st cuadrant
    if ((beta > 0 ) && (beta <= 90)) {
        ang_clockwise = beta + 90
        ang_counterclockwise = beta - 90
    }
    // 2nd cuadrant
    if ((beta < 0 ) && (beta >= -90)) {
        ang_clockwise = beta + 90
        ang_counterclockwise = beta - 90
    }
    // 3rd cuadrant
    if ((beta < 0 ) && (beta < -90)) {
        ang_clockwise = 360 + beta - 90
        ang_counterclockwise = beta + 90
    }
    // 4th cuadrant
    if ((beta > 0 ) && (beta > 90)) {
        ang_clockwise = beta - 90
        ang_counterclockwise = beta + 90 - 360
    }

    return {ang_clockwise, ang_counterclockwise}
}

/**
 * Computes a rectangle enclosing the line segment between two points.
 * The width of the rectangle is controlled by the parameter 'd'.
 * @param {numeric} d - Distance {m] between two coordinates
 * @param {L.latLng} thisCoords - Coordinates of source point
 * @param {L.latLng} nextCoords - Coordinates of destination point
 * @returns 
 */

export const computeRectangle = (d, thisCoords, nextCoords) => {
    const beta = L.GeometryUtil.bearing(thisCoords, nextCoords) 

    const {ang_clockwise, ang_counterclockwise} = anglesForMarkersExtendedLimits(beta)
    
    const this_point_clockwise = L.GeometryUtil.destination(thisCoords, ang_clockwise, d)
    const this_point_counterclockwise = L.GeometryUtil.destination(thisCoords, ang_counterclockwise, d)

    const next_point_clockwise = L.GeometryUtil.destination(nextCoords, ang_clockwise, d)
    const next_point_counterclockwise = L.GeometryUtil.destination(nextCoords, ang_counterclockwise, d)

    return {this_point_clockwise, this_point_counterclockwise, next_point_clockwise, next_point_counterclockwise}
}
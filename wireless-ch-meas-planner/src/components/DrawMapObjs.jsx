import { Polyline } from "react-leaflet";
import { DroneMarkersContext } from "../context/dronemarkers.jsx";
import { useContext } from "react";
import { drone_heading_to_next_marker, drone_yaw_to_set } from "../logic/utils.js"
import GeometryUtil from "leaflet-geometryutil"

export function DrawDronePath () {
    const {markers} = useContext(DroneMarkersContext)

    return (
        <>
            { markers.map((entry, cnt)=> {
                if (cnt > 0) {
                    const position = [[entry.lat, entry.lng], [markers[cnt-1].lat, markers[cnt-1].lng]];
                    return(
                        <Polyline key={cnt} pathOptions={{color: 'lime'}} positions={position}></Polyline>
                    )
                }                
            })}        
        </>
    )
}

export function DrawDroneGimbalYaw () {    
    const { markers } = useContext(DroneMarkersContext)

    return (
        <>
            {   
                markers.map((entry, cnt)=> {
                    if (cnt < markers.length - 1) {
                        const thisCoords = L.latLng(entry.lat, entry.lng)
                        const nextCoords = L.latLng(markers[cnt+1].lat, markers[cnt+1].lng)

                        const droneHeading = drone_heading_to_next_marker(thisCoords, nextCoords)
                        const drone_gimbal_yaw_wrt_drone_head = drone_yaw_to_set(thisCoords, groundCoords, droneHeading)

                        const drone_gimbal_yaw_heading_point = L.GeometryUtil.destination(thisCoords, drone_gimbal_yaw_wrt_drone_head, 5)
                        const line_gimbal_heading = [[thisCoords.lat, thisCoords.lng], 
                                                     [drone_gimbal_yaw_heading_point.lat, drone_gimbal_yaw_heading_point.lng]]
                        return (
                            <Polyline pathOptions={{color: 'red'}} positions={line_gimbal_heading}></Polyline>
                        )
                    }
                })                
            }
        </>
    )
}
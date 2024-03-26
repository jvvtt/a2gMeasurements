import { useContext } from "react"
import { DroneMarkersContext } from "../context/dronemarkers.jsx"
import { PDRSZonesContext } from "../context/pdrszones.jsx"
import GeometryUtil from "leaflet-geometryutil"
import { Polygon } from "react-leaflet"
import { flight_geography_opts, contingency_volume_opts, ground_risk_buffer_opts } from "../constants/constants.js"
import { DroneRegulationDefinitions } from "../logic/droneOperationsRules.js"
import { computeRectangle } from "../logic/utils.js"

export function FlightGeography () {
    const { markers } = useContext(DroneMarkersContext)

    const distBoundFlightGeography = DroneRegulationDefinitions.Scv

    return (
        <>
        { 
            markers.map((entry, cnt) => {
                if (cnt < markers.length - 1) {
                    const thisCoords = L.latLng(entry.lat, entry.lng)
                    const nextCoords = L.latLng(markers[cnt+1].lat, markers[cnt+1].lng)
                    const {this_point_clockwise, this_point_counterclockwise, next_point_clockwise, next_point_counterclockwise} = computeRectangle(distBoundFlightGeography, thisCoords, nextCoords)
                    
                    const rect_vertex = [[this_point_clockwise.lat, this_point_clockwise.lng],
                                         [this_point_counterclockwise.lat, this_point_counterclockwise.lng],
                                         [next_point_counterclockwise.lat, next_point_counterclockwise.lng],
                                         [next_point_clockwise.lat, next_point_clockwise.lng]]
                    return (
                        <Polygon key={cnt} positions={rect_vertex} pathOptions={flight_geography_opts}></Polygon>
                    )
                }                
            })
        }
        </>
    )
}


export function FlightGeography2(){
    const { fgVertex, cvVertex, grbVertex } = useContext(PDRSZonesContext) 
    return (
        <>
            <Polygon positions={fgVertex} pathOptions={flight_geography_opts}></Polygon>
            <Polygon positions={cvVertex} pathOptions={contingency_volume_opts}></Polygon>
            <Polygon positions={grbVertex} pathOptions={ground_risk_buffer_opts}></Polygon>
        </>
    )
}
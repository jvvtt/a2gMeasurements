import { useContext } from "react"
import { MapContext } from "../context/map"
import GeometryUtil from "leaflet-geometryutil"
import { Polygon } from "react-leaflet"
import { flight_geography_opts } from "../constants/constants.js"
import { DroneRegulationDefinitions } from "../logic/droneOperationsRules.js"

const rad2deg = (rad) =>{
    return rad*(180/Math.PI)
}
const deg2rad = (deg) => {
    return deg*(Math.PI/180)
}

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

const computeRectangle = (d, thisCoords, nextCoords) => {
    const beta = L.GeometryUtil.bearing(thisCoords, nextCoords) 

    const {ang_clockwise, ang_counterclockwise} = anglesForMarkersExtendedLimits(beta)
    
    const this_point_clockwise = L.GeometryUtil.destination(thisCoords, ang_clockwise, d)
    const this_point_counterclockwise = L.GeometryUtil.destination(thisCoords, ang_counterclockwise, d)

    const next_point_clockwise = L.GeometryUtil.destination(nextCoords, ang_clockwise, d)
    const next_point_counterclockwise = L.GeometryUtil.destination(nextCoords, ang_counterclockwise, d)

    return {this_point_clockwise, this_point_counterclockwise, next_point_clockwise, next_point_counterclockwise}
}

export function FlightGeography () {
    const { markers } = useContext(MapContext)

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